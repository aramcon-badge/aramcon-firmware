import random
import time
from adafruit_ble import BLERadio
from adafruit_ble.services.nordic import UARTService
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from arambadge import badge

from apps.scratchpad.ble_service import ScratchPadService

class ScratchPadApp:
    def __init__(self, init_ui = True):
        self.ble = BLERadio()
        self.service = ScratchPadService()
        self.advertisement = ProvideServicesAdvertisement(self.service)
        self.scan_response = Advertisement()
        self.scan_response.complete_name = "SCRATCHPAD-LIOR"
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

    def run(self):
        self.running = True
        while self.running:
            self.process_input()
            self.update()

    def cleanup(self):
        self.ble.stop_advertising()
        self.running = False

def main():
    return ScratchPadApp()