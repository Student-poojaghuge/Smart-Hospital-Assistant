from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
from pathlib import Path

router = APIRouter(
    prefix="/disease",
    tags=["Disease Prediction"]
)

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "models" / "disease_prediction_model.pkl"
FEATURES_PATH = BASE_DIR / "models" / "disease_prediction_features.pkl"

try:
    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURES_PATH)
except Exception as e:
    model = None
    feature_columns = None
    print("Disease prediction model could not be loaded:", e)


class DiseaseRequest(BaseModel):
    symptoms: list[str]


@router.post("/predict")
def predict_disease(data: DiseaseRequest):

    if model is None or feature_columns is None:
        raise HTTPException(
            status_code=500,
            detail="Disease prediction model is not available"
        )

    try:
        user_symptoms = set()

        for symptom in data.symptoms:
            cleaned = (
                symptom.strip()
                .lower()
                .replace(" ", "_")
            )

            cleaned = "_".join(
                part for part in cleaned.split("_") if part
            )

            user_symptoms.add(cleaned)

        input_data = pd.DataFrame(
            0,
            index=[0],
            columns=feature_columns
        )

        matched_symptoms = []

        for symptom in user_symptoms:
            if symptom in input_data.columns:
                input_data.loc[0, symptom] = 1
                matched_symptoms.append(symptom)

        if not matched_symptoms:
            raise HTTPException(
                status_code=400,
                detail="None of the supplied symptoms match the supported symptom list."
            )

        prediction = model.predict(input_data)[0]

        confidence = None

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(input_data)[0]
            confidence = float(max(probabilities))

        return {
            "predicted_disease": str(prediction),
            "confidence": confidence,
            "matched_symptoms": matched_symptoms,
            "notice": (
                "This is an educational ML prediction and "
                "not a medical diagnosis. Consult a qualified "
                "healthcare professional for medical evaluation."
            )
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Disease prediction failed: {str(e)}"
        )