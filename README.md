# Home Assistant School Holidays Integration

[![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/M4RKU5-C0D3/HASH)
[![GitHub release](https://img.shields.io/github/v/release/M4RKU5-C0D3/HASH?style=for-the-badge)](https://github.com/M4RKU5-C0D3/HASH/releases)
[![Validate](https://img.shields.io/github/actions/workflow/status/M4RKU5-C0D3/HASH/validate.yml?branch=master&style=for-the-badge&label=Validate)](https://github.com/M4RKU5-C0D3/HASH/actions/workflows/validate.yml)

Home Assistant custom component for **school holidays per German federal state** via the [OpenHolidays API](https://openholidaysapi.org). Primary use case: automations that react differently depending on whether schools are on holiday – e.g. a later alarm time during breaks.

## Why this integration exists

The OpenHolidays API is freely accessible, requires **no API key** and provides official holiday dates for the German federal states. This integration fetches them once a day and exposes them as native Home Assistant entities:

- A real **calendar** with all holiday periods (for `calendar` triggers such as `event: start`)
- A **binary sensor** indicating whether holidays are currently running
- A **sensor** with the next holidays as a countdown

The API allows query windows of at most 3 years – this is handled internally: the integration queries `today − 30 days` through `today + 365 days`, so ongoing holidays are detected and a full year ahead can be planned.

## Requirements

- Home Assistant with internet access to `openholidaysapi.org`
- No account, no API key

## Installation

### Via HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=M4RKU5-C0D3&repository=HASH&category=integration)

1. In HACS go to **HACS → ⋮ → Custom repositories**
2. Add the repository URL `https://github.com/M4RKU5-C0D3/HASH` with category **Integration**
3. Click **Download** on "School Holidays"
4. Restart Home Assistant
5. Go to **Settings → Devices & Services → Add Integration** → search **"School Holidays"** and pick the desired federal state

### Manually

1. Copy the `custom_components/school_holidays/` directory into `<config>/custom_components/school_holidays/`
2. Restart Home Assistant
3. Add it via the UI as described above

Multiple states? Simply add the integration multiple times – each federal state gets its own config entry with its own entities.

## Provided entities

All entities belong to their respective device (e.g. "School Holidays Niedersachsen") and refresh once a day (`iot_class: cloud_polling`). Entity IDs are derived from the state name.

| Entity | Type | Purpose |
|---|---|---|
| `calendar.school_holidays_<state>` | Calendar | One event per holiday period, summary = holiday name |
| `binary_sensor.school_holidays_active_<state>` | Binary sensor | `on` while today is a holiday |
| `sensor.next_school_holidays_<state>` | Sensor | Name of the next (or currently running) holidays |

Example for Lower Saxony (`niedersachsen`): `calendar.school_holidays_niedersachsen`, `binary_sensor.school_holidays_active_niedersachsen`, `sensor.next_school_holidays_niedersachsen`.

### Attributes of `binary_sensor.school_holidays_active_*`

| Attribute | Type | Description |
|---|---|---|
| `holiday_name` | str \| null | Name of the current holidays (e.g. "Sommerferien") or `null` |
| `holiday_end` | str \| null | End date of the current holidays (ISO) or `null` |

### Attributes of `sensor.next_school_holidays_*`

| Attribute | Type | Description |
|---|---|---|
| `start` | str | Start date (ISO); for ongoing holidays the start of the running period |
| `end` | str | End date (ISO) |
| `days_until_start` | int | Days until the start, `0` if already running |
| `duration_days` | int | Total duration including first and last day |

The sensor's state is the name of the next (or currently running) holidays.

## Example automations

Different alarm times depending on holiday status – a ready-to-use template lives in [`examples/automations.yaml`](examples/automations.yaml): one automation with an early alarm during school term, and one with a later alarm while the binary sensor reports active holidays.

The calendar additionally allows triggers on `calendar.school_holidays_<state>` with `event: start` / `event: end` – e.g. for a notification on the last day of the holidays.

## Data source & updates

- Source: [OpenHolidays API](https://openholidaysapi.org) – endpoints `/Subdivisions` (for the state selection in the config flow) and `/SchoolHolidays`
- Update interval: once a day; holiday dates rarely change, so on API errors the last known data is kept instead of briefly making entities unavailable

## Disclaimer

This is a personal project. It only uses the public OpenHolidays API without authentication.

## Vibe coding

This project was built with AI assistance via [opencode](https://opencode.ai) using the model `big-pickle`. All code was reviewed and released by a human maintainer.
