# CLI Tool - Text Statistics
# Processes text files and outputs statistics

fn show_help(): void
    print("CLI Text Statistics Tool")
    print("Usage: slang run cli1/sl --input <file> [--output <file>]")
    print("")
    print("Options:")
    print("  --input <file>   Input text file to process")
    print("  --output <file>  Output file for results (optional)")
    print("  --help           Show this help message")

fn add(a: int, b: int): int
    return a + b

fn subtract(a: int, b: int): int
    return a - b

fn main(): int
    print("CLI Tool ready. Use --help for usage information.")
    return 0

main()