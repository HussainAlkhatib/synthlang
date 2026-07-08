# Process management module (Go backed)
@go module "./src/go/std/process" as proc_native

fn spawn(command: list):
    proc_native.process_spawn(command[0], command[1:])

fn run(command: str):
    proc_native.process_execute(command, [])

fn get_input(prompt: str):
    native_input(prompt)

fn native_input(prompt):
    # Use Python for stdin interaction
    @python module "builtins" as _builtins
    return _builtins.input(prompt)