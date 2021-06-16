from arambadge import badge
from debounce import wait_for_button_release
import displayio
import terminalio
from adafruit_display_text import bitmap_label
from adafruit_display_shapes.rect import Rect
import board
from digitalio import DigitalInOut

SCREEN_SIZE = 6
APP_ROOT = '/'.join(__file__.split('/')[:-1])

class LuzApp:
    def __init__(self):
        self.agenda = []
        with open("{}/agenda_day1.txt".format(APP_ROOT), "r") as agendafile:
            self.agenda.append(list(map(lambda line: line.rstrip(), agendafile.readlines())))

        with open("{}/agenda_day2.txt".format(APP_ROOT), "r") as agendafile:
            self.agenda.append(list(map(lambda line: line.rstrip(), agendafile.readlines())))
        
        self.screen = -1
        self.next_screen = 0
        
        self.current_agenda = 0
        self.next_agenda = 0

        self.screen_count = [(len(agenda) + SCREEN_SIZE - 1) // SCREEN_SIZE for agenda in self.agenda]

    def render(self):
        display = badge.display
        screen = displayio.Group()

        screen.append(Rect(0, 32, display.width, display.height - 32, fill=0xffffff))
        banner_image = displayio.OnDiskBitmap(open("{}/icon.bmp".format(APP_ROOT), "rb"))
        palette = displayio.Palette(1)
        palette[0] = 0xffffff
        banner = displayio.TileGrid(banner_image, pixel_shader=palette, x=4, y=0)
        screen.append(banner)

        app_label = bitmap_label.Label(terminalio.FONT, text="Conference Agenda", color=0xffffff, save_text=True)
        app_label_group = displayio.Group(scale=2, x=40, y=14)
        app_label_group.append(app_label)
        screen.append(app_label_group)

        lines_group = displayio.Group(x=8, y=48)
        lines = self.agenda[self.current_agenda][self.screen * SCREEN_SIZE:(self.screen + 1) * SCREEN_SIZE]
        for (index, line) in enumerate(lines):
            lines_group.append(bitmap_label.Label(terminalio.FONT, text=line[0:40], color=0x0, y = index * 12, save_text=True))
        screen.append(lines_group)

        # Display up/down arrows as needed
        if self.screen > 0:
            more_icon = displayio.OnDiskBitmap(open("{}/arrow_up.bmp".format(APP_ROOT), "rb"))
            screen.append(displayio.TileGrid(more_icon, pixel_shader=displayio.ColorConverter(), x=display.width - 20, y=40))
        if self.screen + 1 < self.screen_count[self.current_agenda]:
            more_icon = displayio.OnDiskBitmap(open("{}/arrow_down.bmp".format(APP_ROOT), "rb"))
            screen.append(displayio.TileGrid(more_icon, pixel_shader=displayio.ColorConverter(), x=display.width - 20, y=display.height - 16))

        display.show(screen)
    
    def update_next_agenda(self, agenda):
        self.next_agenda = agenda
        if agenda < 0:
            self.next_agenda = 1
        if agenda > 1:
            self.next_agenda = 0

    def update_next_screen(self, screen):
        self.next_screen = screen
        screen_count = self.screen_count[self.current_agenda]
        if screen < 0:
            self.next_screen = screen_count - 1
        if screen >= screen_count:
            self.next_screen = 0

    def process_input(self):
        buttons = badge.gamepad.get_pressed() 
        wait_for_button_release()
        if buttons & badge.BTN_UP:
            self.update_next_screen(self.screen - 1)
            return True
        if buttons & badge.BTN_DOWN:
            self.update_next_screen(self.screen + 1)
            return True
        if buttons & badge.BTN_RIGHT:
            self.update_next_agenda(self.current_agenda + 1)
            self.update_next_screen(0)
            return True
        if buttons & badge.BTN_LEFT:
            self.update_next_agenda(self.current_agenda - 1)
            self.update_next_screen(0)
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
            if self.next_screen != self.screen or self.next_agenda != self.current_agenda:
                self.current_agenda = self.next_agenda
                self.screen = self.next_screen
                self.render()
            
            while display.time_to_refresh > 0:
                pass

            display.refresh()

            self.process_input()


def main():
    return LuzApp()
