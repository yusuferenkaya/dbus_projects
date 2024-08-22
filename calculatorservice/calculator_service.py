from pydbus import SessionBus
from gi.repository import GLib
from pydbus.generic import signal

class CalculatorService:
    """
    <node>
        <interface name='calculator.service'>
            <method name='add'>
                <arg type='d' name='a' direction='in'/>
                <arg type='d' name='b' direction='in'/>
                <arg type='d' name='result' direction='out'/>
            </method>
            <method name='subtract'>
                <arg type='d' name='a' direction='in'/>
                <arg type='d' name='b' direction='in'/>
                <arg type='d' name='result' direction='out'/>
            </method>
            <method name='multiply'>
                <arg type='d' name='a' direction='in'/>
                <arg type='d' name='b' direction='in'/>
                <arg type='d' name='result' direction='out'/>
            </method>
            <method name='divide'>
                <arg type='d' name='a' direction='in'/>
                <arg type='d' name='b' direction='in'/>
                <arg type='d' name='result' direction='out'/>
            </method>
            <property name='History' type='as' access='read'/>
        </interface>
    </node>
    """

    def __init__(self):
        self._history = []

    def add(self, a, b):
        result = a + b
        self._history.append(f"Added {a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        result = a - b
        self._history.append(f"Subtracted {a} - {b} = {result}")
        return result

    def multiply(self, a, b):
        result = a * b
        self._history.append(f"Multiplied {a} * {b} = {result}")
        return result

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self._history.append(f"Divided {a} / {b} = {result}")
        return result

    @property
    def History(self):
        return self._history

if __name__ == "__main__":
    bus = SessionBus()
    bus.publish("calculator.service", CalculatorService())

    print("Calculator service is running...")

    loop = GLib.MainLoop()
    loop.run()