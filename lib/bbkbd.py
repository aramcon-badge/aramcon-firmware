# BB Keyboard Driver
# 
# Released under The MIT License (MIT)
#
# Copyright (c) 2021 Uri Shaked

from arambadge import badge

KBD_ADDRESS       = 0x42
CMD_BACKLIGHT_ON  = 0x03
CMD_RESET         = 1 << 7
RESP_RESET        = 0xfe
RESP_EOF          = 0xff
RESP_FLAG_KEYDOWN = 1 << 6
RESP_FLAG_KEYUP   = 1 << 7

kbd_matrix = [
    'QERUO',
    'WSGHL',
    ('sym', 'D', 'T', 'Y', 'I'),
    ('A', 'P', 'RShift', 'Enter', 'Backspace'),
    ('Alt', 'X', 'V', 'B', '$'),
    ' ZCNM',
    ('Microphone', 'LShift', 'F', 'J', 'K'),
]

kbd_matrix_alt = [
    '#23_+',
    '14/:"',
    ('sym', '5', '(', ')', '-'),
    ('*', '@', 'RShift', 'Enter', 'Backspace'),
    ('Alt', '8', '?', '!', 'Speaker'),
    ' 79,.',
    ('0', 'LShift', '6', ';', '\''),
]

def kbd_init():
    badge.i2c.try_lock()
    try:
        badge.i2c.writeto(KBD_ADDRESS, bytes([CMD_RESET | CMD_BACKLIGHT_ON]))
    finally:
        badge.i2c.unlock()

def kbd_read():
    buf = bytearray(1)
    badge.i2c.try_lock()
    try:
        badge.i2c.readfrom_into(KBD_ADDRESS, buf)
        if buf[0] != RESP_RESET and buf[0] != RESP_EOF:
            return buf[0]
        return None
    finally:
        badge.i2c.unlock()

def kbd_decode_key(code, alt = False):
    matrix = kbd_matrix_alt if alt else kbd_matrix
    col = code & 7
    row = (code >> 3) & 7
    return matrix[row-1][col-1]

def kbd_decode_event(event, alt = False):
    key = kbd_decode_key(event, alt)
    if event & RESP_FLAG_KEYDOWN:
        return ("keydown", key)
    if event & RESP_FLAG_KEYUP:
        return ("keyup", key)
    return ("repeat", key)

class BBKeyboard:
    def __init__(self):
        self.reset()

    def reset(self):
        kbd_init()
        self.shift = False
        self.alt = False
        self.last_key = None
    
    def read(self):
        event = kbd_read()
        if not event:
            return None
        alt = self.alt
        (event_type, key) = kbd_decode_event(event, alt)
        if event_type != 'keydown':
          return None
        self.last_key = key
        self.alt = False
        if len(key) == 1:
            shift = self.shift
            self.shift = False
            return key if shift else key.lower()
        elif key == 'Enter':
            return '\n'
        elif key == 'Backspace':
            return '\b'
        elif key == 'LShift' or key == 'RShift':
            self.shift = True
        elif key == 'Alt':
            self.alt = True
        return None
