""" Platform for generating and exposing a MUD file. """
from __future__ import annotations
import os
import shutil
import voluptuous as vol
import logging
import json
from datetime import datetime

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
        self.print_mud_draft()

        self._add_mud_rules()
        self.print_mud_draft()

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
        elif mode == "LLDP":
            _LOGGER.debug("Exposing the MUD file through LLDP")
        elif mode == "802.1AR":
            _LOGGER.debug("Exposing the MUD file inside a X.509 certificate through 802.1AR")
        else:
            _LOGGER.error("MUD file not exposed, unrecognized mode!")


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
