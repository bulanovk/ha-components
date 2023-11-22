from homeassistant import core
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up The metar component."""
    # @TODO: Add setup code.
    _LOGGER.info("KOBU Config %s", config)
    return True
