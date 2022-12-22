"""Platform for integrating a Simple Altering Light."""
from __future__ import annotations
from typing import Any, Final
import gc
import time
import logging

# Import the device class from the component that you want to support
from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

NAME_KEY = "name"
DEFAULT_NAME = "Light Altering State"
DEFAULT_TARGET = "switch.switch_target"

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Adding the LightAlteringState to Home Assistant."""

    if NAME_KEY in config:
        name = config[NAME_KEY]
    else:
        name = DEFAULT_NAME

    add_entities([LightAlteringState(name)])
    return True


class LightAlteringState(LightEntity):
    """A Light able to modify other components"""

    _use_api: Final[bool] = False

    def __init__(self, name: str = DEFAULT_NAME, target: str = DEFAULT_TARGET) -> None:
        """Initialize a LightAlteringState."""
        self._name = name
        self._brightness = None
        self._state = False
        self._target = target

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
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._brightness = 255
        self._state = True
        self.toggle_switch_target(self._use_api)

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._brightness = 0
        self._state = False
        self.toggle_switch_target(self._use_api)

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
        return

    def toggle_switch_target(self, use_api: bool = False):
        """This method toggles the status of a target switch."""

        t_state = self.hass.states.get(self._target)
        _LOGGER.info("<%s> current state: <%s>", self._target, t_state.state)

        if use_api:  # Updating component using APIs
            self.hass.services.call(
                domain="switch",
                service="toggle",
                service_data={"entity_id": self._target},
            )
        else:  # Updating the value accessing the instance through the Garbage Collector
            obj = self._get_target("Switch Target")
            if obj:
                obj.toggle()
            else:
                _LOGGER.info("Switch Target not found!")

        # Waiting for update
        time.sleep(2)

        # Retrieving and printing the updated status
        t_state = self.hass.states.get(self._target)
        _LOGGER.info("<%s> new state: <%s>", self._target, t_state.state)

        return True

    def _get_target(self, target_name: str):
        """Getting an integration reference through the Garbage Collector"""

        for obj in gc.get_objects():
            if isinstance(obj, SwitchEntity):
                if obj.name == target_name:
                    _LOGGER.info("%s found!", target_name)
                    return obj

        return False
