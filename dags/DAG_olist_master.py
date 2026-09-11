from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator  # tambahan import

import pandas as pd

with DAG(
    dag_id='olist_master',
    start_date=pd.Timestamp("2026-1-1"),
    schedule_interval=None,
    catchup=False,
) as dag:

    start_task = EmptyOperator(task_id='start')

    # Trigger DAG extract and load data
    trigger_extract_load = TriggerDagRunOperator(
        task_id='trigger_extract_load',
        trigger_dag_id='olist_extract_load',
        wait_for_completion=True, # Tunggu hingga DAG yang ditrigger selesai sebelum melanjutkan ke task berikutnya
    )

    # Trigger DAG star_schema
    trigger_star_schema = TriggerDagRunOperator(
        task_id='trigger_star_schema',
        trigger_dag_id='olist_star_schema',
        wait_for_completion=True,
    )

    trigger_seller_performance = TriggerDagRunOperator(
        task_id='trigger_seller_performance',
        trigger_dag_id='olist_seller_performance',
    )

    trigger_delay_analysis = TriggerDagRunOperator(
        task_id='trigger_delay_analysis',
        trigger_dag_id='olist_delay_analysis',
    )

    trigger_regional_delay = TriggerDagRunOperator(
        task_id='trigger_regional_delay',
        trigger_dag_id='olist_regional_delay',
    )

    end_task = EmptyOperator(task_id='end')

    # Define the task dependencies

start_task >> trigger_extract_load >> trigger_star_schema >> [
    trigger_seller_performance,
    trigger_delay_analysis,
    trigger_regional_delay
] >> end_task
