# ⚙️ End-to-End Energy Utility MLOps Platform

## 📌 Project Overview
This repository implements an end-to-end MLOps pipeline for **Energy Utility Load Forecasting**. It demonstrates how production-ready ML systems are built by combining data ingestion, orchestration, experiment tracking, model serving, and containerized infrastructure.

**Key Features:**
*   **Forecasting:** Predicts future energy consumption using multiple approaches.
    *   **Baseline:** Linear Regression (using voltage, power factor, temperature).
    *   **Advanced:** **Time Series Forecasting (Prophet)** for seasonal trend analysis.
*   **Orchestration:** **Apache Airflow** manages the entire pipeline (Ingestion → Training → Logging).
*   **Tracking:** **MLflow** tracks experiments, metrics (MSE, MAE), and stores model artifacts.
*   **Serving:** **FastAPI** serves the best model for real-time predictions.
*   **Infrastructure:** Fully containerized with **Docker Compose**.

---

## � How to Run

### 1. Start the Project
Run this command from the project root:
```bash
docker-compose -f infrastructure/docker-compose.yml up -d --build
```

### 2. Access Services
| Service | URL | Credentials |
| :--- | :--- | :--- |
| **Apache Airflow** | [http://localhost:38081](http://localhost:38081) | `admin` / `admin` |
| **MLflow UI** | [http://localhost:5050](http://localhost:5050) | N/A |
| **Model API** | [http://localhost:5501/docs](http://localhost:5501/docs) | N/A |

### 3. Trigger Training
1.  Open Airflow ([http://localhost:38081](http://localhost:38081)).
2.  Trigger the **`meter_training_pipeline_dag`**.
3.  This will train both the **Regression** and **Prophet** models.
4.  Check results in the MLflow UI.

---

## 🧱 Architecture

### Core Stack
*   **Airflow:** Orchestration (DAGs in `airflow_dags/`).
*   **MLflow:** Model Registry & Tracking (Artifacts in `mlflow_artifacts/`).
*   **FastAPI:** Prediction Service (`src/api/`).
*   **PostgreSQL:** Backend database.

### Key Files
*   `src/models/train.py`: Linear Regression training logic.
*   `src/models/train_timeseries.py`: **[NEW]** Prophet Time Series training logic.
*   `airflow_dags/training_pipeline_dag.py`: The automation pipeline.
*   `infrastructure/docker-compose.yml`: Infrastructure configuration.

---

## � Troubleshooting
**First Run (Database Initialization):**
If Airflow fails to start, you may need to initialize the db:
```bash
docker-compose -f infrastructure/docker-compose.yml run --rm airflow_webserver airflow db migrate
docker-compose -f infrastructure/docker-compose.yml run --rm airflow_webserver airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```
