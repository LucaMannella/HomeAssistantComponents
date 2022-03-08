"""Platform for integrating a Simple Altering Light."""
from __future__ import annotations
from typing import Any, Final
import gc
import time

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
    """Adding the Simple Altering light to Home Assistant."""

    add_entities([LightSimpleAltering()])
    return True


class LightSimpleAltering(LightEntity):
    """A Light able to modify other components"""

    _target: Final[str] = "switch.switch_target"
    _use_api: Final[bool] = False

    def __init__(self, upload: bool = False) -> None:
        """Initialize a LightSimpleAltering."""
        self._name = "Simple Altering"
        self._brightness = None
        self._state = False
        self._upload = upload

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
        self.alter_values()

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

    def alter_values(self):
        """This method alter some values in other integrations."""
        altering_hello_world = False
        toggle_target_switch = True

        if altering_hello_world:
            # Altering hello_world component
            hw_domain = "hello_world"
            component_available = self.hass.states.async_available(hw_domain)
            if component_available:
                target_entity = hw_domain + ".Hello_World"
                self.hass.states.set(hw_domain + ".Hello_World", "Altered!")
                self.hass.states.set(hw_domain + ".New_Entity", 42)
                print(target_entity + " value changed")

        if toggle_target_switch:
            t_state = self.hass.states.get(self._target)
            print(self._target + " - actual state: " + t_state.state)

            if self._use_api:  # Updating component using APIs
                self.hass.services.call(
                    domain="switch",
                    service="toggle",
                    service_data={"entity_id": self._target},
                )
            else:  # Updating the value accessing the instance through the Garbage Collector
                for obj in gc.get_objects():
                    if isinstance(obj, SwitchEntity):
                        if obj.name == "Switch Target":
                            print("Switch Target found!")
                            obj.toggle()

            # Waiting for update
            time.sleep(2)

            # Recupero e stampo lo stato aggiornato
            t_state = self.hass.states.get(self._target)
            print(self._target + " new state: " + t_state.state)

        return True
