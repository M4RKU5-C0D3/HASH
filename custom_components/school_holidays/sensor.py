"""Sensor for the next school holidays."""

from __future__ import annotations

from datetime import date

import homeassistant.util.dt as dt_util
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SchoolHolidaysConfigEntry
from .const import DOMAIN
from .coordinator import HolidayPeriod, SchoolHolidaysCoordinator


def _next_period(coordinator: SchoolHolidaysCoordinator, today: date) -> HolidayPeriod | None:
    """Return the running or next holiday period."""
    periods = coordinator.data or []
    for period in periods:
        if period.includes(today):
            return period
    return next((period for period in periods if period.start > today), None)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchoolHolidaysConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor."""
    coordinator = entry.runtime_data
    async_add_entities([NextSchoolHolidaysSensor(entry, coordinator, entry.title)])


class NextSchoolHolidaysSensor(
    CoordinatorEntity[SchoolHolidaysCoordinator], SensorEntity
):
    """Expose the next (or currently running) school holidays."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-star"

    def __init__(
        self,
        entry: SchoolHolidaysConfigEntry,
        coordinator: SchoolHolidaysCoordinator,
        state_name: str,
    ) -> None:
        super().__init__(coordinator, context=None)
        self._attr_unique_id = f"{entry.entry_id}_next"
        self._attr_name = "Next Holidays"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"School Holidays {state_name}",
            manufacturer="M4RKU5-C0D3",
            model="OpenHolidays API",
        )

    @property
    def native_value(self) -> str | None:
        """Name of the next or running holidays."""
        period = _next_period(self.coordinator, dt_util.now().date())
        return period.name if period else None

    @property
    def extra_state_attributes(self) -> dict:
        """Details about the next holidays."""
        today = dt_util.now().date()
        period = _next_period(self.coordinator, today)
        if period is None:
            return {}
        attrs = {
            "start": period.start.isoformat(),
            "end": period.end.isoformat(),
            "days_until_start": max(0, (period.start - today).days),
            "duration_days": period.duration_days,
        }
        if period.includes(today):
            attrs["days_remaining"] = (period.end - today).days + 1
        return attrs
