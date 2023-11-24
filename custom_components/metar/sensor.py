import logging
import string
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import core as ha_core
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity

from .const import *
from .core.coordinator import MetarCoordinator

SCAN_INTERVAL = timedelta(seconds=3600)
BASE_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/"

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_AIRPORT_NAME): cv.string,
    vol.Required(CONF_AIRPORT_CODE): cv.string,
    vol.Optional(CONF_TOKEN): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


def setup_platform(hass: ha_core.HomeAssistant, conf: dict, add_entities, discovery_info=None):
    _LOGGER.debug("Sensor Init config=%s discovery=%s", conf, discovery_info)
    if discovery_info is not None:
        config: dict = discovery_info["cfg"]
        dev = []

        for variable in config.get(CONF_MONITORED_CONDITIONS, ["temperature"]):
            dev.append(
                MetarSensorEntity(hass, str(config.get(CONF_AIRPORT_NAME)), str(config.get(CONF_AIRPORT_CODE)),
                                  variable, SENSOR_TYPES[variable][1]))
        add_entities(dev, True)


class MetarSensorEntity(Entity):
    _coordinator: MetarCoordinator

    def __init__(self, hass: ha_core.HomeAssistant, name: string, code: string, sensor_type,
                 temp_unit):
        self._state = None
        self._name = SENSOR_TYPES[sensor_type][0]
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._airport_name = name
        self.type = sensor_type
        self._hass = hass
        self._coordinator = hass.data[DOMAIN][COORDINATOR]
        self._code = code

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Metar " + self._airport_name + " " + self._name;

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    async def async_update(self):
        """Get the latest data from Metar and updates the states."""
        try:
            await self._coordinator.async_update()
        except Exception:
            _LOGGER.error("Error when retrieving update data")
            return

        if self._coordinator.get(self._code) is None:
            _LOGGER.info("METAR Data for %s is None", self._code)
            return

        try:
            if self.type == 'time':
                self._state = self._coordinator.get(self._code).time
            if self.type == 'temperature':
                self._state = self._coordinator.get(self._code).temp
                _LOGGER.info("METAR Temp=%s", self._state)
            elif self.type == 'weather':
                self._state = self._coordinator.get(self._code).weather
            elif self.type == 'wind':
                self._state = self._coordinator.get(self._code).wind
            elif self.type == 'pressure':
                self._state = self._coordinator.get(self._code).pressure
            elif self.type == 'visibility':
                self._state = self._coordinator.get(self._code).visibility
            # elif self.type == 'precipitation':
            # self._state = self.weather_data.sensor_data.precip_1hr.string("in")
            # self._unit_of_measurement = 'mm'
            elif self.type == 'sky':
                self._state = self._coordinator.get(self._code).sky
        except KeyError:
            self._state = None
            _LOGGER.warning(
                "Condition is currently not available: %s", self.type)
