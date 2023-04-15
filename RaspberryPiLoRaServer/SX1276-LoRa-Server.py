from time import sleep
from SX127x.LoRa import *
from SX127x.board_config import BOARD
import configparser
from azure.iot.device import IoTHubDeviceClient, Message
import json
import re

BOARD.setup()

class LoRaRcvCont(LoRa):
    connection_string = None
    iot_hub_device_client = None

    def __init__(self, verbose=True):
        super(LoRaRcvCont, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.connection_string = config['azureiot']['connectionstring']
        self.iot_hub_device_client = IoTHubDeviceClient.create_from_connection_string(self.connection_string)
        self.iot_hub_device_client.connect()

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        while True:
            sleep(.5)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()

    def parse_payload(self, payload_string):
        try:
            payload_trimmed = payload_string[:11]
            parts =  payload_trimmed.split(';')
            temp = re.sub("\u0000", "", parts[0])
            hum = re.sub("\u0000", "", parts[1])
            print(f'Temperature: {temp}')
            print(f'Humidity: {hum}')
            return temp, hum
        except:
            print('Cannot parse payload because not the expected foramt of temp;hum')
            return None, None

    def send_to_iothub(self, temp, hum):
        obj = { "temp" : temp, "hum" : hum}
        message = Message(json.dumps(obj))
        self.iot_hub_device_client.send_message(message)
        print(f'Message sent to IoT Hub: {message}')
        return True

    def on_rx_done(self):
        print("\nReceived: ")
        rssi = self.get_rssi_value()
        print(f'RSSI: {rssi}')
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        payload_str = bytes(payload).decode("utf-8",'ignore')
        print(payload_str)
        temp, hum = self.parse_payload(payload_str)
        self.send_to_iothub(temp, hum)
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT) 


lora = LoRaRcvCont(verbose=False)
lora.set_mode(MODE.STDBY)

#  Medium Range  Defaults after init are 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on 13 dBm
lora.set_pa_config(pa_select=1)
lora.set_freq(868.0)
lora.set_bw(BW.BW31_25)
lora.set_coding_rate(CODING_RATE.CR4_8)
lora.set_spreading_factor(9)
print('Started LoRa receiver with 868Mhz, BW 31.25, CR 4/8, SF 512 (9)\n')

try:
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
