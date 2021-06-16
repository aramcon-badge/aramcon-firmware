import displayio
import terminalio
from arambadge import badge
from adafruit_display_text import label

def alert(message, x = 60, y = 64, scale = 2, color=0xffffff):
    display = badge.display
    screen = displayio.Group()
    group = displayio.Group(scale=scale, x=x, y=y)
    all_done = label.Label(terminalio.FONT, text=message, color=color)
    group.append(all_done)
    screen.append(group)
    display.show(screen)
    display.refresh()
