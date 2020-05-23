# AramCon Badge 2020 Main Firmware
from arambadge import badge
from eeprom import EEPROM
import addons
import time
import supervisor
from apps.menu.main import MenuApp

print("AramCon Badge 2020 Firmware")

def i2c_device_available(i2c, addr):
    if i2c.try_lock():
        try:
            return addr in i2c.scan()
        finally:
            i2c.unlock()

e = EEPROM(badge.i2c)
menu = MenuApp()

name_refresh = 5
while True:
    if name_refresh:
        try:
            badge.show_bitmap('nametag.bmp')
            name_refresh -= 1
        except:
            name_refresh = 0

    for i in range(4):
        badge.pixels[i] = (255 * badge.left, 255 * badge.up, 255 * badge.right)
    badge.vibration = badge.down

    buttons = badge.gamepad.get_pressed()
    if buttons & badge.BTN_ACTION:
        # Wait until the action button is released
        badge.vibration = True
        while badge.gamepad.get_pressed() & badge.BTN_ACTION:
            pass
        badge.vibration = False
        menu.run()
        name_refresh = 5

    addon = addons.read_addon_descriptor(e)
    if addon:
        print("Add-on connected: {}".format(addon['name']))
        driver = __import__('drivers/' + addon['driver'].replace('.py', ''))
        try:
            driver.main(addon)
        finally:
            supervisor.reload()
