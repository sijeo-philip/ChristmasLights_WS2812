#include <stdint.h>

void c_fade_strip(uint32_t *leds, int count, float factor) {
    if (!leds || count <= 0) return;
    if (factor < 0.0f) factor = 0.0f;
    if (factor > 1.0f) factor = 1.0f;
    for (int i = 0; i < count; ++i) {
        uint32_t c = leds[i];
        uint8_t r = (c >> 16) & 0xFF;
        uint8_t g = (c >> 8) & 0xFF;
        uint8_t b = c & 0xFF;
        r = (uint8_t)(r * factor);
        g = (uint8_t)(g * factor);
        b = (uint8_t)(b * factor);
        leds[i] = ((uint32_t)r << 16) | ((uint32_t)g << 8) | b;
    }
}

void c_draw_bar(uint32_t *leds, int start, int length,
                uint8_t r, uint8_t g, uint8_t b, float intensity) {
    if (!leds || length <= 0) return;
    if (intensity <= 0.0f) return;
    if (intensity > 1.0f) intensity = 1.0f;
    if (start < 0) start = 0;
    int end = start + length;
    for (int i = start; i < end; ++i) {
        uint8_t ir = (uint8_t)(r * intensity);
        uint8_t ig = (uint8_t)(g * intensity);
        uint8_t ib = (uint8_t)(b * intensity);
        uint32_t c = leds[i];
        uint8_t cr = (c >> 16) & 0xFF;
        uint8_t cg = (c >> 8) & 0xFF;
        uint8_t cb = c & 0xFF;
        int nr = cr + ir; if (nr > 255) nr = 255;
        int ng = cg + ig; if (ng > 255) ng = 255;
        int nb = cb + ib; if (nb > 255) nb = 255;
        leds[i] = ((uint32_t)nr << 16) | ((uint32_t)ng << 8) | nb;
    }
}
