from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.docker.operators.docker import DockerOperator

import pandas as pd
import requests, zipfile, os
from sqlalchemy import create_engine,text

KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
KAGGLE_KEY      = os.getenv("KAGGLE_API_TOKEN")
POSTGRES_PORT   = os.getenv("POSTGRES_PORT")
DATASET_DIR     = "/opt/airflow/datasets"
POSTGRES_CONN   = "postgresql+psycopg2://airflow:airflow@postgres:5432/dwh"

def download_ds():
    if os.path.exists(DATASET_DIR) and os.listdir(DATASET_DIR):
        print("Dataset exist, skip download.")
        return
    
    os.makedirs(DATASET_DIR, exist_ok=True)
    zip_path = f"{DATASET_DIR}/olist.zip"
    url = "https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce"
    
    response = requests.get(url, auth=(KAGGLE_USERNAME, KAGGLE_KEY), stream=True)
    if response.status_code != 200:
        raise Exception(f"Download failed. Status code: {response.status_code}")
    
    with open(zip_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
        
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(DATASET_DIR)

    os.remove(zip_path)

def olist_ds():
    orders = pd.read_csv(f"{DATASET_DIR}/olist_orders_dataset.csv", parse_dates=[
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ])
    order_items = pd.read_csv(f"{DATASET_DIR}/olist_order_items_dataset.csv")
    reviews = pd.read_csv(f"{DATASET_DIR}/olist_order_reviews_dataset.csv")
    sellers = pd.read_csv(f"{DATASET_DIR}/olist_sellers_dataset.csv")
    customers = pd.read_csv(f"{DATASET_DIR}/olist_customers_dataset.csv")
    
    return orders, order_items, reviews, sellers, customers

def load_ds(df, table_name):
    engine = create_engine(POSTGRES_CONN)
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        conn.execute(text(f"DROP TABLE IF EXISTS raw.{table_name} CASCADE"))
        
        df.to_sql(table_name, con=conn, schema="raw", if_exists="append", index=False)

def extract_and_load():
    olist = olist_ds()
    load_ds(olist[0], "raw_orders")
    load_ds(olist[1], "raw_order_items")
    load_ds(olist[2], "raw_reviews")
    load_ds(olist[3], "raw_sellers")
    load_ds(olist[4], "raw_customers")

with DAG(
    dag_id="olist_extract_load",
    start_date=pd.Timestamp("2026-1-1"),
    schedule_interval=None,
    catchup=False,
) as dag:

    start_task = EmptyOperator(task_id="Start")

    download_task = PythonOperator(
        task_id = "Download_Dataset",
        python_callable = download_ds
    )
    
    extract_load_task = PythonOperator(
        task_id = "Extract_and_Load",
        python_callable = extract_and_load
    )

    dbt_bronze_task  = DockerOperator(
        task_id     ="dbt_bronze",
        image       ="olist-dbt:1.0",
        command     ="dbt run --select path:models/bronze",
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

    end_task = EmptyOperator(task_id="End")

    start_task >> download_task >> extract_load_task >> dbt_bronze_task >> end_task