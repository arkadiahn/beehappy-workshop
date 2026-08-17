-- ============================================================================
-- Metabase cards for the BeeHappy dashboard.
--
-- One numbered block per card, in dashboard order. Create each as a Native
-- (SQL) question in Metabase, set the visualization noted in its header, then
-- add it to the dashboard.
--
-- SCHEMA REMINDER
--   The Dragino S31-LB fills  temperature + relative_humidity  (temp_c* NULL).
--   The Dragino D23-LB fills  temp_c1/c2/c3                    (temperature NULL).
--   So "hive temperature" below always means the S31-LB reading -- the same
--   instrument the cover-material experiment is built on.
--
-- DATE FILTER
--   Cards using {{start}} / {{end}} expect two Metabase Date variables.
--   Set defaults to "past 7 days" and "now", then map both to the dashboard's
--   date filter so every card moves together.
--
-- COLOR
--   Assign each hive a fixed hue in Metabase's series settings and never change
--   it. Outside/ambient is always neutral gray -- it is context, not a hive.
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1. KPI TILES -- current temperature per hive          [Visualization: Trend]
--    Create three copies filtered to one hive each, or one Table card.
--    Delta is against the 35 °C brood-nest ideal.
-- ----------------------------------------------------------------------------
SELECT DISTINCT ON (h.hive_name)
       h.hive_name                        AS hive,
       m.temperature                      AS temp_c,
       m.relative_humidity                AS humidity_pct,
       round((m.temperature - 35)::numeric, 1) AS delta_vs_ideal_c,
       m.recorded_at
FROM   hive_measurements m
JOIN   sensors s ON s.id = m.sensor_id
JOIN   hives   h ON h.id = s.hive_id
WHERE  m.temperature IS NOT NULL
ORDER  BY h.hive_name, m.recorded_at DESC;


-- ----------------------------------------------------------------------------
-- 1b. KPI TILE -- current outside conditions            [Visualization: Trend]
-- ----------------------------------------------------------------------------
SELECT temperature AS outside_c,
       humidity    AS outside_humidity_pct,
       windspeed   AS wind_ms,
       recorded_at
FROM   weather
ORDER  BY recorded_at DESC
LIMIT  1;


-- ----------------------------------------------------------------------------
-- 2. HIVE TEMPERATURE OVER TIME                          [Visualization: Line]
--    Series breakout = `series`. Add a GOAL LINE at 35.
--    Ambient shares the axis legitimately (same unit) but must be gray.
--    Do NOT add humidity here -- that is card 3. Two y-scales on one plot
--    makes both unreadable.
-- ----------------------------------------------------------------------------
SELECT date_trunc('hour', m.recorded_at) AS ts,
       h.hive_name                       AS series,
       avg(m.temperature)                AS temp_c
FROM   hive_measurements m
JOIN   sensors s ON s.id = m.sensor_id
JOIN   hives   h ON h.id = s.hive_id
WHERE  m.temperature IS NOT NULL
  AND  m.recorded_at BETWEEN {{start}} AND {{end}}
GROUP  BY 1, 2

UNION ALL

SELECT date_trunc('hour', recorded_at),
       'Außentemperatur',
       avg(temperature)
FROM   weather
WHERE  recorded_at BETWEEN {{start}} AND {{end}}
GROUP  BY 1, 2
ORDER  BY 1;


-- ----------------------------------------------------------------------------
-- 3. HIVE HUMIDITY OVER TIME                             [Visualization: Line]
--    Series breakout = `series`. Add a GOAL LINE at 60.
-- ----------------------------------------------------------------------------
SELECT date_trunc('hour', m.recorded_at) AS ts,
       h.hive_name                       AS series,
       avg(m.relative_humidity)          AS humidity_pct
FROM   hive_measurements m
JOIN   sensors s ON s.id = m.sensor_id
JOIN   hives   h ON h.id = s.hive_id
WHERE  m.relative_humidity IS NOT NULL
  AND  m.recorded_at BETWEEN {{start}} AND {{end}}
GROUP  BY 1, 2
ORDER  BY 1;


-- ----------------------------------------------------------------------------
-- 4. SENSOR HEALTH                                      [Visualization: Table]
--    Covers BOTH fact tables, so the weather station appears too.
--    The gaps in this data are real device outages, not ETL loss -- without
--    this card a flat line reads as "stable colony" when it means "no data".
--    72 = expected readings per day at the ~20 min uplink interval.
-- ----------------------------------------------------------------------------
WITH readings AS (
    SELECT sensor_id, recorded_at FROM hive_measurements
    UNION ALL
    SELECT sensor_id, recorded_at FROM weather
)
SELECT s.sensor_name,
       s.sensor_type,
       coalesce(h.hive_name, '— (kein Stock)')                        AS hive,
       max(r.recorded_at)                                             AS last_reading,
       round(extract(epoch FROM now() - max(r.recorded_at)) / 60)::int AS minutes_ago,
       count(*) FILTER (WHERE r.recorded_at > now() - interval '24 hours') AS readings_24h,
       round(100.0 * count(*) FILTER (WHERE r.recorded_at > now() - interval '24 hours')
             / 72.0, 0)                                               AS coverage_pct_24h,
       s.is_active
FROM   sensors s
LEFT   JOIN readings r ON r.sensor_id = s.id
LEFT   JOIN hives    h ON h.id = s.hive_id
GROUP  BY s.sensor_name, s.sensor_type, h.hive_name, s.is_active
ORDER  BY minutes_ago NULLS LAST;


-- ----------------------------------------------------------------------------
-- 5. WEATHER CONTEXT                                     [Visualization: Line]
--    Supporting card. Temperature and humidity are separate series but share
--    no axis meaning -- if you want both, use two small cards, not two axes.
-- ----------------------------------------------------------------------------
SELECT date_trunc('hour', recorded_at) AS ts,
       avg(temperature)     AS outside_c,
       avg(humidity)        AS humidity_pct,
       avg(windspeed)       AS wind_ms,
       sum(rain_gauge)      AS rain,
       avg(light_intensity) AS light_lux
FROM   weather
WHERE  recorded_at BETWEEN {{start}} AND {{end}}
GROUP  BY 1
ORDER  BY 1;


-- ============================ EXPERIMENT SECTION ============================


-- ----------------------------------------------------------------------------
-- 6 + 7. COVER-MATERIAL SCORECARD                         [Visualization: Bar]
--    Two bars from one query -- create the card twice, once per measure.
--
--      stability_c    = stddev of hive temperature. LOWER IS BETTER.
--      mean_abs_dev_c = average distance from the 35 °C ideal. LOWER IS BETTER.
--
--    Both are needed: a hive can be perfectly STABLE at the WRONG temperature.
--    Stability and accuracy are different questions.
-- ----------------------------------------------------------------------------
SELECT h.hive_name                                        AS hive,
       h.comment                                          AS cover_material,
       round(stddev_samp(m.temperature)::numeric, 2)      AS stability_c,
       round(avg(abs(m.temperature - 35))::numeric, 2)    AS mean_abs_dev_c,
       round(avg(m.temperature)::numeric, 2)              AS mean_temp_c,
       round(avg(m.relative_humidity)::numeric, 1)        AS mean_humidity_pct,
       round(stddev_samp(m.relative_humidity)::numeric,2) AS humidity_stability,
       count(*)                                           AS readings
FROM   hive_measurements m
JOIN   sensors s ON s.id = m.sensor_id
JOIN   hives   h ON h.id = s.hive_id
WHERE  m.temperature IS NOT NULL
  AND  m.recorded_at BETWEEN {{start}} AND {{end}}
GROUP  BY h.hive_name, h.comment
ORDER  BY stability_c;


-- ----------------------------------------------------------------------------
-- 8. INSULATION PERFORMANCE                           [Visualization: Scatter]
--    x = outside_c, y = hive_c, series breakout = hive, trend line ON.
--
--    A FLATTER SLOPE IS BETTER BUFFERING -- which is exactly what a cover
--    material is for. This answers the experiment more directly than any
--    time series does.
--
--    Hourly buckets join the two ~20 min streams accurately enough and far
--    more cheaply than a nearest-timestamp lateral join.
-- ----------------------------------------------------------------------------
WITH hive AS (
    SELECT date_trunc('hour', m.recorded_at) AS bucket,
           h.hive_name                       AS hive,
           avg(m.temperature)                AS hive_c
    FROM   hive_measurements m
    JOIN   sensors s ON s.id = m.sensor_id
    JOIN   hives   h ON h.id = s.hive_id
    WHERE  m.temperature IS NOT NULL
      AND  m.recorded_at BETWEEN {{start}} AND {{end}}
    GROUP  BY 1, 2
),
outside AS (
    SELECT date_trunc('hour', recorded_at) AS bucket,
           avg(temperature)                AS outside_c
    FROM   weather
    WHERE  recorded_at BETWEEN {{start}} AND {{end}}
    GROUP  BY 1
)
SELECT hive.hive,
       round(outside.outside_c::numeric, 1) AS outside_c,
       round(hive.hive_c::numeric, 2)       AS hive_c
FROM   hive
JOIN   outside USING (bucket)
ORDER  BY outside_c;


-- ----------------------------------------------------------------------------
-- 8b. BUFFERING COEFFICIENT                               [Visualization: Bar]
--     The slope of card 8, as one number per hive. LOWER IS BETTER.
--
--     Read it as: "for every 1 °C the outside moves, this hive moves N °C."
--     A perfect insulator scores 0; an uncovered box scores 1. This is the
--     cleanest single statement of what a cover material actually does, and
--     it is more reliable than reading slopes off a scatter by eye.
--
--     r2 is included as an honesty check -- a slope from a poor fit should not
--     be quoted as a result.
-- ----------------------------------------------------------------------------
WITH hive AS (
    SELECT date_trunc('hour', m.recorded_at) AS bucket,
           h.hive_name                       AS hive,
           avg(m.temperature)                AS hive_c
    FROM   hive_measurements m
    JOIN   sensors s ON s.id = m.sensor_id
    JOIN   hives   h ON h.id = s.hive_id
    WHERE  m.temperature IS NOT NULL
      AND  m.recorded_at BETWEEN {{start}} AND {{end}}
    GROUP  BY 1, 2
),
outside AS (
    SELECT date_trunc('hour', recorded_at) AS bucket,
           avg(temperature)                AS outside_c
    FROM   weather
    WHERE  recorded_at BETWEEN {{start}} AND {{end}}
    GROUP  BY 1
)
SELECT hive.hive,
       round(regr_slope(hive.hive_c, outside.outside_c)::numeric, 3) AS buffering_coefficient,
       round(regr_r2(hive.hive_c, outside.outside_c)::numeric, 3)    AS r2,
       count(*)                                                      AS hourly_points
FROM   hive
JOIN   outside USING (bucket)
GROUP  BY 1
ORDER  BY buffering_coefficient;


-- ----------------------------------------------------------------------------
-- 9. DIURNAL RHYTHM                    [Visualization: Pivot table + heatmap
--                                       conditional formatting on mean_temp_c]
--    Rows = hour_of_day, Columns = hive. Shows whether a colony holds its
--    temperature overnight. Metabase has no true heatmap chart; a pivot table
--    with conditional formatting is the working equivalent.
-- ----------------------------------------------------------------------------
SELECT extract(hour FROM m.recorded_at)::int AS hour_of_day,
       h.hive_name                           AS hive,
       round(avg(m.temperature)::numeric, 2) AS mean_temp_c,
       round(avg(m.relative_humidity)::numeric, 1) AS mean_humidity_pct
FROM   hive_measurements m
JOIN   sensors s ON s.id = m.sensor_id
JOIN   hives   h ON h.id = s.hive_id
WHERE  m.temperature IS NOT NULL
  AND  m.recorded_at BETWEEN {{start}} AND {{end}}
GROUP  BY 1, 2
ORDER  BY 1, 2;


-- ----------------------------------------------------------------------------
-- 10. THREE-PROBE THERMAL PROFILE (D23-LB)               [Visualization: Line]
--
--     *** HOLD THIS CARD ***
--     The API returns EMPTY descriptions for tempC1/C2/C3. The project text
--     mentions Brutkammer / Futterkammer / Stock -- three places matching the
--     three probes -- but which probe is which is unconfirmed. Until a beekeeper
--     confirms it, this is three unlabeled lines and the 35 °C ideal may not
--     even apply to them. Ship it only after relabeling c1/c2/c3.
-- ----------------------------------------------------------------------------
SELECT date_trunc('hour', m.recorded_at) AS ts,
       h.hive_name                       AS hive,
       avg(m.temp_c1)                    AS probe_c1,
       avg(m.temp_c2)                    AS probe_c2,
       avg(m.temp_c3)                    AS probe_c3
FROM   hive_measurements m
JOIN   sensors s ON s.id = m.sensor_id
JOIN   hives   h ON h.id = s.hive_id
WHERE  m.temp_c1 IS NOT NULL
  AND  m.recorded_at BETWEEN {{start}} AND {{end}}
GROUP  BY 1, 2
ORDER  BY 1;
