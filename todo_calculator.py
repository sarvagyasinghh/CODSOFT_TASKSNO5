"""
Simple Calculator
A basic Python calculator that performs addition, subtraction,
multiplication, and division based on user input.

Internship: CodSoft
"""

def calculator():
    print("=== Simple Calculator ===")
    print("Operations: +, -, *, /")

    try:
        num1 = float(input("Enter first number: "))
        op = input("Choose operation (+, -, *, /): ").strip()
        num2 = float(input("Enter second number: "))
    except ValueError:
        print("Error: Please enter valid numbers.")
        return

    if op == '+':
        result = num1 + num2
    elif op == '-':
        result = num1 - num2
    elif op == '*':
        result = num1 * num2
    elif op == '/':
        if num2 == 0:
            print("Error: Cannot divide by zero.")
            return
        result = num1 / num2
    else:
        print("Invalid operation. Please choose +, -, *, or /.")
        return

    print(f"Result: {num1} {op} {num2} = {result}")


if __name__ == "__main__":
    calculator()