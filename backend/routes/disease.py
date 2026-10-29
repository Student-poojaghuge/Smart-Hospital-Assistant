
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd
import joblib
from pathlib import Path

from database.database import get_db
from database.models import Prediction

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
    patient_id: int = Field(gt=0)
    symptoms: list[str] = Field(min_length=1)


@router.post("/predict")
def predict_disease(
    data: DiseaseRequest,
    db: Session = Depends(get_db)
):
    if model is None or feature_columns is None:
        raise HTTPException(
            status_code=500,
            detail="Disease prediction model is not available"
        )

    try:
        user_symptoms = set()

        for symptom in data.symptoms:
            if not symptom.strip():
                continue

            cleaned = symptom.strip().lower().replace(" ", "_")
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

        # Confirm that the patient exists.
        from database.models import Patient

        patient = db.query(Patient).filter(
            Patient.patient_id == data.patient_id
        ).first()

        if patient is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found."
            )

        prediction = str(model.predict(input_data)[0])

        confidence = None
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(input_data)[0]
            confidence = float(max(probabilities))

        # Save the successful prediction.
        record = Prediction(
            patient_id=data.patient_id,
            prediction_date=datetime.now().isoformat(),
            prediction_type="Disease Prediction",
            predicted_result=prediction,
            confidence_score=(
                str(round(confidence, 4))
                if confidence is not None else None
            ),
            model_name=type(model).__name__,
            explanation="Matched symptoms: " + ", ".join(
                sorted(matched_symptoms)
            )
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "prediction_id": record.prediction_id,
            "patient_id": record.patient_id,
            "predicted_disease": prediction,
            "confidence": confidence,
            "matched_symptoms": matched_symptoms,
            "saved_to_database": True,
            "notice": (
                "Educational ML prediction only; this is not a medical "
                "diagnosis. Consult a qualified healthcare professional."
            )
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Disease prediction failed: {str(e)}"
        )
