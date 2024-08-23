from pydbus import SessionBus
from gi.repository import GLib
from pydbus.generic import signal

class CalculatorService:
    """
    <node>
        <interface name='calculator.service'>
            <method name='Add'>
                <arg type='d' name='a' direction='in'/>
                <arg type='d' name='b' direction='in'/>
                <arg type='d' name='result' direction='out'/>
            </method>
            <method name='Subtract'>
                <arg type='d' name='a' direction='in'/>
                <arg type='d' name='b' direction='in'/>
                <arg type='d' name='result' direction='out'/>
            </method>
            <method name='Multiply'>
                <arg type='d' name='a' direction='in'/>
                <arg type='d' name='b' direction='in'/>
                <arg type='d' name='result' direction='out'/>
            </method>
            <method name='Divide'>
                <arg type='d' name='a' direction='in'/>
                <arg type='d' name='b' direction='in'/>
                <arg type='d' name='result' direction='out'/>
            </method>
            <property name='History' type='as' access='read'/>
            <property name='LastOperationResult' type='d' access='read'/>
        </interface>
    </node>
    """

    PropertiesChanged = signal()

    def __init__(self):
        self._history = []
        self._last_result = 0.0

    def Add(self, a, b):
        result = a + b
        self._update_history(f"Added {a} + {b} = {result}")
        self._update_last_result(result)
        return result

    def Subtract(self, a, b):
        result = a - b
        self._update_history(f"Subtracted {a} - {b} = {result}")
        self._update_last_result(result)
        return result

    def Multiply(self, a, b):
        result = a * b
        self._update_history(f"Multiplied {a} * {b} = {result}")
        self._update_last_result(result)
        return result

    def Divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self._update_history(f"Divided {a} / {b} = {result}")
        self._update_last_result(result)
        return result

    @property
    def History(self):
        return self._history

    @property
    def LastOperationResult(self):
        return self._last_result

    def _update_history(self, entry):
        self._history.append(entry)

    def _update_last_result(self, result):
        self._last_result = result
        # Emitting PropertiesChanged sinyal
        self.PropertiesChanged('calculator.service', {'LastOperationResult': self._last_result}, [])

if __name__ == "__main__":
    bus = SessionBus()
    bus.publish("calculator.service", CalculatorService())

    print("Calculator service is running...")

    loop = GLib.MainLoop()
    loop.run()