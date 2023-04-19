"""An example of switch configured as calculated."""
from __future__ import annotations
import time
import logging
import requests

# from voluptuous.validators import PathExists
from homeassistant.components.switch import SwitchEntity

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

NAME_KEY = "name"
URL_KEY = "url"
DEFAULT_NAME = "Switch Remote"
DOMAIN = "switch_remote"

UPDATE_STATUS = GET_LAST_STATUS = "/api/switches/1"

""" To work properly this integration needs to have a configured "scan_interval".
    Every x seconds the update() function is called fetching the remote value from the server.

    switch:
    - platform: switch_remote
      scan_interval: 300  // number of seconds that will trigger an update
      url: localhost      // "host.docker.internal" if the integration is running in a container
"""

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    if NAME_KEY in config:
        name = config[NAME_KEY]
    else:
        name = DEFAULT_NAME
    if URL_KEY in config:
        url = config[URL_KEY]
    else:
        url = "localhost"

    add_entities([SwitchRemote(name, url)])
    return True


class SwitchRemote(SwitchEntity):
    """This Switch uses almost all the method of its superclasses."""

    def __init__(self, name, url):
        self._name = name
        self._url = url
        self._get_url = self._url + GET_LAST_STATUS
        self._put_url = self._url + UPDATE_STATUS
        remote_value = self._get_remote_value()
        if remote_value is None:
            self._attr_is_on = False
        else:
            self._attr_is_on = remote_value

    @property
    def name(self):
        """Name of the entity."""
        return self._name

    def _get_remote_value(self) -> bool:
        """This method periodically checks if the status of the switch was remotely updated."""
        response = requests.get(self._get_url, allow_redirects=True, timeout=10)
        if response.status_code != 200:
            _LOGGER.error("Impossible to retrieve switch status!")
            return None
        else:
            try:
                value = response.json()
                if value and "value" in value:
                    return bool(value["value"])
                else:
                    return None
            except Exception as ex:
                _LOGGER.error("Error parsing json object: %s", ex)
                return None

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self.update_value(True)

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self.update_value(False)

    def update_value(self, value: bool):
        # time.sleep(2)
        self._attr_is_on = value
        if self._update_remote_value():
            _LOGGER.debug("Switch status succesfully updated to <%s>", self._attr_is_on)
        else:
            _LOGGER.error(
                "Impossible to update switch's status on remote server: <%s>", self._url
            )

    def _update_remote_value(self) -> bool:
        response = requests.put(
            self._put_url,
            json={"value": self._attr_is_on, "id": 1, "user": 1},
            timeout=10,
        )
        if response.status_code == 200:
            return True
        else:
            _LOGGER.error("Error storing new status: %s", response.json()["error"])
            return False

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        remote_value = self._get_remote_value()
        if remote_value is None:
            _LOGGER.error("Impossible to retrieve remote status!")
        else:
            if remote_value != self._attr_is_on:
                _LOGGER.info(
                    "New value <%s> fetched from <%s>", remote_value, self._url
                )
                self._attr_is_on = remote_value
