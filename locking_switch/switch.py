"""This custom switch tries to lock Home Assistant."""
from __future__ import annotations
import time
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.switch import SwitchEntity

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    add_entities([SwitchLocking()])
    return True


class SwitchLocking(SwitchEntity):
    """This is a virtual switch designed to try to lock Home Assistant."""

    def __init__(self, printing: bool = False):
        """Initialize the Switch"""
        _LOGGER.info("Initializing switch: %s", self.name)
        self._is_on = False

    @property
    def name(self):
        """Name of the entity."""
        return "Switch Locking"

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.debug("%s - turning 'on' the switch", self.name)
        should_be_locked = True
        count = 1
        while should_be_locked:
            time.sleep(1)
            _LOGGER.info("turning on... %s second elapsed", str(count))
            count += 1

        self._is_on = True
        _LOGGER.warning("Turned on!")

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        _LOGGER.debug("%s - turning 'off' the Switch", self.name)
        should_be_locked = True
        count = 1
        while should_be_locked:
            time.sleep(1)
            _LOGGER.info("turning off... %s second elapsed", str(count))
            count += 1

        self._is_on = False
        _LOGGER.warning("Turned off!")
