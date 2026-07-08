@rust module "math_utils.rs" as math_utils
@python module "math" as math

fn calculate() -> int:
    # Call Rust function for performance-critical math
    result = math_utils.factorial(10)
    return result

fn main():
    let rust_result = calculate()
    print("Rust factorial(10) =", rust_result)
    
    # Fallback to Python
    let py_result = math.factorial(10)
    print("Python factorial(10) =", py_result)