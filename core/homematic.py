#!python

import core
import urllib2
from core.Logger import log
version = "1.0.5"


def get_device_to_check():
    log("Connecting to the CCU to get device list : " + str(core.IP_CCU), "debug")
    try:
        response = urllib2.urlopen('http://' + str(core.IP_CCU) + '/config/xmlapi/sysvarlist.cgi', timeout=2)
        if not core.CCU_CONNECTION_OK:
            log("Connection to the CCU establish (RX): " + str(core.IP_CCU), "info")
            core.CCU_CONNECTION_OK = True

    except (urllib2.URLError) as e:
        #	disrupted
        if core.CCU_CONNECTION_OK:
            log("Timeout by connection to the CCU (RX): " + str(core.IP_CCU), "error")
            core.CCU_CONNECTION_OK = False
        print("There was an error: %r" % e)
        device_dict = None
        return device_dict
    except:
        if core.CCU_CONNECTION_OK:
            log("Timeout by connection to the CCU (RX): " + str(core.IP_CCU), "error")
            core.CCU_CONNECTION_OK = False
        device_dict = None
        return device_dict

    html = response.read()                                                  # Lode XML files into the variable
    device_dict = {}                                                        #
    import xml.etree.ElementTree as ET                                      #
    try:
        root = ET.fromstring(html)                                          # read the xml information
    except :
        if core.CCU_CONNECTION_OK:
            log("XML ParseError CCU (RX): " + str(core.IP_CCU), "error")
            core.CCU_CONNECTION_OK = False
        print("There was an error")
        device_dict = None
        return device_dict

    for var_spot in root.findall('systemVariable'):                         # walk through the xml elements with the name 'systemVariable'
        var_mac = var_spot.get('name')                                      # read element
        if var_mac.find('spot_') != -1:                                     # look for the name 'spot_'

            nametmp = var_spot.get('name')
            nametmp = nametmp.split('_')                                    # separate the individual values (spot_CC:29:F5:67:B7:EC_marius_iPhone)
            device_dic_val = {}
            try:
                device_dic_val["presence"] = str(var_spot.get('value'))
                device_dic_val['name'] = str(nametmp[3])
                device_dic_val['ise_id'] = str(var_spot.get('ise_id'))
                device_dic_val['first_not_seen'] = None
                device_dic_val['times_not_seen'] = 0
                device_dic_val['seen_by'] = {}
                device_dic_val['device'] = str(nametmp[4])
                device_dict[nametmp[2]] = device_dic_val
            except IndexError:
                log("sysvar from CCU has wrong format! We need var_spot_80:B0:3D:2D:5F:16_Paulina_iPhone", "error")
                exit()

    return device_dict


def send_device_status_to_ccu(ise_id, var_status):
    # send one Device Status at a time
    command = "http://" + str(core.IP_CCU) + "/config/xmlapi/statechange.cgi?ise_id=" + ise_id + "&new_value=" + \
              var_status
    log("sendVariableToCCU2 Command : " + str(command), "debug")
    try:
        response = urllib2.urlopen(command, timeout=2)
        if not core.CCU_CONNECTION_OK:
            log("Connection to the CCU establish (TX): " + str(core.IP_CCU), "info")
            core.CCU_CONNECTION_OK = True

    except urllib2.URLError, e:
        if core.CCU_CONNECTION_OK:
            log("Timeout by connection to the CCU (TX): " + str(core.IP_CCU), "error")
            core.CCU_CONNECTION_OK = False
        if not core.PROG_DAEMONIZE:
            print("There was an error: %r" % e)
        return False

    html = response.read()
    log("sendVariableToCCU2.html Answer from CCU2 : " + str(html), "debug")
    if response.msg == 'OK':
        return True
    else:
        return False

#if __name__ == "__main__":
#    getDeviceToCheck()
