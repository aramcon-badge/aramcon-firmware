from eeprom import EEPROM
from arambadge import badge
import addons

def initaddon(name, driver_name, data = b''):
    eeprom = EEPROM(badge.i2c)
    addons.write_addon_descriptor(eeprom, {
        "name": name,
        "driver": driver_name,
        "data": data,
    })
    return addons.read_addon_descriptor(eeprom)
