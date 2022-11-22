"""Platform for sensor integration."""
from __future__ import annotations
from typing import Final
from random import randint
import logging
import requests

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

MIN_TEMP_KEY = "min_temp"
MAX_TEMP_KEY = "max_temp"
NAME_KEY = "name"
URL_KEY = "url"
DEFAULT_NAME = "Emulated Remote Temperature Sensor"
DOMAIN = "emulated_temp_sensor"
DEFAULT_MIN_TEMP = 18
DEFAULT_MAX_TEMP = 30
GET_LAST_TEMP_URL = "/api/temperatures/last"
POST_LAST_TEMP_URL = "/api/temperatures"


# Work but does not support scan_interval
# PLATFORM_SCHEMA = vol.Schema(
#    {
#        vol.Required(CONF_PLATFORM): DOMAIN,
#        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
#        vol.Optional(MIN_TEMP_KEY, default=18): cv.positive_int,
#        vol.Optional(MAX_TEMP_KEY, default=25): cv.positive_int,
#    },
#    extra=vol.ALLOW_EXTRA,
# )

""" To work properly this integration needs to have a configured "scan_interval".
    Every x seconds the update() function is called updating the emulated temperature.

    sensor:
    - platform: emulated_temp_sensor
      scan_interval: 300  // number of seconds that will trigger an update
      url: localhost      // "host.docker.internal" if the integration is running in a container
"""
_LOGGER = logging.getLogger(__name__)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    if NAME_KEY in config:
        name = config[NAME_KEY]
    else:
        name = DEFAULT_NAME
    if MIN_TEMP_KEY in config:
        min_temp = config[MIN_TEMP_KEY]
    else:
        min_temp = DEFAULT_MIN_TEMP
    if MAX_TEMP_KEY in config:
        max_temp=config[MAX_TEMP_KEY]
    else:
        max_temp=DEFAULT_MAX_TEMP
    if URL_KEY in config:
        url = config[URL_KEY]
    else:
        url = "localhost"

    add_entities([EmulatedRemoteTempSensor(name=name, min_temp=min_temp, max_temp=max_temp, url=url)])


class EmulatedRemoteTempSensor(SensorEntity):
    """Representation of a Sensor. Extends Restore Entity to retrieve last temperature value."""

    def __init__(
        self, name:str=DEFAULT_NAME, min_temp:int=DEFAULT_MIN_TEMP, max_temp:int=DEFAULT_MAX_TEMP, url:str="localhost"
    ) -> None:
        """Initialize the sensor."""
        self._sensor_name = name
        self._unique_id = "PoliTo.e-Lite.LM."+self._sensor_name
        self._MIN_TMP: Final[int] = min_temp
        self._MAX_TMP: Final[int] = max_temp
        self._url = url
        last_temp = self.get_last_temperature()
        if last_temp:
            self._state = last_temp
        else:
            _LOGGER.critical("Error retriving last temperature from remote server! Temperature randomly generated!")
            self._state = self.random_temp()
        _LOGGER.debug("Initial temperature value: %.2f", self._state)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._sensor_name

    @property
    def unique_id(self) -> str | None:
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def get_last_temperature(self) -> float | None:
        url = self._url+GET_LAST_TEMP_URL
        response = requests.get(url, allow_redirects=True)
        if response.status_code != 200:
            _LOGGER.error("Impossible to retrieve temperature!")
            return None
        else:
            try:
                value = response.json()
                if value and value["value"]:
                    return value["value"]
                else:
                    return None
            except Exception as ex:
                _LOGGER.error("Error parsing json object: %s", ex)
                return None

    def post_last_temperature(self) -> bool:
        url = self._url+POST_LAST_TEMP_URL
        response = requests.post(url, json={"value": self._state})
        if response.status_code == 200:
            return True
        else:
            _LOGGER.error("Error storing temperature: %s", response.json()["error"])
            return False

    def random_temp(self) -> float:
        integer = randint(self._MIN_TMP, self._MAX_TMP - 1)
        mantissa = randint(0, 9)
        temp = float(str(integer) + "." + str(mantissa))
        return temp

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        # Emulating a call to a remote server
        # self._remote_server_call()

        diff = float("0." + str(randint(0, 9)))
        case = randint(0, 2)
        if case == 0:
            pass
        elif case == 1:
            self._state = self._state - diff
        elif case == 2:
            self._state = self._state + diff

        if self.post_last_temperature():
            _LOGGER.debug("Temperature succesfully updated (%.2f)", self._state)
        else:
            _LOGGER.error("Impossible to store temperature on remote server: <%s>", self._url)
