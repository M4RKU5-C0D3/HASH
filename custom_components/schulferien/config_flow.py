"""Config Flow für die Schulferien-Integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
import voluptuous as vol

from .api import OpenHolidaysApiClient, OpenHolidaysApiError
from .const import CONF_SUBDIVISION, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def _async_fetch_subdivisions(
    hass: HomeAssistant,
) -> tuple[dict[str, str], str | None]:
    """Lädt die Bundesländer; liefert (Optionen, Fehlerbasis) zurück."""
    client = OpenHolidaysApiClient(async_get_clientsession(hass))
    try:
        return await client.async_get_subdivisions(), None
    except (OpenHolidaysApiError, HomeAssistantError) as err:
        _LOGGER.warning("Subdivisions konnten nicht geladen werden: %s", err)
        return {}, "cannot_connect"


class SchulferienConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Verarbeitet den Config-Flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._subdivisions: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if not self._subdivisions:
            self._subdivisions, error_base = await _async_fetch_subdivisions(self.hass)
            if error_base and user_input is None:
                errors["base"] = error_base

        schema = vol.Schema(
            {
                vol.Required(CONF_SUBDIVISION): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=code, label=name)
                            for code, name in self._subdivisions.items()
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )

        if user_input is None or errors.get("base") == "cannot_connect":
            return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

        code: str = user_input[CONF_SUBDIVISION]
        name = self._subdivisions.get(code)
        if name is None:
            errors["base"] = "invalid_subdivision"
            return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

        await self.async_set_unique_id(code)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(title=name, data={CONF_SUBDIVISION: code})
