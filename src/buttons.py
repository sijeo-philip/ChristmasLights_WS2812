#!/usr/bin/env python3
import time
try:
    import RPi.GPIO as GPIO
    HAVE_GPIO = True
except ImportError:
    HAVE_GPIO = False

BUTTON_MODE = 5
BUTTON_NEXT = 6
BUTTON_PREV = 13
BUTTON_PLAY = 19

_last = {}
_setup = False


def setup():
    global _setup
    if not HAVE_GPIO or _setup:
        return
    GPIO.setmode(GPIO.BCM)
    for pin in (BUTTON_MODE, BUTTON_NEXT, BUTTON_PREV, BUTTON_PLAY):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    _setup = True


def cleanup():
    global _setup
    if not HAVE_GPIO:
        return
    GPIO.cleanup()
    _setup = False


def button_pressed(pin, debounce=0.05):
    if not HAVE_GPIO:
        return False
    now = time.time()
    last = _last.get(pin, 0.0)
    if now - last < debounce:
        return False
    if GPIO.input(pin) == GPIO.LOW:
        _last[pin] = now
        return True
    return False
