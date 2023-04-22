# RaspberryP2PLoRa
A repository for the client and server code to connect a Arduino MCU to Raspberry Pi via LoRa and send the data to Azure IoT Hub

## RaspberryPiLoRaServer

This is the Python implementation for the receiving LoRa server. Raspberry Pi Server continously receives data from any node with the same LoRa configuration and forwards the data to Azure IoT Hub.

## Arduino Feather Client

This folder contains an Arduino IDE sketch implementation for a LoRa sender. The Arduino Feather reads the temperature and humidity data from a DHT22 sensor and sends it via LoRa to a receiving server. 