#!/usr/bin/env python
#
# -*- coding: <utf-8> -*-
version = "1.1.0"
from core.Logger import log
import time
import core

try:
    import bluetooth
except (ImportError, NameError) as e:
    print("bluetooth python Module is not installed! do apt-get install bluetooth python-bluez to fix it")
    #log("bluetooth python Module is not installed", "error")


def checkdevice(mac):
    if core.BT_SUPPORT:
        try:
            my_timeout = 0
            result2 = "None"

            while result2 == "None":
                my_timeout += 1
                result2 = bluetooth.lookup_name(mac, timeout=1)
                if my_timeout > 3:
                    break

        except (bluetooth.btcommon.BluetoothError, NameError) as e:
            log("bluetooth python Module is not installed - returning : devices are not present", "error")
            result2 = "None"
            time.sleep(1.2)
    else:
        result2 = "None"

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
