@python module "subprocess" as subprocess

fn spawn(command: list):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.pid

fn run(command: str):
    result = subprocess.run(command, shell=true, capture_output=true, text=true)
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}

fn get_input(prompt: str):
    return input(prompt)