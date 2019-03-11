import machine
from machine import I2C
from network import LoRa
import socket
import binascii
import struct
import pycom
import sys
import time

# Setup the LoRaWAN part
# Initialize LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN)
# create an ABP authentication params
dev_addr = struct.unpack(">l", binascii.unhexlify(secrets.DEV_ADDR.replace(' ','')))[0]
nwk_swkey = binascii.unhexlify(secrets.NWK_SWKEY.replace(' ',''))
app_swkey = binascii.unhexlify(secrets.APP_SWKEY.replace(' ',''))
# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
# remove all the non-default channels
for i in range(3, 16):
    lora.remove_channel(i)
# set the 3 default channels to the same frequency
lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(2, frequency=868100000, dr_min=0, dr_max=5)
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
# make the socket blocking
s.setblocking(False)

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
