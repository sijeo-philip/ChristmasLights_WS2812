#ifndef EFFECTS_H
#define EFFECTS_H
#include <stdint.h>
void c_fade_strip(uint32_t *leds, int count, float factor);
void c_draw_bar(uint32_t *leds, int start, int length,
                uint8_t r, uint8_t g, uint8_t b, float intensity);
#endif
