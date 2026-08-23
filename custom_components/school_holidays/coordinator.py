"""DataUpdateCoordinator for the school holidays integration."""

from __future__ import annotations

from datetime import date, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .api import HolidayPeriod, OpenHolidaysApiClient, OpenHolidaysApiError
from .const import CONF_SUBDIVISION, DOMAIN, LOOKAHEAD_DAYS, LOOKBACK_DAYS, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SchoolHolidaysCoordinator(DataUpdateCoordinator[list[HolidayPeriod]]):
    """Coordinate holiday data for a single federal state."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: OpenHolidaysApiClient,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.data[CONF_SUBDIVISION]}",
            update_interval=UPDATE_INTERVAL,
            config_entry=entry,
        )
        self.entry = entry
        self.client = client

    @property
    def subdivision_code(self) -> str:
        """The configured subdivision code, e.g. DE-NI."""
        return self.entry.data[CONF_SUBDIVISION]

    async def _async_update_data(self) -> list[HolidayPeriod]:
        today: date = dt_util.now().date()
        valid_from = today - timedelta(days=LOOKBACK_DAYS)
        valid_to = today + timedelta(days=LOOKAHEAD_DAYS)
        try:
            return await self.client.async_get_school_holidays(
                self.subdivision_code, valid_from, valid_to
            )
        except OpenHolidaysApiError as err:
            raise UpdateFailed(str(err)) from err
