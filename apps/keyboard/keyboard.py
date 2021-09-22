from arambadge import badge
import bbkbd
import displayio
import terminalio
from adafruit_display_text import bitmap_label
from adafruit_display_shapes.rect import Rect

class KeyboardApp:
    def __init__(self):
        try:
            self.keyboard = bbkbd.BBKeyboard()
        except:
            self.keyboard = None
        self.update_screen = True
        self.text = ''

    def render(self):
        display = badge.display
        screen = displayio.Group()

        screen.append(Rect(0, 32, display.width, display.height - 32, fill=0xffffff))

        app_label = bitmap_label.Label(terminalio.FONT, text="Keyboard Test", color=0xffffff, save_text=True)
        app_label_group = displayio.Group(scale=2, x=40, y=14)
        app_label_group.append(app_label)
        screen.append(app_label_group)

        if self.keyboard:
            key_label = bitmap_label.Label(terminalio.FONT, text=self.text, color=0x0, scale=3,
                anchor_point=(0.5, 0.5), anchored_position=(display.width // 2, 70))
        else:
            key_label = bitmap_label.Label(terminalio.FONT, text="Keyboard not connected\n         :-(", color=0x0, scale=2,
                anchor_point=(0.5, 0.5), anchored_position=(display.width // 2, 70))
        screen.append(key_label)

        display.show(screen)
        self.update_screen = False
    
    def process_input(self):
        if self.keyboard:
            key = self.keyboard.read()
            while key:
                self.update_screen = True
                if key == '\b':
                    self.text = self.text[:-1]
                else:
                    self.text += key
                key = self.keyboard.read()
        if badge.action:
            self.running = False
            return True
        
        return False

    def run(self):
        display = badge.display
        self.running = True

        display.rotation=90 # Upside down

        try:
            while self.running:
                if self.update_screen:
                    self.render()

                while display.time_to_refresh > 0:
                    pass
                display.refresh()

                self.process_input()
        finally:
            display.rotation=270 # Restore default orientation

def main():
    return KeyboardApp()
