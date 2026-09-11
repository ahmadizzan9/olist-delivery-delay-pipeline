from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.docker.operators.docker import DockerOperator

import pandas as pd

UPSTREAM_MODELS = [
    "mart_seller_monthly_performance",
]

DOWNSTREAM_MODELS = [
    "mart_seller_declining_trend_recent",
    "mart_seller_declining_trend_summary",
]

with DAG(
    dag_id="olist_seller_performance",
    start_date=pd.Timestamp("2026-1-1"),
    schedule_interval=None,
    catchup=False,
) as dag:

    start_task = EmptyOperator(task_id="start")

    load_seller_monthly_performance_task = DockerOperator(
        task_id     ="load_seller_monthly_performance",
        image       ="olist-dbt:1.0",
        command     =f"dbt run --select {' '.join(UPSTREAM_MODELS)}",
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

    load_seller_performance_task = DockerOperator(
            task_id     ="load_seller_performance",
            image       ="olist-dbt:1.0",
            command     =f"dbt run --select {' '.join(DOWNSTREAM_MODELS)}",
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

    start_task >> load_seller_monthly_performance_task >> load_seller_performance_task >> end_task