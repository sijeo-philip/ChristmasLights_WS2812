#!/usr/bin/env python3
import time, socket, os, ctypes, random, math, colorsys
from rpi_ws281x import PixelStrip, Color, ws
from protocol import (SOCKET_PATH, MODE_MUSIC, MODE_AMBIENT, MODE_OFF,
                      MODE_TREE, MODE_CHASE, MODE_SPARKLE)

LED_COUNT = 300
LED_PIN = 10
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0
LED_STRIP_TYPE = ws.WS2811_STRIP_GRB

FADE_FACTOR = 0.80


class LightServer:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        lib_path = os.path.join(base_dir, "..", "lib", "libeffects.so")
        self.lib = ctypes.CDLL(lib_path)
        self.lib.c_fade_strip.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                                          ctypes.c_int, ctypes.c_float]
        self.lib.c_draw_bar.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                                        ctypes.c_int, ctypes.c_int,
                                        ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8,
                                        ctypes.c_float]
        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                                LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP_TYPE)
        self.strip.begin()
        self.leds = (ctypes.c_uint32 * LED_COUNT)()
        self.ptr = ctypes.cast(self.leds, ctypes.POINTER(ctypes.c_uint32))

        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(SOCKET_PATH)
        self.server.listen(1)
        self.server.setblocking(False)

        self.frame = 0
        self.chase_pos = 0.0

    def push(self):
        for i in range(LED_COUNT):
            c = self.leds[i]
            r = (c >> 16) & 0xFF
            g = (c >> 8) & 0xFF
            b = c & 0xFF
            self.strip.setPixelColor(i, Color(r, g, b))
        self.strip.show()

    def fade(self, factor=FADE_FACTOR):
        self.lib.c_fade_strip(self.ptr, LED_COUNT, float(factor))

    def clear(self):
        for i in range(LED_COUNT):
            self.leds[i] = 0

    def render_music(self, note, level, gliss, kick, snare):
        self.fade()
        if note >= 0:
            section = 20
            base = (note % 12) * section
            hue = (note / 12.0 + gliss * 0.1) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            inten = min(level * 3.0, 1.0)
            self.lib.c_draw_bar(self.ptr, base, section,
                                int(r * 255), int(g * 255), int(b * 255),
                                float(inten))
        if kick > 0.1:
            self.lib.c_draw_bar(self.ptr, 240, 30, 255, 80, 0, float(kick))
        if snare > 0.1:
            self.lib.c_draw_bar(self.ptr, 270, 30, 200, 200, 255, float(snare))

    def render_ambient(self, level):
        # Gentle breathing using level as brightness hint
        self.fade(0.95)
        # Add a slow hue wave
        hue = (self.frame % 600) / 600.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.6, 0.4 + 0.4 * level)
        self.lib.c_draw_bar(self.ptr, 0, LED_COUNT,
                            int(r * 255), int(g * 255), int(b * 255),
                            0.2)

    def render_tree(self):
        # Festive: red/green/gold sparkles + gentle fade
        self.fade(0.90)
        palette = [
            (0, 180, 0),    # deep green
            (0, 255, 40),   # bright green
            (255, 0, 0),    # red
            (255, 50, 0),   # warm red
            (255, 180, 0),  # gold
            (255, 255, 40), # yellowish star
        ]
        # A few random sparkles per frame
        for _ in range(10):
            idx = random.randrange(0, LED_COUNT)
            r, g, b = random.choice(palette)
            self.lib.c_draw_bar(self.ptr, idx, 1, r, g, b, 1.0)

    def render_chase(self):
        # Rainbow chase bar
        self.fade(0.85)
        bar_len = max(10, LED_COUNT // 15)
        self.chase_pos = (self.chase_pos + 1.5) % LED_COUNT
        head = int(self.chase_pos)
        for i in range(bar_len):
            pos = (head + i) % LED_COUNT
            t = i / bar_len
            hue = (self.chase_pos / LED_COUNT + t) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            self.lib.c_draw_bar(self.ptr, pos, 1,
                                int(r * 255), int(g * 255), int(b * 255),
                                1.0 - 0.3 * t)

    def render_sparkle(self):
        # Cold white/blue sparkles
        self.fade(0.88)
        for _ in range(15):
            if random.random() < 0.5:
                idx = random.randrange(0, LED_COUNT)
                # white/blue mix
                if random.random() < 0.5:
                    r, g, b = 255, 255, 255
                else:
                    r, g, b = 120, 120, 255
                self.lib.c_draw_bar(self.ptr, idx, 1, r, g, b, 1.0)

    def run(self):
        conn = None
        buf = ""
        try:
            while True:
                if conn is None:
                    try:
                        conn, _ = self.server.accept()
                        conn.setblocking(False)
                    except BlockingIOError:
                        pass
                if conn is not None:
                    try:
                        data = conn.recv(1024)
                        if not data:
                            conn.close(); conn = None
                        else:
                            buf += data.decode()
                    except BlockingIOError:
                        pass
                    except (BrokenPipeError, ConnectionResetError):
                        conn = None

                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if parts[0] != "STATE" or len(parts) != 7:
                        continue
                    try:
                        mode = int(parts[1])
                        note = int(parts[2])
                        level = float(parts[3])
                        gliss = float(parts[4])
                        kick = float(parts[5])
                        snare = float(parts[6])
                    except ValueError:
                        continue

                    if mode == MODE_MUSIC:
                        self.render_music(note, level, gliss, kick, snare)
                    elif mode == MODE_AMBIENT:
                        self.render_ambient(level)
                    elif mode == MODE_OFF:
                        self.clear()
                    elif mode == MODE_TREE:
                        self.render_tree()
                    elif mode == MODE_CHASE:
                        self.render_chase()
                    elif mode == MODE_SPARKLE:
                        self.render_sparkle()

                    self.push()
                    self.frame += 1

                time.sleep(0.01)
        finally:
            if conn is not None:
                conn.close()
            self.server.close()
            self.clear()
            self.push()


if __name__ == "__main__":
    LightServer().run()
