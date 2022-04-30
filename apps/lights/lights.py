import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics.stream import StreamIn
from arambadge import badge
import adafruit_ble.services
import displayio
import terminalio
from adafruit_display_text import bitmap_label

class Service(adafruit_ble.services.Service):
    uuid = VendorUUID(0xfeee)
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

class App:
    def __init__(self):
        self.ble = BLERadio()
        self.service = Service()
        self.advertisement = ProvideServicesAdvertisement(self.service)
        self.scan_response = Advertisement()
        self.scan_response.complete_name = "LIGHTS-SERVER"
        self.ble.start_advertising(self.advertisement, self.scan_response)

    def update(self):
        if self.ble.connected:
            self.service.update()

    def process_input(self):
        buttons = badge.gamepad.get_pressed()
        if buttons & badge.BTN_ACTION:
            self.cleanup()
            return True
        return False

    def render_instruction_screen(self):
        text = """--- Flashlight as a service ---

Connect using BLE to {mac:X}.
Send 6 bytes to {service_uid} to set the
color of the LEDs.

Press the action button to
exit the application.""".format(
            mac=int.from_bytes(self.ble.address_bytes, 'little'),
            service_uid=str(self.service.uuid)
        )
        print(text)

        screen = displayio.Group()
        lines_group = displayio.Group(x=8, y=10)
        for (index, line) in enumerate(text.splitlines()):
            lines_group.append(bitmap_label.Label(
                terminalio.FONT,
                text=line[0:40],
                color=0xffffff,
                y = index * 12,
                save_text=True
            ))
        screen.append(lines_group)
        badge.display.show(screen)
        while badge.display.time_to_refresh > 0:
            pass
        badge.display.refresh()

    def run(self):
        self.running = True
        self.render_instruction_screen()
        while self.running:
            self.process_input()
            self.update()

    def cleanup(self):
        badge.pixels[0] = (0, 0, 0)
        badge.pixels[1] = (0, 0, 0)
        self.ble.stop_advertising()
        self.running = False

def main():
    return App()
