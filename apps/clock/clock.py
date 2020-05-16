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
    def __init__(self):
        # Load all assets
        self.assets = {}
        for asset in ASSET_LIST:
            self.assets[asset] = displayio.OnDiskBitmap(open(ASSET_ROOT + '/font/%s.bmp' % asset, 'rb'))
        self.assets[':'] = self.assets['colon']

    def draw_time(self, dt, x, y):
        timestr = '%02d:%02d' % (dt.tm_hour, dt.tm_min)
        group = displayio.Group(max_size=len(timestr), x=x, y=y)
        xpos = 0
        for ch in timestr:
            sprite = displayio.TileGrid(self.assets[ch], x=xpos, pixel_shader=displayio.ColorConverter())
            group.append(sprite)
            xpos += self.assets[ch].width + 8
        return group

    def run(self):
        display = badge.display

        while True:
            rtc_instance = rtc.RTC()
            group = displayio.Group()
            group.append(Rect(0, 0, display.width, display.height, fill=0xffffff))
            group.append(self.draw_time(rtc_instance.datetime, 48, 40))
            display.show(group)
            while display.time_to_refresh > 0:
                pass
            display.refresh()
            time.sleep(60-time.time()%60)
