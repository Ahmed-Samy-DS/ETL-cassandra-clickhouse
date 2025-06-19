    # 🚀 ETL Pipeline: Cassandra ➜ Airflow ➜ ClickHouse

This project demonstrates a local ETL pipeline that extracts synthetic sensor data from **Cassandra**, processes it via **Apache Airflow**, and loads it into **ClickHouse** for analytical use.

All services are containerized with **Docker Compose**.

---

## 🧰 Tech Stack

- **Cassandra** – Source database (NoSQL)
- **ClickHouse** – Target OLAP database
- **Apache Airflow** – ETL orchestration
- **PostgreSQL** – Metadata database for Airflow
- **Docker Compose** – Multi-service container orchestration

---

## 📁 Project Structure



project/
├── docker-compose.yml
├── airflow/
│   ├── dags/
│   │   └── cassandra_to_clickhouse_dag.py
├── scripts/
│   ├── insert_dummy_data.py
│   ├── create_tables.cql
│   ├── create_clickhouse_table.sql
├── README.md



---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Ahmed-Samy-DS/ETL-cassandra-clickhouse.git
cd ETL-cassandra-clickhouse

2️⃣ Start Services

docker-compose up -d

Services will start on the following ports:

Service	Port(s)
Airflow UI	http://localhost:8080
Cassandra	9042 (native)
ClickHouse	8123 (HTTP), 9000 (native)
PostgreSQL	5432

Wait 1–2 minutes for all services to initialize.


🗃️ Create Tables

✅ Cassandra Table
docker exec -i cassandra cqlsh < scripts/create_tables.cql


✅ ClickHouse Table
docker exec -i clickhouse-client clickhouse-client < scripts/create_clickhouse_table.sql


📥 Insert Dummy Data

docker exec -it airflow-worker python /scripts/insert_dummy_data.py

🌬️ Run Airflow DAG
🔑 Configure Airflow Connections
Open http://localhost:8080 and go to Admin → Connections:

1. Cassandra Connection
Conn ID: cassandra_conn

Conn Type: Cassandra

Host: cassandra

Port: 9042

Schema: test_keyspace

2. ClickHouse Connection
Conn ID: clickhouse_conn

Conn Type: HTTP

Host: clickhouse

Port: 8123

Schema: default

▶️ Trigger the DAG
Find the DAG named etl_cassandra_to_clickhouse_dag

Turn it ON

Click Trigger DAG ▶️ to run it manually

✅ Verify the Data Load

SELECT COUNT(*) FROM test_keyspace.sensor_data;

SELECT COUNT(*) FROM sensor_data;

find row_counts_log.txt with verification like that 
[2025-06-18T22:41:03.579726] Cassandra row count: 500
ClickHouse row count: 500
Row counts match.


🧼 Tear Down

docker-compose down -v









