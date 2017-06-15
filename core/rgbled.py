#!/usr/bin/env python
#
# -*- coding: <utf-8> -*-
"""
The Protocol:

"""
import core
import time
import RPi.GPIO as GPIO
from core.Logger import log
version = "1.0.2"
log("Loading Module RGBLED.", "debug")

is_initialized = False

RED = int(core.RGBLED_RED)
GREEN = int(core.RGBLED_GREEN)
BLUE = int(core.RGBLED_BLUE)


def set_color(rgb_code):
    if not is_initialized:
        log("set_color call initialize RGB LED", "debug")
        initialize()
    time.sleep(0.2)
    request = rgb_code
    if (len(request) == 3):
        if request is not '000':
            GPIO.output(RED, int(request[0]))
            GPIO.output(GREEN, int(request[1]))
            GPIO.output(BLUE, int(request[2]))
        else:
            log("set_color call cleanup RGB LED", "debug")
            cleanup()


def initialize():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.output(RED, 0)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.output(GREEN, 0)
    GPIO.setup(BLUE, GPIO.OUT)
    GPIO.output(BLUE, 0)
    is_initialized = True


def cleanup():
    GPIO.cleanup()
    is_initialized = False