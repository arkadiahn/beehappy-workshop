# Snapshot manifest

Taken: **2026-08-18 14:41 UTC** from ChatBotDB (Railway project `bee-happy`).

Copied verbatim — no deduplication, no filtering, no repair. The defects
are the workshop. If a future export does not reproduce these numbers, the
upstream data changed and the exercises need rechecking.

| Property | Value |
|---|---|
| `rows_data` | 2355297 |
| `distinct_keys` | 1839824 |
| `pct_redundant` | 21.9 |
| `max_duplicate_multiplicity` | 797 |
| `keys_with_conflicting_values` | 0 |
| `null_values` | 0 |
| `measurement_units` | 11 |
| `sensors` | 9 |
| `beehives` | 3 |
| `weather_sensor_registrations` | 3 |
| `first_ts` | 2025-06-13 13:09:35.952000 |
| `last_ts` | 2026-08-18 14:36:12.504000 |
| `days_spanned` | 432 |

## Known defects, all intentional

- **Duplicate rows.** A live bug in the `ChatBotCollector` service, running at
  20-28% in every month observed. `reading_id` is retained so it is provable
  these are separate INSERTs rather than a query artifact.
- **Weather station registered three times** (`sensor_id` 1/2/3) with the same
  device MAC `LoRa-2CF7F1C0613005BC`, one per beehive. Joining hive readings to
  weather without collapsing these triples every weather row.
- **Implicit missingness.** No NULLs anywhere; rows are simply absent for hours
  a device did not report. Only a complete time index reveals them.
- **`ts` is `timestamp without time zone` holding UTC.** Local-time analysis
  needs Europe/Berlin, and the span covers two DST transitions.

## Caveats not visible in the data

- The hive-to-sensor mapping is **unconfirmed** — `hives.toml` marks it
  `UNBESTÄTIGT`, and ChatBotDB's mapping disagrees with that guess.
- `rainGauge` reaches 228.6 and looks cumulative rather than per-interval;
  unverified against the source API.
