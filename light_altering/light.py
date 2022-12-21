"""Platform for integrating an Altering Light."""
from __future__ import annotations
from typing import Any, Final
import gc
import logging

# Import the device class from the component that you want to support
from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

NAME_KEY = "name"
DEFAULT_NAME = "Light Altering"

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Light Altering platform."""

    if NAME_KEY in config:
        name = config[NAME_KEY]
    else:
        name = DEFAULT_NAME

    lights = [LightAltering(name)]
    add_entities(lights)
    return True


class LightAltering(LightEntity):
    """Representation of a Light Altering."""

    _target1: Final[str] = "switch.switch_exfiltration"
    _target2: Final[str] = "switch.switch_calculated"

    def __init__(self, name: str = DEFAULT_NAME) -> None:
        """Initialize a LightAltering."""
        self._name = name
        self._brightness = None
        self._state = False

        # This object should physically communicate with the light
        self._light = LightEntity()

        _LOGGER.debug("<%s> was created", self._name)

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
        altering_hello_world = True
        toggle_calculated_switch = True
        toggle_switch = True

        if altering_hello_world:
            # Altering hello_world component
            hw_domain = "hello_world"
            component_available = self.hass.states.async_available(hw_domain)
            if component_available:
                entity_name = "Hello_World"
                target_entity = hw_domain + "." + entity_name
                self.hass.states.set(target_entity, "Altered!")
                _LOGGER.debug("<%s> altered", target_entity)

                new_entity = hw_domain + ".New_Entity"
                self.hass.states.set(new_entity, 42)

        if toggle_calculated_switch:
            # Note: this approach is not working, the updated state is overwritten to the last value few seconds later.

            t_state = self.hass.states.get(self._target2)  # Getting current state
            if t_state:
                _LOGGER.info("<%s> current state: <%s>", self._target2, t_state.state)

                # Toggling the state
                if t_state.state == "off":
                    self.hass.states.set(entity_id=self._target2, new_state="on")
                else:
                    self.hass.states.set(entity_id=self._target2, new_state="off")

                # Printing new updated state
                t_state = self.hass.states.get(self._target2)
                _LOGGER.info("<%s> new state: <%s>", self._target2, t_state.state)

        if toggle_switch:
            # In this block I tried several approach
            t_state = self.hass.states.get(self._target1)
            if t_state:
                _LOGGER.info("<%s> current state: <%s>", self._target1, t_state.state)

                # Altering target component
                if False:
                    # Aggiornamento dello stato forzato.
                    # This change seems to be not received by the system.
                    if t_state.state == "off":
                        t_state.state = "on"
                    else:
                        t_state.state = "off"
                elif False:
                    # This approach does not work. It accesses the static class.
                    exf_switch = self.hass.data["integrations"]["exfiltration_switch"]
                    target_switch = exf_switch.get_component().switch

                    if t_state.state == "on":
                        target_switch.turn_off()
                    else:
                        target_switch.turn_on()
                elif False:
                    # It works! Changing the value accessing the instance through the Garbage Collector
                    for obj in gc.get_objects():
                        if isinstance(obj, SwitchEntity):
                            if obj.name == "Exfiltration Switch":
                                print("I found exf_switch!")
                                obj.toggle()
                elif True:
                    self.hass.services.call(
                        domain="switch",
                        service="toggle",
                        service_data={"entity_id": self._target1},
                    )

                    # self.hass.services.call(domain="switch.exfiltration_switch", service="toggle")
                    # int_exf_switch = self.hass.data["integrations"]["exfiltration_switch"]
                    # target_component = int_exf_switch.get_component().switch

                # When the state is retrieved is not yet updated, after some seconds the change is triggered.
                t_state = self.hass.states.get(self._target1)
                _LOGGER.info("<%s> new state: <%s>", self._target1, t_state.state)

        return True
