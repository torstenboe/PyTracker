import machine
from machine import I2C
import pycom
import sys
import time
# see https://github.com/inmcm/micropyGPS/blob/master/micropyGPS.py
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
if 'date' in last_data:
    print("@ ", last_data['date'])
if 'latitude' in last_data and 'longitude' in last_data:
    print("> ", last_data['latitude'], " ", last_data['longitude'])
i2c.deinit()
