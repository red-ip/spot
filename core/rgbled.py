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
version = "1.0.1"
log("Loading Module RGBLED.", "debug")

GPIO.setmode(GPIO.BCM)

RED = int(core.RGBLED_RED)
GREEN = int(core.RGBLED_GREEN)
BLUE = int(core.RGBLED_BLUE)

GPIO.setup(RED, GPIO.OUT)
GPIO.output(RED, 0)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.output(GREEN, 0)
GPIO.setup(BLUE, GPIO.OUT)
GPIO.output(BLUE, 0)

#GPIO.cleanup()


def set_color(rgb_code):
    time.sleep(0.2)
    request = rgb_code
    if (len(request) == 3):
        if request is not '000':
            GPIO.output(RED, int(request[0]))
            GPIO.output(GREEN, int(request[1]))
            GPIO.output(BLUE, int(request[2]))
        else:
            GPIO.cleanup()
