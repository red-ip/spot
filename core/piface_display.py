#!/usr/bin/env python
#
# -*- coding: <utf-8> -*-

import pifacecad
from time import sleep
from core.Helper import get_local_ip

version = "1.0.3"

# Init the CAD
def init_cad():
    cad.lcd.blink_off()
    cad.lcd.cursor_off()
    cad.lcd.clear()
    cad.lcd.backlight_on()


# Handle pushed pins
def handle_pin(event):
    event.chip.lcd.clear()
    event.chip.lcd.set_cursor(0, 0)
    if(str(event.pin_num)=="0"):
        event.chip.lcd.write("IP Address:")
        event.chip.lcd.set_cursor(0, 1)
        event.chip.lcd.write(str(get_local_ip()))
    elif(str(event.pin_num)=="1"):
        display_banner()
    else:
        event.chip.lcd.write("Pressed button:")
        event.chip.lcd.set_cursor(0, 1)
        event.chip.lcd.write(str(event.pin_num))


def blink_display(times=3):
    #cad = pifacecad.PiFaceCAD()
    for x in range(0, times):
        cad.lcd.backlight_off()
        sleep(0.5)
        cad.lcd.backlight_on()
        sleep(0.5)


def display_msg(msg):
    cad.lcd.clear()
    cad.lcd.set_cursor(0, 0)
    cad.lcd.write("Spot:")
    cad.lcd.set_cursor(0, 1)
    cad.lcd.write(str(msg))
    blink_display()


def display_banner():
    cad.lcd.clear()
    cad.lcd.set_cursor(0, 0)
    cad.lcd.write("SPOT")
    cad.lcd.set_cursor(0, 1) # by REDIP
    cad.lcd.write("    by REDIP")


def init_support_switches():
    listener = pifacecad.SwitchEventListener(chip=cad)

    for i in range(8):
        listener.register(i, pifacecad.IODIR_FALLING_EDGE, handle_pin)
    listener.activate()


cad = pifacecad.PiFaceCAD()
init_cad()
