from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database.database import get_db
from database.models import Doctor, User


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


class DoctorRegistrationRequest(BaseModel):
    user_id: int
    specialization: str
    qualification: str
    experience: int
    phone: str
    hospital_name: str


@router.post("/register")
def register_doctor(
    doctor_data: DoctorRegistrationRequest,
    db: Session = Depends(get_db)
):
    # Check whether the user exists
    user = db.query(User).filter(
        User.user_id == doctor_data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check whether a doctor profile already exists
    existing_doctor = db.query(Doctor).filter(
        Doctor.user_id == doctor_data.user_id
    ).first()

    if existing_doctor:
        raise HTTPException(
            status_code=400,
            detail="Doctor profile already exists"
        )

    # Create doctor profile
    new_doctor = Doctor(
        user_id=doctor_data.user_id,
        specialization=doctor_data.specialization,
        qualification=doctor_data.qualification,
        experience=doctor_data.experience,
        phone=doctor_data.phone,
        hospital_name=doctor_data.hospital_name
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return {
        "message": "Doctor registered successfully",
        "doctor_id": new_doctor.doctor_id,
        "user_id": new_doctor.user_id
    }
@router.get("/")
def get_all_doctors(
    db: Session = Depends(get_db)
):
    doctors = db.query(Doctor).all()

    return {
        "message": "Doctors fetched successfully",
        "total_doctors": len(doctors),
        "doctors": [
            {
                "doctor_id": doctor.doctor_id,
                "user_id": doctor.user_id,
                "specialization": doctor.specialization,
                "qualification": doctor.qualification,
                "experience": doctor.experience,
                "phone": doctor.phone,
                "hospital_name": doctor.hospital_name
            }
            for doctor in doctors
        ]
    }
@router.get("/{doctor_id}")
def get_doctor_details(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.doctor_id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return {
        "message": "Doctor details fetched successfully",
        "doctor": {
            "doctor_id": doctor.doctor_id,
            "user_id": doctor.user_id,
            "specialization": doctor.specialization,
            "qualification": doctor.qualification,
            "experience": doctor.experience,
            "phone": doctor.phone,
            "hospital_name": doctor.hospital_name
        }
    }