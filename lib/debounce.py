from arambadge import badge

def wait_for_button_release():
    while badge.gamepad.get_pressed():
        pass