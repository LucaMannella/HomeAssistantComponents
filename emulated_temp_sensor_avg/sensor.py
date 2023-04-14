"""Platform for sensor integration."""
from __future__ import annotations
from typing import Final
from random import randint
from datetime import datetime
import logging

from homeassistant.components.sensor import SensorEntity, DOMAIN as SENSOR_DOMAIN
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

NAME_KEY = "name"
MIN_TEMP_KEY = "min_temp"
MAX_TEMP_KEY = "max_temp"

DEFAULT_NAME = "Emulated Temperature Sensor Avg"
UNIQUE_ID_PREFIX = "PoliTo.eLite.LM."

""" To work properly this integration needs to have a configured "scan_interval".
    Every x seconds the update() function is called updating the emulated temperature.

    sensor:
    - platform: emulated_temp_sensor_simple
      scan_interval: 300
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

    if (MIN_TEMP_KEY in config) and (MAX_TEMP_KEY in config):
        add_entities(
            [EmulatedTempSensorAvg(name, config[MIN_TEMP_KEY], config[MAX_TEMP_KEY])]
        )
    elif MIN_TEMP_KEY in config:
        add_entities([EmulatedTempSensorAvg(name, min_temp=config[MIN_TEMP_KEY])])
    elif MAX_TEMP_KEY in config:
        add_entities([EmulatedTempSensorAvg(name, max_temp=config[MAX_TEMP_KEY])])
    else:
        add_entities([EmulatedTempSensorAvg(name)])


class EmulatedTempSensorAvg(SensorEntity):
    """Representation of a Sensor. Extends Restore Entity to retrieve last temperature value."""

    def __init__(
        self, name=DEFAULT_NAME, min_temp: int = 18, max_temp: int = 25
    ) -> None:
        """Initialize the sensor."""
        self._sensor_name = name
        self._unique_id = UNIQUE_ID_PREFIX + SENSOR_DOMAIN + "." + DOMAIN
        self._MIN_TMP: Final[int] = min_temp
        self._MAX_TMP: Final[int] = max_temp
        self._state = self.compute_random_temp()
        _LOGGER.info("Initial temperature: %s", str(self._state))
        self.append_last_temperature(self._state)

    def compute_random_temp(self) -> float:
        """This method computes a random initial state."""
        integer = randint(self._MIN_TMP, self._MAX_TMP - 1)
        mantissa = randint(0, 9)
        return float(str(integer) + "." + str(mantissa))

    def append_last_temperature(self, temperature: float) -> None:
        """This method appends the current state to the consumption file"""
        with open("./temperatures.txt", "a+", encoding="utf-8") as temperature_file:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text_to_write = f"{current_time}: {temperature:.2f}\n"
            temperature_file.write(text_to_write)

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

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        new_temp = self.compute_random_temp()
        _LOGGER.debug("New temp: %.2f", new_temp)
        self.append_last_temperature(new_temp)
        self._state = self.compute_avg()

    def compute_avg(self) -> float:
        """This method computes the average temperature."""
        lines = 0
        overall = 0
        with open("./temperatures.txt", "r", encoding="utf-8") as temperature_file:
            line = temperature_file.readline()
            while line:
                value = float(line.split()[2])
                overall += value
                lines += 1
                line = temperature_file.readline()
        if lines > 0:
            average = overall / lines
        else:
            average = 0
        return round(average, 2)
