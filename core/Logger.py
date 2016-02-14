#import os
import logging
import core
import random
# log("Background scan for xxx information was startet", 'info')
# info_level : info, error, debug


def log(message, info_level):
    try:
        if core.DEBUG_LOG:
            logging.basicConfig(
                filename=core.LOG_FILE_NAME,
                level=logging.DEBUG, # 				level = logging.INFO,
                format="%(asctime)s [%(levelname)-8s] %(message)s",
                datefmt="%d.%m.%Y %H:%M:%S")
        else:
            logging.basicConfig(
                filename=core.LOG_FILE_NAME,
                level=logging.INFO, # 				level = logging.INFO,
                format="%(asctime)s [%(levelname)-8s] %(message)s",
                datefmt="%d.%m.%Y %H:%M:%S")
        logger = getattr(logging, info_level)
        logger(message)
    except IOError:
        print ('{:9}'.format(info_level) + message)
        core.LOG_FILE_NAME = "/tmp/spot_sensor.log." + str(random.randint(100, 999))
        print ('{:9}'.format("error") + "IO ERROR by writing to the log file, now log file : " +
               str(core.LOG_FILE_NAME))

    if core.PROG_DAEMONIZE == False:
        print ('{:9}'.format(info_level) + message)

