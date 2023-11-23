import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import core

from .const import *

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_AIRPORT_CODE): cv.string,
        vol.Required(CONF_AIRPORT_NAME): cv.string,

    }, extra=vol.ALLOW_EXTRA
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({
            vol.Required(METAR_TOKEN_FIELD): cv.string,
            vol.Required("sensor"): cv.ensure_list_csv(SENSOR_SCHEMA),
            vol.Optional(CONF_MONITORED_CONDITIONS, None, ["temperature"]): cv.ensure_list_csv(cv.string),
        },
            extra=vol.ALLOW_EXTRA,
        )

    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Home Heat Calc component."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][METAR_TOKEN_FIELD] = config[DOMAIN][METAR_TOKEN_FIELD]
    for cfg in config[DOMAIN]["sensor"]:
        hass.helpers.discovery.load_platform('sensor', DOMAIN, {"cfg": cfg}, config)
    return True
