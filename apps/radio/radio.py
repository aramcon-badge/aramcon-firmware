from arambadge import badge
from si4703 import SI4703
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
import board
from digitalio import DigitalInOut

# Radio icon from https://icons8.com/icon/9643/radio

class RadioApp:
    def __init__(self):
        self.fm = SI4703(badge.i2c, DigitalInOut(board.D2), channel=103)
        self.fm.reset()
        self.fm.volume = 7

    def render(self):
        screen = displayio.Group()

        screen.append(Rect(0, 0, badge.display.width, 32, fill=0xffffff))
        banner_image = displayio.OnDiskBitmap(open("/apps/radio/icon.bmp", "rb"))
        banner = displayio.TileGrid(banner_image, pixel_shader=displayio.ColorConverter(), x=4, y=-2)
        screen.append(banner)

        app_label = label.Label(terminalio.FONT, text="Radio", color=0x0)
        app_label_group = displayio.Group(scale=2, x=40, y=14)
        app_label_group.append(app_label)
        screen.append(app_label_group)
        
        volume_label = label.Label(terminalio.FONT, text="Volume: {}".format(self.fm.volume), color=0xffffff)
        channel_label = label.Label(terminalio.FONT, text="Station: {} FM".format(self.fm.channel), color=0xffffff, y=16)
        controls_group = displayio.Group(scale=2, x=8, y=48)
        controls_group.append(volume_label)
        controls_group.append(channel_label)
        screen.append(controls_group)

        badge.display.show(screen)

    def process_input(self):
        buttons = badge.gamepad.get_pressed() 
        if buttons & badge.BTN_LEFT:
            self.fm.channel -= 1
            return True
        if buttons & badge.BTN_RIGHT:
            self.fm.channel += 1
            return True
        if buttons & badge.BTN_UP:
            self.fm.volume += 1
            return True
        if buttons & badge.BTN_DOWN:
            self.fm.volume -= 1
            return True
        if buttons & badge.BTN_ACTION:
            self.running = False
            return True
        return False

    def run(self):
        display = badge.display
        self.running = True

        while self.running:
            self.render()
            while display.time_to_refresh > 0:
                pass
            if not self.process_input():
                display.refresh()

def main():
    return RadioApp()
