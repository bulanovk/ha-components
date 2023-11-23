import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import core
from homeassistant.config_entries import ConfigEntry

from .const import METAR_TOKEN_FIELD, DOMAIN

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({
            vol.Required(METAR_TOKEN_FIELD): cv.string
        })
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Home Heat Calc component."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][METAR_TOKEN_FIELD] = config[DOMAIN][METAR_TOKEN_FIELD]
    entry: ConfigEntry = ConfigEntry()
    entry.title = "Metar Sensor"
    entry.data = {"code": "UWWW", "name": "KUF"}
    await hass.config_entries.async_forward_entry_setups(entry, "sensor")
    return True
