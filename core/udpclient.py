#!python
'''

'''
import core
from core.Logger import log
import socket

PORT = 55555
TIME_TO_DISCOVERY = 2
# The results are stored in core.SPOT_SENSOR directly !


def updclientstart():
    core.SPOT_SENSOR = None
    core.SPOT_SENSOR = {}
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
    s.settimeout(TIME_TO_DISCOVERY)
    log("sending broadcast for discovery of the sensors", "debug")
    s.sendto("spot", ("<broadcast>", PORT))

    try:
        for n in range(1, 10, 1):
            (sensor_ip, sensor_port) = s.recv(23).split(":")
            core.SPOT_SENSOR[sensor_ip] = sensor_port

    except socket.timeout:
        log(str(len(core.SPOT_SENSOR)) + " sensors discovered : " + str(core.SPOT_SENSOR), "info")
    s.close()
