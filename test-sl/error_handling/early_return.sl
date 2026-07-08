fn early_return_fn(x: int): int
    if x > 100:
        return 999
    return x
    return 0

let r = early_return_fn(50)
print(r)