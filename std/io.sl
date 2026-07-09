# I/O module
@python module "sys" as sys_native

fn print(*args):
    print(*args)

fn input(prompt: str):
    return input(prompt)

fn read_line() -> str:
    return sys_native.stdin.readline()

fn read_all() -> str:
    return sys_native.stdin.read()

fn write_line(s: str):
    sys_native.stdout.write(s + "\n")

fn flush():
    sys_native.stdout.flush()

fn stderr_write(s: str):
    sys_native.stderr.write(s)