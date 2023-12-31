from homeassistant.const import CONF_MONITORED_CONDITIONS
from homeassistant.const import CONF_SCAN_INTERVAL

SENSOR_TYPES = {
    'time': ['Updated ', None],
    'weather': ['Condition', None],
    'temperature': ['Temperature', 'C'],
    'wind': ['Wind speed', None],
    'pressure': ['Pressure', None],
    'visibility': ['Visibility', None],
    'precipitation': ['Precipitation', None],
    'sky': ['Sky', None],
}
DOMAIN = "metar"
CONF_AIRPORT_NAME = 'name'
CONF_AIRPORT_CODE = 'code'
CONF_TOKEN = "token"
COORDINATOR = "coordinator"
