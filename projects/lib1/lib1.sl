# Reusable Library - Mathematical and Utility Functions
# Can be imported by other SynthLang projects

fn add(a: int, b: int): int
    return a + b

fn subtract(a: int, b: int): int
    return a - b

fn multiply(a: int, b: int): int
    return a * b

fn factorial(n: int): int
    if n <= 1:
        return 1
    return n * factorial(n - 1)

fn main(): int
    print("lib1 - SynthLang Math Library v1.1.0")
    print("Functions: add, subtract, multiply, factorial, fibonacci")
    return 0

main()