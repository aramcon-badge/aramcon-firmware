from adafruit_ble.uuid import StandardUUID
from adafruit_ble.characteristics.stream import StreamIn
from arambadge import badge
import adafruit_ble.services
import time

class Service(adafruit_ble.services.Service):
    uuid = StandardUUID(0xfeee)
    _disp_rx = StreamIn(uuid=uuid, timeout=1.0, buffer_size=100)

    def __init__(self):
        super().__init__()

    def update(self):
        buffer = []
        while self._disp_rx.in_waiting > 0:
            byte = int.from_bytes(self._disp_rx.read(1), 'little')
            buffer.append(byte)
            if len(buffer) == 6:
                badge.pixels[0] = tuple(buffer[0:3])
                badge.pixels[1] = tuple(buffer[3:6])
                buffer = []
                time.sleep(1)
