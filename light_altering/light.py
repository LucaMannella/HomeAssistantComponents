"""Platform for integrating an Light Altering."""
from __future__ import annotations
from typing import Any, Final
import gc

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
    """Set up the Light Altering platform."""

    lights = [LightAltering()]
    add_entities(lights)
    return True


class LightAltering(LightEntity):
    """Representation of a Light Altering."""

    _target1: Final[str] = "switch.exfiltration_switch"
    _target2: Final[str] = "switch.switch_calculated"

    def __init__(self, upload: bool = False) -> None:
        """Initialize a LightAltering."""
        self._light = LightEntity()
        self._name = "Light Altering"
        self._brightness = None
        self._state = False
        self._upload = upload
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

    async def async_alter_values(self):
        """This method alters values of other integrations."""

        # Stato originale
        t_state = self.hass.states.get(self._target2)
        print(self._target2 + " - actual state: " + t_state.state)

        # Modifica dello stato
        if t_state.state == "off":
            await self.hass.states.async_set(entity_id=self._target2, new_state="on")
        else:
            await self.hass.states.async_set(entity_id=self._target2, new_state="off")

        # Stampo lo stato aggiornato
        t_state = self.hass.states.get(self._target2)
        print(self._target2 + " new state: " + t_state.state)

        t_state = self.hass.states.get(self._target1)
        print(self._target1 + " - actual state: " + t_state.state)

        if t_state.state == "off":
            self.hass.states.async_set(entity_id=self._target1, new_state="on")
        else:
            self.hass.states.async_set(entity_id=self._target1, new_state="off")

        # Recupero e stampo lo stato aggiornato
        t_state = self.hass.states.get(self._target1)
        print(self._target1 + " new state: " + t_state.state)

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
                target_entity = hw_domain + ".Hello_World"
                self.hass.states.set(hw_domain + ".Hello_World", "Altered!")
                self.hass.states.set(hw_domain + ".New_Entity", 42)
                print(target_entity + " value changed")

        if toggle_calculated_switch:
            t_state = self.hass.states.get(self._target2)
            print(self._target2 + " - actual state: " + t_state.state)

            if t_state.state == "off":
                self.hass.states.set(entity_id=self._target2, new_state="on")
            else:
                self.hass.states.set(entity_id=self._target2, new_state="off")

            # Recupero e stampo lo stato aggiornato
            t_state = self.hass.states.get(self._target2)
            print(self._target2 + " new state: " + t_state.state)

        if toggle_switch:
            # Retrieving and printing the state to alter
            t_state = self.hass.states.get(self._target1)
            print(self._target1 + " - actual state: " + t_state.state)

            # Altering target component
            if False:
                # Aggiornamento dello stato forzato.
                # Non viene recepito dal sistema.
                if t_state.state == "off":
                    t_state.state = "on"
                else:
                    t_state.state = "off"
            elif False:
                # Aggiornamento dello stato tramite metodo setter.
                # Lo stato viene poi automaticamente sovrascritto (dal componente?)
                if t_state.state == "off":
                    self.hass.states.set(entity_id=self._target1, new_state="on")
                else:
                    self.hass.states.set(entity_id=self._target1, new_state="off")
            elif False:
                # Questo approccio non funziona in quanto accede alla classe statica
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

            # Recupero e stampo lo stato aggiornato
            t_state = self.hass.states.get(self._target1)
            print(self._target1 + " new state: " + t_state.state)

        return True

    def read_values(self):
        """This method reads some values from other integrations."""
        print_integration = False
        print_entities = False
        print_services = False

        if print_integration:
            # Vengono listate tutte i componenti disponibili
            print("\nList of available components:")
            for comp in self.hass.config.components:
                print(comp)
            print()

        # Per listare le entità disponibili (istanze dei componenti)
        if print_entities:
            n_entities = self.hass.states.async_entity_ids_count()
            print("\nNumber of available entities: " + str(n_entities))

            print("--- List of filtered entities ---")
            for ent in self.hass.states.all():
                # Ho deciso di stampare solo alcune per testing
                if "switch" in ent.object_id or "light" in ent.object_id:
                    print(ent)
            print()

        if print_services:
            services = self.hass.services.services

            for x, domain in services.items():
                print("---" + x + "---")
                for s in domain:
                    print(s)
