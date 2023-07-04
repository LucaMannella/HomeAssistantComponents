"""Platform for integrating a LightAll."""
from __future__ import annotations
from typing import Any
import logging

# Import the device class from the component that you want to support
from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity
from homeassistant.exceptions import ServiceNotFound
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
    """Adding the LightAll to Home Assistant."""

    if NAME_KEY in config:
        name = config[NAME_KEY]
    else:
        name = DEFAULT_NAME

    add_entities([LightAll(name)])
    return True


class LightAll(LightEntity):
    """A Light able to turn off all the lights."""

    def __init__(self, name: str = DEFAULT_NAME) -> None:
        """Initialize a LightAll."""
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
        self.turn(False)
        # self.turn_recursive(False)
        # self.turn_switches(False)

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        self._brightness = 255
        self._state = True
        self.turn(True)
        # self.turn_recursive(True)
        # self.turn_switches(True)

    def turn(self, on: bool = True) -> None:
        """Turn on or off all the lights."""
        if on:
            turn = "turn_on"
        else:
            turn = "turn_off"

        entities = self.hass.states.all()
        for entity in entities:
            if entity.entity_id.startswith("light."):
                if self.entity_id != entity.entity_id:
                    self.hass.services.call(
                        "light", turn, {"entity_id": entity.entity_id}
                    )

    # This method is recursevely called (user cannot interact properly with the lights anymore)
    def turn_recursive(self, on: bool = True) -> None:
        """Turn on or off all the lights (it is recursive) (T7)."""
        if on:
            turn = "turn_on"
        else:
            turn = "turn_off"

        entities = self.hass.states.all()
        for entity in entities:
            if entity.entity_id.startswith("light."):
                self.hass.services.call("light", turn, {"entity_id": entity.entity_id})

    # This method interact with switches instead of lamps
    def turn_switches(self, on: bool = True) -> None:
        """Turn on or off switches instead of lamps (T3)."""
        if on:
            turn = "turn_on"
        else:
            turn = "turn_off"

        # x = self.hass.services._services
        entities = self.hass.states.all()
        for entity in entities:
            if self.entity_id != entity.entity_id:
                self.hass.services.call("switch", turn, {"entity_id": entity.entity_id})

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
        return
