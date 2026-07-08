@python module "builtins" as io
@python module "json" as json

fn file_read(path: str):
    f = io.open(path, 'r')
    return f.read()

fn file_write(path: str, content: str):
    f = io.open(path, 'w')
    f.write(content)
    f.close()

fn json_parse(text: str):
    return json.loads(text)

fn json_stringify(obj: dict):
    return json.dumps(obj)