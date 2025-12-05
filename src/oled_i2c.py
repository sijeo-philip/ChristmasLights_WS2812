#!/usr/bin/env python3
HAVE_OLED = False
_oled = None
try:
    import board, busio
    from adafruit_ssd1306 import SSD1306_I2C
    from PIL import Image, ImageDraw, ImageFont
    HAVE_OLED = True
except ImportError:
    HAVE_OLED = False


class OLEDStub:
    def show_text(self, l1="", l2="", l3=""):
        pass


class RealOLED:
    def __init__(self, drv, w, h, font=None):
        self.drv = drv
        self.w = w
        self.h = h
        self.Image = Image
        self.ImageDraw = ImageDraw
        self.font = font

    def show_text(self, l1="", l2="", l3=""):
        img = self.Image.new("1", (self.w, self.h))
        draw = self.ImageDraw.Draw(img)
        draw.rectangle((0, 0, self.w, self.h), outline=0, fill=0)
        draw.text((0, 0), str(l1), font=self.font, fill=255)
        draw.text((0, 10), str(l2), font=self.font, fill=255)
        draw.text((0, 20), str(l3), font=self.font, fill=255)
        self.drv.image(img)
        self.drv.show()


def _init():
    global _oled
    if not HAVE_OLED:
        _oled = OLEDStub()
        return
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        drv = SSD1306_I2C(128, 32, i2c)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        _oled = RealOLED(drv, 128, 32, font)
    except Exception as e:
        print("OLED init failed:", e)
        _oled = OLEDStub()


def oled_show(l1="", l2="", l3=""):
    global _oled
    if _oled is None:
        _init()
    _oled.show_text(l1, l2, l3)
