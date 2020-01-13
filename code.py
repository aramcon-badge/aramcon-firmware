# AramCon Badge 2020 Main Firmware

from arambadge import badge
from eeprom import EEPROM
import addons
import time
import supervisor

print("AramCon Badge 2020 Firmware")

def i2c_device_available(i2c, addr):
    if i2c.try_lock():
        try:
            return addr in i2c.scan()
        finally:
            i2c.unlock()

e = EEPROM(badge.i2c)
addon = addons.read_addon_descriptor(e)

if not addon:
    badge.show_bitmap('assets/banner.bmp')

while True:
    for i in range(4):
        badge.pixels[i] = (255 * badge.left, 255 * badge.up, 255 * badge.right)
    badge.vibration = badge.action

    addon = addons.read_addon_descriptor(e)
    if addon:
        print("Add-on connected: {}".format(addon['name']))
        driver = __import__('drivers/' + addon['driver'].replace('.py', ''))
        try:
            driver.main(addon)
        finally:
            supervisor.reload()
