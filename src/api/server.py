# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# import joblib
# import os
# import pandas as pd

# app = FastAPI()

# # --------------------------
# # Load model + encoder
# # --------------------------
# MODEL_PATH = os.getenv("MODEL_PATH", "src/models/artifacts/models/logistic_regression_model.pkl")
# ENCODER_PATH = os.getenv("ENCODER_PATH", "src/models/artifacts/models/encoder.pkl")

# print(f"🔧 [API] Loading model from: {MODEL_PATH}")
# print(f"🔧 [API] Loading encoder from: {ENCODER_PATH}")

# model = joblib.load(MODEL_PATH)
# encoder = joblib.load(ENCODER_PATH)

# print("✅ [API] Model and encoder loaded successfully.")

# # --------------------------
# # CORS
# # --------------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --------------------------
# # Serve static HTML
# # --------------------------
# app.mount("/static", StaticFiles(directory="src/api/templates"), name="static")


# class TitanicFeatures(BaseModel):
#     age: float
#     sex: str          # "male" / "female"
#     who: str          # "man" / "woman" / "child"
#     pclass: int       # 1 / 2 / 3
#     fare: float
#     embarked: str     # "S" / "C" / "Q"


# @app.post("/predict")
# def predict(features: TitanicFeatures):
#     """
#     Make a single prediction using the same preprocessing
#     as the training pipeline.
#     """

#     # Build DataFrame with one row
#     df = pd.DataFrame([{
#         "age": features.age,
#         "sex": features.sex,
#         "who": features.who,
#         "pclass": features.pclass,
#         "fare": features.fare,
#         "embarked": features.embarked,
#     }])

#     # Handle missing values (mirror train.py)
#     df["age"] = df["age"].fillna(df["age"].median())
#     df["fare"] = df["fare"].fillna(df["fare"].median())
#     df["embarked"] = df["embarked"].fillna("S")

#     # Encode categorical
#     cat_features = ["sex", "who", "embarked"]
#     X_cat = encoder.transform(df[cat_features])
#     X_cat_df = pd.DataFrame(X_cat, columns=encoder.get_feature_names_out(cat_features))

#     # Numeric
#     X_num = df.drop(columns=cat_features).reset_index(drop=True)

#     # Final feature matrix
#     X_prepared = pd.concat([X_num, X_cat_df.reset_index(drop=True)], axis=1)

#     # Predict
#     pred = int(model.predict(X_prepared)[0])
#     prob_survive = float(model.predict_proba(X_prepared)[0][1])  # probability of class 1

#     return {
#         "prediction": pred,
#         "probability": prob_survive,
#     }


# @app.get("/", response_class=HTMLResponse)
# def home():
#     with open("src/api/templates/index.html", "r") as f:
#         return f.read()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import joblib
import os
import pandas as pd

app = FastAPI()

# ----------------------------------------
# CORS (unchanged)
# ----------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# TEMPLATE ENGINE + STATIC FILES
# ----------------------------------------
templates = Jinja2Templates(directory="src/api/templates")

app.mount(
    "/static",
    StaticFiles(directory="src/api/static"),
    name="static"
)

# ----------------------------------------
# MODEL LOADING (unchanged)
# ----------------------------------------
MODEL_PATH = os.getenv("MODEL_PATH",
                       "src/models/artifacts/models/logistic_regression_model.pkl")
ENCODER_PATH = os.getenv("ENCODER_PATH",
                         "src/models/artifacts/models/encoder.pkl")

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)


# ----------------------------------------
# INPUT MODEL (unchanged)
# ----------------------------------------
class InputData(BaseModel):
    pclass: int
    sex: int
    age: float
    fare: float
    embarked: str


@app.post("/predict")
def predict(data: InputData):
    df = pd.DataFrame([data.dict()])
    cat_cols = ["embarked"]
    df_encoded = encoder.transform(df[cat_cols])
    df_num = df.drop(columns=cat_cols)

    X_prepared = pd.concat([
        df_num.reset_index(drop=True),
        pd.DataFrame(df_encoded, columns=encoder.get_feature_names_out(cat_cols))
    ], axis=1)

    pred = int(model.predict(X_prepared)[0])
    prob_survive = float(model.predict_proba(X_prepared)[0][1])

    return {
        "prediction": pred,
        "probability": prob_survive,
    }


# ----------------------------------------
# DASHBOARD UI ROUTE
# ----------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Serve the dashboard UI (meter.html) while keeping model/predict logic unchanged.
    """
    return templates.TemplateResponse("meter.html", {"request": request})
