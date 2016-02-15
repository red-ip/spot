#!python
import socket
import threading
import core
from SocketServer import UDPServer, BaseRequestHandler
from core.Logger import log
from core.Helper import get_local_ip

version = "1.0.0"

PORT = 55555

class MasterUDPServer(threading.Thread):
    def run(self):
        addr = ("", PORT)
        log("UDP server listening on : " + str(addr), "debug")
        server = UDPServer(addr, Handler)
        server.serve_forever()


class Handler(BaseRequestHandler):

    number_client = 0
    my_addr = get_local_ip('8.8.8.8')

    def handle(self):
        request = self.request[0].strip()
        if request == "spot": # is it our UDP client?
            Handler.number_client += 1
            log("Detected client : " + str(Handler.number_client) + " on " + str(self.client_address), "debug")
            socket = self.request[1]
            reply = "%s:%i " % (Handler.my_addr, core.SRV_PORT)
            socket.sendto(reply, self.client_address)
        else:
            log("Detected wrong upb request from client : " + str(self.client_address), "debug")


def updserverstart():
    udp_server = MasterUDPServer()
    udp_server.start()


if __name__ == "__main__":
    updserverstart()
