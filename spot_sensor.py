#!/usr/bin/env python
#
# -*- coding: <utf-8> -*-
"""

The Protocol:
    (Start)
    Expecting first a function that should be processed
    Currently there are this functions : checkdevice,

    if the function is available, an "True" will be send, otherwise an "Fals" (False, but we send just 4 characters)
    After sending an "Fals", the communication is done an the application is waiting for a new command (function call)

    if the function is available and an "True" was send, the rest of the communication is depending on the actually
    function.
    (Function)
    checkdevice :   we expecting a list of mac addresses in this format :   a3:d2:b8:89:43:ac\n
                                                                            03:d2:b8:89:df:23\n
                    the correct receiving will be confirmed with an "True" otherwise an "Fals"
                    after checking the mac, the list will be send back. The application
                    add a True for seen or False not seen after the mac-address. The two information
                    are divided by "|"
                                                                        a3:d2:b8:89:43:ac|True\n
                                                                        03:d2:b8:89:df:23|False\n
                    performance info: the check of each mac can tack up to 2-3s
                    after the list was send, the function ist done
                    > checkdevice
                    < True
                    > a3:d2:b8:89:43:ac\n
                      03:d2:b8:89:df:23\n
                    < True
                    < a3:d2:b8:89:43:ac|True\n
                      03:d2:b8:89:df:23|False\n



    (End)
    After the function is done, the application go back to waiting for command mode
"""
import os
import time
import socket
import core
from optparse import OptionParser
from core.Logger import log
from core.Helper import get_local_ip, is_mac
from core.bluetoothserver import check_device_dict
from core.daemon import startstop

from core.udpserver import updserverstart

version = "1.3.6"
print ("------------------- spot_sensore %s -------------------") % version


def writeline(mysock, mymsg):
    mysock.sendall(mymsg)


def writeline_dict(mysock, my_dict):
    mybuffer = ""
    for k, v in my_dict.items():
        mybuffer = mybuffer + k + "|" + v + "\n"    # a3:d2:b8:89:43:ac|True\n03:d2:b8:89:df:23|False\n
    mysock.sendall(mybuffer)


def sayhello(v):        # noch in der Entwiklung
    return v


def getsock():
    # Create a TCP/IP socket
    while (get_local_ip('8.8.8.8') == None):
        time.sleep(1)
    myip = get_local_ip('8.8.8.8')
    log("GetSock got the IP : " + str(myip), "debug")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log("Bind the socket to the IP:Port : " + str(myip) + ":" + str(core.SRV_PORT), "info")
    server_address = ('', core.SRV_PORT)
    try:
        sock.bind(server_address)
        log("Starting up socket on port : " + str(core.SRV_PORT), "debug")
    except socket.error:
        log("Port : " + str(core.SRV_PORT) + " is already in use, changing port", "info")
        core.SRV_PORT += 1
        server_address = ('', core.SRV_PORT)
        sock.bind(server_address)
        log("Starting up socket on port : " + str(core.SRV_PORT), "info")
    return sock


def read_tcp(mysock, recv_buffer=1024):
    sockbuffer = mysock.recv(recv_buffer)
    return sockbuffer


def readlines(mysock, recv_buffer=4096, delim='\n'):
    """
    :rtype: lese die TCP daten DS mit return getrennt
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


def isBefehl(v):
    try:
        return v.lower() in ("checkdevice", "displaytext")
    except AttributeError:
        print("Attribute Error")
        return False


def main():
    log("checking if ip interface is ready", "debug")
    # wait till we have an ip
    while get_local_ip("8.8.8.8") == None:
        time.sleep(1)
    log("IP-Interface ready!", "debug")

    # start to listing port 55555 for clients
    updserverstart()

    # Bind the socket to the address given on the command line
    sock = getsock()
    sock.listen(1)

    while True:
        time.sleep(1)
        try:
            log("Waiting for connection", "debug")
            connection, client_address = sock.accept()
        except (KeyboardInterrupt, socket.error, 'Bad file descriptor') as e:
            if str(e) == 'KeyboardInterrupt':
                if core.PROG_DAEMONIZE:
                    log(str(e) + " !! STOPPING !!", "info")
                    startstop(pidfile=core.PDI_FILE, startmsg='stopping daemon', action='stop')
                else:
                    print("KeyboardInterrupt received, stopping work ")
                sock.close()
                os._exit(0)
            else:
                if core.PROG_DAEMONIZE:
                    log(str(e) + " !! Restarting after Socket Error !!", "error")
                else:
                    print("Got a error : %s - restarting socket ") % str(e)
                sock.close()
                sock = getsock()
                sock.listen(1)
        try:
            log("Client is connected, IP : " + str(client_address), "debug")
            while True:
                line = read_tcp(connection)

                if line == "checkdevice":
                    log("command received and accepted : " + str(line), "debug")
                    log("responding with True", "debug")
                    writeline(connection, "True")

                    log("waiting for command parameters", "debug")

                    parameters = readlines_to_dict(connection)
                    log("parameters: " + str(parameters), "debug")
                    # checking if parameter is a mac address, if not delete this item
                    for k, v in parameters.items():
                        if is_mac(k) == False:
                            log("parameters: " + str(k) + " is not a mac address an will be removed", "debug")
                            del parameters[k]    # remove entry with key 'Name'

                    # check if something left
                    number_of_items_in_dic = len(parameters)
                    if number_of_items_in_dic > 0:
                        log("The number of valid parameters is: " + str(number_of_items_in_dic), "debug")
                        # we have some mac-addresses to work with
                        # sent a ok to the client
                        writeline(connection, "True")
                        time.sleep(1)
                        # check if the mac can be seen and sent the result back to the client
                        log("Transmitting the results back to the client", "debug")
                        writeline_dict(connection, check_device_dict(parameters))

                    else:
                        # we didn't find any mac address
                        writeline(connection, "Fals")
                        break       # stopping the processing

                elif line == "displaytext":
                    print ("ghjkl") # function is not done

                elif line == "ping":
                    log("Received ping, responding with True", "debug")
                    writeline(connection, "True")

                else:
                    log("Unknown command received and discarded : " + str(line), "debug")
                    log("Responding with Fals", "debug")
                    writeline(connection, "Fals")
                    break

        except (KeyboardInterrupt, socket.error, 'Bad file descriptor', UnboundLocalError) as e:
            if str(e) == 'KeyboardInterrupt':
                if core.PROG_DAEMONIZE:
                    startstop(pidfile=core.PDI_FILE, startmsg='stopping daemon', action='stop')
                else:
                    print("KeyboardInterrupt received, stopping work ")
                sock.close()
                os._exit(0)
            else:
                if core.PROG_DAEMONIZE:
                    log("got a error : " + str(e), "error")
                else:
                    print("got a error : %s - restarting socket ") % str(e)
                sock.close()
                sock = getsock()
                sock.listen(1)


if __name__ == "__main__":
    # Set up and gather command line arguments
    usage = "usage: %prog [-options] [arg]"
    p = OptionParser(usage=usage)

    p.add_option('-d', '--daemonize', action="store_true",
                 dest='daemonize', help="Run the server as a daemon")
    p.add_option('-p', '--pidfile',
                 dest='pidfile', default=None,
                 help="Store the process id in the given file")
    p.add_option('-P', '--port',
                 dest='port', default=None,
                 help="Force to listen on this port. normal is 10003")
    p.add_option('-l', '--log', action="store_true",
                 dest='log', help="set log to DEBUG.")
    p.add_option('-s', '--stop', action="store_true",
                 dest='stop', help="stop the daemon")
    p.add_option('-r', '--restart', action="store_true",
                 dest='restart', help="restart the daemon")
    p.add_option('-i', '--status', action="store_true",
                 dest='status',  help="status the daemon")

    options, args = p.parse_args()

    # Set port
    if options.port:
        print "------------------- Port manual set to " + options.port + " -------------------"
        log("Port manual set to " + options.port, "info")
        core.SRV_PORT = int(options.port)

    # PIDfile
    if options.pidfile:
        print "------------------- Set PIDfile to " + options.pidfile + " -------------------"
        log("Set PIDfile to " + options.pidfile, "info")
        core.PDI_FILE = str(options.pidfile)

    # Set LOG
    if options.log:
        print "------------------- Log DEBUG manual set to True -------------------"
        core.DEBUG_LOG = True
        log("DEBUG LOG manual set to True ", "debug")
    else:
        core.DEBUG_LOG = None

    if options.stop:
        log("Got the option to stop the Daemon ", "debug")
        startstop(pidfile=core.PDI_FILE, startmsg='stopping daemon', action='stop')
    elif options.restart:
        log("Got the option to restart the Daemon ", "debug")
        startstop(pidfile=core.PDI_FILE, startmsg='restarting daemon', action='restart')
    elif options.status:
        log("Got the option to return the Daemon status", "debug")
        startstop(stdout='.', stderr=None, stdin='.',
                  pidfile=core.PDI_FILE, startmsg='status of daemon', action='status')
    elif options.daemonize:
        print "------------------- Preparing to run in daemon mode -------------------"
        log("Preparing to run in daemon mode", "info")
        startstop(pidfile=core.PDI_FILE, action='start')
    else:
        print("Starte als Terminal")

    main()
