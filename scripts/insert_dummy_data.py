from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import uuid
import random
from datetime import datetime, timedelta, timezone

cluster = Cluster(['cassandra'])  
session = cluster.connect('test_keyspace')

insert_stmt = session.prepare("""
    INSERT INTO sensor_data (id, device_id, value, timestamp)
    VALUES (?, ?, ?, ?)
""")

base_time = datetime.now(timezone.utc)
for i in range(500):
    sensor_id = uuid.uuid4()
    device_id = f"device_{random.randint(1, 5)}"
    value = round(random.uniform(15.0, 30.0), 2)
    timestamp = base_time + timedelta(seconds=i)

    session.execute(insert_stmt, (sensor_id, device_id, value, timestamp))

print("Inserted 500 rows into sensor_data table.")
