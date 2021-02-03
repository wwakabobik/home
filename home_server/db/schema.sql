DROP TABLE IF EXISTS weather_data;
DROP TABLE IF EXISTS wind_data;
DROP TABLE IF EXISTS power_data;

CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP NOT NULL,
    meas_type INTEGER NOT NULL,
    temperature DOUBLE,
    humidity DOUBLE,
    pressure DOUBLE,
    dew_point DOUBLE
);

CREATE TABLE wind_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP NOT NULL,
    unix_tx INTEGER NOT NULL,
    avg_rps DOUBLE,
    max_rps DOUBLE,
    min_rps DOUBLE,
    avg_ms DOUBLE,
    max_ms DOUBLE,
    min_ms DOUBLE,
    avg_kmh DOUBLE,
    max_kmh DOUBLE,
    min_kmh DOUBLE,
    avg_knots DOUBLE,
    max_knots DOUBLE,
    min_knots DOUBLE,
    heading DOUBLE,
    heading_abbr VARCHAR
);

CREATE TABLE power_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TIMESTAMP NOT NULL,
    unix_tx INTEGER NOT NULL,
    avg_voltage DOUBLE,
    avg_current DOUBLE,
    avg_power DOUBLE,
    avg_consumption DOUBLE
);