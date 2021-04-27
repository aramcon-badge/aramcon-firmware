import os
import json
import displayio
import terminalio
import time
import tasko
from arambadge import badge
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect

APP_DIR = "apps"
MENU_ROOT = '/'.join(__file__.split('/')[:-1])

def load_app(app_path):
    app_file = "{}/app.json".format(app_path)
    try:
        app_json = open(app_file, 'r')
        manifest = json.load(app_json)
        manifest['path'] = app_path
        return manifest
    except:
        return None

def load_apps():
    apps = []
    floppy_app = load_app("/floppy")
    if floppy_app:
        apps.append(floppy_app)
    for app_name in os.listdir(APP_DIR):
        app_path = "{}/{}".format(APP_DIR, app_name)
        app = load_app(app_path)
        if app:
            apps.append(app)
    return apps

async def run_app(app):
    action = app.get('menu_action', None)
    if action:
        return action()
    main = app.get('main', 'main.py')
    module = __import__('{}/{}'.format(app['path'], main.replace('.py', '')))
    return await module.main().run()

class MenuApp:
    def __init__(self):
        self.apps = []
        self.selection = 0

    def render(self):
        display = badge.display
        font = terminalio.FONT
        apps_per_screen = 3

        screen = displayio.Group(max_size=3 + apps_per_screen)
        screen.append(Rect(0, 0, display.width, display.height, fill=0xffffff))
        
        banner_image = displayio.OnDiskBitmap(open("/assets/banner.bmp", "rb"))
        banner = displayio.TileGrid(banner_image, pixel_shader=displayio.ColorConverter())
        screen.append(banner)

        first_app = (self.selection // apps_per_screen) * apps_per_screen

        # List of apps
        for index, app in enumerate(self.apps[first_app:first_app + apps_per_screen]):
            title = app['menu_item']
            y = 5 + (index % apps_per_screen) * 40
            app_group = displayio.Group(x=38, y=y)
            fill = 0
            palette = displayio.Palette(1)
            if first_app + index == self.selection:
                app_group.append(Rect(-5, -4, display.width - 32, 40, fill=0))
                fill = 0xffffff
                palette[0] = 0xffffff
            try:
                app_icon_file = app.get('icon', "{}/icon.bmp".format(app.get('path', '')))
                app_icon = displayio.OnDiskBitmap(open(app_icon_file, "rb"))
                app_group.append(displayio.TileGrid(app_icon, pixel_shader=palette))
            except:
                pass
            app_label = label.Label(font, text=title, color=fill)
            app_label_group = displayio.Group(scale=2, x=38, y=13)
            app_label_group.append(app_label)
            app_group.append(app_label_group)
            screen.append(app_group)

        if first_app + apps_per_screen < len(self.apps):
            # we have more app, display a down arrow
            more_icon = displayio.OnDiskBitmap(open("{}/arrow_down.bmp".format(MENU_ROOT), "rb"))
            screen.append(displayio.TileGrid(more_icon, pixel_shader=displayio.ColorConverter(), x=display.width - 16, y=display.height - 7))
        
        # Show it
        display.show(screen)

    async def process_input(self):
        buttons = badge.gamepad.get_pressed() 
        num_apps = len(self.apps)
        if buttons & badge.BTN_UP:
            self.selection = (self.selection + num_apps - 1) % num_apps
        elif buttons & badge.BTN_DOWN:
            self.selection = (self.selection + 1) % num_apps
        elif buttons & badge.BTN_RIGHT:
            self.selection = (self.selection + num_apps - 3) % num_apps
        elif buttons & badge.BTN_LEFT:
            self.selection = (self.selection + num_apps - 3) % num_apps
        elif buttons & badge.BTN_ACTION:
            badge.vibration = True
            # Wait until the action button is released
            while badge.gamepad.get_pressed() & badge.BTN_ACTION:
                pass
            await tasko.sleep(0.1)
            badge.vibration = False
            await run_app(self.apps[self.selection])
        else:
            return False
        return True

    async def run(self):
        self.apps = list(filter(lambda app: 'menu_item' in app, load_apps()))
        self.apps.append({
            'icon': '{}/home.bmp'.format(MENU_ROOT),
            'menu_item': 'Back', 
            'menu_action': self.stop
        })
        self.selection = 0
        self.running = True
        while self.running:
            self.render()
            while badge.display.time_to_refresh > 0:
                pass
            if not await self.process_input():
                badge.display.refresh()

    def stop(self):
        self.running = False
