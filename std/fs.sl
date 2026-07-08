@python module "builtins" as _builtins
@python module "os" as _os
@python module "json" as json
@python module "os.path" as _path

fn read(path):
    if exists(path):
        f = _builtins.open(path, "r")
        content = f.read()
        f.close()
        return content
    return null

fn write(path, content):
    f = _builtins.open(path, "w")
    f.write(content)
    f.close()
    return true

fn read_json(path):
    if exists(path):
        f = _builtins.open(path, "r")
        content = f.read()
        f.close()
        return json.loads(content)
    return {}

fn write_json(path, data):
    f = _builtins.open(path, "w")
    f.write(json.dumps(data))
    f.close()
    return true

fn exists(path):
    return _os.path.exists(path)

fn delete(path):
    _os.remove(path)
    return true

fn list_dir(path):
    if exists(path):
        return _os.listdir(path)
    return []

fn is_file(path):
    return _os.path.isfile(path)

fn is_dir(path):
    return _os.path.isdir(path)

fn join_path(a, b):
    return _os.path.join(a, b)

fn get_parent(path):
    return _os.path.dirname(path)

fn get_name(path):
    return _os.path.basename(path)