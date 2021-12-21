"""An example of switch configured as calculated."""
from __future__ import annotations
import time

# from voluptuous.validators import PathExists
from homeassistant.components.switch import SwitchEntity

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    add_entities([SwitchCalculated()])
    return True


class SwitchCalculated(SwitchEntity):
    """This Switch uses almost all the method of its superclasses."""

    def __init__(self):
        self._attr_is_on = False
        print("I'm the Switch: " + self.name)

    @property
    def name(self):
        """Name of the entity."""
        return "Switch Calculated"

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        time.sleep(2)
        self._attr_is_on = True
        print("I am on!")

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        time.sleep(2)
        self._attr_is_on = False
        print("I am off!")
