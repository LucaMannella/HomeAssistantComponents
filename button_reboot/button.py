"""This button reboot Home Assistant."""
from __future__ import annotations
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the button."""

    add_entities([ButtonReboot()])
    return True


class ButtonReboot(ButtonEntity):
    "This class extend the ButtonEntity"

    @property
    def name(self):
        """Name of the entity."""
        return "Button Reboot"

    def press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("%s pressed", self.name)
        if self.hass.is_running:
            _LOGGER.info("Restarting HAss...")
            self.hass.services.call(domain="homeassistant", service="restart")
        else:
            _LOGGER.error("HAss is not running?!")
