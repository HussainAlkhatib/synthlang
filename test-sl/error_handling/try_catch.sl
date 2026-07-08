fn risky_division(a, b):
    if b == 0:
        panic("Division by zero")

fn main():
    try risky_division(10, 0):
    handle error:
        print("Error caught:", error)

# Expected output: Error caught: Division by zero