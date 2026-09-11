from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.docker.operators.docker import DockerOperator

import pandas as pd

SELECTED_MODELS = [
    "mart_regional_delay_dest_3m",
    "mart_regional_delay_dest_at",
    "mart_regional_delay_orig_3m",
    "mart_regional_delay_orig_at",
]

with DAG(
    dag_id="olist_regional_delay",
    start_date=pd.Timestamp("2026-1-1"),
    schedule_interval=None,
    catchup=False,
) as dag:

    start_task = EmptyOperator(task_id="start")

    load_regional_delay_task = DockerOperator(
        task_id     ="load_regional_delay",
        image       ="olist-dbt:1.0",
        command     =f"dbt run --select {' '.join(SELECTED_MODELS)}",
        docker_url  ="unix://var/run/docker.sock",
        network_mode="olist_net",
        mounts=[
            {
                "source": "D:/@Important_stuff/Dibimbing-DE-Bootcamp/FINAL/delivery_batch_pipeline/dbt",
                "target": "/usr/app/dbt",   
                "type"  : "bind",
            }
        ],
        environment={
            "DBT_PROFILES_DIR": "/usr/app/dbt",
        },
        auto_remove=True,
    )

    end_task = EmptyOperator(task_id="end")

    start_task >> load_regional_delay_task >> end_task