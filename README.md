# Olist Delivery Delay Pipeline

A batch data pipeline that analyzes the impact of delivery delays on an e-commerce platform, covering customer ratings, seller performance, and regional trends. Built with **Airflow**, **dbt**, **PostgreSQL**, and **Metabase**, fully orchestrated via **Docker Compose**.

---

## Background & Problem Statement

Delivery delay is one of the key factors affecting customer satisfaction on e-commerce platforms. This project was built to help a platform's operations team understand:

- How much delivery delay impacts customer ratings, and at which delay stage the most significant rating drop occurs.
- How seller performance trends quarter over quarter, and which sellers show a declining trend in recent months.
- Which regions have the highest delay rates, both from the origin and destination side.
- The overall delay trend across the platform over time.

Dataset used: [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle.

---

## Architecture

The pipeline follows a **medallion architecture** (bronze → silver → gold), orchestrated by Airflow through multiple DAGs split by analysis scope, rather than a single monolithic DAG.

```
Kaggle (Olist Dataset, CSV)
        │
        ▼
Pandas (extraction & load: read csv file, parse dates, convert to sql table format, load to database (schema "raw"))
        │
        ▼
PostgreSQL - raw schema (raw_orders, raw_sellers, raw_reviews, raw_customers, raw_order_items)
        │
        ▼
dbt - Bronze (staging: stg_customers, stg_order_items, stg_orders, stg_reviews, stg_sellers)
        │
        ▼
dbt - Silver (dimensional model: dim_customers, dim_sellers, fact_orders)
        │
        ▼
dbt - Gold (data marts: 
             mart_delay_rating_impact, mart_delay_trend_platform,
             mart_regional_delay_dest_3m, mart_regional_delay_dest_at,
             mart_regional_delay_orig_3m, mart_regional_delay_orig_at,
             mart_seller_declining_trend_recent, mart_seller_declining_trend_summary,
             mart_seller_monthly_performance
           )
        │
        ▼
Metabase (dashboard: overview, rating impact, platform delay trend, seller trend, regional delay, problematic sellers)
```

Orchestration is split across several Airflow DAGs by analysis scope:

- `DAG_olist_extract_load` — extracts the dataset and loads it into the raw schema
- `DAG_olist_star_schema` — transforms bronze into silver (dim/fact)
- `DAG_olist_delay_analysis` — marts related to delay's impact on rating and platform trend
- `DAG_olist_regional_delay` — regional delay marts (origin/destination)
- `DAG_olist_seller_performance` — seller performance and decline-trend marts
- `DAG_olist_master` — orchestrator that runs/sequences the DAGs above

---

## Tech Stack

| Component | Technology |
|---|---|
| Orchestration | Apache Airflow (LocalExecutor) |
| Data transformation | dbt 1.8.0 |
| Database | PostgreSQL (database `dwh`) |
| Visualization | Metabase |
| Initial extraction & load raw | Python (Pandas) |
| Containerization | Docker & Docker Compose |

---

## Project Structure

```
delivery_batch_pipeline/
├── dags/                     # Airflow DAGs
├── datasets/                 # Raw dataset (CSV, not committed)
├── dbt/
│   ├── macros/
│   ├── models/
│   │   ├── bronze/           # Staging models
│   │   ├── silver/           # Dimensional model (dim/fact)
│   │   └── gold/             # Data marts
│   ├── dbt_project.yml
│   ├── Dockerfile 
│   └── profiles.yml
├── scripts/
│   └── init-multi-db.sh
├── .env
├── Batch Data Pipeline & Analisis Delay Pengiriman.pptx
├── docker-compose.yml 
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## How to Run

### Initial setup

Grant execute permission to the multi-database init script:

```bash
chmod +x scripts/init-multi-db.sh
```

copy the .env.example into .env

```bash
cp .env.example .env
```

fill these column with your own credential

```
KAGGLE_USERNAME = "your_kaggle_username"
KAGGLE_API_TOKEN = "your_kaggle_api_token"
```

### Running all services (first time)

```bash
docker compose up -d --build
```

This command starts every service: PostgreSQL, Airflow, dbt, and Metabase.

### Running dbt models manually (if needed)

To run the dbt manually:

```bash
docker compose exec dbt dbt run --select "models_to_run"
```

### Usefull command (if needed)

To make dbt lineage report

```bash
docker compose exec dbt dbt docs generate
```

To see the report, acces from your browser and navigate to: http://localhost:8085

```bash
docker compose exec dbt dbt docs serve --port 8080
```

---

## Service Access

**Airflow**
- URL: `http://localhost:8080` (adjust to the port set in docker-compose)
- Username: `admin`
- Password: `admin123`

**Metabase**
- URL: `http://localhost:3000` (adjust to the port set in docker-compose)
- Email: `email@email.com`
- Password: `Adminadmin123`

> The credentials above are defaults for local/demo use. Replace them before using the project outside a local development environment.

---

## Dashboard

The final dashboard is built in Metabase and covers:

- General overview (total sellers, total customers, total orders, late rate percentage)
- Delay's impact on customer rating
- Platform delay trend
- Seller performance decline trend, including a detailed table of individual declining sellers
- Regional delay rate (origin & destination, recent 3 months and all-time)

---

## Dataset

Source: [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — Kaggle.

---

## Author

Built by **Ahmad Izzan** as a final project for the **Data Engineering Bootcamp, Dibimbing (Batch 14)**.