"""Platform for sensor integration."""
from __future__ import annotations
from typing import Final
from random import randint

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.restore_state import (
    RestoreEntity,
)  # To restore last stored value

MIN_TEMP_KEY = "min_temp"
MAX_TEMP_KEY = "max_temp"
DOMAIN = "emulated_temp_sensor"
DEFAULT_NAME = "Emulated Temperature Sensor"


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    if "name" in config:
        name = config["name"]
    else:
        name = DEFAULT_NAME

    if (MIN_TEMP_KEY in config) and (MAX_TEMP_KEY in config):
        add_entities(
            [EmulatedTempSensor(name, config[MIN_TEMP_KEY], config[MAX_TEMP_KEY])]
        )
    elif MIN_TEMP_KEY in config:
        add_entities([EmulatedTempSensor(name, min_temp=config[MIN_TEMP_KEY])])
    elif MAX_TEMP_KEY in config:
        add_entities([EmulatedTempSensor(name, max_temp=config[MAX_TEMP_KEY])])
    else:
        add_entities([EmulatedTempSensor(name)])


class EmulatedTempSensor(SensorEntity, RestoreEntity):
    """Representation of a Sensor. Extends Restore Entity to retrieve last temperature value."""

    def __init__(
        self, name=DEFAULT_NAME, min_temp: int = 18, max_temp: int = 25
    ) -> None:
        """Initialize the sensor."""
        self._sensor_name = name
        self._MIN_TMP: Final[int] = min_temp
        self._MAX_TMP: Final[int] = max_temp

    async def async_added_to_hass(self):
        """Call when entity about to be added to hass."""

        # Retrieving last temperature value (if available)
        last_state = await self.async_get_last_state()
        if last_state:
            self._state = float(last_state.state)
        else:  # Creating a random starting value
            integer = randint(self._MIN_TMP, self._MAX_TMP - 1)
            mantissa = randint(0, 9)
            self._state = float(str(integer) + "." + str(mantissa))

        print(self._sensor_name + " - initial temperature: " + str(self._state))

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._sensor_name

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
        diff = float("0." + str(randint(0, 9)))
        x = randint(0, 2)
        if x == 0:
            pass
        elif x == 1:
            self._state = self._state - diff
        elif x == 2:
            self._state = self._state + diff
