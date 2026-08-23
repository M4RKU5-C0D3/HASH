"""Die Schulferien-Integration für Home Assistant.

Bereitet Schulferien pro Bundesland über die OpenHolidays API auf.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OpenHolidaysApiClient
from .const import DOMAIN
from .coordinator import SchulferienCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.CALENDAR, Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type SchulferienConfigEntry = ConfigEntry[SchulferienCoordinator]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Schulferien integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SchulferienConfigEntry) -> bool:
    """Richtet einen Config-Entry ein."""
    client = OpenHolidaysApiClient(async_get_clientsession(hass))
    coordinator = SchulferienCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SchulferienConfigEntry) -> bool:
    """Entlädt einen Config-Entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
