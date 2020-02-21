# Nametags app for Aramcon Badge
# Copyright (C) 2019, Uri Shaked

from arambadge import badge
import adafruit_miniqr
import displayio
import time

palette = displayio.Palette(2)
palette[0] = 0xFFFFFF
palette[1] = 0x000000

def banner():
    image = displayio.OnDiskBitmap(open("/assets/banner.bmp", "rb"))
    return displayio.TileGrid(image, pixel_shader=displayio.ColorConverter())

def bitmap_QR(matrix):
    BORDER_PIXELS  = 2
    bitmap = displayio.Bitmap(matrix.width+2*BORDER_PIXELS,
                              matrix.height+2*BORDER_PIXELS, 2)
    for y in range(matrix.height):
        for x in range(matrix.width):
            if matrix[x, y]:
                bitmap[x+BORDER_PIXELS, y+BORDER_PIXELS] = 1
            else:
                bitmap[x+BORDER_PIXELS, y+BORDER_PIXELS] = 0
    return bitmap

def get_qr_url(addr):
    return 'https://go.urish.org/AC?b={}'.format(addr)

def display_qr(addr):
    global palette
    background = displayio.Bitmap(badge.display.width, badge.display.height, 1)
    background_sprite = displayio.TileGrid(background, pixel_shader=palette)
    
    qr = adafruit_miniqr.QRCode()
    qr.add_data(get_qr_url(addr).encode('utf-8'))
    qr.make()
    qr_bitmap = bitmap_QR(qr.matrix)
    qr_img = displayio.TileGrid(qr_bitmap, pixel_shader=palette)
    qr_group = displayio.Group(scale=4, x=96, y=6)
    qr_group.append(qr_img)

    frame = displayio.Group()
    frame.append(background_sprite)
    frame.append(qr_group)
    frame.append(banner())
    badge.display.show(frame)
    while badge.display.time_to_refresh > 0:
        pass
    badge.display.refresh()

def display_nametag():
    badge.show_bitmap('/nametag.bmp')
