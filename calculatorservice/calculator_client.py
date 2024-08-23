import dbus
import dbus.mainloop.glib
from gi.repository import GLib

def property_changed(interface_name, changed_properties, invalidated_properties):
    if 'LastOperationResult' in changed_properties:
        last_result = changed_properties['LastOperationResult']
        print(f"\nLast Operation Result: {last_result}\n")

def parse_input(expression):
    if '+' in expression:
        a, b = expression.split('+')
        operation = 'Add'
    elif '-' in expression:
        a, b = expression.split('-')
        operation = 'Subtract'
    elif '*' in expression:
        a, b = expression.split('*')
        operation = 'Multiply'
    elif '/' in expression:
        a, b = expression.split('/')
        operation = 'Divide'
    else:
        raise ValueError("Invalid expression")
    
    return operation, float(a), float(b)

if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()

    calculator_object = bus.get_object('calculator.service', '/calculator/service')
    calculator_interface = dbus.Interface(calculator_object, dbus_interface='calculator.service')
    properties_interface = dbus.Interface(calculator_object, dbus_interface='org.freedesktop.DBus.Properties')

    # property changed signal
    properties_interface.connect_to_signal('PropertiesChanged', property_changed)

    while True:
        expression = input("Enter expression (e.g. 5+3, 8*2, 9/3) or type 'history' to view operations: ").strip()

        if expression.lower() == "history":
            history = properties_interface.Get('calculator.service', 'History')
            print("\nOperation History:")
            for entry in history:
                print(entry)
            continue
        elif expression.lower() == "last":
            last_result = properties_interface.Get('calculator.service', 'LastOperationResult')
            print(f"\nLast Operation Result: {last_result}\n")
            continue

        try:
            operation, a, b = parse_input(expression)
        except ValueError as e:
            print(f"Error: {e}")
            continue

        # Call the appropriate D-Bus method based on the operation
        try:
            if operation == 'Add':
                result = calculator_interface.Add(dbus.Double(a), dbus.Double(b))
            elif operation == 'Subtract':
                result = calculator_interface.Subtract(dbus.Double(a), dbus.Double(b))
            elif operation == 'Multiply':
                result = calculator_interface.Multiply(dbus.Double(a), dbus.Double(b))
            elif operation == 'Divide':
                result = calculator_interface.Divide(dbus.Double(a), dbus.Double(b))
                
            print(f"Result: {result}")
        except dbus.DBusException as e:
            print(f"DBus error: {str(e)}")

        print("\nType 'exit' to quit or press Enter to continue...")
        if input().strip().lower() == 'exit':
            break

    # Start the main loop to listen for signals
    loop = GLib.MainLoop()
    loop.run()