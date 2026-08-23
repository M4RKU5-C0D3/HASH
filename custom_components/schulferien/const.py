"""Konstanten für die Schulferien-Integration."""

from datetime import timedelta

DOMAIN = "schulferien"

CONF_SUBDIVISION = "subdivision"

API_BASE = "https://openholidaysapi.org"
API_TIMEOUT = 30

LOOKBACK_DAYS = 30
LOOKAHEAD_DAYS = 365

UPDATE_INTERVAL = timedelta(days=1)
