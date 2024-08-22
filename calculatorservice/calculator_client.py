from pydbus import SessionBus

def parse_input(expression):
    if '+' in expression:
        a, b = expression.split('+')
        operation = 'add'
    elif '-' in expression:
        a, b = expression.split('-')
        operation = 'subtract'
    elif '*' in expression:
        a, b = expression.split('*')
        operation = 'multiply'
    elif '/' in expression:
        a, b = expression.split('/')
        operation = 'divide'
    else:
        raise ValueError("Invalid expression")
    
    return operation, float(a), float(b)

if __name__ == "__main__":
    bus = SessionBus()
    calculator = bus.get("calculator.service")

    while True:
        expression = input("Enter expression (e.g. 5+3, 8*2, 9/3) or type 'history' to view operations: ").strip()
        
        if expression.lower() == "history":
            print("\nOperation History:")
            for entry in calculator.History:
                print(entry)
            continue

        try:
            operation, a, b = parse_input(expression)
        except ValueError as e:
            print(f"Error: {e}")
            continue

        # Call the appropriate D-Bus method based on the operation
        if operation == 'add':
            result = calculator.add(a, b)
        elif operation == 'subtract':
            result = calculator.subtract(a, b)
        elif operation == 'multiply':
            result = calculator.multiply(a, b)
        elif operation == 'divide':
            try:
                result = calculator.divide(a, b)
            except ValueError as e:
                print(f"Error: {e}")
                continue

        print(f"Result: {result}")

        print("\nType 'exit' to quit or press Enter to continue...")
        if input().strip().lower() == 'exit':
            break