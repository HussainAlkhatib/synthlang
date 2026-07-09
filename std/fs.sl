# High-performance file system module (C++ backed)
@cpp module "./src/cpp/fs" as fs_native

fn read(path: str):
    fs_native.read(path)

fn write(path: str, content: str):
    fs_native.write(path, content)

fn read_json(path: str):
    @python module "json" as json
    json.loads(read(path))

fn write_json(path: str, data: dict):
    @python module "json" as json
    write(path, json.dumps(data))

fn exists(path: str):
    fs_native.exists(path)

fn is_file(path: str):
    fs_native.is_file(path)

fn is_dir(path: str):
    fs_native.is_dir(path)

fn list_dir(path: str):
    fs_native.list_dir(path)

fn create_dir(path: str):
    fs_native.create_dir(path)

fn remove(path: str):
    fs_native.remove(path)

fn join_path(a: str, b: str):
    fs_native.join_path(a, b)

fn get_parent(path: str):
    fs_native.get_parent(path)

fn get_name(path: str):
    fs_native.get_name(path)

fn get_size(path: str):
    fs_native.get_size(path)

fn get_modified(path: str):
    fs_native.get_modified(path)