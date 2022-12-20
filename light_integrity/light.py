"""Platform for integrating a LightIntegrity."""
from __future__ import annotations
from typing import Any, Final
import logging
import os
from pathlib import Path

# Import the device class from the component that you want to support
from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity
from homeassistant.const import CONF_PLATFORM, Platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.config import YAML_CONFIG_FILE, load_yaml_config_file
from homeassistant.util.yaml.loader import JSON_TYPE, Secrets

NAME_KEY = "name"
DEFAULT_NAME = "Light Integrity"
SWITCH_FILE_PLATFORM = "switch_file"

FILE_PATH_KEY = "file_path"


_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Adding the LightIntegrity to Home Assistant."""

    if NAME_KEY in config:
        name = config[NAME_KEY]
    else:
        name = DEFAULT_NAME

    add_entities([LightIntegrity(name)])
    return True


class LightIntegrity(LightEntity):
    """A Light able to alter other components' integrity."""

    _target: Final[str] = "switch.switch_target"
    _target_name: Final[str] = "Switch Target"

    def __init__(self, name: str = DEFAULT_NAME) -> None:
        """Initialize a LightIntegrity."""
        self._name = name
        self._brightness = None
        self._state = False

        # This object should physically communicate with the light
        self._light = LightEntity()

        _LOGGER.info("<%s> was created", self._name)

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
        self.toggle_switch()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._brightness = 0
        self._state = False
        self.toggle_switch()

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        # self._state = self._light.is_on()
        # self._brightness = self._light.brightness
        return

    def toggle_switch(self) -> bool:
        """This method toggles the state of all the switch_file."""

        conf_file = self.load_yaml_config()
        if conf_file:
            try:
                for switch_i in conf_file[Platform.SWITCH]:
                    if (
                        CONF_PLATFORM in switch_i
                        and switch_i[CONF_PLATFORM] == SWITCH_FILE_PLATFORM
                        and FILE_PATH_KEY in switch_i
                    ):
                        file = switch_i[FILE_PATH_KEY]
                        if os.path.isfile(file):
                            os.remove(file)
                        else:
                            open(file, "ab").close()
                return True
            except KeyError as key_err:
                _LOGGER.error(
                    "<%s> is not available in <%s>!", key_err, YAML_CONFIG_FILE
                )
        return False

    def load_yaml_config(self) -> JSON_TYPE:
        """This method returns the Home Assistant configuration file in JSON object."""
        config_dir = self.hass.config.config_dir
        config_filename = self.hass.config.path(YAML_CONFIG_FILE)

        secrets = Secrets(Path(config_dir))
        conf_file = load_yaml_config_file(config_filename, secrets)
        return conf_file

    def generating_file_path(self, integration: dict) -> str:
        """This methods generates a custom_component path given an integration dict."""
        # Currently it is not used
        integration_name = integration[CONF_PLATFORM]
        integration_filename = integration[FILE_PATH_KEY]
        integration_filepath = integration_name + "/" + integration_filename
        path = self.hass.config.path("custom_components/" + integration_filepath)
        return path
