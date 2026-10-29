
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import (
    User,
    Patient,
    Doctor,
    Hospital,
    Appointment,
    MedicalRecord,
    EmergencyAssessment,
    Medicine,
    ChatHistory
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/dashboard")
def get_admin_dashboard(
    db: Session = Depends(get_db)
):
    return {
        "message": "Admin dashboard data fetched successfully",
        "statistics": {
            "total_users": db.query(User).count(),
            "total_patients": db.query(Patient).count(),
            "total_doctors": db.query(Doctor).count(),
            "total_hospitals": db.query(Hospital).count(),
            "total_appointments": db.query(Appointment).count(),
            "total_medical_records": db.query(MedicalRecord).count(),
            "total_emergency_assessments": db.query(EmergencyAssessment).count(),
            "total_medicines": db.query(Medicine).count(),
            "total_chat_history": db.query(ChatHistory).count()
        }
    }
@router.get("/test")
def admin_test():
    return {
        "message": "Admin route is working"
    }
@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return {
        "total_users": len(users),
        "users": [
            {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
            for user in users
        ]
    }
@router.get("/appointments")
def get_all_appointments(db: Session = Depends(get_db)):
    appointments = db.query(Appointment).all()

    return {
        "total_appointments": len(appointments),
        "appointments": [
            {
                "appointment_id": appointment.appointment_id,
                "patient_id": appointment.patient_id,
                "doctor_id": appointment.doctor_id,
                "appointment_date": str(appointment.appointment_date),
                "appointment_time": str(appointment.appointment_time),
                "reason": appointment.reason,
                "status": appointment.status,
                "notes": appointment.notes
            }
            for appointment in appointments
        ]
    }
@router.get("/medical-records")
def get_all_medical_records(db: Session = Depends(get_db)):
    records = db.query(MedicalRecord).all()

    return {
        "total_records": len(records),
        "medical_records": [
            {
                "record_id": record.record_id,
                "patient_id": record.patient_id,
                "doctor_id": record.doctor_id,
                "record_date": str(record.record_date),
                "symptoms": record.symptoms,
                "diagnosis": record.diagnosis,
                "allergies": record.allergies,
                "existing_conditions": record.existing_conditions,
                "doctor_notes": record.doctor_notes
            }
            for record in records
        ]
    }
@router.get("/medicines")
def get_all_medicines(db: Session = Depends(get_db)):
    medicines = db.query(Medicine).all()

    return {
        "total_medicines": len(medicines),
        "medicines": [
            {
                "medicine_id": medicine.medicine_id,
                "medicine_name": medicine.medicine_name,
                "generic_name": medicine.generic_name,
                "category": medicine.category,
                "side_effects": medicine.side_effects,
                "prescription_required": medicine.prescription_required,
                "doctor_verified": medicine.doctor_verified
            }
            for medicine in medicines
        ]
    }