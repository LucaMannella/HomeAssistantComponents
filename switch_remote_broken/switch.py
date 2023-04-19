"""An example of switch configured as calculated."""
from __future__ import annotations
import logging
import requests

# from voluptuous.validators import PathExists
from homeassistant.components.switch import SwitchEntity

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

NAME_KEY = "name"
URL_KEY = "url"
ID_KEY = "id"

DEFAULT_NAME = "Switch Remote Broken"
DEFAULT_ID = 1

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
    if ID_KEY in config:
        switch_id = config[ID_KEY]
    else:
        switch_id = DEFAULT_ID

    add_entities([SwitchRemote(name, url, switch_id)])
    return True


class SwitchRemote(SwitchEntity):
    """A Switch designed to be also remotely controlled."""

    def __init__(self, name, url, switch_id=1):
        self._name = name
        self._url = url
        self._switch_id = switch_id
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
        get_url = self._url + "/api/switches/" + str(self._switch_id)
        response = requests.get(get_url, timeout=10)
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
        """This method updates the state of the switch locally and on the remote server."""
        self._attr_is_on = value
        if self._update_remote_value():
            _LOGGER.debug("Switch status succesfully updated to <%s>", self._attr_is_on)
        else:
            _LOGGER.error(
                "Impossible to update switch's status on remote server: <%s>", self._url
            )

    def _update_remote_value(self) -> bool:
        """This method tries to update the remote value of the switch"""
        put_url = self._url + "/api/switches/1"
        obj_to_send = {"value": self._attr_is_on, "id": 1, "user": 1}
        response = requests.put(put_url, json=obj_to_send, timeout=10)
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
