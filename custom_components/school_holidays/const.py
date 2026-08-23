"""Constants for the school holidays integration."""

from datetime import timedelta

DOMAIN = "school_holidays"

CONF_SUBDIVISION = "subdivision"

API_BASE = "https://openholidaysapi.org"
API_TIMEOUT = 30

LOOKBACK_DAYS = 30
LOOKAHEAD_DAYS = 365

UPDATE_INTERVAL = timedelta(days=1)
