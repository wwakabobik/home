from time import sleep

import requests
from SX127x.LoRa import *
from SX127x.board_config import BOARD


endpoint = "http://0.0.0.0:80/api/v1"


class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            sleep(.5)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        formatted_payload = bytes(payload).decode("utf-8", 'ignore')
        status = self.send_to_home(formatted_payload)
        if status:
            sleep(1)  # we got the data, force sleep for a while to skip repeats
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    def send_to_home(self, payload):
        if str(payload[:2]) == '0,':
            requests.post(url=f'{endpoint}/add_wind_data', json={'data': payload})
        elif str(payload[:2]) == '1,':
            requests.post(url=f'{endpoint}/add_power_data', json={'data': payload})
        else:
            print("Garbage collected, ignoring")  # debug
            status = 1
        return status


def run_lora():
    BOARD.setup()
    lora = LoRaRcvCont(verbose=False)
    lora.set_mode(MODE.STDBY)
    # Medium Range  Defaults after init are 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on 13 dBm
    lora.set_pa_config(pa_select=1)
    assert (lora.get_agc_auto_on() == 1)

    try:
        lora.start()
    finally:
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()
