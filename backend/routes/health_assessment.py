from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database.database import get_db
from database.models import Patient, EmergencyAssessment


router = APIRouter(
    prefix="/health",
    tags=["Health Assessment"]
)


class HealthAssessmentRequest(BaseModel):
    user_id: int
    heart_rate: Optional[float] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    temperature: Optional[float] = None
    oxygen_level: Optional[float] = None
    symptoms: Optional[str] = None


def calculate_risk(
    heart_rate=None,
    systolic_bp=None,
    diastolic_bp=None,
    temperature=None,
    oxygen_level=None,
    symptoms=None
):
    risk_score = 0
    warnings = []

    # Heart rate screening
    if heart_rate is not None:
        if heart_rate < 50 or heart_rate > 120:
            risk_score += 2
            warnings.append("Abnormal heart rate")

    # Blood pressure screening
    if systolic_bp is not None and diastolic_bp is not None:
        if systolic_bp >= 180 or diastolic_bp >= 120:
            risk_score += 3
            warnings.append("Very high blood pressure")
        elif systolic_bp >= 140 or diastolic_bp >= 90:
            risk_score += 1
            warnings.append("Elevated blood pressure")
        elif systolic_bp < 90:
            risk_score += 2
            warnings.append("Low systolic blood pressure")

    # Temperature screening
    if temperature is not None:
        if temperature >= 103 or temperature < 95:
            risk_score += 2
            warnings.append("Abnormal body temperature")
        elif temperature >= 100.4:
            risk_score += 1
            warnings.append("Elevated body temperature")

    # Oxygen level screening
    if oxygen_level is not None:
        if oxygen_level < 90:
            risk_score += 3
            warnings.append("Very low oxygen level")
        elif oxygen_level < 94:
            risk_score += 2
            warnings.append("Low oxygen level")

    # Symptom keyword screening
    if symptoms:
        emergency_keywords = [
            "chest pain",
            "difficulty breathing",
            "shortness of breath",
            "unconscious",
            "severe bleeding",
            "stroke"
        ]

        symptom_text = symptoms.lower()

        for keyword in emergency_keywords:
            if keyword in symptom_text:
                risk_score += 3
                warnings.append(f"Emergency symptom reported: {keyword}")

    # Risk classification
    if risk_score >= 5:
        emergency_level = "High Risk"
    elif risk_score >= 2:
        emergency_level = "Moderate Risk"
    else:
        emergency_level = "Low Risk"

    if emergency_level == "High Risk":
        recommendation = (
            "Seek immediate medical attention. "
            "Contact local emergency services if symptoms are severe."
        )
    elif emergency_level == "Moderate Risk":
        recommendation = (
            "Consult a qualified healthcare professional promptly "
            "for further evaluation."
        )
    else:
        recommendation = (
            "No major warning detected by this basic screening rule. "
            "Continue monitoring and consult a healthcare professional "
            "if symptoms persist."
        )

    return risk_score, emergency_level, recommendation, warnings


@router.post("/assessment")
def create_health_assessment(
    health_data: HealthAssessmentRequest,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.user_id == health_data.user_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    risk_score, emergency_level, recommendation, warnings = calculate_risk(
        heart_rate=health_data.heart_rate,
        systolic_bp=health_data.systolic_bp,
        diastolic_bp=health_data.diastolic_bp,
        temperature=health_data.temperature,
        oxygen_level=health_data.oxygen_level,
        symptoms=health_data.symptoms
    )

    new_assessment = EmergencyAssessment(
        patient_id=patient.patient_id,
        assessment_date=datetime.now(),
        heart_rate=health_data.heart_rate,
        systolic_bp=health_data.systolic_bp,
        diastolic_bp=health_data.diastolic_bp,
        temperature=health_data.temperature,
        oxygen_level=health_data.oxygen_level,
        symptoms=health_data.symptoms,
        risk_score=risk_score,
        emergency_level=emergency_level,
        ai_recommendation=recommendation
    )

    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)

    return {
        "message": "Health assessment completed successfully",
        "assessment_id": new_assessment.assessment_id,
        "patient_id": patient.patient_id,
        "risk_score": risk_score,
        "emergency_level": emergency_level,
        "recommendation": recommendation,
        "warnings": warnings
    }


@router.get("/assessment/{user_id}")
def get_health_assessments(
    user_id: int,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.user_id == user_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    assessments = db.query(EmergencyAssessment).filter(
        EmergencyAssessment.patient_id == patient.patient_id
    ).order_by(
        EmergencyAssessment.assessment_date.desc()
    ).all()

    return {
        "message": "Health assessment history fetched successfully",
        "patient_id": patient.patient_id,
        "total_assessments": len(assessments),
        "assessments": [
            {
                "assessment_id": assessment.assessment_id,
                "assessment_date": assessment.assessment_date,
                "heart_rate": assessment.heart_rate,
                "systolic_bp": assessment.systolic_bp,
                "diastolic_bp": assessment.diastolic_bp,
                "temperature": assessment.temperature,
                "oxygen_level": assessment.oxygen_level,
                "symptoms": assessment.symptoms,
                "risk_score": assessment.risk_score,
                "emergency_level": assessment.emergency_level,
                "ai_recommendation": assessment.ai_recommendation
            }
            for assessment in assessments
        ]
    }