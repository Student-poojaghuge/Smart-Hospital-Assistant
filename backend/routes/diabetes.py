from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
from pathlib import Path

router = APIRouter(
    prefix="/diabetes",
    tags=["Diabetes Prediction"]
)

# Model paths
MODEL_PATH = Path(
    r"C:\Users\hp\OneDrive\Desktop\smart_hospital_assistant\models\diabetes_model.pkl"
)

SCALER_PATH = Path(
    r"C:\Users\hp\OneDrive\Desktop\smart_hospital_assistant\models\diabetes_scaler.pkl"
)

# Load model and scaler
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    model = None
    scaler = None
    print("Diabetes model/scaler could not be loaded:", e)


class DiabetesRequest(BaseModel):
    Pregnancies: float
    Glucose: float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: float


@router.post("/predict")
def predict_diabetes(data: DiabetesRequest):

    if model is None or scaler is None:
        raise HTTPException(
            status_code=500,
            detail="Diabetes model or scaler is not available"
        )

    try:
        input_data = pd.DataFrame([{
            "Pregnancies": data.Pregnancies,
            "Glucose": data.Glucose,
            "BloodPressure": data.BloodPressure,
            "SkinThickness": data.SkinThickness,
            "Insulin": data.Insulin,
            "BMI": data.BMI,
            "DiabetesPedigreeFunction": data.DiabetesPedigreeFunction,
            "Age": data.Age
        }])

        # Scale input
        input_scaled = scaler.transform(input_data)

        # Prediction
        prediction = model.predict(input_scaled)[0]

        probability = None

        if hasattr(model, "predict_proba"):
            probability = float(
                model.predict_proba(input_scaled)[0][1]
            )

        return {
            "prediction": int(prediction),
            "predicted_class": (
                "Diabetes predicted"
                if prediction == 1
                else "No diabetes predicted"
            ),
            "probability": probability,
            "notice": (
                "This is an educational ML prediction "
                "and not a medical diagnosis."
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )