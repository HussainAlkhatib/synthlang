# Image processing module (C backed)
@c module "./src/c/image" as image_native

fn load(path):
    image_native.image_load(path, null, null, null)

fn get_pixel(data, x, y, width, channels):
    image_native.image_get_pixel(data, x, y, width, channels)

fn create(width, height, channels):
    image_native.image_create(width, height, channels)

fn resize(data, width, height, channels, new_width, new_height):
    image_native.image_resize(data, width, height, channels, new_width, new_height)

# High-level wrapper
fn load_image(path):
    let data = load(path)
    return {"data": data, "width": null, "height": null, "channels": null}