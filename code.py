# AramCon Badge 2020 Main Firmware

from arambadge import badge
from eeprom import EEPROM
import addons
import time
import supervisor
from nametags.nametags import NametagsApp

REFRESH_TIME = 3

print("AramCon Badge 2020 Firmware")

def i2c_device_available(i2c, addr):
    if i2c.try_lock():
        try:
            return addr in i2c.scan()
        finally:
            i2c.unlock()

e = EEPROM(badge.i2c)
addon = addons.read_addon_descriptor(e)

apps = [NametagsApp(not addon)]
active_app = apps[0]

last_update = time.monotonic()

while True:
    
    active_app.update()
    if (time.monotonic() - last_update) > REFRESH_TIME:
        active_app.render()

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
