# Nametags app for Aramcon Badge
# Copyright (C) 2019, Uri Shaked

import random
import os
import time
from adafruit_ble import BLERadio
from adafruit_ble.services.nordic import UARTService
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from arambadge import badge
from application import Application
from .nameservice import NameService
from . import ui

class NametagsApp(Application):
    def __init__(self, init_ui = True):
        super().__init__(self, 'Nametags')
        self.ble = BLERadio()
        self.nameservice = NameService()
        self.advertisement = ProvideServicesAdvertisement(self.nameservice)
        self.scan_response = Advertisement()
        self.scan_response.complete_name = "BADGE-{}".format(self.addr_suffix)

        self.should_render = False
        self.show_name = False
        self.advertising = False
        if init_ui:
            self.show_name = self.nametag_file_exists()
            self.should_render = True
            self.render()
            if self.show_name:
                self.start_advertising()

    @property
    def addr_suffix(self):
        addr = self.ble.address_bytes
        return "{:02X}{:02X}{:02X}".format(addr[3], addr[4], addr[5])

    def start_advertising(self):
        if not self.advertising:
                self.advertising = True
                self.ble.start_advertising(self.advertisement, self.scan_response)

    def stop_advertising(self):
        if self.advertising:
            self.advertising = False
            self.ble.stop_advertising()

    def nametag_file_exists(self):
        try:
            os.stat('/nametag.bmp')
            return True
        except OSError:
            return False

    def handle_event(self, event):
        pass

    def update(self):
        updated = False

        if self.ble.connected:
            self.nameservice.update()
        if badge.action:
            while badge.action:
                pass
            self.show_name = False if self.show_name else self.nametag_file_exists()
            updated = True
            self.should_render = True
        if updated:
            if self.show_name:
                self.stop_advertising()
            else:
                self.start_advertising()

    def render(self):
        if self.should_render:
            self.should_render = False
            if self.show_name:
                ui.display_nametag()
            else:    
                ui.display_qr(self.addr_suffix)

