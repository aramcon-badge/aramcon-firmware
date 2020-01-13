# Released under The MIT License (MIT)
#
# Copyright (c) 2019 Uri Shaked

import board
import busio
from digitalio import DigitalInOut, Pull
from analogio import AnalogIn
import displayio
import neopixel

class Badge:
    BTN_UP = 1 << 0
    BTN_DOWN = 1 << 1
    BTN_RIGHT = 1 << 2
    BTN_LEFT = 1 << 3
    BTN_ACTION = 1 << 4

    def __init__(self):
        self._up = DigitalInOut(board.UP_BUTTON)
        self._up.switch_to_input(pull=Pull.UP)
        self._down = DigitalInOut(board.DOWN_BUTTON)
        self._down.switch_to_input(pull=Pull.UP)
        self._left = DigitalInOut(board.LEFT_BUTTON)
        self._left.switch_to_input(pull=Pull.UP)
        self._right = DigitalInOut(board.RIGHT_BUTTON)
        self._right.switch_to_input(pull=Pull.UP)
        self._action = DigitalInOut(board.ACTION_BUTTON)
        self._action.switch_to_input(pull=Pull.UP)
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
        self._gamepad = None

    @property
    def up(self):
        """``True`` when the up button is pressed. ``False`` if not."""
        return not self._up.value

    @property
    def down(self):
        """``True`` when the down button is pressed. ``False`` if not."""
        return not self._down.value

    @property
    def left(self):
        """``True`` when the left button is pressed. ``False`` if not."""
        return not self._left.value

    @property
    def right(self):
        """``True`` when the right button is pressed. ``False`` if not."""
        return not self._right.value
    
    @property
    def action(self):
        """``True`` when the action button is pressed. ``False`` if not."""
        return not self._action.value

    @property
    def gamepad(self):
        if not self._gamepad:
            import gamepad
            self._gamepad = gamepad.GamePad(
                self._up, self._left, self._down, self._right, self._action
            )
        return self._gamepad
    
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
            self._i2c = busio.I2C(board.SCL, board.SDA)
        return self._i2c

    @property
    def spi(self):
        """direct access to the SPI bus"""
        if not self._spi:
            self._spi = busio.SPI(board.SCK, MISO=board.MISO, MOSI=board.MOSI)
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
            import adafruit_il0373
            displayio.release_displays()
            self._display = adafruit_il0373.IL0373(self.display_bus, width=296, height=128, rotation=270,
                                                   seconds_per_frame=5, busy_pin=board.DISP_BUSY, swap_rams=True)
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
        grid = displayio.TileGrid(image, pixel_shader=pixel_shader)
        group = displayio.Group(max_size=1)
        group.append(grid)
        self.display.show(group)
        while self.display.time_to_refresh > 0:
            pass
        self.display.refresh()

badge = Badge()
