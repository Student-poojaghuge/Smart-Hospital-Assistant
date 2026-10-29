
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel, Field

from database.database import get_db
from database.models import Patient, User, EmergencyAssessment
from backend.services.auth_dependency import get_current_user


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


# =========================
# REQUEST MODEL
# =========================

class PatientProfileRequest(BaseModel):
    user_id: int = Field(gt=0)
    age: int = Field(ge=0, le=120)
    gender: str = Field(min_length=1, max_length=30)
    phone: str = Field(min_length=7, max_length=20)
    blood_group: str = Field(min_length=1, max_length=10)
    address: str = Field(min_length=1, max_length=500)


# =========================
# AUTHORIZATION HELPER
# =========================

def verify_patient_access(
    requested_user_id: int,
    current_user: dict
):
    try:
        authenticated_user_id = int(current_user["user_id"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if authenticated_user_id != requested_user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this patient's data"
        )


# =========================
# CREATE PATIENT PROFILE
# =========================

@router.post("/profile")
def create_patient_profile(
    request: PatientProfileRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Users can create profiles only for themselves.
    verify_patient_access(request.user_id, current_user)

    user = db.query(User).filter(
        User.user_id == request.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    existing_patient = db.query(Patient).filter(
        Patient.user_id == request.user_id
    ).first()

    if existing_patient:
        raise HTTPException(
            status_code=400,
            detail="Patient profile already exists"
        )

    patient = Patient(
        user_id=request.user_id,
        age=request.age,
        gender=request.gender.strip(),
        phone=request.phone.strip(),
        blood_group=request.blood_group.strip(),
        address=request.address.strip()
    )

    try:
        db.add(patient)
        db.commit()
        db.refresh(patient)

        return {
            "message": "Patient profile created successfully",
            "patient_id": patient.patient_id,
            "user_id": patient.user_id
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create patient profile"
        )


# =========================
# PATIENT DASHBOARD
# =========================

@router.get("/dashboard/{user_id}")
def get_patient_dashboard(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Prevent patients from viewing another user's dashboard.
    verify_patient_access(user_id, current_user)

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    patient = db.query(Patient).filter(
        Patient.user_id == user_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    # Fetch the latest health assessment.
    latest_assessment = db.query(EmergencyAssessment).filter(
        EmergencyAssessment.patient_id == patient.patient_id
    ).order_by(
        desc(EmergencyAssessment.assessment_date)
    ).first()

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
