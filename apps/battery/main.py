import time

import displayio
import terminalio
import arambadge
import adafruit_display_text.bitmap_label

class App:
    AMOUNT_OF_SECONDS_TO_SLEEP_BETWEEN_MEASURMENTS = 30

    @staticmethod
    def should_quit() -> bool:
        return arambadge.badge.action

    @staticmethod
    def render_battery_status(voltage: float):
        message = f"BATTERY\nVOLTAGE {voltage}V\nPERCENTAGE: unknown\nCHARGING: unknown"
        print(message)
        screen = displayio.Group()
        label_group = displayio.Group(
            scale=2,
            x=10,
            y=10
        )

        for (i, line) in enumerate(message.splitlines()):
            label = adafruit_display_text.bitmap_label.Label(
                terminalio.FONT,
                text=line,
                color=0xffffff,
                y=(i * 12),
            )
            label_group.append(label)

        screen.append(label_group)
        arambadge.badge.display.show(screen)

    def run(self):
        amount_seconds_left_until_next_measurement = 0
        while not self.should_quit():
            if amount_seconds_left_until_next_measurement > 0:
                # "idle"
                time.sleep(0.1)
                amount_seconds_left_until_next_measurement -= 0.1
                continue

            battery_voltage = arambadge.badge.battery_voltage
            self.render_battery_status(battery_voltage)

            while arambadge.badge.display.time_to_refresh > 0:
                pass
            arambadge.badge.display.refresh()

            amount_seconds_left_until_next_measurement = \
                self.AMOUNT_OF_SECONDS_TO_SLEEP_BETWEEN_MEASURMENTS

def main():
    return App()
