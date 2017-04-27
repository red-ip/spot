#!/usr/bin/env python
#
# -*- coding: <utf-8> -*-
"""
The Protocol:
    (Start)
    Expecting first a function that should be processed

    (End)
    After the function is done, the application go back to waiting for command mode
"""
import copy
import datetime
import os
import socket
import sys
import time
from optparse import OptionParser

import core
from core.Helper import get_local_ip
from core.Logger import log
from core.daemon import startstop
from core.homematic import get_device_to_check, send_device_status_to_ccu
from core.sensor_com import check_device_dict_via_sensor, check_sensor, display_msg
from core.udpclient import updclientstart

version = "1.3.6"
core.LOG_FILE_NAME = "spot_check"
## initial vari
core.LOG_FILE_LOCATION = os.path.split(sys.argv[0])[0] + "/log"
core.PROG_DIR = '/opt/spot'  #core.PROG_DIR, filename = os.path.split(sys.argv[0])
#core.PROG_DIR = "/Users/marius/Documents/PyCharm/spot"
import core.config
core.SLEEP_TIMER_IN = core.SLEEP_TIMER  # must be after import core.config

print("------------------- Spot %s -------------------") % version


def display_msg_on_sensors_display(MSG_Text):
    # send the MSG to all sensors, store all in sensor_data[k]
    for k, v in core.SPOT_SENSOR.items():
        # (k)ey = IP-Address
        # (v)alue = Port
        log(str(k) + " sending msg to sensor's display : " + MSG_Text, "debug")
        check_sensor(k, v)
        time.sleep(1)
        display_msg(k, v, MSG_Text)
        '''
        if check_sensor(k, v):  # ping the sensor

            display_msg(k, v, MSG_Text)

        else:

            log("Sensor ping failed to : " + str(k) + " . Moving on to the next sensor - display_msg_on_sensors_display", "debug")
        '''

def writeline(mysock, mymsg):
    mysock.sendall(mymsg)


def getsock():
    # Create a TCP/IP socket
    while (get_local_ip('8.8.8.8') == None):
        time.sleep(1)
    myip = get_local_ip('8.8.8.8')
    log("GetSock got the IP : " + str(myip), "debug")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log("Bind the socket to the Port : " + str(core.SRV_PORT), "info")
    server_address = ('', core.SRV_PORT)
    try:
        sock.bind(server_address)
        log("starting up socket, port: " + str(core.SRV_PORT), "debug")
    except socket.error:
        log("Port : " + str(core.SRV_PORT) + " is already in use, changing port", "info")
        core.SRV_PORT += 1
        server_address = ('', core.SRV_PORT)
        sock.bind(server_address)
        log("starting up socket, port: " + str(core.SRV_PORT), "info")
    return sock


def read_tcp(mysock, recv_buffer=1024):
    sockbuffer = mysock.recv(recv_buffer)
    return sockbuffer


def readlines(mysock, recv_buffer=4096, delim='\n'):
    """
    :rtype: read the TCP data
    """
    tcpbuffer = mysock.recv(recv_buffer)

    while tcpbuffer.find(delim) != -1:
        line, tcpbuffer = tcpbuffer.split('\n', 1)
        yield line
    return


def readlines_to_dict(sock):
    message = {}
    for line in readlines(sock):
        log("Command parameter received : " + str(line), "debug")
        message[line] = ""
    return message


def writelimes(mysock, mymsg):
    mysock.sendall(mymsg)


def accumulate_sensor_data(sensor_data):
    ''' sensor_data
        ["192.168.1.100" = ["CC:29:F5:67:B7:EC" = [ (presence = True) ] ] ]
    '''
    device_dict = {}
    for k, v in sensor_data.items():
        for device_key, device_val in v.items():
            if device_val["presence"] == "True":
                try:
                    device_dict[device_key] += 1
                except KeyError:
                    device_dict[device_key] = 1
            else:
                try:
                    device_dict[device_key] += 0
                except KeyError:
                    device_dict[device_key] = 0
    return device_dict


def discovery_devices(wait_till_found=True):
    # get the devices from the ccu2
    try:
        while get_local_ip("8.8.8.8") is None:      # check if we have a ip
            time.sleep(1)

        devices_to_check = get_device_to_check()
        if wait_till_found:
            while devices_to_check is None:
                time.sleep(2)
                devices_to_check = get_device_to_check()
        return devices_to_check

    except KeyboardInterrupt:
        log("Got signal to STOP", "info")
        if core.PROG_DAEMONIZE:
            startstop(pidfile=core.PDI_FILE, startmsg='stopping daemon', action='stop')
        else:
            print("KeyboardInterrupt received, stopping work ")
        os._exit(0)


def discovery_sensors(wait_till_found=True):
    # look up for the sensors
    # sensors are stored at core.SPOT_SENSOR
    try:
        while get_local_ip("8.8.8.8") is None:      # check if we have a ip
            time.sleep(1)

        if wait_till_found:
            updclientstart()
            while len(core.SPOT_SENSOR) == 0:
                updclientstart()
                time.sleep(1)
        else:
            updclientstart()
    except KeyboardInterrupt:
        log("Got signal to STOP", "info")
        if core.PROG_DAEMONIZE:
            startstop(pidfile=core.PDI_FILE, startmsg='stopping daemon', action='stop')
        else:
            print("KeyboardInterrupt received, stopping work ")
        os._exit(0)


def main():
    nearby_devices_counter = 0          # how many devices are in the coverage of Spot / in the Homezone
    devices_to_check_counter = 0        # how many devices to check
    nearby_devices_counter_last_run = 0

    log("Starting to collect parameters", "info")
    log("checking if ip interface is ready", "debug")
    # wait till we have an ip
    while get_local_ip("8.8.8.8") is None:
        time.sleep(1)
    log("IP interface is ready to go! local IP : " + str(get_local_ip("8.8.8.8")), "debug")

    if core.AUTO_DISCOVERY:
        log("Running Auto Discovery for Sensors ", "debug")
        discovery_sensors()
    log("Getting Devices for check from CCU2", "debug")
    # we will work with devices_to_check all the time and save the response from the sensors here
    devices_to_check = discovery_devices()
    devices_to_check_counter = devices_to_check.__len__()
    log("All parameters collected. System OK -> STARTING WORK", "info")

    try:
        request_discovery = False               # from time to time I'll rediscover sensors and the "device to check list"
        counter = 0                             # loop counter
        while True:
            counter += 1                        # count every loop
            sensor_data = {}
            pre_lookup = True                  # to speed up detection
            if request_discovery:               # in some cases we will need to rediscover sensors and devices
                request_discovery = False
                log("Rediscovering Sensor and devices. Loop : " + str(counter), "debug")
                devices_to_check = {}
                devices_to_check = copy.deepcopy(discovery_devices())
                devices_to_check_counter = devices_to_check.__len__()
                discovery_sensors()

            # send the device list to all sensors, store all in sensor_data[k]
            for k, v in core.SPOT_SENSOR.items():
                # (k)ey = IP-Address of the Sensor
                # (v)alue = Port of the Sensor
                if check_sensor(k, v):  # ping the sensor
                    cp_device = {}
                    cp_device = copy.deepcopy(devices_to_check)                     # deepcopy to avoiding references
                    sensor_data[k] = check_device_dict_via_sensor(k, v, cp_device)  # collect dates from all sensors

                    # to speed up detection and to send the msg to the ccu2 a user entered the homezone
                    if nearby_devices_counter == 0 and pre_lookup:
                        for item_dev, itemd in sensor_data[k].items():
                            if itemd['presence'].lower() == 'true':
                                pre_lookup = False
                                send_ok = send_device_status_to_ccu(itemd['ise_id'], 'true')
                                display_msg_on_sensors_display("Hello " + str(itemd['name']))
                                break

                    if not core.SENSOR_AVAILABLE:
                        log("Sensor is online", "info")
                        core.SENSOR_AVAILABLE = True
                else:
                    log("Sensor ping failed to : " + str(k) + " . Moving on to the next sensor", "debug")
                    request_discovery = True
            presence_of_devices = {}
            presence_of_devices = accumulate_sensor_data(sensor_data)

            # create a time stamp
            time_now = time.time()
            time_stamp = datetime.datetime.fromtimestamp(time_now).strftime('%Y-%m-%d-%H:%M:%S')
            if len(presence_of_devices) == 0:
                if core.SENSOR_AVAILABLE:
                    log("All Sensor are offline!", "error")
                    core.SENSOR_AVAILABLE = False
                log("All Sensors Down. loop counter " + str(counter), "debug")
                request_discovery = True
            else:
                # checking if device presence has changed
                for k, v in devices_to_check.items():   # k = mac-address
                    if devices_to_check[k]['presence'].lower() == 'true' and presence_of_devices[k] > 0:
                        # was visible   ist visible     do nothing
                        devices_to_check[k]['first_not_seen'] = None
                        devices_to_check[k]['times_not_seen'] = 0
                        log(str(k) + " is still present. Loop : " + str(counter), "debug")

                    elif devices_to_check[k]['presence'].lower() == 'true' and presence_of_devices[k] == 0 and \
                        devices_to_check[k]['times_not_seen'] < core.MAX_TIME_NOT_SEEN:
                        # was visible   ist not visible < MAX   count not seen + 1, set first time not seen
                        devices_to_check[k]['times_not_seen'] += 1
                        if devices_to_check[k]['first_not_seen'] is None:
                            devices_to_check[k]['first_not_seen'] = time_stamp
                            log(str(k) + " is first time no seen. Loop : " + str(counter), "debug")

                    elif devices_to_check[k]['presence'].lower() == 'true' and presence_of_devices[k] == 0 and \
                                    devices_to_check[k]['times_not_seen'] >= core.MAX_TIME_NOT_SEEN:
                        # was visible   ist not visible = MAX!   update ccu2, was visible = False
                        # send update to ccu2
                        send_ok = send_device_status_to_ccu(devices_to_check[k]['ise_id'], 'false')
                        log("OUT - " + str(devices_to_check[k]['name']) + " since " + \
                            str(devices_to_check[k]['first_not_seen']) + ".", "info")
                        log(str(k) + " - " + str(devices_to_check[k]['name']) + \
                            " is last seen at " + \
                            str(devices_to_check[k]['first_not_seen']) + ". going to update the CCU2", "debug")

                        if send_ok:      # successful
                            log(str(k) + " changes successfully updated to CCU2", "debug")
                        else:
                            log(str(k) + " problem trying to update changes to CCU2", "debug")
                        devices_to_check[k]['presence'] = 'False'                       # update the dict
                        display_msg_on_sensors_display(str(devices_to_check[k]['name']) + " left")
                        time.sleep(1)
                        # passing to a DB ->

                    elif devices_to_check[k]['presence'].lower() == 'false' and presence_of_devices[k] > 0:
                        # was not visible   ist visible        update ccu2, was visible = True, reset counter and stamp
                        # send update to ccu2
                        send_ok = send_device_status_to_ccu(devices_to_check[k]['ise_id'], 'true')
                        log(" IN - " + str(devices_to_check[k]['name']) + " since " + str(time_stamp) + ".", "info")

                        log(str(k) + " - " + str(devices_to_check[k]['name']) + \
                            " is here now. Update is sent to CCU2", "debug")
                        if send_ok:      # successful
                            log(str(k) + " changes successfully updated to CCU2", "debug")
                        else:
                            log(str(k) + " problem trying to update changes to CCU2", "debug")
                        devices_to_check[k]['times_not_seen'] = 0                       # reset not seen counter to 0
                        devices_to_check[k]['first_not_seen'] = None                    # reset first time stamp
                        devices_to_check[k]['presence'] = 'True'                        # update the dict
                        display_msg_on_sensors_display("Hello " + str(devices_to_check[k]['name']))
                        time.sleep(1)
                        # passing to a DB ->
                    else:
                        log(str(k) + " remains unavailable", "debug")

                # if activated, send a alive signal to ccu2. To activate it, u need to create a
                # system variable ('last_update_') on the ccu2
                #if core.CCU_LAST_UPDATE is not None:
                #    send_ok = send_device_status_to_ccu('last_update_', '"' + time_stamp + '"')

            # calculate how many devices are around, for this run
            nearby_devices_counter = 0
            for dev, int_presence in presence_of_devices.items():  # dev = int (0 / 1)
                nearby_devices_counter += int(int_presence)

            log(str(nearby_devices_counter) + " of " + str(devices_to_check_counter) + " are in the coverage of Spot", "debug")
            if nearby_devices_counter_last_run != nearby_devices_counter:
                nearby_devices_counter_last_run = nearby_devices_counter
                if nearby_devices_counter == 0:
                    log("no more devices around", "debug")
                    # no one there. Start process
                    core.SLEEP_TIMER = core.SLEEP_TIMER_OUT

                else:
                    # someone is there. Start process
                    log("devices around", "debug")
                    core.SLEEP_TIMER = core.SLEEP_TIMER_IN


            if counter > 15:           # Rediscover after every x loops
                counter = 0
                request_discovery = True
            log("going sleep for " + str(core.SLEEP_TIMER) + " s", "debug")
            time.sleep(core.SLEEP_TIMER)

    except KeyboardInterrupt:
        log("Got signal to STOP", "info")
        if core.PROG_DAEMONIZE:
            startstop(pidfile=core.PDI_FILE, startmsg='stopping daemon', action='stop')
        else:
            print("KeyboardInterrupt received, stopping work ")
        os._exit(0)






def start_local_sensor(scrip_parameters):
    import subprocess
    scrip_name = 'spot_sensor.py'
    script_abspath = core.PROG_DIR + '/' + scrip_name

    if os.path.isfile(script_abspath):
        # Check if the Script is already running
        log("Script file is present, OK .", "debug")
        cmd_command = 'ps aux | grep ' + scrip_name + ' | grep -v grep'

        process = subprocess.Popen(cmd_command, shell=True, stdout=subprocess.PIPE)
        output, err = process.communicate()
        if len(output) > 0:
            log("Script is already running, OK .", "debug")
        else:
            log("Starting : " + scrip_name, "debug")
            os.system(('python ' + script_abspath + ' -s'))                 # just in case, old pid-file is present
            time.sleep(1)                                                   # giving the os time
            os.system(('python ' + script_abspath + ' ' + scrip_parameters))
    else:
        log("Not able to start local SENSOR due to its absence: " + script_abspath + " ! System will try to discover "
                                                                            " remote Sensor ", "error")


def stop_local_sensor():
    import subprocess
    scrip_name = 'spot_sensor.py'
    script_abspath = core.PROG_DIR + '/' + scrip_name

    if os.path.isfile(script_abspath):
        # Check if the Script is running
        log("Script file is present: OK .", "debug")
        cmd_command = 'ps aux | grep ' + scrip_name + ' | grep -v grep'

        process = subprocess.Popen(cmd_command, shell=True, stdout=subprocess.PIPE)
        output, err = process.communicate()
        if len(output) > 0:
            log("Sending shutdown command: OK .", "debug")
            os.system(('python ' + script_abspath + ' -s'))
        else:
            log("Script is not running : " + scrip_name, "debug")
    else:
        log("Can not determine if script is running. Script-file not present : " + scrip_name, "error")


if __name__ == "__main__":
    # Set up and gather command line arguments
    usage = "usage: %prog [-options] [arg]"
    p = OptionParser(usage=usage)

    p.add_option('-m', '--manually',
                 dest='manually', help="Automatic Discovery Mode off - manually set up a sensor (ip:port)")
    p.add_option('-d', '--daemonize', action="store_true",
                 dest='daemonize', help="Run the server as a daemon")
    p.add_option('-n', '--no_local_sensor', action="store_true",
                 dest='no_local_sensor', help="use -n to not start/stop a local Sensor")
    p.add_option('-p', '--pidfile',
                 dest='pidfile', default=None,
                 help="Store the process id in the given file")
    p.add_option('-t', '--test', action="store_true",
                 dest='test', default=None,
                 help="function test")
    p.add_option('-l', '--log', action="store_true",
                 dest='log', help="set log to DEBUG.")
    p.add_option('-s', '--stop', action="store_true",
                 dest='stop', help="stop the daemon")
    p.add_option('-r', '--restart', action="store_true",
                 dest='restart', help="restart the daemon")
    p.add_option('-i', '--status', action="store_true",
                 dest='status',  help="status of the daemon")

    options, args = p.parse_args()

    if options.manually:
        # Set port
        # nametmp = nametmp.split('_')
        #try:
        #core.SPOT_SENSOR = options.manually.split(':')
        core.SPOT_SENSOR = dict(item.split(":") for item in options.manually.split(","))
        #except error:
        print "------------------- IP manual set to " + options.manually + " -------------------"
        if len(core.SPOT_SENSOR) < 8:
            p.error("Sensor IP and Port (10.1.1.2:10002) Mandatory if you not using Automatic Discovery Mode")
    else:
        core.AUTO_DISCOVERY = True

    # PIDfile
    if options.pidfile:
        print "------------------- Set PID file to " + options.pidfile + " -------------------"
        log("Set PIDfile to " + options.pidfile, "info")
        core.PDI_FILE = str(options.pidfile)

    # Set LOG
    if options.log:
        print "------------------- Log DEBUG manual set to True -------------------"
        core.DEBUG_LOG = True
        log("DEBUG LOG manual set to True ", "debug")
    else:
        core.DEBUG_LOG = None

    # Teste Funktion!
    if options.test:
        print "------------------- Test of a function -------------------"
        core.DEBUG_LOG = True
        log("Test of a function, auto debug True", "debug")
        start_local_sensor('d')
        p.error("Function test End")

    if options.stop:
        log("Got the option to stop the Daemon ", "debug")
        if options.no_local_sensor is None:
            stop_local_sensor()
        startstop(pidfile=core.PDI_FILE, startmsg='stopping daemon', action='stop')

    elif options.restart:
        log("Got the option to restart the Daemon ", "debug")
        if options.no_local_sensor is None:
            stop_local_sensor()
            start_local_sensor("-d")
        startstop(pidfile=core.PDI_FILE, startmsg='restarting daemon', action='restart')

    elif options.status:
        log("Got the option to return the Daemon status", "debug")
        if options.no_local_sensor is None:
            start_local_sensor("-i")
        startstop(stdout='.', stderr=None, stdin='.',
                  pidfile=core.PDI_FILE, startmsg='status of daemon', action='status')
    elif options.daemonize:
        print "------------------- Preparing to run in daemon mode -------------------"
        log("Preparing to run in daemon mode", "info")
        if options.no_local_sensor is None:
            if options.log:
                start_local_sensor("-l -d")
            else:
                start_local_sensor("-d")
        startstop(pidfile=core.PDI_FILE, action='start')
    else:
        print("Terminal Mode")
        if options.no_local_sensor is None:
            print("Local Sensor Mode Enabled - You will need to stop the Sensor manually : python spot_sensor.py -s")
            if options.log:
                start_local_sensor("-l -d")
            else:
                start_local_sensor("-d")

    main()
