import machine
from machine import I2C
from network import LoRa
import socket
import ubinascii
import struct
import pycom
import sys
import time

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
# create an OTAA authentication parameters
app_eui = ubinascii.unhexlify(secrets.APP_EUI)
app_key = ubinascii.unhexlify(secrets.APP_KEY)
# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
s.setblocking(True)
# send some data
s.send(bytes([0x01, 0x02, 0x03]))
# make the socket non-blocking
# (because if there's no data received it will block forever...)
s.setblocking(False)
# get any data received (if any...)
data = s.recv(64)
print(data)

# for microGPS see https://github.com/inmcm/micropyGPS/blob/master/micropyGPS.py
from micropyGPS import MicropyGPS
pycom.heartbeat(True)
print("Initializing...")
GPS_TIMEOUT_SECS=10
# init I2C to P21/P22
i2c = machine.I2C(0, mode=I2C.MASTER, pins=('P22', 'P21'))
# write to address of GPS
GPS_I2CADDR = const(0x10)
raw = bytearray(1)
i2c.writeto(GPS_I2CADDR, raw)
# create MicropyGPS instance
gps = MicropyGPS()
# start a timer
chrono = machine.Timer.Chrono()
chrono.start()
# store results here.
last_data = {}
print("Start reading GPS data...")
def check_for_valid_coordinates(gps):

    '''
    Given a MicropyGPS object, this function checks if valid coordinate
    data has been parsed successfully. If so, copies it over to global last_data.
    '''
    if gps.satellite_data_updated() and gps.valid:
        last_data['timestamp'] = gps.timestamp
        last_data['date'] = gps.date_string("long")
        last_data['latitude'] = gps.latitude_string()
        last_data['longitude'] = gps.longitude_string()
while True:
    # read some data from module via I2C
    raw = i2c.readfrom(GPS_I2CADDR, 16)
    # feed into gps object
    for b in raw:
        sentence = gps.update(chr(b))
        if sentence is not None:
            # gps successfully parsed a message from module
            # see if we have valid coordinates
            res = check_for_valid_coordinates(gps)
    elapsed = chrono.read()
    if elapsed > GPS_TIMEOUT_SECS:
        break
print("Finished.")
if 'timestamp' in last_data:
    print("@ ", last_data['timestamp'])
if 'date' in last_data:
    print("@ ", last_data['date'])
if 'latitude' in last_data and 'longitude' in last_data:
    print("> ", last_data['latitude'], " ", last_data['longitude'])
i2c.deinit()
