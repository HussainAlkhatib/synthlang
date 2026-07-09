# Environment variables and process module
@python module "os" as os_native
@python module "sys" as sys_native

fn get(name: str):
    os_native.getenv(name)

fn set(name: str, value: str):
    os_native.environ[name] = value

fn unset(name: str):
    del os_native.environ[name]

fn args() -> list:
    sys_native.argv[1:]

fn exec(cmd: str):
    import subprocess
    subprocess.run(cmd, shell=True, check=True)

fn exit(code: int):
    import sys
    sys.exit(code)

fn getenv(name: str, default: str = ""):
    os_native.getenv(name, default)

fn environ() -> dict:
    dict(os_native.environ)