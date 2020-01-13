# Nametags app for Aramcon Badge
# Copyright (C) 2019, Uri Shaked

import random
import time
from adafruit_ble import BLERadio
from adafruit_ble.services.nordic import UARTService
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from arambadge import badge
from . import ui

class NametagsApp:
    def __init__(self, init_ui = True):
        self.ble = BLERadio()
        self.name_service = UARTService()
        self.advertisement = ProvideServicesAdvertisement(self.name_service)
        self.scan_response = Advertisement()
        self.scan_response.complete_name = "BADGE-{}".format(self.addr_suffix)
        if init_ui:
            self.showing_name = ui.display_nametag()
            if not self.showing_name:
                ui.display_qr(self.addr_suffix)
                self.ble.start_advertising(self.advertisement, self.scan_response)

    @property
    def addr_suffix(self):
        addr = self.ble.address_bytes
        return "{:02X}{:02X}{:02X}".format(addr[3], addr[4], addr[5])

    def update(self):
        if badge.action:
            while badge.action:
                pass
            if self.showing_name:
                self.showing_name = False
                ui.display_qr(self.addr_suffix)
                self.ble.start_advertising(self.advertisement, self.scan_response)
            else:
                self.showing_name = ui.display_nametag()
                if self.showing_name:
                    self.ble.stop_advertising()
