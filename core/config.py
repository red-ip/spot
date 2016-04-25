#!/usr/bin/env python
#
# -*- coding: <utf-8> -*-

import core
import os
from core.Logger import log
import ConfigParser
version = "1.0.3"

file_name = 'spot.cfg'

# Test
if __name__ == "__main__":
    #core.PROG_DIR = '/Users/marius/Documents/PyCharm/spot'
    core.LOG_FILE_LOCATION = '/Users/marius/Documents/PyCharm/spot/log'
    core.LOG_FILE_NAME = 'Test'


def check_file():
    script_abspath = core.PROG_DIR + '/' + file_name

    if os.path.isfile(script_abspath):
        # Check if the config is already there
        return True
    else:
        return False


def load_config_from_file():
    print("lading CFG")
    core.CFG = ConfigParser.RawConfigParser()
    core.CFG.read((core.PROG_DIR + '/' + file_name))


def parse_config():
    core.LOG_FILE_LOCATION = core.CFG.get('SPOT', 'LOG_FILE_LOCATION')

    core.SLEEP_TIMER = core.CFG.getfloat('SPOT', 'SLEEP_TIMER_SEC')
    core.MAX_TIME_NOT_SEEN = core.CFG.getfloat('SPOT', 'MAX_TIME_NOT_SEEN')

    core.LOG_FILE_LOCATIONS_CLIENTS = core.CFG.get('CLIENTS', 'LOG_FILE_LOCATIONS_CLIENTS')

    core.IP_CCU = core.CFG.get('CCU', 'IP_CCU')


def writing_default_config_to_file():
    core.CFG = ConfigParser.RawConfigParser()
    core.CFG.add_section('SPOT')
    core.CFG.set('SPOT', 'LOG_FILE_LOCATION', '/opt/spot/log')

    core.CFG.set('SPOT', 'SLEEP_TIMER_SEC', 80)
    core.CFG.set('SPOT', 'MAX_TIME_NOT_SEEN', 2)

    core.CFG.add_section('CLIENTS')
    core.CFG.set('CLIENTS', 'LOG_FILE_LOCATIONS_CLIENTS', '/opt/spot/log')

    core.CFG.add_section('CCU')
    #   core.CFG.set('CCU', 'CCU_SUPPORT', True)
    core.CFG.set('CCU', 'IP_CCU', '192.168.178.220')

    try:
        # Writing the configuration file to 'spot.cfg'
        with open((core.PROG_DIR + '/' + file_name), 'wb') as configfile:
            core.CFG.write(configfile)
            configfile.close()
    except IOError:
        log("Can not write the Config File. Exiting", "error")
        print ('Can not write in : ' + core.PROG_DIR + '/' + file_name)
        os._exit(0)

if not check_file():
    writing_default_config_to_file()
    parse_config()
    log("Make sure the configuration apply for you", "info")
else:
    load_config_from_file()
    parse_config()
    log("Lading Config file", "debug")

