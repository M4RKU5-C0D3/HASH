"""Sensor für die nächsten Schulferien."""

from __future__ import annotations

from datetime import date

import homeassistant.util.dt as dt_util
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SchulferienConfigEntry
from .const import DOMAIN
from .coordinator import HolidayPeriod, SchulferienCoordinator


def _next_period(coordinator: SchulferienCoordinator, today: date) -> HolidayPeriod | None:
    """Liefert die laufenden oder nächsten Ferien."""
    periods = coordinator.data or []
    for period in periods:
        if period.includes(today):
            return period
    return next((period for period in periods if period.start > today), None)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchulferienConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richtet den Sensor ein."""
    coordinator = entry.runtime_data
    async_add_entities([NaechsteSchulferienSensor(entry, coordinator, entry.title)])


class NaechsteSchulferienSensor(
    CoordinatorEntity[SchulferienCoordinator], SensorEntity
):
    """Zeigt die nächsten (oder laufenden) Schulferien."""

    _attr_has_entity_name = False
    _attr_icon = "mdi:calendar-star"

    def __init__(
        self,
        entry: SchulferienConfigEntry,
        coordinator: SchulferienCoordinator,
        state_name: str,
    ) -> None:
        super().__init__(coordinator, context=None)
        self._attr_unique_id = f"{entry.entry_id}_next"
        self._attr_name = f"Next School Holidays {state_name}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"School Holidays {state_name}",
            manufacturer="M4RKU5-C0D3",
            model="OpenHolidays API",
        )

    @property
    def native_value(self) -> str | None:
        """Name der nächsten bzw. laufenden Ferien."""
        period = _next_period(self.coordinator, dt_util.now().date())
        return period.name if period else None

    @property
    def extra_state_attributes(self) -> dict:
        """Details zu den nächsten Ferien."""
        today = dt_util.now().date()
        period = _next_period(self.coordinator, today)
        if period is None:
            return {}
        return {
            "start": period.start.isoformat(),
            "end": period.end.isoformat(),
            "days_until_start": max(0, (period.start - today).days),
            "duration_days": period.duration_days,
        }
