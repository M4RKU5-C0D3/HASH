"""The school holidays integration for Home Assistant.

Provides school holidays per German federal state via the OpenHolidays API.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OpenHolidaysApiClient
from .const import DOMAIN
from .coordinator import SchoolHolidaysCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.CALENDAR, Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type SchoolHolidaysConfigEntry = ConfigEntry[SchoolHolidaysCoordinator]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the School Holidays integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SchoolHolidaysConfigEntry) -> bool:
    """Set up a config entry."""
    client = OpenHolidaysApiClient(async_get_clientsession(hass))
    coordinator = SchoolHolidaysCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SchoolHolidaysConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
