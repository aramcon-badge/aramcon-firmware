from arambadge import badge
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
import board
from digitalio import DigitalInOut

SCREEN_SIZE = 6
APP_ROOT = '/'.join(__file__.split('/')[:-1])

class LuzApp:
    def __init__(self):
        with open("{}/agenda.txt".format(APP_ROOT), "r") as agendafile:
            self.agenda = list(map(lambda line: line.strip(), agendafile.readlines()))
        self.screen = 0
        self.screen_count = (len(self.agenda) + SCREEN_SIZE - 1) // SCREEN_SIZE

    def render(self):
        display = badge.display
        screen = displayio.Group()

        screen.append(Rect(0, 32, display.width, display.height - 32, fill=0xffffff))
        banner_image = displayio.OnDiskBitmap(open("{}/icon.bmp".format(APP_ROOT), "rb"))
        palette = displayio.Palette(1)
        palette[0] = 0xffffff
        banner = displayio.TileGrid(banner_image, pixel_shader=palette, x=4, y=0)
        screen.append(banner)

        app_label = label.Label(terminalio.FONT, text="Conference Agenda", color=0xffffff)
        app_label_group = displayio.Group(scale=2, x=40, y=14)
        app_label_group.append(app_label)
        screen.append(app_label_group)

        lines_group = displayio.Group(x=8, y=48)
        lines = self.agenda[self.screen * SCREEN_SIZE:(self.screen + 1) * SCREEN_SIZE]
        for (index, line) in enumerate(lines):
            lines_group.append(label.Label(terminalio.FONT, text=line, color=0x0, y = index * 12))
        screen.append(lines_group)

        # Display up/down arrows as needed
        if self.screen > 0:
            more_icon = displayio.OnDiskBitmap(open("{}/arrow_up.bmp".format(APP_ROOT), "rb"))
            screen.append(displayio.TileGrid(more_icon, pixel_shader=displayio.ColorConverter(), x=display.width - 20, y=40))
        if self.screen + 1 < self.screen_count:
            more_icon = displayio.OnDiskBitmap(open("{}/arrow_down.bmp".format(APP_ROOT), "rb"))
            screen.append(displayio.TileGrid(more_icon, pixel_shader=displayio.ColorConverter(), x=display.width - 20, y=display.height - 16))

        display.show(screen)

    def process_input(self):
        buttons = badge.gamepad.get_pressed() 
        if buttons & badge.BTN_UP:
            self.screen -= 1
            if self.screen < 0:
                self.screen = self.screen_count - 1
            return True
        if buttons & badge.BTN_DOWN:
            self.screen += 1
            if self.screen == self.screen_count:
                self.screen = 0
            return True
        if buttons & badge.BTN_ACTION:
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
    return LuzApp()
