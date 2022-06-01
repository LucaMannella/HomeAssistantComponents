"""An example of switch shown at PyCon 2016"""
from __future__ import annotations
import os
import logging

# from voluptuous.validators import PathExists
from homeassistant.components.switch import SwitchEntity

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    add_entities([SwitchFile(config["file_path"])])


class SwitchFile(SwitchEntity):
    """This Switch base its state on a file."""

    def __init__(self, path):
        self._path = path
        self.update()
        _LOGGER.info("I'm the SwitchFile: %s", self.name)

    @property
    def name(self):
        """Name of the entity."""
        return os.path.basename(self._path)

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        open(self._path, "ab").close()

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        os.remove(self._path)

    def update(self):
        """Update the status of the switch."""
        self._state = os.path.isfile(self._path)
