# Image processing module (C backed)
@c module "./src/c/image" as image_native

fn load(path: str):
    image_native.load(path)

fn save(path: str, data: dict):
    image_native.save(path, data)

fn resize(data: dict, width: int, height: int):
    image_native.resize(data, width, height)

fn rotate(data: dict, degrees: float):
    image_native.rotate(data, degrees)

fn crop(data: dict, x: int, y: int, w: int, h: int):
    image_native.crop(data, x, y, w, h)

fn blur(data: dict, radius: float):
    image_native.blur(data, radius)

fn grayscale(data: dict):
    image_native.grayscale(data)

fn contrast(data: dict, amount: float):
    image_native.contrast(data, amount)

fn brightness(data: dict, amount: float):
    image_native.brightness(data, amount)