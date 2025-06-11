from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


# Hàm test để in ra log
def say_hello():
    print("Hello from Airflow!")


# Khai báo DAG
with DAG(
    dag_id='test_hello_dag',
    start_date=datetime(2025, 6, 6),
    schedule_interval='@daily',
    catchup=False,  # Không chạy bù các lần trong quá khứ
    tags=["test"]
) as dag:

    # Task dùng PythonOperator
    hello_task = PythonOperator(
        task_id='say_hello_task',
        python_callable=say_hello
    )
