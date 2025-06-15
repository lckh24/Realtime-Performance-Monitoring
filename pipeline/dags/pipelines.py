import pandas
import sys
import os
import psutil
psutil.PROCFS_PATH = '/proc'
from scripts.pj.monitor import SystemMonitor
from scripts.pj.producer import KafkaProducerClient
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.hooks.base import BaseHook
from airflow.utils.email import send_email
from datetime import datetime, timedelta
import requests
import time



def send_slack_message(context, status="STARTED"):
    slack_webhook_token = BaseHook.get_connection("slack_webhook").password
    dag_id = context.get('dag').dag_id
    task_instance = context.get('task_instance')
    task_id = task_instance.task_id
    execution_date = context.get('execution_date')
    run_id = context.get('run_id')
    try_number = task_instance.try_number
    log_url = task_instance.log_url

    emoji = {
        "STARTED": ":arrow_forward:",
        "SUCCESS": ":white_check_mark:",
        "FAILED": ":x:"
    }.get(status, ":grey_question:")

    message = f"""{emoji} *Airflow Task Notification*\n
        *Status*: `{status}`\n
        *DAG*: `{dag_id}`\n
        *Task*: `{task_id}`\n
        *Run ID*: `{run_id}`\n
        *Execution Time*: `{execution_date}`\n
        *Try Number*: `{try_number}`\n
        *Logs*: <{log_url}|View Logs>"""

    requests.post(slack_webhook_token, json={"text": message})

    

def refresh_mv():
    hook = PostgresHook(postgres_conn_id='postgres_default')
    hook.run("REFRESH MATERIALIZED VIEW CONCURRENTLY gold.mv_perf_5min;")


def get_data():
    current_date = time.time()
    kafka = KafkaProducerClient()

    while True:
        if time.time() > current_date + 3600:
            break
        try:
            response = requests.get("http://host.docker.internal:8000/system-stats")
            if response.status_code == 200:
                stats = response.json()
                kafka.send_message(stats)
                print(f"Sent stats: {stats}")
            else:
                print(f"Failed to fetch stats from API. Status code: {response.status_code}")
            time.sleep(0.5)
        except Exception as e:
            print(f"An error occurred: {e}")
            
default_args = {
    'owner': 'Khanhle',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 6),
    'retries': 3,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    dag_id='ingest_data',
    default_args=default_args,
    start_date=datetime(2025, 6, 6),
    schedule_interval='@daily'
) as dag:
    task = PythonOperator(
        task_id='streaming_data',
        python_callable=get_data
    )
    
with DAG(
    dag_id='refresh_gold_mv_30min',
    default_args=default_args,
    description='Refresh gold.mv_perf_5min every 30 minutes',
    schedule_interval='*/30 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:
    refresh_task = PythonOperator(
        task_id='refresh_mv_perf_5min',
        python_callable=refresh_mv,
        on_execute_callback=lambda context: send_slack_message(context, status="STARTED"),
        on_success_callback=lambda context: send_slack_message(context, status="SUCCESS"),
        on_failure_callback=lambda context: send_slack_message(context, status="FAILED"),
    )