# Desktop Application Stub
# This demonstrates desktop app capability via @desktop annotation or FFI

fn show_message(msg: str): void
    print("[Desktop] " + msg)

fn main(): int
    show_message("Desktop app would open a window here.")
    print("Desktop application stub loaded.")
    print("To extend: implement FFI calls or add @desktop annotation support.")
    return 0

main()