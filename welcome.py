import displayio
import terminalio
from adafruit_display_text import label
from arambadge import badge

def show_welcome():
    display = badge.display

    frame = displayio.Group()

    pic = displayio.OnDiskBitmap(open("assets/welcome.bmp", "rb"))
    grid = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
    frame.append(grid)

    pic = displayio.OnDiskBitmap(open("assets/banner.bmp", "rb"))
    grid = displayio.TileGrid(pic, pixel_shader=pic.pixel_shader)
    frame.append(grid)

    text_area = label.Label(terminalio.FONT, text="Welcome!", color=0x0, x=76, y=20)
    frame.append(text_area)

    display.show(frame)