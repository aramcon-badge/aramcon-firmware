from arambadge import badge
import time
import tasko
import board
import digitalio
from pulseio import PWMOut

def note(name):
    octave = int(name[-1])
    PITCHES = "c,c#,d,d#,e,f,f#,g,g#,a,a#,b".split(",")
    pitch = PITCHES.index(name[:-1].lower())
    return 440 * 2 ** ((octave - 4) + (pitch - 9) / 12.)

sequence = [
  ("e5", 2), ("e5", 2), ("e5", 4), ("e5", 2), ("e5", 2), ("e5", 4),
  ("e5", 2), ("g5", 2), ("c5", 4), ("d5", 1), ("e5", 6), (None, 2),
  ("f5", 2), ("f5", 2), ("f5", 3), ("f5", 1), ("f5", 2), ("e5", 2),
  ("e5", 2), ("e5", 1), ("e5", 1), ("e5", 2), ("d5", 2), ("d5", 2),
  ("e5", 2), ("d5", 4), ("g5", 2), (None, 2),
  ("e5", 2), ("e5", 2), ("e5", 4), ("e5", 2), ("e5", 2), ("e5", 4),
  ("e5", 2), ("g5", 2), ("c5", 4), ("d5", 1), ("e5", 6), (None, 2),
  ("f5", 2), ("f5", 2), ("f5", 3), ("f5", 1), ("f5", 2), ("e5", 2),
  ("e5", 2), ("e5", 1), ("e5", 1), ("g5", 2), ("g5", 2), ("f5", 2),
  ("d5", 2), ("c5", 6), (None, 2)
]

async def main(addon):
    await badge.show_bitmap('drivers/assets/speaker.bmp')
    
    audio = PWMOut(board.GPIO1, duty_cycle=0, frequency=440, variable_frequency=True)
    led = digitalio.DigitalInOut(board.GPIO2)
    led.switch_to_output(True)
    try:
        for (notename, eigths) in sequence:
            length = eigths * 0.1
            if notename:
                led.value = False
                audio.frequency = round(note(notename))
                audio.duty_cycle = 0x8000
            await tasko.sleep(length)
            led.value = True
            audio.duty_cycle = 0
            await tasko.sleep(0.025)
        
        await tasko.sleep(3)
    finally:
        led.deinit()
        audio.deinit()
