# ARAMCON 2 Badge Main Firmware
from arambadge import badge

# Before going on, give the user some indication we're starting...
badge.pixels.fill((0, 0, 10))

from eeprom import EEPROM
import addons
import time
import supervisor
from welcome import show_welcome
from apps.menu.main import MenuApp

# Extra start-up indication for the user
badge.vibration = True
print("ARAMCON 2 Badge Firmware")

def i2c_device_available(i2c, addr):
    if i2c.try_lock():
        try:
            return addr in i2c.scan()
        finally:
            i2c.unlock()

def main_screen():
    badge.display.push_mode(badge.display.MODE_QUICK)
    try:
        badge.show_bitmap('nametag.bmp')
    except:
        show_welcome()
    while badge.display.time_to_refresh > 0:
        pass
    badge.display.refresh()
    badge.display.pop_mode()

e = EEPROM(badge.i2c)
menu = MenuApp()

main_screen()

last_addon = None
badge.vibration = False
badge.pixels.fill(0)
while True:
    if badge.action:
        badge.vibration = True
        time.sleep(0.1)
        badge.vibration = False
        menu.run()
        main_screen()

    addon = addons.read_addon_descriptor(e)
    if addon:
        if last_addon != addon['driver']:
            print("Add-on connected: {}".format(addon['name']))
            last_addon = addon['driver']
            driver = __import__('drivers/' + addon['driver'].replace('.py', ''))
            had_error = True
            try:
                driver.main(addon)
                had_error = False
            finally:
                if had_error:
                    supervisor.reload()
                main_screen()
    else:
        last_addon = None
