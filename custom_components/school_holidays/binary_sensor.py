"""Binary sensor for currently active school holidays."""

from __future__ import annotations

from datetime import date

import homeassistant.util.dt as dt_util
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SchoolHolidaysConfigEntry
from .const import DOMAIN
from .coordinator import HolidayPeriod, SchoolHolidaysCoordinator

ENTITY_DESCRIPTION = BinarySensorEntityDescription(
    key="current",
    icon="mdi:palm-tree",
)


def _current_period(
    coordinator: SchoolHolidaysCoordinator, today: date
) -> HolidayPeriod | None:
    return next(
        (period for period in coordinator.data or [] if period.includes(today)),
        None,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchoolHolidaysConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            SchoolHolidaysActiveBinarySensor(
                entry, coordinator, ENTITY_DESCRIPTION, entry.title
            )
        ]
    )


class SchoolHolidaysActiveBinarySensor(
    CoordinatorEntity[SchoolHolidaysCoordinator], BinarySensorEntity
):
    """Indicate whether school holidays are currently running."""

    _attr_has_entity_name = False

    def __init__(
        self,
        entry: SchoolHolidaysConfigEntry,
        coordinator: SchoolHolidaysCoordinator,
        entity_description: BinarySensorEntityDescription,
        state_name: str,
    ) -> None:
        super().__init__(coordinator, context=None)
        self.entity_description = entity_description
        self._attr_unique_id = f"{entry.entry_id}_{entity_description.key}"
        self._attr_name = f"School Holidays Active {state_name}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"School Holidays {state_name}",
            manufacturer="M4RKU5-C0D3",
            model="OpenHolidays API",
        )

    @property
    def is_on(self) -> bool:
        """Return true if today is a holiday."""
        today = dt_util.now().date()
        return _current_period(self.coordinator, today) is not None

    @property
    def extra_state_attributes(self) -> dict:
        """Name and end date of the running holidays."""
        today = dt_util.now().date()
        current = _current_period(self.coordinator, today)
        return {
            "holiday_name": current.name if current else None,
            "holiday_end": current.end.isoformat() if current else None,
        }
