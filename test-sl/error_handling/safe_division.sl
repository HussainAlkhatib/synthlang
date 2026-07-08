fn safe_div(a: int, b: int): int
    if b == 0:
        return 0
    return a / b

let r1 = safe_div(10, 2)
let r2 = safe_div(10, 0)
print(r1)
print(r2)