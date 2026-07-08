fn add(a: int, b: int): int
    return a + b

fn multiply(a: int, b: int): int
    return a * b

fn complex(): int
    let x = add(2, 3)
    let y = multiply(4, 5)
    return x + y

let r = complex()
print(r)