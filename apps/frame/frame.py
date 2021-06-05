import board
import busio
import time
import rtc
import adafruit_il0373
import displayio
from arambadge import badge
from adafruit_display_shapes.rect import Rect

ASSET_ROOT = '/'.join(__file__.split('/')[:-1])
ASSET_LIST = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'colon']
DIGIT_WIDTH = 8
DIGIT_HEIGHT = 12
DIGIT_SPACE = 1

class FrameApp:
    rtc = rtc.RTC()
    
    def __init__(self):
        # Load all assets
        self.assets = {}
        for asset in ASSET_LIST:
            self.assets[asset] = displayio.OnDiskBitmap(open(ASSET_ROOT + '/font/%s.bmp' % asset, 'rb'))
        self.assets[':'] = self.assets['colon']

    def draw_time(self, dt, x, y):
        timestr = '%02d:%02d' % (dt.tm_min, dt.tm_sec)
        group = displayio.Group(max_size=len(timestr)+1, x=x, y=y)
        xpos = 0
        for index, ch in enumerate(timestr):
            shader = displayio.ColorConverter()
            sprite = displayio.TileGrid(self.assets[ch], x=xpos, pixel_shader=shader)
            group.append(sprite)
            xpos += self.assets[ch].width + DIGIT_SPACE
        return group

    def update_time(self, hour_delta = 0, minute_delta = 0):
        (yr, mon, day, hr, min, sec) = self.rtc.datetime[:6]
        self.rtc.datetime = time.struct_time((yr, mon, day, hr + hour_delta, min + minute_delta, sec, 0, -1, -1))

    def process_input(self):
        buttons = badge.gamepad.get_pressed()
        if buttons & badge.BTN_UP:
            print("Mode hybrid")
            badge.display.push_mode(badge.display.MODE_HYBRID)
            while badge.gamepad.get_pressed() & badge.BTN_UP:
                pass
        elif buttons & badge.BTN_DOWN:
            print("Mode normal")
            badge.display.push_mode(badge.display.MODE_NORMAL)
            while badge.gamepad.get_pressed() & badge.BTN_DOWN:
                pass
        elif buttons & badge.BTN_RIGHT:
            print("Mode quick")
            badge.display.push_mode(badge.display.MODE_QUICK)
            while badge.gamepad.get_pressed() & badge.BTN_RIGHT:
                pass
        elif buttons & badge.BTN_LEFT:
            print("Mode quicker")
            badge.display.push_mode(badge.display.MODE_QUICKER)
            while badge.gamepad.get_pressed() & badge.BTN_LEFT:
                pass
        elif buttons & badge.BTN_ACTION:
            print("Popped out:", badge.display.pop_mode())
            while badge.gamepad.get_pressed() & badge.BTN_ACTION:
                pass
        else:
            return False
        return True

    def run(self):
        display = badge.display

        group = displayio.Group()
        group.append(Rect(0, 0, display.width, display.height, fill=0xffffff))
        display.show(group)
        while display.time_to_refresh > 0:
            pass
        display.refresh()

        x = 48
        y = 40
        self.running = True
        while self.running:
            group = displayio.Group()
            group.append(Rect(0, 0, display.width, display.height, fill=0xffffff))
            group.append(self.draw_time(self.rtc.datetime, x, y))
            display.show(group)
            while display.time_to_refresh > 0:
                pass
            display.refresh()
            x += 5
            if x + 4 * DIGIT_SPACE + 5 * DIGIT_WIDTH >= display.width:
                x = 0
            y += 5
            if y + DIGIT_HEIGHT >= display.height:
                y = 0
            self.process_input()

def main():
    return FrameApp()
