from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse

from api.schemas.prediction import AthleteInput
from database.database import SessionLocal
from database.models import Prediction

import pandas as pd
import joblib

from io import BytesIO

app = FastAPI(
    title="Athlete Recovery Prediction API",
    version="1.0"
)

# =====================================================
# Load ML Model
# =====================================================

model = joblib.load("models/model.pkl")

# =====================================================
# Home
# =====================================================

@app.get("/")
def home():
    return {
        "message": "Athlete Recovery Prediction API is Running"
    }

# =====================================================
# Health Check
# =====================================================

@app.get("/health")
def health():
    return {
        "status": "Healthy"
    }

# =====================================================
# Single Prediction
# =====================================================

@app.post("/predict")
def predict(data: AthleteInput):

    df = pd.DataFrame([{
        "Day": 1,
        "Week": 1,
        "Day_of_Week": "Monday",

        "Age": data.Age,
        "Gender": data.Gender,
        "Sport_Type": data.Sport_Type,
        "Training_Type": data.Training_Type,
        "Training_Duration_Min": data.Training_Duration_Min,
        "Training_Intensity": data.Training_Intensity,
        "Sleep_Duration_Hours": data.Sleep_Duration_Hours,
        "Caffeine_Intake_mg": data.Caffeine_Intake_mg,
        "Stress_Level": data.Stress_Level,
        "Resting_Heart_Rate": data.Resting_Heart_Rate,
        "HRV_ms": data.HRV_ms,
        "Mood_Score": data.Mood_Score,
        "Muscle_Soreness": data.Muscle_Soreness,
        "Energy_Level": data.Energy_Level
    }])

    prediction = float(model.predict(df)[0])

    db = SessionLocal()

    new_prediction = Prediction(
        Age=data.Age,
        Gender=data.Gender,
        Sport_Type=data.Sport_Type,
        Training_Type=data.Training_Type,
        Training_Duration_Min=data.Training_Duration_Min,
        Training_Intensity=data.Training_Intensity,
        Sleep_Duration_Hours=data.Sleep_Duration_Hours,
        Caffeine_Intake_mg=data.Caffeine_Intake_mg,
        Stress_Level=data.Stress_Level,
        Resting_Heart_Rate=data.Resting_Heart_Rate,
        HRV_ms=data.HRV_ms,
        Mood_Score=data.Mood_Score,
        Muscle_Soreness=data.Muscle_Soreness,
        Energy_Level=data.Energy_Level,
        Prediction=prediction
    )

    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    db.close()

    return {
        "prediction": round(prediction, 2)
    }

# =====================================================
# Past Predictions
# =====================================================

@app.get("/past-predictions")
def get_past_predictions():

    db = SessionLocal()

    predictions = db.query(Prediction).all()

    result = []

    for p in predictions:

        result.append({
            "id": p.id,
            "Age": p.Age,
            "Gender": p.Gender,
            "Sport_Type": p.Sport_Type,
            "Training_Type": p.Training_Type,
            "Prediction": round(float(p.Prediction), 2)
        })

    db.close()

    return result

# =====================================================
# Batch Prediction
# =====================================================

@app.post("/batch-predict")
async def batch_predict(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)

    if "Athlete_ID" in df.columns:
        df = df.drop(columns=["Athlete_ID"])

    if "Recovery_Score" in df.columns:
        df = df.drop(columns=["Recovery_Score"])

    if "Day" not in df.columns:
        df["Day"] = 1

    if "Week" not in df.columns:
        df["Week"] = 1

    if "Day_of_Week" not in df.columns:
        df["Day_of_Week"] = "Monday"

    stress_map = {
        "Low": 3,
        "Medium": 6,
        "High": 9
    }

    if df["Stress_Level"].dtype == object:
        df["Stress_Level"] = df["Stress_Level"].map(stress_map)

    predictions = model.predict(df)

    df["Predicted_Recovery_Score"] = predictions.round(2)

    output = BytesIO()

    df.to_csv(output, index=False)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=batch_predictions.csv"
        }
    )