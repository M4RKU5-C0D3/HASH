"""Client for the OpenHolidays API (https://openholidaysapi.org)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import logging
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession, ClientTimeout

from homeassistant.exceptions import HomeAssistantError

from .const import API_BASE, API_TIMEOUT

_LOGGER = logging.getLogger(__name__)

PREFERRED_LANGUAGES = ("DE", "EN")


@dataclass(frozen=True)
class HolidayPeriod:
    """A holiday period."""

    name: str
    start: date
    end: date

    @property
    def duration_days(self) -> int:
        """Total duration in days (first and last day included)."""
        return (self.end - self.start).days + 1

    def includes(self, day: date) -> bool:
        """Return true if the given day falls within the period."""
        return self.start <= day <= self.end


class OpenHolidaysApiError(HomeAssistantError):
    """Error while communicating with the OpenHolidays API."""


def _localized_text(entries: list[dict[str, Any]] | None) -> str | None:
    """Return the text in the preferred language (DE before EN)."""
    if not entries:
        return None
    by_language = {str(e.get("language", "")).upper(): e.get("text") for e in entries}
    for language in PREFERRED_LANGUAGES:
        text = by_language.get(language)
        if text:
            return str(text)
    first = entries[0].get("text")
    return str(first) if first else None


def _parse_date(raw: Any) -> date | None:
    try:
        return date.fromisoformat(str(raw))
    except (TypeError, ValueError):
        return None


class OpenHolidaysApiClient:
    """Async client for the OpenHolidays API."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def _request(self, path: str, params: dict[str, str]) -> Any:
        try:
            response = await self._session.get(
                f"{API_BASE}{path}",
                params=params,
                timeout=ClientTimeout(total=API_TIMEOUT),
            )
            response.raise_for_status()
            return await response.json()
        except TimeoutError as err:
            raise OpenHolidaysApiError(f"Timeout while requesting {path}") from err
        except ClientResponseError as err:
            raise OpenHolidaysApiError(
                f"HTTP {err.status} while requesting {path}"
            ) from err
        except ClientError as err:
            raise OpenHolidaysApiError(f"Connection error while requesting {path}") from err

    async def async_get_subdivisions(self) -> dict[str, str]:
        """Return a mapping of subdivision code to federal state name."""
        payload = await self._request(
            "/Subdivisions",
            {"countryIsoCode": "DE", "languageIsoCode": "DE"},
        )
        subdivisions: dict[str, str] = {}
        for entry in payload or []:
            code = entry.get("code")
            categories = [
                str(c.get("text", "")).lower() for c in entry.get("category", []) or []
            ]
            if not code or categories and "bundesland" not in categories:
                continue
            name = _localized_text(entry.get("name"))
            if name:
                subdivisions[str(code)] = name
        return dict(sorted(subdivisions.items(), key=lambda item: item[1]))

    async def async_get_school_holidays(
        self,
        subdivision_code: str,
        valid_from: date,
        valid_to: date,
    ) -> list[HolidayPeriod]:
        """Fetch school holidays of the given state within the requested range."""
        payload = await self._request(
            "/SchoolHolidays",
            {
                "countryIsoCode": "DE",
                "subdivisionCode": subdivision_code,
                "languageIsoCode": "DE",
                "validFrom": valid_from.isoformat(),
                "validTo": valid_to.isoformat(),
            },
        )
        periods: list[HolidayPeriod] = []
        for entry in payload or []:
            start = _parse_date(entry.get("startDate"))
            end = _parse_date(entry.get("endDate"))
            if start is None or end is None or end < start:
                _LOGGER.warning(
                    "Skipping invalid holiday entry: %s", entry.get("id")
                )
                continue
            periods.append(
                HolidayPeriod(
                    name=_localized_text(entry.get("name")) or "Holidays",
                    start=start,
                    end=end,
                )
            )
        return sorted(periods, key=lambda period: period.start)
