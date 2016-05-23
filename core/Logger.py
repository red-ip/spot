import logging
import core
import random
# log("Background scan for xxx information was startet", 'info')
# info_level : info, error, debug
version = "1.0.2"


def log(message, info_level):
    log_file = core.LOG_FILE_LOCATION + '/' + core.LOG_FILE_NAME + ".log"
    try:
        if core.DEBUG_LOG:
            logging.basicConfig(
                filename=log_file,
                level=logging.DEBUG,
                format="%(asctime)s [%(levelname)-8s] %(message)s",
                datefmt="%d.%m.%Y %H:%M:%S")
        else:
            logging.basicConfig(
                filename=log_file,
                level=logging.INFO,
                format="%(asctime)s [%(levelname)-8s] %(message)s",
                datefmt="%d.%m.%Y %H:%M:%S")
        logger = getattr(logging, info_level)
        logger(message)
    except IOError:
        print ('{:9}'.format(info_level) + message)
        core.LOG_FILE_NAME += str(random.randint(100, 999))
        print ('{:9}'.format("error") + "IO ERROR by writing to the log file, now log file : " +
               str(core.LOG_FILE_LOCATION + "/" + core.LOG_FILE_NAME))

    if not core.PROG_DAEMONIZE:
        print ('{:9}'.format(info_level) + message)

