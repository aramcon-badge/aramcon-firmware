# Nametags app for Aramcon Badge
# Copyright (C) 2019, Uri Shaked

from adafruit_ble.uuid import StandardUUID
from adafruit_ble.services import Service
from adafruit_ble.characteristics.stream import StreamIn
from arambadge import badge
from .bitmapsave import bitmap_save
import displayio    
import storage

# Protocol:
# struct packet {
#   int has_offset: 1; // MSB
#   int size: 7;
#   uint16_t offset; // little-endian. Optional, only if has_offset is 1
#   uint8_t bytes[size];
# }

class NameService(Service):
    uuid = StandardUUID(0xfeef)
    _disp_rx = StreamIn(uuid=StandardUUID(0xfeee), timeout=1.0, buffer_size=64)

    def __init__(self):
        super().__init__()
        self._bitmap = displayio.Bitmap(badge.display.width, badge.display.height, 2)
        self._palette = displayio.Palette(2)
        self._palette[0] = 0x000000
        self._palette[1] = 0xffffff
        self._offset = 0
        self._bufsize = 0
        self._dirty = False
        self._ledstate = False
     
    def update(self):
        while self._disp_rx.in_waiting > 0:
            if self._bufsize == 0:
                value = int.from_bytes(self._disp_rx.read(1), 'little')
                if value == 0:
                    self._finish_update()
                    continue
                self._bufsize = value & 0x7f
                if value & 0x80:
                    self._offset = None
            if self._offset is None and self._disp_rx.in_waiting >= 2:
                self._offset = int.from_bytes(self._disp_rx.read(2), 'little')
            if self._bufsize > 0 and self._offset is not None:
                data = self._disp_rx.read(min(self._bufsize, self._disp_rx.in_waiting))
                self._bufsize -= len(data)
                for i in range(len(data)):
                    for bit in range(8):
                        self._bitmap[self._offset*8+bit] = 1 if data[i] & (1 << bit) else 0
                    self._offset += 1
                self._ledstate = not self._ledstate
                badge.pixels.fill((0, 0, 0x10 * self._ledstate))
        if self._dirty and badge.display.time_to_refresh == 0:
            badge.display.refresh()
            self._dirty = False

    def _store_bitmap(self):
        try:
            storage.remount('/', False)
        except:
            pass
        try:
            bitmap_save('/nametag.bmp', self._bitmap)
        except Exception as err:
            print("Couldn't save file: {}".format(err))
        try:
            storage.remount('/', True)
        except:
            pass
    
    def _finish_update(self):
        print("Update done!")
        self._offset = 0
        self._bufsize = 0
        self._ledstate = False
        badge.pixels.fill(0)
        frame = displayio.Group()
        frame.append(displayio.TileGrid(self._bitmap, pixel_shader=self._palette))
        badge.display.show(frame)
        self._dirty = True
        self._store_bitmap()
