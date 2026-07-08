fn outer(x: int): int
    fn inner(y: int): int
        return y * y
    return inner(x)

let r = outer(5)
print(r)