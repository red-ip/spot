import re
import socket
import os
import sys
import core
import subprocess
from core.Logger import log


def str2bool(v):
    try:
        return v.lower() in ("yes", "true", "t", "1", "-1")
    except AttributeError:
        if(type(v) is bool):
            return v
        else:
            log("str2bool. Konnte variable nicht umwandeln Exit : " + str(v), "info")
            os._exit(0)


def str2date(var_date):
    try:
        a = time.strptime(var_date, '%Y-%m-%d %H:%M:%S')

    except ValueError:
        a = time.strptime("1980-10-29 10:10:10", '%Y-%m-%d %H:%M:%S')

    return a


def Replacesq(string):

    try:
        cleanstr = string.replace("'", "''")

    except:
        cleanstr = string

    return string


def get_local_ip(try_with = '8.8.8.8'):
    # From http://stackoverflow.com/a/7335145
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((try_with, 9))
        ip = s.getsockname()[0]
    except socket.error:
        return None
    except socket.gaierror:
        return None
    finally:
        del s
    return ip


def is_number(var_test, return_by_true=True, return_by_false=False):
    try:
        int(var_test)
        return return_by_true

    except ValueError:
        return return_by_false


def is_mac(var_test):
    if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", var_test.lower()):
        return True
    else:
        return False


def ParseTyps(deviceSerial, description):

    data = {}
    serial = ''

    for items in description:
        for key, values in items.iteritems():
            if key == 'INDEX' and values == 1:
                for key, values in items.items():
                    if key == 'PARENT':
                        serial = values
                    if key == 'PARENT_TYPE':
                        name = values
                    if key == 'TYPE':
                        type = values

                    if serial == deviceSerial:
                        data[deviceSerial] = name, type

    return data


def pid_file_create():
    #/usr/bin/env python

    pid = str(os.getpid())
    pidfile = core.PDI_FILE

    if os.path.isfile(pidfile):
        log("PID file already exists  : " + str(pidfile), "warning")
        #
        ex_pid = open(pidfile).read()
        if isProcessRunning(ex_pid):
            log("Spot is already runing, exiting  : " + str(pidfile), "error")
            sys.exit()
        else:
            log("overwriting PID  file : " + str(pidfile), "warning")
            file(pidfile, 'w').write(pid)
    else:
        try:
            file(pidfile, 'w').write(pid)

        except IOError:
            log("overwriting PID file not possible maybe: Permission denied: " + str(pidfile), "error")

    return pid


# region can be removed coz no need for it anymore
def findProcess(processId):
    shell_befehl = "ps aux | grep " + str(processId)
    #log("ps aux befehl : " + shell_befehl,"debug")
    ps = subprocess.Popen(shell_befehl, shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read()
    #log("befehl ausgabe : " + str(output),"debug")
    ps.stdout.close()
    ps.wait()
    return output
# endregion


def isProcessRunning(process_id):
    shell_befehl = "ps aux | grep " + str(process_id)
    ps = subprocess.Popen(shell_befehl, shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    if re.search("  " + str(process_id), str(output)) is None:
        return False
    else:
        return True


def pid_file_destroy(PDI_FILE):
    os.unlink(PDI_FILE)