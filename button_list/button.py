from __future__ import annotations
from typing import Final
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.button import ButtonEntity

NAME_KEY = "name"
MUD_ONLY_KEY = "mud_only"

DEFAULT_NAME = "Button List"
UNIQUE_ID_PREFIX = "PoliTo.e-Lite.LM."

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the button."""

    if NAME_KEY in config:
        name = config[NAME_KEY]
    else:
        name = DEFAULT_NAME
    if MUD_ONLY_KEY in config:
        mud_only = MUD_ONLY_KEY
    else:
        mud_only = False

    add_entities([ButtonList(name, mud_only)])
    return True


class ButtonList(ButtonEntity):
    "This button prints on the console some information about Home Assistant's status."

    def __init__(self, name: str = DEFAULT_NAME, mud_only: bool = False):
        """Initialize the button."""
        self._name = name
        self._unique_id = UNIQUE_ID_PREFIX + self._name
        self._mud_only = mud_only
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

        _LOGGER.debug("<%s> pressed", self.name)
        if not self.hass:
            _LOGGER.warning("<hass> object not available now!")
            return

        if self._mud_only:
            self.print_manifests_with_mud_snippet()
        else:
            self.print_manifests()
        _LOGGER.info("\n\n\n")

        self.print_hass_info(True, True, True)
        _LOGGER.info("\n\n\n")

    def print_manifests(self):
        """This method prints on the console all the integrations' manifests."""
        integrations = self.hass.data["integrations"]
        for key, value in integrations.items():
            _LOGGER.info("%s --- %s", key, value)
            for m_key, m_value in value.manifest.items():
                _LOGGER.info("%s: %s", m_key, m_value)
            _LOGGER.info("\n\n")

    def print_manifests_with_mud_snippet(self):
        """This method prints on the console the manifests of all the integrations with a specified MUD snippet."""
        integrations = self.hass.data["integrations"]
        for key, value in integrations.items():
            _LOGGER.debug("%s --- %s", key, value)

            manifest = value.manifest
            if "mud_file" in manifest:
                for m_key, m_value in manifest.items():
                    _LOGGER.info("%s: %s", m_key, m_value)

                mud_path = manifest["mud_file"]
                if mud_path.lower().startswith("http"):
                    _LOGGER.warning("This MUD is remotely stored!")
                else:
                    _LOGGER.info("This is a local MUD snippet!")

    def print_hass_info(
        self, integrations: bool = False, entities: bool = False, services: bool = False
    ):
        """This method reads some values from other integrations."""

        if integrations:
            # Vengono listate tutte i componenti disponibili
            _LOGGER.info("\nList of available components:")
            for comp in self.hass.config.components:
                _LOGGER.info(comp)
            _LOGGER.info("\n\n")

        # Per listare le entità disponibili (istanze dei componenti)
        if entities:
            n_entities = self.hass.states.async_entity_ids_count()
            _LOGGER.info("\nNumber of available entities: <%d>\n", n_entities)
            for ent in self.hass.states.all():
                # To print only some entitites
                # if "switch" in ent.object_id or "light" in ent.object_id:
                _LOGGER.info(ent)
            _LOGGER.info("\n\n")

        if services:
            services = self.hass.services.services
            _LOGGER.info("\nList of available services:")
            for x, domain in services.items():
                _LOGGER.info("--- %s ---", x)
                for s in domain:
                    _LOGGER.info(s)
