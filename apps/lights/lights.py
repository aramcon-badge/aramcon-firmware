import time

from arambadge import badge
import displayio
import terminalio
from adafruit_display_text import bitmap_label

SECONDS_TO_SLEEP_BETWEEN_UPDATES = 0.16

def add_in_range(number, addition, range_min, range_max):
    return min(range_max, max(range_min, (number + addition)))


class App:
    def __init__(self):
        self.prev_buttons = 0
        self.color_index = 0

    def button_up(self, buttons, button_mask):
        return ((self.prev_buttons & button_mask)
                and not (buttons & button_mask))

    def change_brightness(self, amount):
        for i in range(len(badge.pixels)):
            pixel_lst = list(badge.pixels[i])
            pixel_lst[self.color_index] = add_in_range(
                pixel_lst[self.color_index],
                amount,
                0,
                0xff
            )
            badge.pixels[i] = tuple(pixel_lst)

    def process_input(self, buttons):
        if buttons & badge.BTN_ACTION:
            self.cleanup()
            return True

        if buttons & badge.BTN_UP:
            self.change_brightness(15)
            return True

        if buttons & badge.BTN_DOWN:
            self.change_brightness(-15)
            return True

        if self.button_up(buttons, badge.BTN_LEFT):
            self.color_index = add_in_range(self.color_index, -1, 0, 2)
            return True

        if self.button_up(buttons, badge.BTN_RIGHT):
            self.color_index = add_in_range(self.color_index, 1, 0, 2)
            return True

        return False

    def render_instruction_screen(self):
        text = """--- Flashlight ---
Use the LEFT/RIGHT buttons to select
a color to modify

Use the UP/DOWN buttons to control the
brightness of the selected color

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
            print(self.color_index)
            print(badge.pixels)
            buttons = badge.gamepad.get_pressed()
            self.process_input(buttons)
            self.prev_buttons = buttons
            time.sleep(SECONDS_TO_SLEEP_BETWEEN_UPDATES)

    def cleanup(self):
        badge.pixels[0] = (0, 0, 0)
        badge.pixels[1] = (0, 0, 0)
        self.running = False

def main():
    return App()
