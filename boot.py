# boot.py -- run on boot-up
import os
import time
import pycom
import machine
import secrets
from network import WLAN
from machine import UART

uart = UART(0, 115200)
os.dupterm(uart)

uart1 = UART(1, 9600)

pycom.heartbeat(False)
pycom.rgbled(0x7f0000) # red

wlan = WLAN() # get current object, without changing the mode

if machine.reset_cause() != machine.SOFT_RESET:
    wlan.init(mode=WLAN.STA)
    # configuration below MUST match your home router settings!!
    wlan.ifconfig(config=(secrets.WIFI_IP, secrets.WIFI_SUBNET, secrets.WIFI_GATEWAY, secrets.WIFI_DNS1))

nets = wlan.scan()

for net in nets:
    if net.ssid == secrets.WIFI_SSID:
        if not wlan.isconnected():
            wlan.connect(secrets.WIFI_SSID, auth=(WLAN.WPA2, secrets.WIFI_PASS), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        pycom.rgbled(0x007f00) # green
        print("Connected to " + secrets.WIFI_SSID)
        time.sleep(3)
        pycom.rgbled(0)
        break
