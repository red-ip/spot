#!/usr/bin/env python
#
# -*- coding: <utf-8> -*-

import pifacecad
from time import sleep
from datetime import datetime
from core.Helper import get_local_ip

version = "1.1.1"
lastLCDline = ""

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
    if(str(event.pin_num) == "0"):
        event.chip.lcd.write("IP Address:")
        event.chip.lcd.set_cursor(0, 1)
        event.chip.lcd.write(str(get_local_ip()))
    elif(str(event.pin_num) == "1"):
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
    global lastLCDline
    cad.lcd.clear()
    cad.lcd.set_cursor(0, 0)
    current_time = datetime.now().time().strftime('%H:%M')
    display = '{message: <{width}}'.format(message=msg, width=11)
    display_text = display[0:11] + "{0}".format(current_time)
    cad.lcd.write(display_text)
    cad.lcd.set_cursor(0, 1)
    cad.lcd.write(lastLCDline)
    lastLCDline = display_text

    blink_display()
    if(str(msg) == "ALL OUT"):
        display_off()


def display_banner():
    cad.lcd.clear()
    cad.lcd.set_cursor(0, 0)
    cad.lcd.write("SPOT")
    cad.lcd.set_cursor(0, 1)
    cad.lcd.write("    by REDIP")


def display_off():
    cad.lcd.backlight_off()


def init_support_switches():
    listener = pifacecad.SwitchEventListener(chip=cad)

    for i in range(8):
        listener.register(i, pifacecad.IODIR_FALLING_EDGE, handle_pin)
    listener.activate()


cad = pifacecad.PiFaceCAD()
init_cad()
