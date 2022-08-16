"""
The "hello world" custom component.
This component implements the bare minimum that a component should implement.

Configuration:
To use the hello_world component you will need to add the following line into your configuration.yaml file

hello_world:
"""
from __future__ import annotations
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
_LOGGER = logging.getLogger(__name__)

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "hello_world"


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up a skeleton component."""
    # States are in the format DOMAIN.OBJECT_ID.
    hass.states.set(DOMAIN + ".Hello_World", "Works!")
    _LOGGER.info("I'm the component: " + DOMAIN)

    # Return boolean to indicate that initialization was successfully.
    return True
