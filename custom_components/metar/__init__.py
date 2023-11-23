import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import core

from .const import METAR_TOKEN_FIELD, DOMAIN

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({
            vol.Required(METAR_TOKEN_FIELD): cv.string
        },
            extra=vol.ALLOW_EXTRA,
        )

    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Home Heat Calc component."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][METAR_TOKEN_FIELD] = config[DOMAIN][METAR_TOKEN_FIELD]
    for cfg in config[DOMAIN]["sensor"]:
      hass.async_create_task(hass.helpers.discovery.async_load_platform('sensor', DOMAIN, {"cfg":cfg}, config))
    return True
