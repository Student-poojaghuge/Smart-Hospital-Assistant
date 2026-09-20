from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.models import Patient, User, EmergencyAssessment
from sqlalchemy import desc

from database.database import get_db
from database.models import Patient, User

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


class PatientProfileRequest(BaseModel):
    user_id: int
    age: int
    gender: str
    phone: str
    blood_group: str
    address: str


@router.get("/dashboard/{user_id}")
def get_patient_dashboard(
    user_id: int,
    db: Session = Depends(get_db)
):
    # Find patient profile
    patient = db.query(Patient).filter(
        Patient.user_id == user_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    # Find user details
    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    # Find latest health assessment
    latest_assessment = db.query(EmergencyAssessment).filter(
        EmergencyAssessment.patient_id == patient.patient_id
    ).order_by(
        desc(EmergencyAssessment.assessment_date)
    ).first()

    # Prepare latest assessment data
    latest_health_data = None

    if latest_assessment:
        latest_health_data = {
            "assessment_id": latest_assessment.assessment_id,
            "assessment_date": latest_assessment.assessment_date,
            "heart_rate": latest_assessment.heart_rate,
            "systolic_bp": latest_assessment.systolic_bp,
            "diastolic_bp": latest_assessment.diastolic_bp,
            "temperature": latest_assessment.temperature,
            "oxygen_level": latest_assessment.oxygen_level,
            "symptoms": latest_assessment.symptoms,
            "risk_score": latest_assessment.risk_score,
            "emergency_level": latest_assessment.emergency_level,
            "ai_recommendation": latest_assessment.ai_recommendation
        }

    return {
        "message": "Patient dashboard data fetched successfully",

        "patient": {
            "patient_id": patient.patient_id,
            "name": user.name,
            "email": user.email,
            "age": patient.age,
            "gender": patient.gender,
            "phone": patient.phone,
            "blood_group": patient.blood_group,
            "address": patient.address
        },

        "latest_health_assessment": latest_health_data,

        "modules": {
            "health_assessment": "Available",
            "risk_prediction": "Available",
            "appointments": "Coming soon",
            "medical_records": "Coming soon",
            "medicine_information": "Coming soon",
            "medical_ai_assistant": "Coming soon"
        }
    }