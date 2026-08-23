# AGENTS.md — Richtlinien für KI-Agenten

Anleitung für Coding-Agenten, die an diesem Repository arbeiten (analog zum Vorbild-Projekt [HAKI](https://github.com/M4RKU5-C0D3/HAKI)).

## Projektüberblick

Home Assistant Custom Integration **`school_holidays`**: stellt Schulferien pro Bundesland über die [OpenHolidays API](https://openholidaysapi.org) bereit. Ein Config-Entry = ein Bundesland. Datenquelle ist öffentlich und ohne API-Key.

## Repository-Struktur

```
.github/workflows/validate.yml     HACS-Validierung (hacs/action)
custom_components/school_holidays/
  __init__.py                      Setup/Unload, PLATFORMS, ConfigEntry-Typ
  api.py                           OpenHolidaysApiClient + HolidayPeriod + Fehlerklasse
  binary_sensor.py                 laufende Ferien (on/off)
  calendar.py                      Calendar-Entity mit allen Zeiträumen
  config_flow.py                   Bundesland-Dropdown via /Subdivisions
  const.py                         DOMAIN, CONF_*, API-Basis, Intervalle
  coordinator.py                   DataUpdateCoordinator (24 h)
  manifest.json                    Domain, Version, Codeowner
  sensor.py                        nächste Ferien + Attribute
  strings.json                     UI-Texte (EN, Fallback)
  translations/de.json             UI-Texte (DE)
  brand/                           icon.png/@2x, logo.png/@2x
examples/                          YAML-Beispiele für die Doku
```

## Konventionen

- **Sprache:** Code, Docstrings, Logging und README auf Englisch; UI-Texte des Config-Flows auf Deutsch (`translations/de.json`), Fallback `strings.json` auf Englisch.
- **Entity-/Attribut-Namen:** ebenfalls Englisch und kurz gehalten (`has_entity_name = True`); das Gerät trägt den Bundeslandnamen, die Entität nur ihre Funktion – z. B. Gerät „School Holidays Niedersachsen" mit `binary_sensor.school_holidays_niedersachsen_active`, Attributen wie `holiday_name`, `days_until_start`.
- **Async überall:** Kein blockierender I/O; HTTP ausschließlich über den geteilten aiohttp-Client (`homeassistant.helpers.aiohttp_client.async_get_clientsession`).
- **Keine externen Requirements:** `aiohttp` ist in HA enthalten. Neue Abhängigkeiten nur mit gutem Grund.
- **HA-Stil:** `DataUpdateCoordinator` für Polling, Entities als `CoordinatorEntity`, `DeviceInfo` pro Entry, Unique IDs aus `entry.entry_id` + Suffix.
- **Kommentare:** Nur wenn wirklich nötig – der Code soll sich selbst erklären.

## Fachliche Randbedingungen der OpenHolidays API

- Abfragefenster (`validFrom`/`validTo`) darf **maximal 3 Jahre** umfassen. Die Integration fragt bewusst `heute − 30 Tage … heute + 365 Tage` ab (`const.py`: `LOOKBACK_DAYS`, `LOOKAHEAD_DAYS`) – nicht vergrößern.
- Datumsfelder sind reine Kalendertage (`YYYY-MM-DD`). Calendar-Events benötigen ein **exklusives Ende** → Event-Ende = Feriende + 1 Tag (`calendar.py`).
- `/Subdivisions` liefert auch Kind-Ebenen (`children`, z. B. Städte); gefiltert wird auf Kategorie „Bundesland" (`api.py`).
- Bei API-Fehlern behält der Coordinator den letzten Stand (`UpdateFailed` statt Exception nach außen): Entitäten bleiben verfügbar, Ferientermine ändern sich nicht kurzfristig.

## Verifikation vor jedem Commit

```bash
python3 -m compileall custom_components/school_holidays       # Syntax
python3 - <<'EOF'                                            # JSON valide?
import json, pathlib
for p in pathlib.Path("custom_components/school_holidays").rglob("*.json"):
    json.loads(p.read_text())
EOF
python3 -c "import yaml, pathlib; [yaml.safe_load(p.read_text()) for p in pathlib.Path('.').rglob('*.y*ml')]"
ruff check custom_components/school_holidays                  # falls installiert
```

Manueller End-to-End-Test: `custom_components/school_holidays/` in das `config/custom_components/` einer HA-Installation kopieren, neu starten, Integration hinzufügen und Log auf Fehler prüfen.

## Release-Prozess

1. `version` in `manifest.json` erhöhen (SemVer)
2. Commit auf `master`, Tag `vX.Y.Z` setzen, GitHub Release erstellen
3. Die Validate-Workflow prüft HACS-Konformität automatisch
