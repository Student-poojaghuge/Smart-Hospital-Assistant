from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database.database import get_db
from database.models import Appointment, Patient, Doctor


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


class AppointmentRequest(BaseModel):
    user_id: int
    doctor_id: int
    appointment_date: str
    appointment_time: str
    reason: str


@router.post("/book")
def book_appointment(
    appointment_data: AppointmentRequest,
    db: Session = Depends(get_db)
):
    # Validate date and time format
    try:
        datetime.strptime(
            appointment_data.appointment_date,
            "%Y-%m-%d"
        )

        datetime.strptime(
            appointment_data.appointment_time,
            "%H:%M"
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Use date format YYYY-MM-DD and time format HH:MM"
        )

    # Check patient
    patient = db.query(Patient).filter(
        Patient.user_id == appointment_data.user_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    # Check doctor
    doctor = db.query(Doctor).filter(
        Doctor.doctor_id == appointment_data.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # Check existing appointment
    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == appointment_data.doctor_id,
        Appointment.appointment_date == appointment_data.appointment_date,
        Appointment.appointment_time == appointment_data.appointment_time,
        Appointment.status != "Cancelled"
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="Doctor is already booked for this time"
        )

    # Create appointment using strings
    new_appointment = Appointment(
        patient_id=patient.patient_id,
        doctor_id=doctor.doctor_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
        reason=appointment_data.reason,
        status="Pending"
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return {
        "message": "Appointment booked successfully",
        "appointment_id": new_appointment.appointment_id,
        "patient_id": patient.patient_id,
        "doctor_id": doctor.doctor_id,
        "appointment_date": new_appointment.appointment_date,
        "appointment_time": new_appointment.appointment_time,
        "status": new_appointment.status
    }


@router.get("/patient/{user_id}")
def get_patient_appointments(
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

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient.patient_id
    ).all()

    return {
        "message": "Patient appointments fetched successfully",
        "total_appointments": len(appointments),
        "appointments": [
            {
                "appointment_id": appointment.appointment_id,
                "doctor_id": appointment.doctor_id,
                "appointment_date": appointment.appointment_date,
                "appointment_time": appointment.appointment_time,
                "reason": appointment.reason,
                "status": appointment.status,
                "notes": appointment.notes
            }
            for appointment in appointments
        ]
    }