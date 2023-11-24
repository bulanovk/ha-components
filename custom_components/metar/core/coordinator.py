import datetime
import logging
import string
from datetime import timedelta

import httpx
from homeassistant import core as ha_core
from homeassistant.util import Throttle

from ..const import *

SCAN_INTERVAL = timedelta(seconds=300)

_LOGGER = logging.getLogger(__name__)


class MetarAirport:
    name: string
    temp: string
    time: string
    weather: string
    wind: string
    pressure: string
    visibility: string
    sky: string


class MetarCoordinator:
    def __init__(self, haas: ha_core.HomeAssistant):
        self._haas = haas
        self.sensors_data = None
        self._codes = []

    def get(self, code: string) -> MetarAirport:
        return self.sensors_data.get(code)

    def add_code(self, code: string):
        self._codes.append(code)

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        token = self._haas.data[DOMAIN][CONF_TOKEN]
        code = ",".join(self._codes)
        url = f'https://api.checkwx.com/metar/{code}/decoded?x-api-key={token}'
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            data = resp.json()
            for airport in data['data']:
                data: MetarAirport = MetarAirport()
                data.temp = airport['temperature']['celsius']
                data.name = airport['icao']
                data.time = airport['observed']
                data.weather = airport['conditions']['text']
                self.sensors_data[data.name] = data
