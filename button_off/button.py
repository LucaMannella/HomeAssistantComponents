from __future__ import annotations
import logging

# Import the device class from the component that you want to support
from homeassistant.core import HomeAssistant, split_entity_id
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

DEFAULT_NAME = "Button Off"


_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    add_entities([ButtonOff()])

    return True


class ButtonOff(ButtonEntity):
    """This button turns off all the available entitites."""

    def __init__(self, name: str = DEFAULT_NAME) -> None:
        self._attr_name = name
        _LOGGER.debug("Button Off initialized\n")

    def press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Button Off pressed\n")

        entities = self.hass.states.entity_ids()
        for key in entities:
            domain = split_entity_id(key)
            if self.hass.services.has_service(domain=domain[0], service="turn_off"):
                self.hass.services.call(
                    domain=domain[0],
                    service="turn_off",
                    target={"entity_id": key},
                )
