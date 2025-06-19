CREATE TABLE IF NOT EXISTS sensor_data (
    id String,
    device_id String,
    value Float64,
    timestamp DateTime
)
ENGINE = MergeTree
ORDER BY (device_id, timestamp);
