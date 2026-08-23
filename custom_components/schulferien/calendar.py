"""Calendar-Entity mit allen Schulferien-Zeiträumen."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import UndefinedType
from homeassistant.util import dt as dt_util
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SchulferienConfigEntry
from .const import DOMAIN
from .coordinator import HolidayPeriod, SchulferienCoordinator


def _as_calendar_event(period: HolidayPeriod) -> CalendarEvent:
    """Wandelt einen Ferienzeitraum in ein Kalender-Event (Ende exklusiv)."""
    return CalendarEvent(
        start=period.start,
        end=period.end + timedelta(days=1),
        summary=period.name,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchulferienConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richtet die Calendar-Entity ein."""
    coordinator = entry.runtime_data
    async_add_entities([SchulferienCalendarEntity(entry, coordinator, entry.title)])


class SchulferienCalendarEntity(
    CoordinatorEntity[SchulferienCoordinator], CalendarEntity
):
    """Stellt alle Ferienzeiträume als Kalender-Events bereit."""

    _attr_has_entity_name = False

    def __init__(
        self,
        entry: SchulferienConfigEntry,
        coordinator: SchulferienCoordinator,
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
        """Das laufende oder nächste Ferien-Event."""
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
        """Alle Ferien-Events, die den Zeitraum schneiden."""
        start_day = start_date.date()
        end_day = end_date.date()
        return [
            _as_calendar_event(period)
            for period in self.coordinator.data or []
            if period.start <= end_day and period.end >= start_day
        ]
