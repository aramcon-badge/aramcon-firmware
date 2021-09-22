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
        try:
            self.fm = SI4703(badge.i2c, DigitalInOut(board.D2), channel=103)
            self.fm.reset()
            self.fm.volume = 7
        except:
            print('Missing FM module')
            self.fm = None

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

        controls_group = displayio.Group(scale=2, x=8, y=48)
        
        if self.fm is not None:
            volume_label = label.Label(terminalio.FONT, text="Volume: {}".format(self.fm.volume), color=0xffffff)
            channel_label = label.Label(terminalio.FONT, text="Station: {} FM".format(self.fm.channel), color=0xffffff, y=16)
            controls_group.append(volume_label)
            controls_group.append(channel_label)
        else:
            missing_module_label = label.Label(terminalio.FONT, text="FM module missing\n or not working", color=0xffffff)
            controls_group.append(missing_module_label)

        screen.append(controls_group)

        badge.display.show(screen)

    def process_input(self):
        if self.fm is not None:
            self.fm.channel = round(self.fm.channel, 1)
            if badge.left:
                self.fm.channel -= 0.1
                return True
            if badge.right:
                self.fm.channel += 0.1
                return True
            if badge.up:
                self.fm.volume += 1
                return True
            if badge.down:
                self.fm.volume -= 1
                return True
            self.fm.channel = round(self.fm.channel, 1)
        if badge.action:
            self.running = False
            return True
        return False

    def run(self):
        display = badge.display
        self.running = True

        self.render()
        while display.time_to_refresh > 0:
            pass
        display.refresh()

        while self.running:
            if self.process_input():
                self.render()
                while display.time_to_refresh > 0:
                    pass
                display.refresh()

def main():
    return RadioApp()
