#!/usr/bin/env python3.7

from multiprocessing.pool import ThreadPool

from flask import Flask

from db.db import init_app
from lora_reciever import run_lora


app = Flask(__name__, template_folder='templates')  # fistly, start Flask

# import all routes
import routes.api
import routes.pages
import routes.single_page


if __name__ == '__main__':
    # Start LoRa receiver as subprocess
    pool = ThreadPool(processes=1)
    pool.apply_async(run_lora)
    # Start Flask server
    init_app(app)
    app.run(debug=True, host='0.0.0.0', port='80')
    # Teardown
    pool.terminate()
    pool.join()
