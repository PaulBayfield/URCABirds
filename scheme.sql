-- API keys: one per worker/sensor
CREATE TABLE IF NOT EXISTS api_keys (
    id         SERIAL PRIMARY KEY,
    key        TEXT NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    admin      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sensor registry
CREATE TABLE IF NOT EXISTS sensors (
    id               SERIAL PRIMARY KEY,
    sensor_id        TEXT NOT NULL UNIQUE,
    name             TEXT NOT NULL,
    latitude         DOUBLE PRECISION NOT NULL,
    longitude        DOUBLE PRECISION NOT NULL,
    description      TEXT,
    api_key_id       INTEGER NOT NULL REFERENCES api_keys(id) ON DELETE CASCADE,
    first_registered TIMESTAMPTZ DEFAULT NOW(),
    last_connection  TIMESTAMPTZ DEFAULT NOW()
);

-- Detections: sensor_id is an INTEGER FK -> sensors.id
CREATE TABLE IF NOT EXISTS detections (
    id         SERIAL PRIMARY KEY,
    sensor_id  INTEGER NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    timestamp  TEXT NOT NULL,
    species    TEXT NOT NULL,
    confidence REAL NOT NULL
);
