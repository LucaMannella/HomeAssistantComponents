""" Platform for generating and exposing a MUD file. """
from __future__ import annotations
import voluptuous as vol
import logging
from pprint import pformat

import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.button import ButtonEntity

from .mud_generator import MUDGenerator


# Validation of the user's configuration
PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string
})

_LOGGER = logging.getLogger("mud_generator_button")

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """ Set up the MUD Generator platform. """
    _LOGGER.info(pformat(config))

    params = {CONF_NAME: "MUD Generator"} #config[CONF_NAME]}

    add_entities([MUDGeneratorButton(params)])
    return True


class MUDGeneratorButton(ButtonEntity):
    """ This button can recreate and expose the MUD file. """

    def __init__(self, params):
        self._name = params[CONF_NAME]
        _LOGGER.info('Creating %s', self._name)

        self._mud_gen = MUDGenerator()
        self._mud_gen.generate_mud_file()
        self._mud_gen.expose_mud_file()

    def press(self) -> None:
        # ToDo: necessary to implement a mechanism for not joining same MUD files
        # self._mud_gen.generate_mud_file()
        # self._mud_gen.print_mud_draft()
        self._mud_gen.expose_mud_file()
