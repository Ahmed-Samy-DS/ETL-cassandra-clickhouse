from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from datetime import datetime, timedelta, timezone
from cassandra.cluster import Cluster
from clickhouse_connect import get_client
import pandas as pd
import logging

def extract_from_cassandra():
    logging.info("Connecting to Cassandra...")
    conn = BaseHook.get_connection('cassandra_conn')
    cluster = Cluster([conn.host])
    session = cluster.connect('test_keyspace')

    logging.info("Executing SELECT query from Cassandra...")
    rows = session.execute("SELECT id, device_id, value, timestamp FROM sensor_data")

    data = []
    for row in rows:
        data.append((str(row.id), row.device_id, row.value, row.timestamp))

    df = pd.DataFrame(data, columns=['id', 'device_id', 'value', 'timestamp'])

    session.shutdown()
    cluster.shutdown()

    logging.info(f"Extracted {len(df)} rows from Cassandra.")
    return df.to_dict(orient='records')

def transform_data(df):
    df['id'] = df['id'].astype(str)
    df['device_id'] = df['device_id'].astype(str)
    df['value'] = df['value'].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    return df

def transform(**context):
    df_dict = context['ti'].xcom_pull(task_ids='extract')
    df = pd.DataFrame(df_dict)
    df = transform_data(df)
    logging.info(f"Transformed data with {len(df)} rows.")
    return df.to_dict(orient='records')

def load_into_clickhouse(**context):
    df_dict = context['ti'].xcom_pull(task_ids='transform')
    df = pd.DataFrame(df_dict)
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True) #change_to_datetime
    
    conn = BaseHook.get_connection('clickhouse_conn')
    
    username = conn.login or 'default'
    password = conn.password or ''
    
    client = get_client(host=conn.host, port=8123, username=username, password=password)

    logging.info("Inserting data into ClickHouse...")
    client.insert_df('sensor_data', df)
    logging.info("Insert completed successfully.")
    
def compare_row_counts():
    # Cassandra row count
    cass_conn = BaseHook.get_connection('cassandra_conn')
    cluster = Cluster([cass_conn.host])
    session = cluster.connect('test_keyspace')
    cass_result = session.execute("SELECT COUNT(*) FROM sensor_data")
    cass_count = cass_result.one()[0]
    session.shutdown()
    cluster.shutdown()

    # ClickHouse row count
    click_conn = BaseHook.get_connection('clickhouse_conn')
    
    username = click_conn.login or 'default'
    password = click_conn.password or ''
    
    client = get_client(host=click_conn.host, port=8123, username=username, password=password)
    
    click_result = client.query("SELECT COUNT(*) FROM sensor_data")
    click_count = click_result.result_rows[0][0]

    log_message = (
        f"Cassandra row count: {cass_count}\n"
        f"ClickHouse row count: {click_count}\n"
    )

    if cass_count == click_count:
        log_message += "Row counts match.\n"
    else:
        log_message += "Row count mismatch!\n"

    logging.info(log_message)

    # Write to log file
    output_path = "/opt/airflow/logs/row_counts_log.txt"
    try:
        with open(output_path, "a") as f:
            f.write(f"[{datetime.utcnow().isoformat()}] {log_message}\n")
    except Exception as e:
        logging.error(f"Failed to write log file: {e}")


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 6, 17),
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id="etl_cassandra_to_clickhouse",
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=["etl", "cassandra", "clickhouse"]
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_from_cassandra
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform,
        provide_context=True
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load_into_clickhouse,
        provide_context=True
    )
    
    compare_counts = PythonOperator(
        task_id="compare_row_counts",
        python_callable=compare_row_counts
    )

    extract >> transform_task >> load >> compare_counts
