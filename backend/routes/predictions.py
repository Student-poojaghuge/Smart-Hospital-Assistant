
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Prediction, Patient

router = APIRouter(
    prefix="/predictions",
    tags=["Prediction History"]
)


@router.get("/{patient_id}")
def get_prediction_history(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found."
        )

    records = (
        db.query(Prediction)
        .filter(Prediction.patient_id == patient_id)
        .order_by(Prediction.prediction_id.desc())
        .all()
    )

    return {
        "patient_id": patient_id,
        "total_predictions": len(records),
        "predictions": [
            {
                "prediction_id": record.prediction_id,
                "prediction_date": record.prediction_date,
                "prediction_type": record.prediction_type,
                "predicted_result": record.predicted_result,
                "confidence_score": record.confidence_score,
                "model_name": record.model_name,
                "explanation": record.explanation
            }
            for record in records
        ]
    }
