#!/usr/bin/env python
#
# -*- coding: <utf-8> -*-

from core.Logger import log
import bluetooth
import time

def checkdevice(mac):
    try:
        result2 = bluetooth.lookup_name(mac, timeout=5)
    except bluetooth.btcommon.BluetoothError:
        result2 = "None"
        time.sleep(5)

    if str(result2) != "None":
        log("bluetooth lookup for MAC : " + str(result2) + " : True ", "debug")
        return True
    else:
        log("bluetooth lookup for MAC : " + str(result2) + " : False ", "debug")
        return False


def check_device_dict(mac_dict):
    for k, v in mac_dict.items():
        if checkdevice(k):
            mac_dict[k] = "True"
        else:
            mac_dict[k] = "False"
    return mac_dict
