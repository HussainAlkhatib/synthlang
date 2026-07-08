fn double(x: int): int
    return x * 2

fn quadruple(x: int): int
    return double(double(x))

let r = quadruple(5)
print(r)