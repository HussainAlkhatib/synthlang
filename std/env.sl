@python module "os" as os

fn env_get(var_name: str):
    return os.getenv(var_name)

fn env_set(var_name: str, value: str):
    os.environ[var_name] = value