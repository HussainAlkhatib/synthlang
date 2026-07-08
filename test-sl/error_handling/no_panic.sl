fn test_panic(): int
    if true:
        return 0
    return 1

let r = test_panic()
print(r)