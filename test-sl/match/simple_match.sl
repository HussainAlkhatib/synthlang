fn main():
    match 1:
        case 1:
            print("One")
        case 2, 3:
            print("Two or Three")
        case _:
            print("Other")

# Expected output: One