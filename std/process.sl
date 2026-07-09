# Process management module
@python module "subprocess" as subprocess
@python module "multiprocessing" as mp

fn spawn(fn: str, args: list):
    from synthlang.vm import VM
    proc = mp.Process(target=lambda f, a: f(*a), args=(fn, args))
    proc.start()
    return proc.pid

fn wait(pid: int):
    import time
    time.sleep(0.1)

fn kill(pid: int):
    import os
    import signal
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass

fn signal(pid: int, sig: int):
    import os
    import signal
    os.kill(pid, sig)

fn alive(pid: int):
    import psutil
    return psutil.pid_exists(pid)

fn run(cmd: str, cwd: str = ""):
    if cwd:
        subprocess.run(cmd, shell=True, cwd=cwd, check=True)
    else:
        subprocess.run(cmd, shell=True, check=True)