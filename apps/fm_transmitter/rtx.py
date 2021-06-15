from arambadge import badge
from adafruit_si4713 import SI4713
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
import board
from digitalio import DigitalInOut
from time import time

class RadioTx:
    def __init__(self):
        self.fm = SI4713(badge.i2c, reset = DigitalInOut(board.GPIO2), timeout_s = 0.5)
        self.fm.reset()
        self.fm.tx_frequency_khz = 106800
        self.fm.tx_power = 115

    def process_input(self):
        buttons = badge.gamepad.get_pressed()
        if buttons & badge.BTN_LEFT:
            return True
        if buttons & badge.BTN_RIGHT:
            return True
        if buttons & badge.BTN_UP:
            return True
        if buttons & badge.BTN_DOWN:
            return True
        if buttons & badge.BTN_ACTION:
            self.running = False
            return True
        return False

    def render(self):
        screen = displayio.Group()

        screen.append(Rect(0, 0, badge.display.width, 32, fill=0xffffff))
        banner_image = displayio.OnDiskBitmap(open("/apps/radio/icon.bmp", "rb"))
        banner = displayio.TileGrid(banner_image, pixel_shader=displayio.ColorConverter(), x=4, y=-2)
        screen.append(banner)

        app_label = label.Label(terminalio.FONT, text="FM Transmitter", color=0x0)
        app_label_group = displayio.Group(scale=2, x=40, y=14)
        app_label_group.append(app_label)
        screen.append(app_label_group)

        badge.display.show(screen)

    def run(self):
        display = badge.display
        self.running = True

        while self.running:
            self.render()
            if self.process_input():
                display.refresh()
            while display.time_to_refresh > 0:
                pass
            
def main():
    return RadioTx()