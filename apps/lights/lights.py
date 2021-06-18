import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from arambadge import badge
import displayio
import terminalio
from adafruit_display_text import bitmap_label

from apps.lights.ble_service import Service

class App:
    def __init__(self, init_ui = True):
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
