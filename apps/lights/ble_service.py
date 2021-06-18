from adafruit_ble.uuid import StandardUUID
from adafruit_ble.characteristics.stream import StreamIn
from arambadge import badge
import adafruit_ble.services
import time

class Service(adafruit_ble.services.Service):
    uuid = StandardUUID(0xfeee)
    _disp_rx = StreamIn(uuid=StandardUUID(0xfeee), timeout=1.0, buffer_size=100)

    def __init__(self):
        super().__init__()
        self._buffer = []

    def update(self):
        while self._disp_rx.in_waiting > 0:
            byte = int.from_bytes(self._disp_rx.read(1), 'little')
            self._buffer.append(byte)
            if len(self._buffer) == 6:
                badge.pixels[0] = tuple(self._buffer[0:3])
                badge.pixels[1] = tuple(self._buffer[3:6])
                self._buffer = []
                time.sleep(1)
