DROP TABLE IF EXISTS weather_data;

CREATE TABLE weather_data (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TIMESTAMP NOT NULL,
  meas_type INTEGER NOT NULL,
  temperature DOUBLE,
  humidity DOUBLE,
  pressure DOUBLE,
  dew_point DOUBLE
);