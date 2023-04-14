"""Platform for integrating a LightTarget."""
from __future__ import annotations
from typing import Any
import logging

# Import the device class from the component that you want to support
from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity, DOMAIN as LIGHT_DOMAIN
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

DEFAULT_NAME = "Light Target"
NAME_KEY = "name"

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Adding the LightTarget to Home Assistant."""

    if NAME_KEY in config:
        name = config[NAME_KEY]
    else:
        name = DEFAULT_NAME

    add_entities([LightTarget(name)])
    return True


class LightTarget(LightEntity):
    """Just an emulated light."""

    def __init__(self, name: str = DEFAULT_NAME) -> None:
        """Initialize a LightTarget."""
        self._attr_unique_id = "PoliTo.eLite.LM." + LIGHT_DOMAIN + "." + DOMAIN
        self._name = name
        self._brightness = None
        self._state = False

        # This object should physically communicate with the light
        self._light = LightEntity()

        _LOGGER.info("<%s> was created", self._name)

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
        """Instruct the light to turn on."""
        self._brightness = 255
        self._state = True
        _LOGGER.debug("Turned on!")

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._brightness = 0
        self._state = False
        _LOGGER.debug("Turned off!")

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
        return
