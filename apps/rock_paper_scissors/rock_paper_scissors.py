from arambadge import badge, Badge
import time
import binascii


from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.button_packet import ButtonPacket

import displayio
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect
import terminalio

palette = displayio.Palette(2)
palette[0] = 0xffffff
palette[1] = 0


# Icons from:
# https://fontawesome.com/icons/hand-rock?style=regular
# https://fontawesome.com/icons/hand-paper?style=regular
# https://fontawesome.com/icons/hand-scissors?style=regular

icons = [
    displayio.OnDiskBitmap(open("/apps/rock_paper_scissors/hand-rock-regular.bmp", "rb")),
    displayio.OnDiskBitmap(open("/apps/rock_paper_scissors/hand-paper-regular.bmp", "rb")),
    displayio.OnDiskBitmap(open("/apps/rock_paper_scissors/hand-scissors-regular.bmp", "rb"))
    ]



def show_frame(group, refresh = True):
    badge.display.show(group)
    while refresh:
        if badge.display.time_to_refresh == 0:
            badge.display.refresh()
            break

def large_label(text, x = 0, y = 0, scale = 2):
    group = displayio.Group(scale=scale, x = x, y = y)
    group.append(Label(terminalio.FONT, text=text))
    return group

def wait_for_button_release():
    while badge.gamepad.get_pressed():
        pass

def create_controls(controls, base_x = 30, stride_x = 100, base_y = 120):
    frame = displayio.Group(max_size=3, x = base_x, y = base_y)
    for idx, label in enumerate(controls):
        frame.append(Label(terminalio.FONT, text=label, x = stride_x * idx))
    return frame

def render_menu(menu_name, options, selected_index):
    option_base_x = 100
    option_stride_x = 95
    option_base_y = 60
    option_stride_y = 15


    frame = displayio.Group(max_size=13)

    frame.append(large_label(menu_name, x=35, y=20))

    number_of_options = len(options)
    extended_menu = 0
    if number_of_options > 3:
        extended_menu = 1
        option_base_x = 30
        
    for i in range(number_of_options):
        option_text = '-> ' if i == selected_index else ''
        option_text += options[i]
        option_label = Label(terminalio.FONT, text=option_text)
        x = i // 3
        y = i % 3
        option_label.x = option_base_x + option_stride_x * x * extended_menu
        option_label.y = option_base_y + option_stride_y * y
        frame.append(option_label)

    badge.display.show(frame)

def run_menu(menu_name, options):
    should_refresh = True
    selection_complete = False
    selected_index = 0
    menu_size = len(options)

    while True:
        if not should_refresh:
            buttons = badge.gamepad.get_pressed()
            if buttons & Badge.BTN_DOWN:
                selected_index += 1
                selected_index = selected_index % menu_size
                should_refresh = True
            elif buttons & Badge.BTN_UP:
                selected_index -= 1
                selected_index = selected_index % menu_size
                should_refresh = True
            elif buttons & Badge.BTN_ACTION:
                selection_complete = True

            wait_for_button_release()
            
            if selection_complete:
                return selected_index

        if should_refresh and (badge.display.time_to_refresh == 0):
            render_menu(menu_name, options, selected_index)
            time.sleep(0.1)
            badge.display.refresh()
            should_refresh = False

def render_status(status, controls = None):
    g = displayio.Group()

    connected_label = Label(terminalio.FONT, text=status)
    connected_label.x = 80
    connected_label.y = 60
    g.append(connected_label)

    if controls:
        g.append(create_controls(controls))

    show_frame(g)

def render_game_menu():
    g = displayio.Group(max_size = 6)

    base_x = 30
    base_y = 34
    current_x = base_x
    for i in range(len(icons)):
        grid = displayio.TileGrid(icons[i], pixel_shader=palette, x=current_x, y=base_y)
        g.append(grid)
        current_x += 90
    show_frame(g)

def render_game_over(game_result, my_choice, opponent_choice):
    frame = displayio.Group(max_size=10)

    game_options = ['Rock', 'Paper', 'Scissors']
    game_summary = '{} vs {}'.format(game_options[my_choice], game_options[opponent_choice])

    frame.append(large_label(game_result, x=90, y=20))
    frame.append(Label(terminalio.FONT, text=game_summary, x=94, y=50))
    frame.append(large_label('Rematch?', x=90, y=80))
    frame.append(create_controls(['YES', ' ', 'NO']))

    show_frame(frame)

    while True:
        buttons = badge.gamepad.get_pressed()
        if buttons & Badge.BTN_LEFT:
            wait_for_button_release()
            return True
        elif buttons & Badge.BTN_RIGHT:
            wait_for_button_release()
            return False

def run_game_menu():
    selection = -1
    while True:
        buttons = badge.gamepad.get_pressed()
        if buttons & Badge.BTN_LEFT:
            selection = 0
        elif buttons & Badge.BTN_UP:
            selection = 1
        elif buttons & Badge.BTN_RIGHT:
            selection = 2

        wait_for_button_release()

        if selection != -1:
            return selection


WIN = 'You won'
LOSE = 'You Lost'
TIE =  "It's a tie"

def resolve_game(choices):
    options = {
        '[0, 0]': TIE,
        '[0, 1]': LOSE,
        '[0, 2]': WIN,
        '[1, 0]': WIN,
        '[1, 1]': TIE,
        '[1, 2]': LOSE,
        '[2, 0]': LOSE,
        '[2, 1]': WIN,
        '[2, 2]': TIE}
    return options[choices]




class RockPaperScissorsApp:
    def __init__(self):
        self.ble = BLERadio()
        self.device_name = 'rps-{}'.format(str(binascii.hexlify(bytearray(reversed(self.ble.address_bytes[0:2]))), 'utf-8'))
    
    def send_choice(self, uart, index):
        buttons = [ButtonPacket.BUTTON_1, ButtonPacket.BUTTON_2, ButtonPacket.BUTTON_3]
        button_packet = ButtonPacket(buttons[index], True)
        for i in range(3):
            try:
                uart.write(button_packet.to_bytes())
                break
            except OSError:
                pass
            time.sleep(0.3)

    def receive_choice(self, uart):
        while True:
            packet = Packet.from_stream(uart)
            if isinstance(packet, ButtonPacket):
                return [ButtonPacket.BUTTON_1, ButtonPacket.BUTTON_2, ButtonPacket.BUTTON_3].index(packet.button)


    def host_game(self):
        uart_service = UARTService()
        advertisement = ProvideServicesAdvertisement(uart_service)
        self.ble.start_advertising(advertisement)
        render_status('Hosting on {}'.format(self.device_name), [' ', 'CANCEL'])
        while not self.ble.connected:
            if badge.gamepad.get_pressed() & Badge.BTN_ACTION:
                self.ble.stop_advertising()
                wait_for_button_release()
                return None
        self.ble.stop_advertising()
        return uart_service

    def join_game(self, game_host):
        self.ble.connect(game_host)
        while not self.ble.connected:
            pass
        return self.ble.connections[0][UARTService]

    def scan_for_games(self):
        advertisments = []
        for advertisement in self.ble.start_scan(ProvideServicesAdvertisement, timeout=1):
            if UARTService not in advertisement.services:
                continue
            else:
                advertisments.append(advertisement)
        self.ble.stop_scan()
        return [advertisment for advertisment in advertisments if str(advertisment.complete_name, 'utf-8').startswith('rps')]

    def setup_game(self):
        selected_host = None
        while selected_host is None:
            game_host_options = ['Host game', 'Rescan', 'Quit']
            game_hosts = self.scan_for_games()
            if not game_hosts is None:
                game_host_options = [str(game_host.complete_name, 'utf-8') for game_host in game_hosts] + game_host_options
            
            selected_host_option = run_menu(menu_name='Rock Paper Scissors', options=game_host_options)
            host_option_name = game_host_options[selected_host_option]
            if host_option_name == 'Host game':
                game = self.host_game()
                if game:
                    return game
            elif host_option_name == 'Rescan':
                continue
            elif host_option_name == 'Quit':
                return None
            else:
                host_name = next(game_host for game_host in game_hosts if str(game_host.name, 'utf-8') == host_option_name)
                return self.join_game(host_name)

    def run_game(self, uart):
        render_game_menu()
        selected_game_option = run_game_menu()
        badge.pixels.fill((0, 10, 0))
        badge.vibration = True
        self.send_choice(uart, selected_game_option)
        time.sleep(0.25)
        badge.vibration = False
        other_player_choice = self.receive_choice(uart)
        badge.pixels.fill((0, 0, 0))
        return (selected_game_option, other_player_choice)

    def run(self):
        while True:
            uart = self.setup_game()
            if not uart:
                return
            while True:
                my_choice, opponent_choice = self.run_game(uart)
                game_result = resolve_game(str([my_choice, opponent_choice]))
                play_again = render_game_over(game_result, my_choice, opponent_choice)
                self.send_choice(uart, play_again)
                if play_again:
                    play_again = self.receive_choice(uart)
                if not play_again:
                    render_status('Disconnecting...')
                    break
            uart.disconnect()
            time.sleep(2)

def main():
    return RockPaperScissorsApp()

