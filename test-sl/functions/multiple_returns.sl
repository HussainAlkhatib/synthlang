fn early_return(x: int): int
    if x > 10:
        return 100
    return 0

fn multiple_paths(x: int): int
    if x < 0:
        return -1
    elif x == 0:
        return 0
    else:
        return 1

let a = early_return(15)
let b = multiple_paths(0)
print(a)
print(b)