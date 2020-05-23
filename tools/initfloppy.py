import storage
from eepromvfs import EEPROMVFS
from drivers import floppy
from .initaddon import initaddon

def initfloppy(label="JEDI", capacity=64):
    data = floppy.ADDON_DATA_64KB if capacity == 64 else floppy.ADDON_DATA_32KB
    addon = initaddon("Floppy", "floppy", data)
    eeprom = floppy.create_eeprom(addon)
    eepromvfs = EEPROMVFS(eeprom)
    print("Formating {}K".format(eeprom.size // 1024))
    storage.VfsFat.mkfs(eepromvfs)
    print("Format complete.")
    print("")
    print("Volume label (11 characters, ENTER for none)? {}".format(label))
    fs = storage.VfsFat(eepromvfs)
    fs.label = label
