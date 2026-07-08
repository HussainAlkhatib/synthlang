fn square(x: int): int
    return x * x

fn sum(a: int, b: int): int
    return a + b

let result = square(sum(2, 3))
print(result)