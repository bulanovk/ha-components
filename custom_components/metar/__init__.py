import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import SENSOR_TYPES, DOMAIN, TOKEN_FIELD, CONF_AIRPORT_NAME, CONF_AIRPORT_CODE
from .sensor import MetarData, MetarSensor

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR
]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.state.setdefault(DOMAIN, {})
    hass.state[DOMAIN]["token"] = config[DOMAIN][TOKEN_FIELD]
    sensors = config[DOMAIN]["sensor"]
    for sensor in sensors:
        dev = []
        airport = {'location': str(sensor.get(CONF_AIRPORT_NAME)), 'code': str(sensor.get(CONF_AIRPORT_CODE))}
        data = MetarData(airport)
        await hass.config_entries.async_forward_entry_setups(config, PLATFORMS)
    return True
