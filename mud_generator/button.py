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
from . import constants


# Validation of the user's configuration
PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Optional(constants.INTERFACE_KEY): cv.string,
    vol.Optional(constants.DEPLOY_KEY): cv.string
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

    if CONF_NAME not in config.keys():
        params = {CONF_NAME: "Regenerate MUD"}
    else:
        params = {CONF_NAME: config[CONF_NAME]}

    if constants.INTERFACE_KEY not in config.keys():
        params[constants.INTERFACE_KEY] = "eth0"
    else:
        params[constants.INTERFACE_KEY] = config[constants.INTERFACE_KEY]

    if constants.DEPLOY_KEY not in config.keys():
        params[constants.DEPLOY_KEY] = constants.DEPLOY_CORE
    else:
        params[constants.DEPLOY_KEY] = config[constants.DEPLOY_KEY]

    add_entities([MUDGeneratorButton(params)])
    return True


class MUDGeneratorButton(ButtonEntity):
    """ This button can recreate and expose the MUD file. """

    def __init__(self, params):
        self._name = params[CONF_NAME]
        _LOGGER.info('Creating %s', self._name)
        self._unique_id = "PoliTo.e-Lite.LM."+"MUD-generator"
        _LOGGER.debug("Unique ID: <%s>", self._unique_id)
        self._interface = params[constants.INTERFACE_KEY]
        _LOGGER.info('Interface to use <%s>', self._interface)

        self._mud_gen = MUDGenerator(params[constants.DEPLOY_KEY])
        self._mud_gen.generate_mud_file()
        self._mud_gen.expose_mud_file(self._interface)

    @property
    def name(self):
        """Name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str | None:
        return self._unique_id

    def press(self) -> None:
        # ToDo: necessary to implement a mechanism for not joining same MUD files
        if not self.hass:
            _LOGGER.warning("Variable <hass> is not accessible now!")
            self._mud_gen.generate_mud_file()
        else:
            self._mud_gen.generate_mud_file(self.hass.data["integrations"])
        # self._mud_gen.print_mud_draft()
        self._mud_gen.expose_mud_file(self._interface)
