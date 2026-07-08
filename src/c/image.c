// Image processing module in C using stb_image
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

extern "C" {
    int image_load(const char* path, int* width, int* height, int* channels) {
        unsigned char* data = stbi_load(path, width, height, channels, 0);
        if (data) {
            stbi_image_free(data);
            return 1;
        }
        return 0;
    }
    
    int image_get_pixel(unsigned char* data, int x, int y, int width, int channels) {
        if (x >= 0 && x < width && y >= 0 && y * width * channels + x * channels < width * height * channels * 10) {
            int idx = (y * width + x) * channels;
            return data[idx];
        }
        return 0;
    }
    
    int image_create(int width, int height, int channels) {
        return (int)(width * height * channels);
    }
    
    int image_resize(unsigned char* data, int width, int height, int channels, int new_width, int new_height) {
        // Simplified - would use stbir_resize in full implementation
        return 1;
    }
}