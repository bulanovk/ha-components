from homeassistant import core
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from .const import METAR_TOKEN_FIELD, DOMAIN
from homeassistant.config_entries import ConfigEntry

METAR_SCHEMA = vol.Schema(
    {vol.Required(METAR_TOKEN_FIELD): cv.string}
)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional("metar"): vol.All(cv.Any, METAR_SCHEMA)
    }
)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Home Heat Calc component."""
    hass.data.setdefault(DOMAIN, {})
    hass.data["metar"][METAR_TOKEN_FIELD] = config[DOMAIN]["metar"][METAR_TOKEN_FIELD]
    entry: ConfigEntry = ConfigEntry()
    entry.title = "Metar Sensor"
    entry.data = {"code": "UWWW", "name": "KUF"}
    await hass.config_entries.async_forward_entry_setups(entry, "sensor")
    return True
