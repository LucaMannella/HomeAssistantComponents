"""Platform for integrating a LightIntegrity."""
from __future__ import annotations
from typing import Any
import logging

# Import the device class from the component that you want to support
from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


DEFAULT_NAME = "Light Turn All"
NAME_KEY = "name"


_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Adding the LightIntegrity to Home Assistant."""

    if NAME_KEY in config:
        name = config[NAME_KEY]
    else:
        name = DEFAULT_NAME

    add_entities([LightAll(name)])
    return True


class LightAll(LightEntity):
    """A Light able to turn off all the lights."""

    def __init__(self, name: str = DEFAULT_NAME) -> None:
        """Initialize a LightIntegrity."""
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

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._brightness = 0
        self._state = False

        entities = self.hass.states.all()
        for entity in entities:
            if entity.entity_id.startswith("light."):
                self.hass.services.call(
                    "light", "turn_off", {"entity_id": entity.entity_id}
                )

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        self._brightness = 255
        self._state = True

        entities = self.hass.states.all()
        for entity in entities:
            if entity.entity_id.startswith("light."):
                self.hass.services.call(
                    "light", "turn_on", {"entity_id": entity.entity_id}
                )

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
        return
