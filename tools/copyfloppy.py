import addons
import os
import displayio
import terminalio
import storage
from arambadge import badge
from adafruit_display_text import label
from adafruit_progressbar.horizontalprogressbar import (
    HorizontalProgressBar,
    HorizontalFillDirection,
)

def copyfile(source, target):
    with open(source, 'rb') as inf, open(target, 'wb') as outf:
        buf = inf.read(512)
        while len(buf) > 0:
            outf.write(buf)
            buf = inf.read(512)

def copyfloppy(targetfolder, files = None, caption = "Copying files...", captionx = 60):
    """
    Copy files from a floppy disk into the the badge's local filesystem.

    Returns True if copying succeeded, False in case of an error (e.g. 
    filesystem can't be mounted for writing).
    """
    try:
        storage.remount('/', False)
    except:
        return False
    try:
        os.mkdir(targetfolder)
    except:
        pass
    if not files:
        files = os.listdir('/floppy')
    display = badge.display
    screen = displayio.Group()

    copying_label = label.Label(terminalio.FONT, text=caption, color=0xffffff)
    copying_label_group = displayio.Group(scale=2, x=captionx, y=display.height - 60)
    copying_label_group.append(copying_label)
    screen.append(copying_label_group)

    progress_bar = HorizontalProgressBar(
        (10, display.height - 40),
        (display.width - 20, 30),
        min_value=0,
        max_value=len(files),
        direction=HorizontalFillDirection.LEFT_TO_RIGHT,
    )
    screen.append(progress_bar)  
    display.show(screen)
    display.refresh()
    for filename in files:
        copyfile('/floppy/{}'.format(filename), '{}/{}'.format(targetfolder, filename))
        progress_bar.value += 1
        display.show(screen)
        display.refresh()
    storage.remount('/', True)
    return True
