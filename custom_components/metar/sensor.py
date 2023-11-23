import logging
import string
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import core
from homeassistant.const import CONF_MONITORED_CONDITIONS
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen
from metar import Metar

from .const import SENSOR_TYPES, CONF_AIRPORT_NAME, TOKEN_FIELD, CONF_AIRPORT_CODE

SCAN_INTERVAL = timedelta(seconds=3600)
BASE_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/"

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_AIRPORT_NAME): cv.string,
    vol.Required(CONF_AIRPORT_CODE): cv.string,
    vol.Optional(TOKEN_FIELD): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


async def async_setup_platform(hass: core.HomeAssistant, conf: dict, add_entities, discovery_info=None):
    _LOGGER.debug("Sensor Init config=%s discovery=%s", conf, discovery_info)
    if discovery_info is not None:
        config: dict = discovery_info["cfg"]
        data: MetarData = MetarData(str(config.get(CONF_AIRPORT_CODE)))
        await data.update
        dev = []

        for variable in config.get(CONF_MONITORED_CONDITIONS, ["temperature"]):
            dev.append(MetarSensorEntity(str(config.get(CONF_AIRPORT_NAME)), data, variable, SENSOR_TYPES[variable][1]))
        add_entities(dev, True)


class MetarData:
    def __init__(self, airport_code: string):
        """Initialize the data object."""
        self._airport_code = airport_code
        self.sensor_data = None
        # await self.update()

    @Throttle(SCAN_INTERVAL)
    async def update(self):
        url = BASE_URL + self._airport_code + ".TXT"
        try:
            urlh = urlopen(url)
            report = ''
            for line in urlh:
                if not isinstance(line, str):
                    line = line.decode()
                if line.startswith(self._airport_code):
                    report = line.strip()
                    self.sensor_data = Metar.Metar(line)
                    _LOGGER.info("METAR %s", self.sensor_data.string())
                    break
            if not report:
                _LOGGER.error("No data for %s\n\n", self._airport_code)
        except Metar.ParserError as exc:
            _LOGGER.error("METAR code: %s", line)
            _LOGGER.error(string.join(exc.args, ", ") + "\n", )
        except:
            import traceback
            _LOGGER.error(traceback.format_exc())
            _LOGGER.error("Error retrieving %s data \n", self._airport_code)


class MetarSensorEntity(Entity):

    def __init__(self, name: string, weather_data: MetarData, sensor_type, temp_unit):
        self._state = None
        self._name = SENSOR_TYPES[sensor_type][0]
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._airport_name = name
        self.type = sensor_type
        self.weather_data = weather_data

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Metar " + self._airport_name + " " + self._name;
        # return self._name + " " + self._airport_name;

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    async def async_update(self):
        self._update()

    def _update(self):
        """Get the latest data from Metar and updates the states."""

        try:
            self.weather_data.update()
        except URLCallError:
            _LOGGER.error("Error when retrieving update data")
            return

        if self.weather_data is None:
            return

        try:
            if self.type == 'time':
                self._state = self.weather_data.sensor_data.time.ctime()
            if self.type == 'temperature':
                degree = self.weather_data.sensor_data.temp.string().split(" ")
                self._state = degree[0]
            elif self.type == 'weather':
                self._state = self.weather_data.sensor_data.present_weather()
            elif self.type == 'wind':
                self._state = self.weather_data.sensor_data.wind()
            elif self.type == 'pressure':
                self._state = self.weather_data.sensor_data.press.string("mb")
            elif self.type == 'visibility':
                self._state = self.weather_data.sensor_data.visibility()
                self._unit_of_measurement = 'm'
            # elif self.type == 'precipitation':
            # self._state = self.weather_data.sensor_data.precip_1hr.string("in")
            # self._unit_of_measurement = 'mm'
            elif self.type == 'sky':
                self._state = self.weather_data.sensor_data.sky_conditions("\n     ")
        except KeyError:
            self._state = None
            _LOGGER.warning(
                "Condition is currently not available: %s", self.type)
