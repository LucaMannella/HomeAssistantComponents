"""Platform for integrating a Simple Access Light."""
from __future__ import annotations
from typing import Any, Final
import gc
import random

# Import the device class from the component that you want to support
from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Adding the Simple Access light to Home Assistant."""

    add_entities([LightSimpleAccess()])
    return True


class LightSimpleAccess(LightEntity):
    """A Light able to access other components' data."""

    _target: Final[str] = "switch.switch_target"
    _target_name: Final[str] = "Switch Target"

    def __init__(self, upload: bool = False) -> None:
        """Initialize a LightSimpleAccess."""
        self._name = "Simple Access"
        self._brightness = None
        self._state = False
        self._upload = upload
        self._target_integration = None

        # This object should physically communicate with the light
        self._light = LightEntity()

        print('Light "' + self._name + '" was created.')

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
        self.read_values()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._brightness = 0
        self._state = False
        self.alter_values()

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
        return

    def read_values(self):
        """This method read the secret stored inside the target."""

        if not self._target_integration:
            self._target_integration = self._get_target(self._target_name)

        if self._target_integration:
            secret = self._target_integration._my_secret
            print('The secret of "' + self._target_name + '" is: "' + secret + '"')

    def alter_values(self):
        """This method read the secret stored inside the target."""

        if not self._target_integration:
            self._target_integration = self._get_target(self._target_name)

        if self._target_integration:
            new_secret = "Secret Altered " + str(random.randint(0, 1000))
            self._target_integration._my_secret = new_secret

    def _get_target(self, target_name: str):
        """Getting an integration reference through the Garbage Collector"""

        for obj in gc.get_objects():
            if isinstance(obj, SwitchEntity):
                if obj.name == target_name:
                    print(target_name + " found!")
                    return obj

        return False
