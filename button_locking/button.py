"""This button is designed to try to lock Home Assistant."""
from __future__ import annotations
from typing import Final
import time
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.button import ButtonEntity

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the button."""

    add_entities([ButtonLocking()])
    # Return boolean to indicate that initialization was successfully.
    return True


class ButtonLocking(ButtonEntity):
    "This class extend the ButtonEntity"

    _target1: Final[str] = "switch.switch_calculated"
    _waiting_time: Final[float] = 0.1
    _printing: Final[bool] = False

    @property
    def name(self):
        """Name of the entity."""
        return "Button Locking"

    def press(self) -> None:
        """Handle the button press."""
        print(self.name + " - trying to lock Home Assistant")

        t_state = self.hass.states.get(self._target1)
        print(self._target1 + " - actual state: " + t_state.state)

        should_be_locked = True
        count = 1
        print_count = 1
        print_str = self.name + " pressed... Switch " + self._target1 + "toggled... "
        while should_be_locked:
            self.hass.services.call(
                domain="switch",
                service="toggle",
                service_data={"entity_id": self._target1},
            )
            if self._waiting_time != 0:
                time.sleep(self._waiting_time)
            if self._printing:
                print(print_str + str(count))

            if count == 1000:
                _LOGGER.info("%d000 service calls executed", print_count)
                print_count += 1
                count = 0
            count += 1

        _LOGGER.warning("%s - loop broken!", self.name)

    # async def async_press(self) -> None:
    #    """Handle the button press."""
