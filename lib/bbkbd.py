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
    ['sym', 'D', 'T', 'Y', 'I'],
    ['A', 'P', 'Shift', 'Enter', 'Backspace'],
    ['Alt', 'X', 'V', 'B', '$'],
    ' ZCNM',
    ['Microphone', 'Shift', 'F', 'J', 'K'],
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

def kbd_decode_key(code):
    col = code & 7
    row = (code >> 3) & 7
    return kbd_matrix[row-1][col-1]

def kbd_decode_event(event):
    key = kbd_decode_key(event)
    if event & RESP_FLAG_KEYDOWN:
        return ("keydown", key)
    if event & RESP_FLAG_KEYUP:
        return ("keyup", key)
    return ("repeat", key)
