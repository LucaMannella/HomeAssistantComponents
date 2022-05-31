""" Adding a fake switch to Home Assistant. It will be the target of other components' attacks. """

from __future__ import annotations
import time
import logging

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
    """Adding the Target Switch to Home Assistant."""

    add_entities([SwitchTarget()])
    return True


class SwitchTarget(SwitchEntity):
    """A fake switch integration."""

    def __init__(self):
        self._attr_is_on = False
        self._name = "Switch Target"
        self._my_secret = "This is my secret!"

        _LOGGER.info('Switch %s instantiated', self._name)

    @property
    def name(self):
        """Name of the entity."""
        return self._name

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        # Delay to simulate communication with a physical device
        time.sleep(1)

        self._attr_is_on = True
        _LOGGER.info("%s on!", self._name)

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        # Delay to simulate communication with a physical device
        time.sleep(1)

        self._attr_is_on = False
        _LOGGER.info("%s off!", self._name)
