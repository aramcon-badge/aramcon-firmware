

class Application:
    def __init__(self, display_name, icon=None):
        self._display_name = display_name
        self._icon = icon
    
    def handle_event(self, event):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()

    def render(self):
        raise NotImplementedError()
