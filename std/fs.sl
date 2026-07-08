# High-performance file system module (C++ backed)
@cpp module "./src/cpp/fs" as fs_native

fn read(path):
    # Uses native C++ implementation for high performance
    fs_native.read(path)

fn write(path, content):
    fs_native.write(path, content)

fn exists(path):
    fs_native.exists(path)

fn is_file(path):
    fs_native.is_file(path)

fn is_dir(path):
    fs_native.is_dir(path)

fn join_path(a, b):
    fs_native.join_path(a, b)

fn get_parent(path):
    fs_native.get_parent(path)

fn get_name(path):
    fs_native.get_name(path)

fn list_dir(path):
    fs_native.list_dir(path)