import time

from arambadge import badge
import displayio
import terminalio
from adafruit_display_text import bitmap_label

SECONDS_TO_SLEEP_BETWEEN_UPDATES = 0.16

def change_brightness(amount):
    for i in range(len(badge.pixels)):
        badge.pixels[i] = tuple(max(min((value + amount), 0xff), 0)
                                for value in badge.pixels[i])

class App:
    def __init__(self):
        pass

    def process_input(self):
        buttons = badge.gamepad.get_pressed()
        if buttons & badge.BTN_ACTION:
            self.cleanup()
            return True

        if buttons & badge.BTN_UP:
            change_brightness(5)
            return True

        if buttons & badge.BTN_DOWN:
            change_brightness(-5)
            return True

        return False

    def render_instruction_screen(self):
        text = """--- Flashlight ---
Use the UP/DOWN buttons to control the
brightness

Press the action button to
exit the application."""
        print(text)

        screen = displayio.Group()
        lines_group = displayio.Group(x=8, y=10)
        for (index, line) in enumerate(text.splitlines()):
            lines_group.append(bitmap_label.Label(
                terminalio.FONT,
                text=line[0:40],
                color=0xffffff,
                y = index * 12,
                save_text=True
            ))
        screen.append(lines_group)
        badge.display.show(screen)
        while badge.display.time_to_refresh > 0:
            pass
        badge.display.refresh()

    def run(self):
        self.running = True
        self.render_instruction_screen()
        while self.running:
            self.process_input()
            time.sleep(SECONDS_TO_SLEEP_BETWEEN_UPDATES)

    def cleanup(self):
        badge.pixels[0] = (0, 0, 0)
        badge.pixels[1] = (0, 0, 0)
        self.running = False

def main():
    return App()
