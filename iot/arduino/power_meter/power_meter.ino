/* ***************************************************************************
 * This sketch contains wind speed/direction sensor logic        .           *
 *                                                                           *
 * Sketch uses Arduino Nano controller, and it contains limited amount of    *
 * RAM. Due to that - to achieve stability - at least 20% of RAM should be   *
 * free and debug serial output is commented-out in this sketch.             *
 *                                                                           *
 * Flight controller contains:                                               *
 *    - Arduino Nano v3 (CH340g), 2xAC712 (30A) as ampermeter,               *
 *    B25 Voltage Sensor                                                     *
 *    - Wireless LoRA module (SX1278 (Ra-02)) used as output (433Mhz);       *
 *                                                                           *
 * Note:                                                                     *
 *    - To disble debug outputs comment/uncomment related define;            *
 *    - To use lower current by default for AC712 re-define C1, C2 and C3.   *
 *                                                                           *
 * Logic:                                                                    *
 *    1) Init LoRa;                                                          *
 *    2) Start measure and current several times for a long period;          *
 *    3) Send all data, including power calculations via LoRA                *
 *    4) Go to point 2.                                                      *
 *                                                                           *
 * Sketch written by Iliya Vereshchagin 2021.                                *
 *****************************************************************************/

// Desired outputs, comment/uncomment what is needed
#define DEBUG

// Required includes
#include <SPI.h>
#include <LoRa.h>

/* Globals section */

// Voltage sensors consts
const float R1 = 30000.0;
const float R2 = 7500.0;
const int VOLTAGE_PIN = A1;

// Current sensor (30A) consts
const float C1 = 0.0742;
const float C2 = 37.873;
const float C3 = 1000.0;
const int CURRENT_IN_PIN = A0;
const int CURRENT_OUT_PIN = A3;


// Power Data
struct power_data 
{
    float avg_voltage;
    float avg_current;
    float avg_power;
    float avg_consumption;
};


// Measurement config
const long meas_period = 300000;
const long period_tick = 1000;
const long count_measurements = meas_period / period_tick;


// LoRA config
const int LORA_SEND_RETRIES = 5; // how much ackets will be sent
const int LORA_SEND_DELAY = 20;  // delay between send data
const int LORA_POWER = 20;       // set TX power to maximum 
const int LORA_RETRIES = 12;     // try to init LoRa several times before error
const int LORA_DELAY = 500;      // delay between retries 

// Device id
const String DEVICE_ID = "1";
 
void setup() 
{
    Serial.begin(9600);
    LoRa_init();
}

void loop()
{
    power_data pwr;
    pwr = get_averages();
    LoRa_send(pwr);
}

// Power Data

float read_voltage()
{
    float vout = 0.0;
    float vin = 0.0;
    int value = 0;
    value = analogRead(VOLTAGE_PIN);
    vout = (value * 5.0) / 1024.0;
    vin = vout / (R2 / (R1 + R2));
    #ifdef DEBUG2
    Serial.print("U = ");
    Serial.print(vin);
    Serial.println("V");
    #endif
    return vin;
}

float read_current(int pin)
{
    float current = 0;
    current = (C1 * analogRead(pin) - C2) / C3;
    #ifdef DEBUG2
    Serial.print("I = ");
    Serial.print(current);
    Serial.println("A");
    #endif
    return current;
}

power_data get_averages()
{
    power_data pwr;
    float voltage = 0;
    float current_in = 0;
    float current_out = 0;
    float power = 0;
    float consumption = 0;
    float current_correction = 0;
    
    for (long j=0; j < count_measurements; j ++)
    {
        voltage += read_voltage();
        current_correction = read_current(CURRENT_IN_PIN);
        if (current_correction < 0.0)
        {
            current_correction = 0.0;
        }
        current_in += current_correction;
        current_correction = read_current(CURRENT_OUT_PIN);
        if (current_correction < 0.0)
        {
            current_correction = 0.0;
        }
        current_out += current_correction;
        power += voltage*current_in;
        consumption += voltage*current_out;
        delay(period_tick);
    }
    pwr.avg_voltage += (voltage/count_measurements);
    pwr.avg_current += (current_in/count_measurements);
    pwr.avg_power += (power/count_measurements);
    pwr.avg_consumption += (consumption/count_measurements);
    
    #ifdef DEBUG
    Serial.print("AVG U = ");
    Serial.print(pwr.avg_voltage);
    Serial.println("V");
    Serial.print("AVG I = ");
    Serial.print(pwr.avg_current);
    Serial.println("A");
    Serial.print("AVG P = ");
    Serial.print(pwr.avg_power);
    Serial.println("W");
    Serial.print("AVG C = ");
    Serial.print(pwr.avg_consumption);
    Serial.println("Wmin");
    #endif

    return pwr;
}

// LoRA Functions

void init_LoRa()  // try to init LoRA at 433Mhz for several retries
{
    bool success = false;
    for (int i=0; i < LORA_RETRIES; i++)
    
    {
        if (LoRa.begin(433E6))
        {
            success = true;
            break;
        }
        delay(LORA_DELAY);
    }
    if (!success)
    {
        #ifdef DEBUG
        Serial.println("LoRa init failed.");
        #endif
        stop(4);
    }
    
    LoRa.setTxPower(LORA_POWER);  // aplify TX power
    #ifdef DEBUG
    Serial.println("LoRa started!");
    #endif  
}
#endif

void LoRa_send(power_data data)
{
    String packet = DEVICE_ID + "," + String(data.avg_voltage,2) + ",";
    packet += String(data.avg_current,2) + "," + String(data.avg_power,2) + "," +String(data.avg_consumption,2);
    #ifdef DEBUG
    Serial.println("Sending via LoRa packet with payload: " + packet);
    #endif
    for (int i=0; i < LORA_SEND_RETRIES; i++)
    {
        LoRa.beginPacket();  // just open packet
        LoRa.print(packet);  // send whole data
        LoRa.endPacket();    // end packet
        delay(LORA_SEND_DELAY);
    }  
}
