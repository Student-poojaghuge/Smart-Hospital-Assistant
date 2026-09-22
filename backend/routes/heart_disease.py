from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
from pathlib import Path

router = APIRouter(
    prefix="/heart-disease",
    tags=["Heart Disease Prediction"]
)

# Model path
MODEL_PATH = Path(
    r"C:\Users\hp\OneDrive\Desktop\smart_hospital_assistant\models\heart_disease_model.pkl"
)

# Load model
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print("Heart disease model could not be loaded:", e)


class HeartDiseaseRequest(BaseModel):
    age: float
    sex: float
    cp: float
    trestbps: float
    chol: float
    fbs: float
    restecg: float
    thalch: float
    exang: float
    oldpeak: float
    slope: float
    ca: float
    thal: float


@router.post("/predict")
def predict_heart_disease(data: HeartDiseaseRequest):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Heart disease model is not available"
        )

    try:
        input_data = pd.DataFrame([{
            "age": data.age,
            "sex": data.sex,
            "cp": data.cp,
            "trestbps": data.trestbps,
            "chol": data.chol,
            "fbs": data.fbs,
            "restecg": data.restecg,
            "thalch": data.thalch,
            "exang": data.exang,
            "oldpeak": data.oldpeak,
            "slope": data.slope,
            "ca": data.ca,
            "thal": data.thal
        }])

        prediction = model.predict(input_data)[0]

        probability = None

        if hasattr(model, "predict_proba"):
            probability = float(model.predict_proba(input_data)[0][1])

        return {
            "prediction": int(prediction),
            "predicted_class": (
                "Heart disease predicted"
                if prediction == 1
                else "No heart disease predicted"
            ),
            "probability": probability,
            "notice": (
                "This is an educational ML prediction and "
                "not a medical diagnosis."
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )