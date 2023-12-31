import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import core as ha_core

from .const import *
from .core.coordinator import MetarCoordinator
from .core.coordinator import SCAN_INTERVAL

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_AIRPORT_CODE): cv.string,
        vol.Required(CONF_AIRPORT_NAME): cv.string,
        vol.Optional(CONF_MONITORED_CONDITIONS, None, ["temperature"]): cv.ensure_list_csv(cv.string),
    }, extra=vol.ALLOW_EXTRA
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({
            vol.Required(CONF_TOKEN): cv.string,
            vol.Required(CONF_SCAN_INTERVAL): cv.string,
            vol.Required("sensor"): cv.ensure_list_csv(SENSOR_SCHEMA),
        },
            extra=vol.ALLOW_EXTRA,
        )

    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: ha_core.HomeAssistant, config: dict) -> bool:
    """Set up the Home Heat Calc component."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][CONF_TOKEN] = config[DOMAIN][CONF_TOKEN]
    coordinator: MetarCoordinator = MetarCoordinator(hass)
    hass.data[DOMAIN][COORDINATOR] = coordinator
    for cfg in config[DOMAIN]["sensor"]:
        coordinator.add_code(cfg[CONF_AIRPORT_CODE])
    await coordinator.async_update()
    for cfg in config[DOMAIN]["sensor"]:
        hass.async_create_task(
            hass.helpers.discovery.async_load_platform('sensor', DOMAIN, {"cfg": cfg}, config))
    return True
