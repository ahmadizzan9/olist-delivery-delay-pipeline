from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.docker.operators.docker import DockerOperator

import pandas as pd

SELECTED_MODELS = [
    "dim_customers",
    "dim_sellers",
    "fact_orders",
]

with DAG(
    dag_id="olist_star_schema",
    start_date=pd.Timestamp("2026-1-1"),
    schedule_interval=None,
    catchup=False,
) as dag:

    start_task = EmptyOperator(task_id="start")

    load_star_schema_task = DockerOperator(
        task_id     ="load_star_schema",
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

    start_task >> load_star_schema_task >> end_task