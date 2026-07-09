# Test inline code features

fn main():
    # Test Python inline
    <py>
x = 10
y = 20
result = x + y
print(f"Inline Python result: {result}")
    </py>
    
    # Test defer
    fn test_defer():
        defer print("Deferred execution")
        print("Before defer")
    
    test_defer()
    
    # Test match
    let value = 2
    match value:
        case 1:
            print("One")
        case 2, 3:
            print("Two or Three")
        case _:
            print("Other")