# 🚀 ETL: Cassandra to ClickHouse with Apache Airflow

This project demonstrates a complete local ETL pipeline using Apache Airflow to:
- Extract data from **Cassandra**
- Transform it with Python
- Load it into **ClickHouse**

All services are containerized via Docker Compose.

---

## 📁 Project Structure

project/
├── docker-compose.yml
├── airflow/
│ └── dags/
│ └── cassandra_to_clickhouse_dag.py
├── scripts/
│ ├── insert_dummy_data.py
│ ├── create_tables.cql
│ └── create_clickhouse_table.sql
├── README.md


---

## ⚙️ Installed Services & Ports

| Service      | Port(s)                  |
|--------------|--------------------------|
| Airflow UI   | `localhost:8080`         |
| Cassandra    | `localhost:9042`         |
| ClickHouse   | `localhost:8123`, `9000` |
| PostgreSQL   | `localhost:5432`         |

---

## 📦 Prerequisites

- Docker & Docker Compose installed
- Python 3.8+ (for local testing of scripts)

---

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Ahmed-Samy-DS/ETL-cassandra-clickhouse.git
cd ETL-cassandra-clickhouse

### 2.Start all services

docker-compose up -d

### 3. Create Cassandra Keyspace & Table
docker exec -i cassandra cqlsh < scripts/create_tables.cql

### 4. Generate & Insert Dummy Data into Cassandra
docker cp scripts/insert_dummy_data.py airflow-webserver:/scripts/insert_dummy_data.py
docker exec -it airflow-webserver python /scripts/insert_dummy_data.py


### 5. Create ClickHouse Table
docker cp scripts/create_clickhouse_table.sql clickhouse:/create_clickhouse_table.sql
docker exec -i clickhouse clickhouse-client < /create_clickhouse_table.sql

### 6. Run the Airflow DAG
Open Airflow UI → http://localhost:8080
Login: admin / admin
Enable cassandra_to_clickhouse_dag
Trigger the DAG manually

🧪 Verify the Data Load
In Cassandra

docker exec -it cassandra cqlsh
SELECT COUNT(*) FROM test_keyspace.sensor_data;
exit

In ClickHouse

docker exec -it clickhouse clickhouse-client
SELECT COUNT(*) FROM sensor_data;
exit


You will find row_counts_log.txt 

for more verification in project\airflow\logs

also PostgreSQL to store Airflow metadata DB.

docker exec -it postgres psql -U user -d mydb

\dt










