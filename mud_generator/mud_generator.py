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

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

_DEFAULT_COMPONENTS_PATH = "./homeassistant/components/"
_CUSTOM_COMPONENTS_PATH = "./config/custom_components/"
_LOCAL_EXTENTION_PATH = _CUSTOM_COMPONENTS_PATH+"mud_generator/"
_STORAGE_PATH = "./config/www/MUD/"
_DRAFT_FILENAME = "mud_draft.json"
_MUD_FILENAME = "hass_mud_file.json"
MUD_EXTRACT_FILENAME = "mud_gen.json"

class MUDGenerator():
    """ This class is able to create and expose a MUD file. """
    def __init__(self):
        # self._cwd = os.getcwd()
        with open(_LOCAL_EXTENTION_PATH+_DRAFT_FILENAME, "r", encoding="utf-8") as inputfile:
            self._mud_draft = json.load(inputfile)

    def generate_mud_file(self):
        """ This function generates a MUD file starting from a template """
        self._add_fields()
        self._write_mud_file()

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

            if MUD_EXTRACT_FILENAME in files:
                self._join_mud_files(cur_path, files)

        # Iterate over default components directories
        assert os.path.isdir(_DEFAULT_COMPONENTS_PATH)
        for cur_path, dirs, files in os.walk(_DEFAULT_COMPONENTS_PATH):
            if cur_path == _DEFAULT_COMPONENTS_PATH:
                continue
            elif "__" in cur_path or ".git" in cur_path:
                continue

            if MUD_EXTRACT_FILENAME in files:
                self._join_mud_files(cur_path, files)

    def _join_mud_files(self, cur_path, files):
        """ Looking for the MUD sub-files. """

        if MUD_EXTRACT_FILENAME in files:
            _LOGGER.info("MUD information found in %s", cur_path)
            with open(cur_path+"/"+MUD_EXTRACT_FILENAME, "r", encoding="utf-8") as inputfile:
                mud_extract = json.load(inputfile)

                from_policy = mud_extract["ietf-mud:mud"]["from-device-policy"]["access-lists"]["access-list"]
                self._mud_draft["ietf-mud:mud"]["from-device-policy"]["access-lists"]["access-list"] += from_policy

                to_policy = mud_extract["ietf-mud:mud"]["to-device-policy"]["access-lists"]["access-list"]
                self._mud_draft["ietf-mud:mud"]["to-device-policy"]["access-lists"]["access-list"] += to_policy

                acls = mud_extract["ietf-access-control-list:acls"]["acl"]
                self._mud_draft["ietf-access-control-list:acls"]["acl"] += acls
        # else:
        #    _LOGGER.debug("No MUD details in %s", cur_path)


    def _write_mud_file(self):
        """ Writing the new MUD file on a JSON file. """
        local_path_name = _LOCAL_EXTENTION_PATH+_MUD_FILENAME
        with open(local_path_name, "w", encoding="utf-8") as outfile:
            json.dump(self._mud_draft, outfile, indent=2)
        _LOGGER.debug("The MUD file has been generated inside the integration folder for debug purposes")

        # ToDo: it is necessary to create the folder in advance
        shutil.copyfile(local_path_name, _STORAGE_PATH+_MUD_FILENAME)
        _LOGGER.warning("The MUD file is ready to be exposed!")


    def expose_mud_file(self, mode="DHCP"):
        """ Exposing the MUD file to the MUD manager. """

        if mode == "DHCP":
            _LOGGER.debug("Exposing the MUD file through DHCP")
            self.expose_MUD_file_DHCP()
        elif mode == "LLDP":
            _LOGGER.debug("Exposing the MUD file through LLDP is not yet implemented")
        elif mode == "802.1AR":
            _LOGGER.debug("Exposing the MUD file inside a X.509 certificate through 802.1AR is not yet implemented")
        else:
            _LOGGER.error("MUD file not exposed, unrecognized mode!")

    def expose_MUD_file_DHCP(self):
        HAss_mac = gma()
        HAss_IP = socket.gethostbyname(socket.gethostname())

        _LOGGER.debug("HAss MAC address is: %s", HAss_mac)
        _LOGGER.debug("HAss IP address is: %s", HAss_IP)

        MUD_URL = "http://"+HAss_IP+":8123/local/MUD/hass_mud_file.json"
        _LOGGER.debug("Trying to expose the MUD URL: %s", MUD_URL)
        packet = (
            Ether(dst="ff:ff:ff:ff:ff:ff") /
            IP(src=HAss_IP, dst="255.255.255.255") /
            UDP(sport=68, dport=67) /
            BOOTP(
                chaddr=self.mac_to_bytes(HAss_mac),
                xid=random.randint(1, 2**32-1),  # Random integer required by DHCP
            ) /
            # DHCP(options=[("message-type", "discover"), "end"])
            DHCP(options=[("message-type", "discover"), ("mud-url", MUD_URL), "end"])
        )
        print(packet.__str__)
        x = sendp(packet, iface="eth0", verbose=True, return_packets=True)

        _LOGGER.debug("MUD URL Exposed!")

    def mac_to_bytes(self, mac_addr: str) -> bytes:
        """ Converts a MAC address string to bytes. """
        return int(mac_addr.replace(":", ""), 16).to_bytes(6, "big")

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
