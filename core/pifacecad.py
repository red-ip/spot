from threading import Barrier  # must be using Python 3
import subprocess
import pifacecommon
import pifacecad
from time import sleep
import os
import sys
import signal
import shlex
import math
import lirc

from pifacecad.lcd import LCD_WIDTH


SMILEY_SYMBOL = pifacecad.LCDBitmap([
    0b00000,
    0b01010,
    0b00000,
    0b00100,
    0b00000,
    0b01010,
    0b01110,
    0b00000])
PLAY_SYMBOL = pifacecad.LCDBitmap(
    [0x10, 0x18, 0x1c, 0x1e, 0x1c, 0x18, 0x10, 0x0])
PAUSE_SYMBOL = pifacecad.LCDBitmap(
    [0x0, 0x1b, 0x1b, 0x1b, 0x1b, 0x1b, 0x0, 0x0])
INFO_SYMBOL = pifacecad.LCDBitmap(
    [0x6, 0x6, 0x0, 0x1e, 0xe, 0xe, 0xe, 0x1f])
MUSIC_SYMBOL = pifacecad.LCDBitmap(
    [0x2, 0x3, 0x2, 0x2, 0xe, 0x1e, 0xc, 0x0])

PLAY_SYMBOL_INDEX = 0
PAUSE_SYMBOL_INDEX = 1
INFO_SYMBOL_INDEX = 2
MUSIC_SYMBOL_INDEX = 3
SMILEY_SYMBOL_INDEX = 4



ACTIONS = [
    {'name': "sysinfo",
     'cmd': 'poweroff',
     'info': 'system infos'},
    {'name': "DestroyWLAN",
     'cmd': '...',
     'info': 'destroy all wlan connections'},
]


class Buttons(object):
    def __init__(self, cad, start_action=0):
        self.current_action_index = start_action
        self.action_process = None
        # set up cad
        cad.lcd.blink_off()
        cad.lcd.cursor_off()
        cad.lcd.backlight_on()
        self.cad = cad
        cad.lcd.store_custom_bitmap(SMILEY_SYMBOL_INDEX, SMILEY_SYMBOL)
        cad.lcd.store_custom_bitmap(PLAY_SYMBOL_INDEX, PLAY_SYMBOL)
        cad.lcd.store_custom_bitmap(PAUSE_SYMBOL_INDEX, PAUSE_SYMBOL)
        cad.lcd.store_custom_bitmap(INFO_SYMBOL_INDEX, INFO_SYMBOL)

    @property
    def current_action(self):
        """Returns the current action ."""
        return ACTIONS[self.current_action_index]

    @property
    def processing(self):
        return self._is_processing

    @processing.setter
    def processing(self, should_processing):
        if should_processing:
            self.start()
        else:
            self.stop()

    @property
    def text_status(self):
        """Returns a text represenation of the action status."""
        if self.processing:
            return "Now processing"
        else:
            return "Stopped"

    def play(self):
        """Plays the current action."""
        print("Playing {}.".format(self.current_action['name']))
        # check if is m3u and send -playlist switch to mplayer
        if self.current_action['source'].split("?")[0][-3:] in ['m3u', 'pls']:
            play_command = "mplayer -quiet -playlist {stationsource}".format(
                stationsource=self.current_action['cmd'])
        else:
            play_command = "{stationsource}".format(
                stationsource=self.current_action['cmd'])
        self.action_process = subprocess.Popen(
            play_command,
            #stdout=subprocess.PIPE,
            #stderr=subprocess.PIPE,
            shell=True,
            preexec_fn=os.setsid)
        self._is_processing = True
        self.update_display()

    def stop(self):
        """Stops the current action"""
        print("Stopping action.")
        os.killpg(self.action_process.pid, signal.SIGTERM)
        self._is_processing = False
        self.update_processing()

    def update_processing(self):
        """Updated the processing status."""
        #message = self.text_status.ljust(LCD_WIDTH-1)
        #self.cad.lcd.write(message)
        if self.processing:
            char_index = PLAY_SYMBOL_INDEX
        else:
            char_index = PAUSE_SYMBOL_INDEX

        self.cad.lcd.set_cursor(0, 0)
        self.cad.lcd.write_custom_bitmap(char_index)

    def update_display(self):
        """Updates the action status."""
        message = self.current_action['name'].ljust(LCD_WIDTH-1)
        self.cad.lcd.set_cursor(1, 0)
        self.cad.lcd.write(message)

    def toggle_playing(self, event=None):
        if self.processing:
            self.stop()
        else:
            self.play()

    def close(self):
        self.stop()
        self.cad.lcd.clear()
        self.cad.lcd.backlight_off()

    def change_action(self, new_action_index):
        """Change the station index."""
        was_playing = self.processing
        if was_playing:
            self.stop()
        self.current_action_index = new_action_index % len(ACTIONS)
        if was_playing:
            self.play()

    def next_action(self, event=None):
        self.change_action(self.current_action_index + 1)

    def previous_action(self, event=None):
        self.change_action(self.current_action_index - 1)

def button_preset_switch(event): # Buttons
    global button
    button.change_action(event.pin_num)


if __name__ == "__main__":
    cad = pifacecad.PiFaceCAD()
    global button
    button = Buttons(cad)
    #button.play()

    global end_barrier
    end_barrier = Barrier(2)

    # wait for button presses
    switchlistener = pifacecad.SwitchEventListener(chip=cad)
    for pstation in range(4):
        switchlistener.register(
            pstation, pifacecad.IODIR_ON, button_preset_switch)
    switchlistener.register(4, pifacecad.IODIR_ON, end_barrier.wait)
    switchlistener.register(5, pifacecad.IODIR_ON, button.toggle_playing)
    switchlistener.register(6, pifacecad.IODIR_ON, button.previous_action)
    switchlistener.register(7, pifacecad.IODIR_ON, button.next_action)

    switchlistener.activate()

    end_barrier.wait()  # wait unitl exit

    # exit
    button.close()
    switchlistener.deactivate()
