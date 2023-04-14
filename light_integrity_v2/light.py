"""Platform for integrating a LightIntegrity."""
from __future__ import annotations
from typing import Any, Final
import logging

# Import the device class from the component that you want to support
from homeassistant.core import HomeAssistant
from homeassistant.components.light import (
    LightEntity,
    ATTR_BRIGHTNESS_PCT,
    ColorMode,
    SUPPORT_BRIGHTNESS,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

DEFAULT_NAME = "Light Integrity v2"
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

    add_entities([LightBrIntegrity(name)])
    return True


class LightBrIntegrity(LightEntity):
    """A Light able to alter other components' integrity."""

    _target: Final[str] = "switch.switch_target"
    _target_name: Final[str] = "Switch Target"

    def __init__(self, name: str = DEFAULT_NAME) -> None:
        """Initialize a LightIntegrity."""
        self._name = name
        self._state = False
        self._brightness = None
        self._attr_color_mode = ColorMode.BRIGHTNESS

        _LOGGER.info("<%s> was created", self._name)

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        return self._brightness

    @property
    def supported_features(self) -> int:
        return SUPPORT_BRIGHTNESS

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""

        self._state = True
        new_bri = kwargs.get("brightness")

        if not new_bri:
            _LOGGER.debug("Turning lamp on")
            self._brightness = kwargs.get(ATTR_BRIGHTNESS_PCT, 255)
        elif self._brightness != new_bri:
            _LOGGER.info("Brightness from %s to %s", self._brightness, new_bri)
            self._brightness = new_bri
            _LOGGER.debug("Brightness updated %s %s", self._brightness, new_bri)
        else:
            _LOGGER.debug("Brightness not updated")

        self.store_brightness()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        if self.is_on:
            self._state = False
            self._brightness = 0
            _LOGGER.debug("Lamp turned off")
        else:
            _LOGGER.warning("Light already off")

        self.store_brightness()

    def store_brightness(self) -> None:
        """This method store the brightness on a remote server (T4)."""
        pass