to create user in AIrflow "airflow users create \
  --username admin \
  --password admin \
  --firstname admin \
  --lastname user \
  --role Admin \
  --email admin@example.com"
  run in "docker exec -it airflow_stack bash
"

run it using docker-compose up -d (change username and password in infrastructure/docker-compose )


⚙️ End-to-End MLOps Platform (Forecasting & Classification)
📌 Project Overview

This repository implements an end-to-end MLOps pipeline across two representative machine learning domains:

Electricity / Smart-Meter Load Forecasting (Regression)

The project demonstrates how production-ready ML systems are built by combining data ingestion, orchestration, experiment tracking, model serving, and containerized infrastructure using modern MLOps tools.

🧱 Architecture at a Glance

Core Stack

Airflow – Pipeline orchestration

MLflow – Experiment tracking & artifact management

FastAPI – Model serving & lightweight UI

PostgreSQL – Data storage & MLflow backend

Docker Compose – Reproducible infrastructure

📂 Key Components & Entry Points
🔹 Orchestration

Airflow DAGs:

training_pipeline_dag.py – Meter forecasting training pipeline

Additional DAGs in airflow_dags/

DAGs orchestrate ingestion → training → MLflow logging using PythonOperator and XComs.

🔹 Model Training

Meter Forecasting (train.py)

Linear Regression model

Features: voltage, temperature, power factor, load, frequency

Metrics: MSE, R²

Metric: Accuracy

🔹 Data Ingestion

Raw CSVs stored under raw/

ingestion.py:

Loads CSVs into Postgres raw tables

Performs basic quality checks (file existence, non-empty tables)

🔹 Experiment Tracking

MLflow Server

Tracks runs, metrics, and artifacts

Artifact root: mlflow_artifacts/

Shared across Airflow, MLflow, and API containers

🔹 Serving & UI

FastAPI app (main.py)

Serves predictions (model loading via MODEL_PATH)

Renders a lightweight dashboard (meter.html)

API container exposed via Docker Compose

🗄️ Data & Storage Layer

PostgreSQL

Stores raw ingested datasets

Optionally acts as MLflow backend store

Artifacts

MLflow artifacts persisted in mlflow_artifacts/

Local models stored under models/

📊 Observability & Monitoring

Airflow UI

DAG scheduling, task logs, execution lineage

MLflow UI

Experiments, metrics, artifacts, model versions

Drift Monitoring (Planned)

drift_detector.py exists as a placeholder for future data/model drift detection

🔁 Reproducibility & Reliability Features

✔ Fully containerized runtime (Docker Compose)
✔ Centralized artifact & metric tracking via MLflow
✔ Pipeline lineage and execution history via Airflow
✔ Shared artifact store across services
✔ Explicit metric passing using XComs
✔ Basic data quality checks at ingestion
