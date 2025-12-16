# from pathlib import Path
# import os

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# import joblib
# import pandas as pd

# app = FastAPI(title="Electricity Load Prediction API", 
#               description="Advanced ML-powered electricity consumption forecasting",
#               version="1.0.0")

# # --------------------------------------------------
# # Paths
# # --------------------------------------------------
# BASE_DIR = Path(__file__).resolve().parent.parent       # src/
# API_DIR = BASE_DIR / "api"
# TEMPLATES_DIR = API_DIR / "templates"

# # Load Linear Regression model path from env or default
# MODEL_PATH = Path(
#     os.getenv(
#         "MODEL_PATH",
#         BASE_DIR / "models" / "artifacts" / "models" / "linear_regression_model.pkl",
#     )
# )

# print(f"🔧 [API] BASE_DIR       = {BASE_DIR}")
# print(f"🔧 [API] TEMPLATES_DIR  = {TEMPLATES_DIR}")
# print(f"🔧 [API] MODEL_PATH     = {MODEL_PATH}")

# # --------------------------------------------------
# # Load model
# # --------------------------------------------------
# if not MODEL_PATH.exists():
#     raise RuntimeError(f"❌ Linear regression model file not found at: {MODEL_PATH}")

# model = joblib.load(MODEL_PATH)
# print("✅ [API] Linear regression model loaded successfully.")

# # --------------------------------------------------
# # CORS
# # --------------------------------------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --------------------------------------------------
# # Static files
# # --------------------------------------------------
# if not TEMPLATES_DIR.exists():
#     raise RuntimeError(f"❌ Templates directory not found at: {TEMPLATES_DIR}")

# app.mount("/static", StaticFiles(directory=str(TEMPLATES_DIR)), name="static")

# # --------------------------------------------------
# # Request schema – matches features used for training
# # --------------------------------------------------
# class MeterFeatures(BaseModel):
#     voltage: float
#     temperature: float
#     power_factor: float
#     load_kw: float
#     frequency_hz: float

# # --------------------------------------------------
# # Prediction endpoint
# # --------------------------------------------------
# @app.post("/predict")
# def predict(features: MeterFeatures):
#     try:
#         # Build dataframe in the same order as training
#         X = pd.DataFrame([{
#             "voltage": features.voltage,
#             "temperature": features.temperature,
#             "power_factor": features.power_factor,
#             "load_kw": features.load_kw,
#             "frequency_hz": features.frequency_hz,
#         }])

#         units_pred = model.predict(X)[0]

#         return {
#             "predicted_units": float(units_pred),
#         }

#     except Exception as e:
#         print(f"❌ [API] Error during prediction: {e}")
#         raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

# # --------------------------------------------------
# # Health check endpoint
# # --------------------------------------------------
# @app.get("/health")
# def health_check():
#     return {"status": "healthy", "model_loaded": True}

# # --------------------------------------------------
# # Root – serve meter.html
# # --------------------------------------------------
# @app.get("/", response_class=HTMLResponse)
# def home():
#     html_path = TEMPLATES_DIR / "meter.html"
#     if not html_path.exists():
#         raise HTTPException(
#             status_code=500,
#             detail=f"HTML template not found at {html_path}",
#         )

#     with open(html_path, "r", encoding="utf-8") as f:
#         return f.read()


from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="SmartGrid UI")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def ui_root(request: Request):
    """
    Render the dashboard UI (meter.html).
    """
    return templates.TemplateResponse("meter.html", {"request": request})
