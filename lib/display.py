import adafruit_il0373
import enum

NORMAL_START_SEQUENCE = bytearray(
    b"\x01\x05\x03\x00\x2b\x2b\x09"  # power setting
    b"\x06\x03\x17\x17\x17"  # booster soft start
    b"\x04\x80\x10"  # power on and wait 200 ms
    b"\x00\x01\x9f"  # panel setting. Further filled in below.
    b"\x50\x01\x37"  # CDI setting
    b"\x30\x01\x29"  # PLL set to 50 Hz (M = 7, N = 4)
    b"\x61\x03\x80\x01\x28"  # Resolution
    b"\x82\x81\x12\x32"  # VCM DC and delay 50ms
)

QUICK_START_SEQUENCE = bytearray(
    b"\x01\x05\x03\x00\x2b\x2b\x13"  # power setting
    b"\x06\x03\x17\x17\x17"  # booster soft start
    b"\x04\x80\x01"  # power on and wait 200 ms
    b"\x00\x01\xbf"  # panel setting. Further filled in below.
    b"\x50\x01\x97"  # CDI setting
    b"\x30\x01\x3C"  # PLL set to 50 Hz (M = 7, N = 4)
    b"\x61\x03\x80\x01\x28"  # Resolution
    b"\x82\x81\x12\x01"  # VCM DC and delay 50ms
    # Common voltage
    b"\x20\x2a"
    b"\x40\x0A\x00\x00\x00\x01"
    b"\x00\x0B\x0B\x00\x00\x01"
    b"\x00\x05\x01\x00\x00\x01"
    b"\x00\x07\x07\x00\x00\x01"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    # White to White
    b"\x21\x2a"
    b"\x40\x0A\x00\x00\x00\x01"
    b"\x90\x0B\x0B\x00\x00\x01"
    b"\x40\x05\x01\x00\x00\x01"
    b"\xA0\x07\x07\x00\x00\x01"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    # Black to White
    b"\x22\x2a"
    b"\x40\x0A\x00\x00\x00\x01"
    b"\x90\x0B\x0B\x00\x00\x01"
    b"\x40\x05\x01\x00\x00\x01"
    b"\xA0\x07\x07\x00\x00\x01"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    # White to Black
    b"\x23\x2a"
    b"\x80\x0A\x00\x00\x00\x01"
    b"\x90\x0B\x0B\x00\x00\x01"
    b"\x80\x05\x01\x00\x00\x01"
    b"\x50\x07\x07\x00\x00\x01"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    # Black to Black
    b"\x24\x2a"
    b"\x80\x0A\x00\x00\x00\x01"
    b"\x90\x0B\x0B\x00\x00\x01"
    b"\x80\x05\x01\x00\x00\x01"
    b"\x50\x07\x07\x00\x00\x01"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
)

QUICKER_START_SEQUENCE = bytearray(
    b"\x01\x05\x03\x00\x2b\x2b\x13"  # power setting
    b"\x06\x03\x17\x17\x17"  # booster soft start
    b"\x04\x80\x01"  # power on and wait 200 ms
    b"\x00\x01\xbf"  # panel setting. Further filled in below.
    b"\x50\x01\x97"  # CDI setting
    b"\x30\x01\x3C"  # PLL set to 50 Hz (M = 7, N = 4)
    b"\x61\x03\x80\x01\x28"  # Resolution
    b"\x82\x81\x12\x01"  # VCM DC and delay 50ms
    # Common voltage
    b"\x20\x2a"
    b"\x00\x07\x07\x00\x00\x01"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    # White to White
    b"\x21\x2a"
    b"\xA0\x07\x07\x00\x00\x01"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    # Black to White
    b"\x22\x2a"
    b"\xA0\x07\x07\x00\x00\x01"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    # White to Black
    b"\x23\x2a"
    b"\x50\x07\x07\x00\x00\x01"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    # Black to Black
    b"\x24\x2a"
    b"\x50\x07\x07\x00\x00\x01"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00"
)

class DisplayMode(enum):
    HYBRID = 0
    NORMAL = 1
    QUICK = 2
    QUICKER = 3


MODE_PARAMETERS = {
    DisplayMode.HYBRID : (None, None, 5),
    DisplayMode.NORMAL  : (NORMAL_START_SEQUENCE, 5),
    DisplayMode.QUICK   : (QUICK_START_SEQUENCE, 1),
    DisplayMode.QUICKER : (QUICKER_START_SEQUENCE, 0.33)
}

class Display(adafruit_il0373.IL0373):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.refresh_counter_since_full = 0
        self.modes_stack = [DisplayMode.HYBRID]
        self._change_mode(self.modes_stack[-1])

    def refresh(self):
        if self.modes_stack[-1] != DisplayMode.HYBRID:
            super().refresh()
            return

        if self.refresh_counter_since_full > MODE_PARAMETERS[DisplayMode.HYBRID][2]:
            self._change_mode(DisplayMode.QUICK)
            super().refresh()
            self._change_mode(DisplayMode.QUICKER)
            self.refresh_counter_since_full = 0
        else:
            self.refresh_counter_since_full += 1
            super().refresh()

    def _change_mode(self, display_mode):
        if display_mode != DisplayMode.HYBRID:
            self.update_refresh_mode(*MODE_PARAMETERS[display_mode])
        else:
            self.update_refresh_mode(*MODE_PARAMETERS[DisplayMode.QUICKER])
            self.refresh_counter_since_full = 0

    def push_mode(self, display_mode):
        self._change_mode(display_mode)
        self.modes_stack.append(display_mode)

    def pop_mode(self):
        popped = self.modes_stack.pop()
        head = self.modes_stack[-1]
        self._change_mode(head)
        return popped

