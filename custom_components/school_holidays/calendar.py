"""Calendar entity exposing all school holiday periods."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import UndefinedType
from homeassistant.util import dt as dt_util
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SchoolHolidaysConfigEntry
from .const import DOMAIN
from .coordinator import HolidayPeriod, SchoolHolidaysCoordinator


def _as_calendar_event(period: HolidayPeriod) -> CalendarEvent:
    """Convert a holiday period into a calendar event (exclusive end)."""
    return CalendarEvent(
        start=period.start,
        end=period.end + timedelta(days=1),
        summary=period.name,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchoolHolidaysConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calendar entity."""
    coordinator = entry.runtime_data
    async_add_entities([SchoolHolidaysCalendarEntity(entry, coordinator, entry.title)])


class SchoolHolidaysCalendarEntity(
    CoordinatorEntity[SchoolHolidaysCoordinator], CalendarEntity
):
    """Expose all holiday periods as calendar events."""

    _attr_has_entity_name = False

    def __init__(
        self,
        entry: SchoolHolidaysConfigEntry,
        coordinator: SchoolHolidaysCoordinator,
        state_name: str,
    ) -> None:
        super().__init__(coordinator, context=None)
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_name: str | UndefinedType = f"School Holidays {state_name}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"School Holidays {state_name}",
            manufacturer="M4RKU5-C0D3",
            model="OpenHolidays API",
        )

    @property
    def event(self) -> CalendarEvent | None:
        """The ongoing or next holiday event."""
        today = dt_util.start_of_local_day().date()
        periods = self.coordinator.data or []
        period = next((p for p in periods if p.includes(today)), None)
        if period is None:
            period = next((p for p in periods if p.start > today), None)
        return _as_calendar_event(period) if period else None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """All holiday events overlapping the requested range."""
        start_day = start_date.date()
        end_day = end_date.date()
        return [
            _as_calendar_event(period)
            for period in self.coordinator.data or []
            if period.start <= end_day and period.end >= start_day
        ]
