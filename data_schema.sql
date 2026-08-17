-- Digital Beehive warehouse schema.
--
-- Loaded by bees.db.init_schema(); safe to run repeatedly.
--
-- Conventions:
--   * location is a Postgres POINT stored as (longitude, latitude).
--   * recorded_at is the device uplink timestamp, converted from the API's
--     epoch-milliseconds to a timezone-aware UTC value.
--   * air_pressure is stored exactly as the station reports it, in pascals.

CREATE TABLE IF NOT EXISTS hives (
    id SMALLSERIAL PRIMARY KEY,
    hive_name VARCHAR(50) NOT NULL UNIQUE,
    location POINT,
    installation_date DATE,
    last_inspection_date DATE,
    comment TEXT
);

CREATE TABLE IF NOT EXISTS sensors (
    id SMALLSERIAL PRIMARY KEY,
    sensor_name VARCHAR(50) NOT NULL UNIQUE,
    sensor_type VARCHAR(50),
    hive_id SMALLINT,
    location POINT,
    is_active BOOLEAN DEFAULT TRUE,

    FOREIGN KEY (hive_id) REFERENCES hives(id)
);

-- Readings from sensors mounted inside a hive.
--   Dragino S31-LB populates temperature + relative_humidity.
--   Dragino D23-LB populates temp_c1 / temp_c2 / temp_c3 (three probes).
-- A row therefore always has one family of columns filled and the other NULL.
CREATE TABLE IF NOT EXISTS hive_measurements (
    id SERIAL PRIMARY KEY,
    sensor_id SMALLINT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    temp_c1 FLOAT,
    temp_c2 FLOAT,
    temp_c3 FLOAT,
    temperature FLOAT,
    relative_humidity FLOAT,

    FOREIGN KEY (sensor_id) REFERENCES sensors(id),
    CONSTRAINT hive_measurements_sensor_time_key UNIQUE (sensor_id, recorded_at)
);

-- Readings from the SenseCAP S2120 weather station (not attached to a hive).
CREATE TABLE IF NOT EXISTS weather (
    id SERIAL PRIMARY KEY,
    sensor_id SMALLINT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    windspeed FLOAT,
    wind_direction FLOAT,
    uv_index FLOAT,
    air_pressure FLOAT,
    light_intensity FLOAT,
    rain_gauge FLOAT,

    FOREIGN KEY (sensor_id) REFERENCES sensors(id),
    CONSTRAINT weather_sensor_time_key UNIQUE (sensor_id, recorded_at)
);

-- Chronological scans per sensor ("last 24h for hive 2") are the dominant
-- read pattern; the UNIQUE constraints above already index (sensor_id,
-- recorded_at), so no additional indexes are needed.
