from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from database.database import get_db
from database.models import EmergencyAssessment


router = APIRouter(
    prefix="/emergency",
    tags=["Emergency Risk Assessment"]
)


class EmergencyRequest(BaseModel):
    patient_id: int
    heart_rate: int | None = None
    systolic_bp: int | None = None
    diastolic_bp: int | None = None
    temperature: float | None = None
    oxygen_level: int | None = None
    symptoms: str = ""


@router.post("/assess")
def emergency_assessment(
    data: EmergencyRequest,
    db: Session = Depends(get_db)
):
    try:
        score = 0
        reasons = []

        symptoms = data.symptoms.lower()

        # Symptom checks
        emergency_words = [
            "chest pain",
            "breathing difficulty",
            "difficulty breathing",
            "unconscious",
            "fainting",
            "confusion",
            "severe bleeding",
            "seizure"
        ]

        for word in emergency_words:
            if word in symptoms:
                score += 3
                reasons.append(f"Emergency symptom: {word}")

        # Oxygen
        if data.oxygen_level is not None:
            if data.oxygen_level <= 92:
                score += 4
                reasons.append(
                    f"Low oxygen level: {data.oxygen_level}%"
                )
            elif data.oxygen_level <= 94:
                score += 2
                reasons.append(
                    f"Reduced oxygen level: {data.oxygen_level}%"
                )

        # Blood pressure
        if (
            data.systolic_bp is not None
            and data.diastolic_bp is not None
        ):
            if (
                data.systolic_bp > 180
                or data.diastolic_bp > 120
            ):
                score += 4
                reasons.append(
                    f"Very high BP: "
                    f"{data.systolic_bp}/{data.diastolic_bp}"
                )

            elif (
                data.systolic_bp < 90
                or data.diastolic_bp < 60
            ):
                score += 3
                reasons.append(
                    f"Low BP: "
                    f"{data.systolic_bp}/{data.diastolic_bp}"
                )

        # Heart rate
        if data.heart_rate is not None:
            if data.heart_rate >= 130:
                score += 2
                reasons.append(
                    f"High heart rate: {data.heart_rate} bpm"
                )

            elif data.heart_rate <= 45:
                score += 2
                reasons.append(
                    f"Low heart rate: {data.heart_rate} bpm"
                )

        # Temperature
        if data.temperature is not None:
            if data.temperature >= 39:
                score += 2
                reasons.append(
                    f"High temperature: {data.temperature} °C"
                )

        # Risk level
        if score >= 6:
            emergency_level = "HIGH"
            recommendation = (
                "Seek immediate medical attention."
            )

        elif score >= 3:
            emergency_level = "MODERATE"
            recommendation = (
                "Arrange prompt medical evaluation "
                "and monitor the symptoms."
            )

        else:
            emergency_level = "LOW"
            recommendation = (
                "No major emergency rule was triggered "
                "by the supplied information."
            )

        if not reasons:
            reasons.append(
                "No emergency warning signs detected "
                "from the supplied inputs."
            )

        explanation = "; ".join(reasons)

        # Save assessment to database
        assessment = EmergencyAssessment(
            patient_id=data.patient_id,
            assessment_date=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            heart_rate=data.heart_rate,
            systolic_bp=data.systolic_bp,
            diastolic_bp=data.diastolic_bp,
            temperature=(
                str(data.temperature)
                if data.temperature is not None
                else None
            ),
            oxygen_level=data.oxygen_level,
            symptoms=data.symptoms,
            risk_score=str(score),
            emergency_level=emergency_level,
            ai_recommendation=(
                recommendation +
                " Reason: " +
                explanation
            )
        )

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        return {
            "assessment_id": assessment.assessment_id,
            "patient_id": data.patient_id,
            "risk_score": score,
            "emergency_level": emergency_level,
            "reasons": reasons,
            "recommendation": recommendation,
            "notice": (
                "This is an educational rule-based "
                "screening result, not a medical diagnosis."
            )
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Assessment failed: {str(e)}"
        )