""" Platform for generating and exposing a MUD file. """
from __future__ import annotations
import voluptuous as vol
import logging
import json
from pprint import pformat
from datetime import datetime

_LOGGER = logging.getLogger("mud_generator")
_LOCAL_EXTENTION_PATH = "./config/custom_components/mud_generator/"
_DRAFT_FILENAME = "mud_draft.json"
_MUD_FILENAME = "hass_mud_file.json"

class MUDGenerator():
    """ This class is able to create and expose a MUD file. """
    def __init__(self):
        self._mud_draft = json.load(
            open(_LOCAL_EXTENTION_PATH+_DRAFT_FILENAME, "r", encoding="utf-8")
        )

    def generate_mud_file(self):
        """ This function generates a MUD file starting from a template """
        self._add_fields()
        self._write_mud_file()

    def _add_fields(self):
        """ This function adds the additional requried parameters to the generated MUD file"""
        # mud_draft["mud-url"] = "http://iot-device.example.com/dnsname"
        self._mud_draft["ietf-mud:mud"]["last-update"] = datetime.now().isoformat(timespec="seconds")

        self._add_from_device_policy()
        self._generate_to_device_policy()
        self._add_acls()


    def _add_from_device_policy(self):
        """ Adding 'pointers' to the 'from' rules to the MUD file. """
        # Retrieving access-list array
        access_list = self._mud_draft["ietf-mud:mud"]["from-device-policy"]["access-lists"]["access-list"]
        for x in access_list:
            _LOGGER.warning(x)


    def _generate_to_device_policy(self):
        """ Adding 'pointers' to the 'to' rules to the MUD file. """
        # Retrieving access-list array
        access_list = self._mud_draft["ietf-mud:mud"]["to-device-policy"]["access-lists"]["access-list"]
        for x in access_list:
            _LOGGER.warning(x)


    def _add_acls(self):
        """ Adding the rules to the MUD file. """
        acls = self._mud_draft["ietf-access-control-list:acls"]["acl"]
        for x in acls:
            _LOGGER.warning(x)

    def _write_mud_file(self):
        """ Writing the new MUD file on a JSON file. """
        with open(_LOCAL_EXTENTION_PATH+_MUD_FILENAME, "w", encoding="utf-8") as outfile:
            json.dump(self._mud_draft, outfile, indent=2)
        _LOGGER.warning("The MUD file has been generated")

    def expose_mud_file(self):
        """ Exposing the MUD file to the MUD manager. """
        pass
