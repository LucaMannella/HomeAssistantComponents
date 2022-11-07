""" Platform for generating and exposing a MUD file. """
from __future__ import annotations
from datetime import datetime
import json
import logging
import os
import random
import socket

from getmac import get_mac_address as gma
import voluptuous as vol
from scapy.all import Ether, IP, UDP, BOOTP, DHCP, sendp
import shutil

from . import DOMAIN, constants as c, util_network as nu

_LOGGER = logging.getLogger(__name__)

# Devcontainer paths
_DEV_DEFAULT_COMPONENTS_PATH = "./homeassistant/components/"
_DEV_CUSTOM_COMPONENTS_PATH = "./config/custom_components/"
_DEV_LOCAL_EXTENTION_PATH = _DEV_CUSTOM_COMPONENTS_PATH+"mud_generator/"
_DEV_STORAGE_PATH = "./config/www/MUD/"

# HAss OS paths
_DEFAULT_COMPONENTS_PATH = "/homeassistant/components/"
_CUSTOM_COMPONENTS_PATH = "/config/custom_components/"
_LOCAL_EXTENTION_PATH = _CUSTOM_COMPONENTS_PATH+"mud_generator/"
_STORAGE_PATH = "/config/www/MUD/"

# Filenames
_DRAFT_FILENAME = "mud_draft.json"
_FILENAME = "hass_mud_file"
_MUD_FILENAME = _FILENAME+".json"
_SIGNATURE_FILENAME = _FILENAME+".p7s"
_CERTIFICATE_FILENAME = "cert.pem"
_KEY_FILENAME = "key.pem"

class MUDGenerator():
    """ This class is able to create and expose a MUD file. """
    def __init__(self):
        # self._cwd = os.getcwd()
        with open(_LOCAL_EXTENTION_PATH+_DRAFT_FILENAME, "r", encoding="utf-8") as inputfile:
            self._mud_draft = json.load(inputfile)

        # Checking if the web server directory exists. If not is created.
        if not os.path.exists(_STORAGE_PATH):
            _LOGGER.info("Creating web server folder: <%s>", _STORAGE_PATH)
            os.makedirs(_STORAGE_PATH)
        else:
            _LOGGER.debug("Web server folder already exists: <%s>", _STORAGE_PATH)

    def generate_mud_file(self, sign=True):
        """ This function generates a MUD file starting from a template """
        self._add_fields()
        self._write_mud_file(sign)

    def _add_fields(self):
        """ This function adds the additional requried parameters to the generated MUD file"""
        # mud_draft["mud-url"] = "http://iot-device.example.com/dnsname"
        self._mud_draft["ietf-mud:mud"]["last-update"] = datetime.now().isoformat(timespec="seconds")
        self._add_mud_rules()

    def _add_mud_rules(self):
        """ This function add ACLs to the MUD file. """

        # Iterate over custom components directories
        assert os.path.isdir(_CUSTOM_COMPONENTS_PATH)
        for cur_path, dirs, files in os.walk(_CUSTOM_COMPONENTS_PATH):
            if cur_path == _CUSTOM_COMPONENTS_PATH:
                continue
            elif "__" in cur_path or ".git" in cur_path or DOMAIN in cur_path:
                continue

            if c.MUD_EXTRACT_FILENAME in files:
                self._join_mud_files(cur_path, files)

        # Iterate over default components directories
        assert os.path.isdir(_DEFAULT_COMPONENTS_PATH)
        for cur_path, dirs, files in os.walk(_DEFAULT_COMPONENTS_PATH):
            if cur_path == _DEFAULT_COMPONENTS_PATH:
                continue
            elif "__" in cur_path or ".git" in cur_path:
                continue

            if c.MUD_EXTRACT_FILENAME in files:
                self._join_mud_files(cur_path, files)

    def _join_mud_files(self, cur_path, files):
        """ Looking for the MUD sub-files. """

        if c.MUD_EXTRACT_FILENAME in files:
            _LOGGER.info("MUD information found in %s", cur_path)
            with open(cur_path+"/"+c.MUD_EXTRACT_FILENAME, "r", encoding="utf-8") as inputfile:
                mud_extract = json.load(inputfile)

                from_policy = mud_extract["ietf-mud:mud"]["from-device-policy"]["access-lists"]["access-list"]
                self._mud_draft["ietf-mud:mud"]["from-device-policy"]["access-lists"]["access-list"] += from_policy

                to_policy = mud_extract["ietf-mud:mud"]["to-device-policy"]["access-lists"]["access-list"]
                self._mud_draft["ietf-mud:mud"]["to-device-policy"]["access-lists"]["access-list"] += to_policy

                acls = mud_extract["ietf-access-control-list:acls"]["acl"]
                self._mud_draft["ietf-access-control-list:acls"]["acl"] += acls
        # else:
        #    _LOGGER.debug("No MUD details in %s", cur_path)


    def _write_mud_file(self, sign=True):
        """ Writing the new MUD file on a JSON file. """
        local_path_name = _DEV_LOCAL_EXTENTION_PATH+_MUD_FILENAME
        with open(local_path_name, "w", encoding="utf-8") as outfile:
            json.dump(self._mud_draft, outfile, indent=2)
        _LOGGER.debug("The MUD file has been generated inside the integration folder for debug purposes")

        if sign:
            _LOGGER.debug("Signing the MUD file")
            certificate_path = _DEV_LOCAL_EXTENTION_PATH+_CERTIFICATE_FILENAME
            key_path = _DEV_LOCAL_EXTENTION_PATH+_KEY_FILENAME
            signature_path = _DEV_STORAGE_PATH+_SIGNATURE_FILENAME
            if not os.path.exists(certificate_path):
                _LOGGER.debug("X.509 certificate is missing. I am going to create it")
                # generating certificate
                cert_command = 'openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes -keyout '+key_path+' -out '+certificate_path+' -subj "/CN=HomeAssistantMUDIntegration"'
                ok = os.system(cert_command)
                if ok == 0:
                    _LOGGER.debug("Certificiate succesfully generated!")
                else:
                    _LOGGER.critical("Certificate not generated, will be impossible to sign the MUD file!")

            # Signing the generated MUD file
            sign_command = "openssl cms -sign -signer "+certificate_path+" -inkey "+key_path+" -in "+local_path_name+" -binary -outform DER -binary -out "+signature_path
            ok = os.system(sign_command)
            if ok == 0:
                _LOGGER.debug("MUD file signed")
            else:
                _LOGGER.error("MUD file not signed!")

        if os.path.exists(_DEV_STORAGE_PATH):
            shutil.copyfile(local_path_name, _DEV_STORAGE_PATH+_MUD_FILENAME)
            _LOGGER.warning("The MUD file is ready to be exposed!")
        else:
            _LOGGER.critical("There is no webserver folder!")


    def expose_mud_file(self, interface="eth0", mode="DHCP"):
        """ Exposing the MUD file to the MUD manager. """

        if mode == "DHCP":
            _LOGGER.debug("Exposing the MUD file through DHCP")
            self.expose_MUD_file_DHCP(interface)
        elif mode == "LLDP":
            _LOGGER.debug("Exposing the MUD file through LLDP is not yet implemented")
        elif mode == "802.1AR":
            _LOGGER.debug("Exposing the MUD file inside a X.509 certificate through 802.1AR is not yet implemented")
        else:
            _LOGGER.error("MUD file not exposed, unrecognized mode!")

    def expose_MUD_file_DHCP(self, interface="eth0"):  #wlan0
        HAss_mac = gma()
        byte_mac_addr=nu.mac_to_bytes(HAss_mac)

        hostname = socket.gethostname()
        # HAss_IP = socket.gethostbyname(hostname)
        HAss_IP = nu.get_ip()
        # HAss_IP = "192.168.7.242"

        # _LOGGER.debug("HAss MAC address is: %s", HAss_mac)
        # _LOGGER.debug("HAss IP address is: %s", HAss_IP)
        _LOGGER.debug("Hostname: %s --- Interface: <%s> --- IP: %s --- MAC: %s", hostname, interface, HAss_IP, HAss_mac)

        # _LOGGER.debug("Releasing IP address...")
        # self._send_dchp_message("release", HAss_IP, byte_mac_addr, hostname, interface)

        MUD_URL = "http://"+HAss_IP+":8123/local/MUD/hass_mud_file.json"
        _LOGGER.debug("Trying to expose the MUD URL: %s", MUD_URL)
        # _LOGGER.debug("Renewing IP address with associated MUD file")
        self.send_dchp_message("request", HAss_IP, byte_mac_addr, hostname, interface, MUD_URL)

        _LOGGER.debug("MUD URL Exposed!")
        return

        # packet = (
        #     Ether(dst="ff:ff:ff:ff:ff:ff") /
        #     IP(src=HAss_IP, dst="255.255.255.255") /
        #     UDP(sport=68, dport=67) /
        #     BOOTP(
        #         chaddr=self.mac_to_bytes(HAss_mac),
        #         xid=random.randint(1, 2**32-1),  # Random integer required by DHCP
        #     ) /
        #     # DHCP(options=[("message-type", "discover"), "end"])
        #     # DHCP(options=[("message-type", "discover"), ("mud-url", MUD_URL), "end"])
        #     DHCP(options=[("message-type", "discover"), "end"])
        # )
        # print(packet.__str__)
        # x = sendp(packet, iface="eth0", verbose=True, return_packets=True)


    def send_dchp_message(self, message_type, device_IP, byte_mac_addr, hostname, interface_name, mud_url=None, verbose=True):
        ## MT: discover -> The first message of a DHCP flow -> Can I have a DHCP address?
        ## MT: request -> The third message of a DHCP flow -> I would like to accept your offer
        ## MT: release -> I do not want my address anymore

        client_id = bytearray(byte_mac_addr)
        client_id.insert(0, 1)
        client_id = bytes(client_id)

        dhcp_options = [("message-type", message_type)]
        dhcp_options.append(("client_id", client_id))
        if not message_type == "release":
            dhcp_options.append(("requested_addr", device_IP))
        dhcp_options.append(("hostname", hostname))
        if mud_url:
            dhcp_options.append(("mud-url", mud_url))
        dhcp_options.append("end")
        dhcp_object = DHCP(options=dhcp_options)

        packet = (
            Ether(dst="ff:ff:ff:ff:ff:ff") /
            IP(src="0.0.0.0", dst="255.255.255.255") /  # src=device_ip
            UDP(sport=68, dport=67) /
            BOOTP(
                chaddr=byte_mac_addr,
                xid=random.randint(1, 2**32-1),  # Random integer required by DHCP
            ) /
            dhcp_object
        )
        _LOGGER.debug("Packet to send:\n %s", packet.__str__)
        x = sendp(packet, iface=interface_name, verbose=verbose, return_packets=True)
        return x


    def print_mud_draft(self):
        """ Printing MUD elements. """

        _LOGGER.debug("Printing from policies")
        access_list = self._mud_draft["ietf-mud:mud"]["from-device-policy"]["access-lists"]["access-list"]
        for x in access_list:
            _LOGGER.debug(x)

        _LOGGER.debug("Printing to policies")
        access_list = self._mud_draft["ietf-mud:mud"]["to-device-policy"]["access-lists"]["access-list"]
        for x in access_list:
            _LOGGER.debug(x)

        _LOGGER.debug("Printing ACLs")
        acls = self._mud_draft["ietf-access-control-list:acls"]["acl"]
        for x in acls:
            _LOGGER.debug(x)
