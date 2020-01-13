import time
from arambadge import badge
from eeprom import EEPROM
from eepromvfs import mount_eeprom
import os
import storage

DIR_FLAG = 0x4000
FILE_FLAG = 0x8000

def isdir(path):
    try:
        return os.stat(path)[0] & DIR_FLAG
    except:
        return False

def isfile(path):
    try:
        return os.stat(path)[0] & FILE_FLAG
    except:
        return False

def free_bytes(fs):
    f_bsize, f_frsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, f_favail, f_flag, f_namemax = fs.statvfs('/')
    return f_bsize * f_bavail

def prepare_floppy(source_dir, fs):
    for name in os.listdir(source_dir):
        with open(source_dir + '/' + name, 'rb') as f:
            if name == 'label.txt':
                fs.label = f.read().strip()
                continue
            with fs.open(name, 'wb') as outf:
                outf.write(f.read())

def main(addon):
    print("Floppy disk driver v1.0")
    # TODO: read actual floppy size from addon.data, don't just assume 32kByte
    eeprom = EEPROM(badge.i2c, eeprom_addr=0x51, eeprom_size=32768, page_size=64)
    fs = mount_eeprom(eeprom, "/floppy")
    print("Floppy label:", fs.label)
    print("Files:", os.listdir('/floppy'))
    print("Free space", free_bytes(fs))
    if isdir('/viral'):
        print("Copying files to floppy")
        prepare_floppy('/viral', fs)
        print("Floppy ready!")
    else:
        if isfile('/floppy/main.py'):
            __import__('/floppy/main')
    storage.umount('/floppy')
