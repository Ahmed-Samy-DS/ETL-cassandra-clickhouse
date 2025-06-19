
CREATE KEYSPACE IF NOT EXISTS test_keyspace
WITH REPLICATION = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};


USE test_keyspace;

CREATE TABLE IF NOT EXISTS sensor_data (
  id UUID PRIMARY KEY,
  device_id TEXT,
  value DOUBLE,
  timestamp TIMESTAMP
);
