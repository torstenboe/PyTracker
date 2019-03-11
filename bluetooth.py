import ubinascii
from network import Bluetooth
bluetooth = Bluetooth()

bluetooth.set_advertisement(name="LoPy", service_uuid=b'1234567890123456')
bluetooth.advertise(True)
