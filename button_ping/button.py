from __future__ import annotations
from typing import Final
import time
import logging
from icmplib import ping

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.button import ButtonEntity


_LOGGER = logging.getLogger(__name__)

WAITING_TIME_KEY = "waiting_time"
PING_NUMBER_KEY = "ping_number"
DOMAINS_KEY = "urls"
DEFAULT_WAITING_TIME = 60
DEFAULT_PING_NUMBER = 1
DEFAULT_DOMAINS = ["homeassistant.io"]

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the button."""

    urls = DEFAULT_DOMAINS
    if DOMAINS_KEY in config:
        urls = config[DOMAINS_KEY]

    waiting_time = DEFAULT_WAITING_TIME
    if WAITING_TIME_KEY in config:
        waiting_time = config[WAITING_TIME_KEY]

    ping_number = DEFAULT_PING_NUMBER
    if PING_NUMBER_KEY in config:
        ping_number = config[PING_NUMBER_KEY]

    add_entities([ButtonPing(urls, waiting_time, ping_number)])

    # To indicate that initialization was successfully.
    return True


class ButtonPing(ButtonEntity):
    "When the button is pressed, it starts pinging the specified domains"

    def __init__(self, urls, waiting_time=DEFAULT_WAITING_TIME, ping_number=DEFAULT_PING_NUMBER):
        """Initialize the button."""
        self._name = "Button Ping"
        self._urls: Final[list[str]] = urls
        self._waiting_time: Final[float] = waiting_time
        self._ping_number: Final[float] = ping_number

        _LOGGER.debug("List of domains: {}".format('; '.join(map(str, self._urls))))
        _LOGGER.debug("Numer of pings per domain: %d - waiting time among pings: %d seconds", self._ping_number, self._waiting_time)

    @property
    def name(self):
        """Name of the entity."""
        return self._name

    def press(self) -> None:
        """Handle the button press."""

        _LOGGER.info("Start pinging")

        for _ in range(self._ping_number):
            for url in self._urls:
                _LOGGER.debug("Pinging %s", url)
                host = ping(url)
                if host.is_alive:
                    _LOGGER.debug("Average Ping RTT: %d ms", host.avg_rtt)
                else:
                    _LOGGER.debug("Host unreachable")
                time.sleep(self._waiting_time)

        _LOGGER.info("Pings completed")

    # async def async_press(self) -> None:
    #    """Handle the button press."""
