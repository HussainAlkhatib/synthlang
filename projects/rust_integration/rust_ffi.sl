# Rust Integration Demo
# Demonstrates FFI with Rust modules via C-shared library

@python module "math" as math

# In a real implementation, this would use:
# @rust module "crypto_utils.dll" as crypto
#
# fn hash_password(password: str):
#     # Call Rust functions for performance-critical crypto
#     let hash = crypto.sha256(password)
#     return hash

fn main():
    print("=== Rust Integration Demo ===")
    print("To use Rust FFI, compile Rust to C-shared library:")
    print("  rustup target add x86_64-pc-windows-gnu")
    print("  cargo build --release --target x86_64-pc-windows-gnu")
    print("")
    print("Then load it with:")
    print("  @rust module \"crypto_utils.dll\" as crypto")
    print("  let hash = crypto.sha256(\"password\")")
    print("")
    print("Features available:")
    print("- High-performance cryptography")
    print("- Memory safety at compiled speed")
    print("- Zero-cost abstractions")
    print("- SIMD operations")
    
    # Demo: Using Python math instead (since Rust FFI needs actual dll)
    let demo = math.factorial(10)
    print("Demo (Python math.factorial(10)):", demo)
    
    return "Rust demo complete"