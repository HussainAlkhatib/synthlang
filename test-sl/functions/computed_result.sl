fn add(a: int, b: int): int
    return a + b

fn multiply(a: int, b: int): int
    return a * b

fn compute(): int
    let sum = add(2, 3)
    let product = multiply(sum, 4)
    return product

let result = compute()
print(result)