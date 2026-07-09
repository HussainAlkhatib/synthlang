// Image processing module in C using stb_image
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

int image_load(const char* path, int* width, int* height, int* channels) {
    // Would use stb_image in full implementation
    *width = 0;
    *height = 0;
    *channels = 0;
    return 0;
}

int image_get_pixel(unsigned char* data, int x, int y, int width, int channels) {
    if (data && x >= 0 && x < width && y >= 0) {
        int idx = (y * width + x) * channels;
        return data[idx];
    }
    return 0;
}

int image_create(int width, int height, int channels) {
    return (int)(width * height * channels);
}

int image_resize(unsigned char* data, int width, int height, int channels, int new_width, int new_height) {
    // Would implement resize
    return 1;
}

#ifdef __cplusplus
}
#endif