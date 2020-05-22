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

class ClockApp:
    selected_digit = 4 # 4 means no digit selected
    rtc = rtc.RTC()
    
    def __init__(self):
        # Load all assets
        self.assets = {}
        for asset in ASSET_LIST:
            self.assets[asset] = displayio.OnDiskBitmap(open(ASSET_ROOT + '/font/%s.bmp' % asset, 'rb'))
        self.assets[':'] = self.assets['colon']

    def draw_time(self, dt, x, y):
        timestr = '%02d:%02d' % (dt.tm_hour, dt.tm_min)
        group = displayio.Group(max_size=len(timestr)+1, x=x, y=y)
        xpos = 0
        digit = self.selected_digit
        if digit >= 2:
            # Skip the colon
            digit += 1
        for index, ch in enumerate(timestr):
            shader = displayio.ColorConverter()
            if index == digit:
                rect = Rect(xpos-4, -8, 48, 64, fill=0x0)
                group.append(rect)
                shader = displayio.Palette(2)
                shader[0] = 0xffffff
            sprite = displayio.TileGrid(self.assets[ch], x=xpos, pixel_shader=shader)
            group.append(sprite)
            xpos += self.assets[ch].width + 8
        return group

    def update_time(self, hour_delta = 0, minute_delta = 0):
        (yr, mon, day, hr, min, sec) = self.rtc.datetime[:6]
        self.rtc.datetime = time.struct_time((yr, mon, day, hr + hour_delta, min + minute_delta, sec, 0, -1, -1))

    def process_input(self):
        buttons = badge.gamepad.get_pressed() 
        if buttons & badge.BTN_LEFT:
            self.selected_digit = (self.selected_digit + 5 - 1) % 5
            return True
        if buttons & badge.BTN_RIGHT:
            self.selected_digit = (self.selected_digit + 1) % 5
            return True
        if (buttons & badge.BTN_UP) or (buttons & badge.BTN_DOWN):
            direction = 1 if buttons & badge.BTN_UP else -1
            if self.selected_digit == 0:
                self.update_time(10 * direction)
            elif self.selected_digit == 1:
                self.update_time(direction)
            elif self.selected_digit == 2:
                self.update_time(0, 10 * direction)
            elif self.selected_digit == 3:
                self.update_time(0, direction)
            else:
                return False
            return True
        return False

    def run(self):
        display = badge.display

        while True:
            group = displayio.Group()
            group.append(Rect(0, 0, display.width, display.height, fill=0xffffff))
            group.append(self.draw_time(self.rtc.datetime, 48, 40))
            display.show(group)
            while display.time_to_refresh > 0:
                pass
            if not self.process_input():
                display.refresh()
