from __future__ import annotations
from typing import Final
import time
import logging

from homeassistant.core import HomeAssistant
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

    add_entities([ButtonTest()])
    return True


class ButtonTest(ButtonEntity):
    "When the button is pressed, it starts pinging the specified domains"

    def __init__(self):
        """Initialize the button."""
        self._name = "Button Test"
        self._unique_id = "PoliTo.e-Lite.LM."+self._name
        self.press()  # self.hass not available during init

    @property
    def name(self):
        """Name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str | None:
        return self._unique_id

    def press(self) -> None:
        """Handle the button press."""

        _LOGGER.debug("%s pressed", self.name)
        if not self.hass:
            _LOGGER.warning("<hass> object not available now!")
            return

        integrations = self.hass.data["integrations"]
        for key, value in integrations.items():
            _LOGGER.debug("%s --- %s", key, value)

            manifest = value.manifest
            if "mud_file" in manifest:
                mud_path = manifest["mud_file"]
                if mud_path.lower().startswith("http"):
                    _LOGGER.warning("This MUD is remotely stored!")
                else:
                    _LOGGER.warning("This is a local MUD snippet!")

                for m_key, m_value in manifest.items():
                    _LOGGER.info("%s: %s", m_key, m_value)


