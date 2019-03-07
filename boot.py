import machine
from network import WLAN
from secrets import ACCESS
wlan = WLAN(mode=WLAN.STA)
access = ACCESS()

nets = wlan.scan()
for net in nets:
    if net.ssid == access.ssid():
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, access.pwd()), timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break
