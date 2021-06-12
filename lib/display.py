import adafruit_il0373
import time

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
    b"\x50\x01\x37"  # CDI setting
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
    b"\x50\x01\x37"  # CDI setting
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

class Display(adafruit_il0373.IL0373):
    MODE_HYBRID = 0
    MODE_NORMAL = 1
    MODE_QUICK = 2
    MODE_QUICKER = 3

    MODE_PARAMETERS = {
        MODE_HYBRID: (None, 1, 15),
        MODE_NORMAL: (NORMAL_START_SEQUENCE, 5),
        MODE_QUICK: (QUICK_START_SEQUENCE, 1),
        MODE_QUICKER: (QUICKER_START_SEQUENCE, 0.33)
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.refresh_counter_since_full = 0
        self.modes_stack = [Display.MODE_HYBRID]
        self._change_mode(self.modes_stack[-1])

    def refresh(self):
        try:
            if self.modes_stack[-1] != Display.MODE_HYBRID:
                while self.busy:
                    time.sleep(0.1)
                super().refresh()
                return

            if self.refresh_counter_since_full > Display.MODE_PARAMETERS[Display.MODE_HYBRID][2]:
                while self.busy:
                    time.sleep(0.1)
                super().refresh()
                self._change_mode(Display.MODE_QUICKER)
                while self.busy:
                    time.sleep(0.1)
                self.refresh_counter_since_full = 0
            else:
                while self.busy:
                    time.sleep(0.1)
                super().refresh()
                if self.refresh_counter_since_full == Display.MODE_PARAMETERS[Display.MODE_HYBRID][2]:
                    self._change_mode(Display.MODE_QUICK)
                self.refresh_counter_since_full += 1
        except RuntimeError as e:
            import traceback
            traceback.print_exc()

    def _change_mode(self, display_mode):
        if display_mode != Display.MODE_HYBRID:
            self.update_refresh_mode(*Display.MODE_PARAMETERS[display_mode])
        else:
            self.update_refresh_mode(*Display.MODE_PARAMETERS[Display.MODE_QUICKER])
            self.refresh_counter_since_full = 0


    def update_refresh_mode(self, start_sequence, seconds_per_frame):
        super().update_refresh_mode(start_sequence, seconds_per_frame)


    def push_mode(self, display_mode):
        self._change_mode(display_mode)
        self.modes_stack.append(display_mode)

    def pop_mode(self):
        if len(self.modes_stack) <= 1:
            return None
        popped = self.modes_stack.pop()
        head = self.modes_stack[-1]
        self._change_mode(head)
        return popped

