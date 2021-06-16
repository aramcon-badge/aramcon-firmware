# Nametags app for Aramcon Badge
# Copyright (C) 2019, Uri Shaked

import random
import time
from adafruit_ble import BLERadio
from adafruit_ble.services.nordic import UARTService
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from arambadge import badge
from apps.nametags.nameservice import NameService
from apps.nametags import ui

class NametagsApp:
    def __init__(self, init_ui = True):
        self.ble = BLERadio()
        ui.display_qr(self.addr_suffix)
        self.nameservice = NameService()
        self.advertisement = ProvideServicesAdvertisement(self.nameservice)
        self.scan_response = Advertisement()
        self.scan_response.complete_name = "BADGE-{}".format(self.addr_suffix)
        self.ble.start_advertising(self.advertisement, self.scan_response)

    @property
    def addr_suffix(self):
        addr = self.ble.address_bytes
        return "{:02X}{:02X}{:02X}".format(addr[3], addr[4], addr[5])

    def update(self):
        if self.ble.connected:
            self.nameservice.update()
        ui.display_qr(self.addr_suffix)
    
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
    return NametagsApp()