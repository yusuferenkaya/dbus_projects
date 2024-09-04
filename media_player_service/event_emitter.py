from gi.repository import GLib

class Events:
    _instance = None

    def __init__(self):
        if Events._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Events._instance = self
        self._events = {}

    @staticmethod
    def instance():
        if Events._instance is None:
            Events()
        return Events._instance

    def on(self, event_name, listener):
        """Register a listener for a specific event."""
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append(listener)

    def emit(self, event_name, *args, **kwargs):
        """Emit an event, calling all registered listeners."""
        if event_name in self._events:
            for listener in self._events[event_name]:
                GLib.idle_add(listener, *args, **kwargs)