# Released under The MIT License (MIT)
#
# Copyright (c) 2019 Uri Shaked

import board
from digitalio import DigitalInOut, Pull
from analogio import AnalogIn
import displayio
import neopixel
import display
import keypad

class KeyStates:
    """Convert `keypad.Event` information from the given `keypad` scanner into key-pressed state.
    :param scanner: a `keypad` scanner, such as `keypad.Keys`
    """

    def __init__(self, scanner):
        self._scanner = scanner
        self._pressed = [False] * self._scanner.key_count
        self.update()

    def update(self):
        """Update key information based on pending scanner events."""

        # If the event queue overflowed, discard any pending events,
        # and assume all keys are now released.
        if self._scanner.events.overflowed:
            self._scanner.events.clear()
            self._scanner.reset()
            self._pressed = [False] * self._scanner.key_count

        self._was_pressed = self._pressed.copy()

        while True:
            event = self._scanner.events.get()
            if not event:
                # Event queue is now empty.
                break
            self._pressed[event.key_number] = event.pressed
            if event.pressed:
                self._was_pressed[event.key_number] = True

    def was_pressed(self, key_number):
        """True if key was down at any time since the last `update()`,
        even if it was later released.
        """
        return self._was_pressed[key_number]

    def pressed(self, key_number):
        """True if key is currently pressed, as of the last `update()`."""
        return self._pressed[key_number]

class Badge:
    BTN_UP = 1 << 0
    BTN_LEFT = 1 << 1
    BTN_DOWN = 1 << 2
    BTN_RIGHT = 1 << 3
    BTN_ACTION = 1 << 4

    def __init__(self):
        self._battery = AnalogIn(board.BATTERY_SENSE)
        self._led = DigitalInOut(board.LED)
        self._led.switch_to_output(value=True)
        self._vibration = DigitalInOut(board.VIBRATION_MOTOR)
        self._vibration.switch_to_output()
        self._pixels = neopixel.NeoPixel(board.NEOPIXEL, 4)
        self._i2c = None
        self._lis3dh = None
        self._spi = None
        self._display_bus = None
        self._display = None
        self._sound = None
        self._midi = None
        self._button_pins = [
            board.UP_BUTTON,
            board.DOWN_BUTTON,
            board.LEFT_BUTTON,
            board.RIGHT_BUTTON,
            board.ACTION_BUTTON]
        self._keypad = None
        self._buttons = None

    @property
    def up(self):
        """``True`` when the up button is pressed. ``False`` if not."""
        self.buttons.update()
        return self.buttons.pressed(self._button_pins.index(board.UP_BUTTON))

    @property
    def down(self):
        """``True`` when the down button is pressed. ``False`` if not."""
        self.buttons.update()
        return self.buttons.pressed(self._button_pins.index(board.DOWN_BUTTON))

    @property
    def left(self):
        """``True`` when the left button is pressed. ``False`` if not."""
        self.buttons.update()
        return self.buttons.pressed(self._button_pins.index(board.LEFT_BUTTON))

    @property
    def right(self):
        """``True`` when the right button is pressed. ``False`` if not."""
        self.buttons.update()
        return self.buttons.pressed(self._button_pins.index(board.RIGHT_BUTTON))
    
    @property
    def action(self):
        """``True`` when the action button is pressed. ``False`` if not."""
        self.buttons.update()
        return self.buttons.pressed(self._button_pins.index(board.ACTION_BUTTON))

    @property
    def buttons(self):
        if not self._keypad:
            self._keypad = keypad.Keys(
                self._button_pins,
                value_when_pressed=False,
                pull=True
            )
            self._buttons = KeyStates(self._keypad)
        return self._buttons
    
    @property
    def back_led(self):
        """The LED at the back of the board"""
        return not self._led.value

    @back_led.setter
    def back_led(self, value):
        self._led.value = not value

    @property
    def vibration(self):
        """Set to ``True`` to start vibrating"""
        return self._vibration.value

    @vibration.setter
    def vibration(self, value):
        self._vibration.value = value

    @property
    def pixels(self):
        """Array with the values of the 4 neopixels at the top of the board.

        See `neopixel.NeoPixel` for more info.

        .. code-block:: python
          from badgeio import badge
          import time

          badge.pixels.brightness = 0.5
          while True:
            badge.pixels[0] = (255, 0, 0) # Red
            time.sleep(0.5)
            badge.pixels[0] = (0, 255, 0) # Green
            time.sleep(0.5)
        """
        return self._pixels

    @property
    def i2c(self):
        """direct access to the I2C bus"""
        if not self._i2c:
            self._i2c = board.I2C()
        return self._i2c

    @property
    def spi(self):
        """direct access to the SPI bus"""
        if not self._spi:
            self._spi = board.SPI()
        return self._spi

    @property 
    def display_bus(self):
        if not self._display_bus:
            self._display_bus = displayio.FourWire(self.spi, command=board.DISP_DC, chip_select=board.DISP_CS,
                                                   reset=board.DISP_RESET, baudrate=1000000)
        return self._display_bus

    @property
    def display(self):
        if not self._display:
            displayio.release_displays()
            self._display = display.Display(self.display_bus, width=296, height=128, rotation=270,
                                                   seconds_per_frame=5, busy_pin=board.DISP_BUSY, swap_rams=True,
                                                   black_bits_inverted=False)
        return self._display

    @property
    def acceleration(self):
        """Obtain acceleration as a tuple with 3 elements: (x, y, z)"""
        if not self._lis3dh:
            import adafruit_lis3dh
            self._lis3dh = adafruit_lis3dh.LIS3DH_I2C(self.i2c, address=0x18)
        return self._lis3dh.acceleration

    @property
    def battery_voltage(self):
        """The battery voltage (if currently operating off the battery)"""
        return (self._battery.value * 3.3) / 65536
    
    def show_bitmap(self, path, pixel_shader=displayio.ColorConverter()):
        """Draws the bitmap from the given file. Must be in .bmp format"""
        image = displayio.OnDiskBitmap(open(path, "rb"))
        grid = displayio.TileGrid(image, pixel_shader=image.pixel_shader)
        group = displayio.Group()
        group.append(grid)
        self.display.show(group)
        while self.display.time_to_refresh > 0:
            pass
        self.display.refresh()

badge = Badge()
