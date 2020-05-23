# AramCon Badge Floppy Driver
# Released under The MIT License (MIT)
#
# Copyright (c) 2020, Uri Shaked

from arambadge import badge
from eeprom import EEPROM
from eepromvfs import mount_eeprom
import os
import storage
import struct

# Floppy Add-on data binary format:
#
# Offset Size     Description 
# ------ ----     -----------
# 0      byte     Flags. Reserved and must be 0
# 1      byte     EEPROM address. Usually 0x51
# 3      byte     EEPROM memory size exponent (e.g. 16 for 64kbit)
# 2      byte     EEPROM page size exponent (e.g. 7 for 128 bytes)
#
# If the data is not present we assume 32kbit EEPROM at 0x51 with 64-byte pages.
# 
# JSON addon descriptors are not supported at this time. 

# Common floppy EEPROM configuration profiles
ADDON_DATA_32KB = struct.pack('4B', 0, 0x51, 15, 6)
ADDON_DATA_64KB = struct.pack('4B', 0, 0x51, 16, 7)

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

def read_config(addon):
    data = addon.get('data', b'')
    if len(data) >= 4:
        flags, addr, size_exp, page_exp = struct.unpack('4B', data[:4])
        if addr <= 0x50 or addr > 0x57:
            raise Error('Invalid EEPROM address for floppy storage')
        if size_exp < 14 or size_exp > 16:
            raise Error('Unsupported floppy storage size: {}'.format(2 ** size_exp))
        return (addr, 2 ** size_exp, 2 ** page_exp)
    return (0x51, 32768, 64) # Default config

def create_eeprom(addon):
    eeprom_addr, eeprom_size, page_size = read_config(addon)
    return EEPROM(badge.i2c, eeprom_addr=eeprom_addr, eeprom_size=eeprom_size, page_size=page_size)

def main(addon):
    try:
        storage.umount('/floppy')
    except:
        pass
    print("Floppy disk driver v1.0")
    eeprom = create_eeprom(addon)
    fs = mount_eeprom(eeprom, "/floppy")
    print("Floppy label:", fs.label)
    print("Files:", os.listdir('/floppy'))
    print("Free space", free_bytes(fs))
    if isdir('/viral'):
        print("Copying files to floppy")
        prepare_floppy('/viral', fs)
        storage.umount('/floppy')
        print("Floppy ready!")
    else:
        if isfile('/floppy/main.py'):
            __import__('/floppy/main')
