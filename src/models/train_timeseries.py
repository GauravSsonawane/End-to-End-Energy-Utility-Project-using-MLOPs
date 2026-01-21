import os
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
import mlflow
import mlflow.prophet

# -------------------------------
# Paths
# -------------------------------
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data/raw")
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
MODEL_DIR = os.path.join(ARTIFACTS_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

READINGS_CSV = os.path.join(RAW_DATA_DIR, "meter_readings.csv")

print("🔧 [MODULE LOAD] train_timeseries.py loaded")

def train_prophet_model(**kwargs):
    """
    Train Prophet Time Series model to forecast 'units'.
    """
    print("\n==================== TRAIN PROPHET MODEL ====================")

    if not os.path.exists(READINGS_CSV):
        raise FileNotFoundError(f"❌ Data file not found: {READINGS_CSV}")

    readings = pd.read_csv(READINGS_CSV)
    print(f"📄 [TRAIN] Loaded meter readings: {readings.shape}")

    # Prepare data for Prophet: needs 'ds' (datestamp) and 'y' (target)
    # Aggregating by date might be necessary if there are multiple readings per day,
    # or we can train on the raw timestamp if it's granular.
    # For load forecasting, typically we want hourly or daily aggregation.
    # Let's inspect the data type of reading_date briefly in our minds or assume standard format.
    # We'll convert to datetime first.
    
    readings['reading_date'] = pd.to_datetime(readings['reading_date'])
    
    # Let's aggregate by day for a clearer daily trend for this initial implementation
    # or keep it simple. Let's start with daily sum or mean if there are multiple.
    # Assuming the user wants to predict 'units'.
    
    df_prophet = readings[['reading_date', 'units']].rename(columns={'reading_date': 'ds', 'units': 'y'})
    
    # Sort just in case
    df_prophet = df_prophet.sort_values('ds')

    # Train-test split (time-based)
    train_size = int(len(df_prophet) * 0.8)
    train_df = df_prophet.iloc[:train_size]
    test_df = df_prophet.iloc[train_size:]
    
    print(f"🧪 [TRAIN] Train size: {len(train_df)}, Test size: {len(test_df)}")

    # Initialize and Train Prophet
    model = Prophet()
    # Add holidays if we had a country code, but skipping for now
    model.fit(train_df)

    # Make predictions on test set
    future = test_df[['ds']]
    forecast = model.predict(future)
    
    # Evaluation
    y_true = test_df['y'].values
    y_pred = forecast['yhat'].values
    
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    
    print(f"✅ [TRAIN] Prophet Model trained. MSE: {mse:.4f}, MAE: {mae:.4f}")

    # Save model locally
    model_path = os.path.join(MODEL_DIR, "prophet_model.pkl")
    joblib.dump(model, model_path)
    print(f"💾 [TRAIN] Model saved to: {model_path}")

    # Push metrics to XCom
    if kwargs.get("ti"):
        kwargs["ti"].xcom_push(key="mse", value=float(mse))
        kwargs["ti"].xcom_push(key="mae", value=float(mae))
    
    print("==================== END TRAIN PROPHET MODEL ====================\n")


def log_prophet_to_mlflow(**kwargs):
    """
    Logs Prophet model and metrics to MLflow.
    """
    from mlflow.tracking import MlflowClient

    print("\n==================== LOG PROPHET TO MLFLOW ====================")
    ti = kwargs.get("ti")
    if ti:
        mse = ti.xcom_pull(task_ids="train_prophet_model", key="mse")
        mae = ti.xcom_pull(task_ids="train_prophet_model", key="mae")
    else:
        mse, mae = 0.0, 0.0

    tracking_uri = "http://mlflow_server:5000"
    mlflow.set_tracking_uri(tracking_uri)

    experiment_name = "Meter_Forecasting_Prophet"
    mlflow.set_experiment(experiment_name)

    model_path = os.path.join(MODEL_DIR, "prophet_model.pkl")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")

    client = MlflowClient(tracking_uri=tracking_uri)
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        exp_id = client.create_experiment(experiment_name)
    else:
        exp_id = experiment.experiment_id

    run = client.create_run(experiment_id=exp_id)
    run_id = run.info.run_id

    # Log parameters and metrics
    client.log_param(run_id, "model_type", "Prophet")
    client.log_metric(run_id, "mse", mse)
    client.log_metric(run_id, "mae", mae)

    # Log artifact (model)
    client.log_artifact(run_id, model_path, artifact_path="model")
    
    # Also log using the native mlflow.prophet flavor if possible, but artifact is safer for now
    # mlflow.prophet.log_model(model, "prophet_model") 

    print(f"✅ [LOG] Prophet Model logged to MLflow at: {tracking_uri}")
    print(f"🔗 [LOG] Run URL: {tracking_uri}/#/experiments/{exp_id}/runs/{run_id}")
    print("==================== END LOG PROPHET TO MLFLOW ====================\n")
