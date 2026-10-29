
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database.database import get_db
from database.models import Appointment, Patient, Doctor, User
from backend.services.auth_dependency import get_current_user


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


# =========================================================
# REQUEST MODELS
# =========================================================

class AppointmentRequest(BaseModel):
    user_id: int = Field(gt=0)
    doctor_id: int = Field(gt=0)
    appointment_date: str
    appointment_time: str
    reason: str = Field(min_length=1, max_length=1000)


class AppointmentStatusRequest(BaseModel):
    status: str


# =========================================================
# AUTHORIZATION HELPERS
# =========================================================

def verify_patient_owns_user(user_id: int, current_user: dict):
    try:
        authenticated_user_id = int(current_user["user_id"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    if authenticated_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this patient's data"
        )


def verify_doctor_or_admin(doctor: Doctor, current_user: dict):
    role = current_user.get("role")
    user_id = current_user.get("user_id")

    if role == "admin":
        return

    if role != "doctor" or str(doctor.user_id) != str(user_id):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access these appointments"
        )


def get_doctor_or_404(doctor_id: int, db: Session):
    doctor = db.query(Doctor).filter(
        Doctor.doctor_id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


def get_patient_or_404(user_id: int, db: Session):
    patient = db.query(Patient).filter(
        Patient.user_id == user_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    return patient


def get_patient_details(patient_id: int, db: Session):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id
    ).first()

    patient_user = None

    if patient:
        patient_user = db.query(User).filter(
            User.user_id == patient.user_id
        ).first()

    return {
        "patient_id": patient.patient_id if patient else None,
        "patient_name": patient_user.name if patient_user else None,
        "age": patient.age if patient else None,
        "gender": patient.gender if patient else None,
        "phone": patient.phone if patient else None,
        "blood_group": patient.blood_group if patient else None
    }


def get_doctor_details(doctor_id: int, db: Session):
    doctor = db.query(Doctor).filter(
        Doctor.doctor_id == doctor_id
    ).first()

    doctor_user = None

    if doctor:
        doctor_user = db.query(User).filter(
            User.user_id == doctor.user_id
        ).first()

    return doctor, doctor_user


def build_appointment_result(appointment: Appointment, db: Session):
    doctor, doctor_user = get_doctor_details(
        appointment.doctor_id, db
    )

    return {
        "appointment_id": appointment.appointment_id,
        "doctor": {
            "doctor_id": doctor.doctor_id if doctor else None,
            "doctor_name": doctor_user.name if doctor_user else None,
            "specialization": doctor.specialization if doctor else None,
            "qualification": doctor.qualification if doctor else None,
            "experience": doctor.experience if doctor else None
        },
        "hospital": {
            "hospital_id": doctor.hospital_id if doctor else None,
            "hospital_name": doctor.hospital_name if doctor else None
        },
        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time,
        "reason": appointment.reason,
        "status": appointment.status,
        "notes": appointment.notes
    }


def build_doctor_appointment_result(
    appointment: Appointment,
    db: Session
):
    return {
        "appointment_id": appointment.appointment_id,
        "patient": get_patient_details(
            appointment.patient_id, db
        ),
        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time,
        "reason": appointment.reason,
        "status": appointment.status,
        "notes": appointment.notes
    }


def get_authorized_doctor(
    doctor_id: int,
    current_user: dict,
    db: Session
):
    doctor = get_doctor_or_404(doctor_id, db)
    verify_doctor_or_admin(doctor, current_user)
    return doctor


def fetch_doctor_appointments(
    doctor_id: int,
    db: Session,
    status: str = None,
    today_only: bool = False
):
    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id
    )

    if status is not None:
        query = query.filter(Appointment.status == status)

    today = datetime.now().strftime("%Y-%m-%d")

    if today_only:
        query = query.filter(
            Appointment.appointment_date == today
        )

    appointments = query.all()

    results = [
        build_doctor_appointment_result(appointment, db)
        for appointment in appointments
    ]

    return today, results


# =========================================================
# BOOK APPOINTMENT
# =========================================================

@router.post("/book")
def book_appointment(
    appointment_data: AppointmentRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.get("role") != "patient":
        raise HTTPException(
            status_code=403,
            detail="Only patients can book appointments"
        )

    verify_patient_owns_user(
        appointment_data.user_id, current_user
    )

    try:
        datetime.strptime(
            appointment_data.appointment_date, "%Y-%m-%d"
        )
        datetime.strptime(
            appointment_data.appointment_time, "%H:%M"
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Use date format YYYY-MM-DD and time format HH:MM"
        )

    patient = get_patient_or_404(
        appointment_data.user_id, db
    )

    doctor = get_doctor_or_404(
        appointment_data.doctor_id, db
    )

    if not doctor.hospital_id:
        raise HTTPException(
            status_code=400,
            detail="Doctor is not linked to a hospital"
        )

    doctor_user = db.query(User).filter(
        User.user_id == doctor.user_id
    ).first()

    if not doctor_user:
        raise HTTPException(
            status_code=404,
            detail="Doctor user account not found"
        )

    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.doctor_id,
        Appointment.appointment_date == appointment_data.appointment_date,
        Appointment.appointment_time == appointment_data.appointment_time,
        Appointment.status != "Cancelled"
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="Doctor is already booked for this time"
        )

    new_appointment = Appointment(
        patient_id=patient.patient_id,
        doctor_id=doctor.doctor_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
        reason=appointment_data.reason.strip(),
        status="Pending"
    )

    try:
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to book appointment"
        )

    return {
        "message": "Appointment booked successfully",
        "appointment_id": new_appointment.appointment_id,
        "patient_id": patient.patient_id,
        "doctor": {
            "doctor_id": doctor.doctor_id,
            "doctor_name": doctor_user.name,
            "specialization": doctor.specialization,
            "qualification": doctor.qualification,
            "experience": doctor.experience
        },
        "hospital": {
            "hospital_id": doctor.hospital_id,
            "hospital_name": doctor.hospital_name
        },
        "appointment_date": new_appointment.appointment_date,
        "appointment_time": new_appointment.appointment_time,
        "reason": new_appointment.reason,
        "status": new_appointment.status
    }


# =========================================================
# PATIENT APPOINTMENT HISTORY
# =========================================================

@router.get("/patient/{user_id}")
def get_patient_appointments(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.get("role") != "patient":
        raise HTTPException(
            status_code=403,
            detail="Only patients can access this endpoint"
        )

    verify_patient_owns_user(user_id, current_user)

    patient = get_patient_or_404(user_id, db)

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient.patient_id
    ).all()

    results = [
        build_appointment_result(appointment, db)
        for appointment in appointments
    ]

    return {
        "message": "Patient appointments fetched successfully",
        "total_appointments": len(results),
        "appointments": results
    }


# =========================================================
# TODAY'S DOCTOR APPOINTMENTS
# =========================================================

@router.get("/doctor/{doctor_id}/today")
def get_today_doctor_appointments(
    doctor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    get_authorized_doctor(doctor_id, current_user, db)

    today, results = fetch_doctor_appointments(
        doctor_id, db, today_only=True
    )

    return {
        "message": "Today's appointments fetched successfully",
        "doctor_id": doctor_id,
        "date": today,
        "total_appointments": len(results),
        "appointments": results
    }


# =========================================================
# PENDING DOCTOR APPOINTMENTS
# =========================================================

@router.get("/doctor/{doctor_id}/pending")
def get_pending_doctor_appointments(
    doctor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    get_authorized_doctor(doctor_id, current_user, db)

    _, results = fetch_doctor_appointments(
        doctor_id, db, status="Pending"
    )

    return {
        "message": "Pending appointments fetched successfully",
        "doctor_id": doctor_id,
        "total_pending_appointments": len(results),
        "appointments": results
    }


# =========================================================
# CONFIRMED DOCTOR APPOINTMENTS
# =========================================================

@router.get("/doctor/{doctor_id}/confirmed")
def get_confirmed_doctor_appointments(
    doctor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    get_authorized_doctor(doctor_id, current_user, db)

    _, results = fetch_doctor_appointments(
        doctor_id, db, status="Confirmed"
    )

    return {
        "message": "Confirmed appointments fetched successfully",
        "doctor_id": doctor_id,
        "total_confirmed_appointments": len(results),
        "appointments": results
    }


# =========================================================
# COMPLETED DOCTOR APPOINTMENTS
# =========================================================

@router.get("/doctor/{doctor_id}/completed")
def get_completed_doctor_appointments(
    doctor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    get_authorized_doctor(doctor_id, current_user, db)

    _, results = fetch_doctor_appointments(
        doctor_id, db, status="Completed"
    )

    return {
        "message": "Completed appointments fetched successfully",
        "doctor_id": doctor_id,
        "total_completed_appointments": len(results),
        "appointments": results
    }


# =========================================================
# CANCELLED DOCTOR APPOINTMENTS
# =========================================================

@router.get("/doctor/{doctor_id}/cancelled")
def get_cancelled_doctor_appointments(
    doctor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    get_authorized_doctor(doctor_id, current_user, db)

    _, results = fetch_doctor_appointments(
        doctor_id, db, status="Cancelled"
    )

    return {
        "message": "Cancelled appointments fetched successfully",
        "doctor_id": doctor_id,
        "total_cancelled_appointments": len(results),
        "appointments": results
    }


# =========================================================
# DOCTOR APPOINTMENT SUMMARY
# =========================================================

@router.get("/doctor/{doctor_id}/summary")
def get_doctor_appointment_summary(
    doctor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    get_authorized_doctor(doctor_id, current_user, db)

    today = datetime.now().strftime("%Y-%m-%d")

    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id
    )

    total_appointments = query.count()

    pending = query.filter(
        Appointment.status == "Pending"
    ).count()

    confirmed = query.filter(
        Appointment.status == "Confirmed"
    ).count()

    completed = query.filter(
        Appointment.status == "Completed"
    ).count()

    cancelled = query.filter(
        Appointment.status == "Cancelled"
    ).count()

    rejected = query.filter(
        Appointment.status == "Rejected"
    ).count()

    today_count = query.filter(
        Appointment.appointment_date == today
    ).count()

    return {
        "message": "Doctor appointment summary fetched successfully",
        "doctor_id": doctor_id,
        "date": today,
        "summary": {
            "total_appointments": total_appointments,
            "today_appointments": today_count,
            "pending_appointments": pending,
            "confirmed_appointments": confirmed,
            "completed_appointments": completed,
            "cancelled_appointments": cancelled,
            "rejected_appointments": rejected
        }
    }


# =========================================================
# ALL DOCTOR APPOINTMENTS
# =========================================================

@router.get("/doctor/{doctor_id}")
def get_doctor_appointments(
    doctor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doctor = get_authorized_doctor(
        doctor_id, current_user, db
    )

    doctor_user = db.query(User).filter(
        User.user_id == doctor.user_id
    ).first()

    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id
    ).all()

    results = [
        build_doctor_appointment_result(appointment, db)
        for appointment in appointments
    ]

    return {
        "message": "Doctor appointments fetched successfully",
        "doctor": {
            "doctor_id": doctor.doctor_id,
            "doctor_name": doctor_user.name if doctor_user else None,
            "specialization": doctor.specialization,
            "qualification": doctor.qualification,
            "experience": doctor.experience
        },
        "hospital": {
            "hospital_id": doctor.hospital_id,
            "hospital_name": doctor.hospital_name
        },
        "total_appointments": len(results),
        "appointments": results
    }


# =========================================================
# UPDATE APPOINTMENT STATUS
# =========================================================

@router.put("/{appointment_id}/status")
def update_appointment_status(
    appointment_id: int,
    status_data: AppointmentStatusRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(
        Appointment.appointment_id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    allowed_statuses = {
        "Pending",
        "Confirmed",
        "Rejected",
        "Completed",
        "Cancelled"
    }

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid appointment status"
        )

    role = current_user.get("role")
    user_id = str(current_user.get("user_id"))

    if role == "admin":
        pass

    elif role == "patient":
        patient = db.query(Patient).filter(
            Patient.patient_id == appointment.patient_id
        ).first()

        if not patient or str(patient.user_id) != user_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to update this appointment"
            )

        if status_data.status != "Cancelled":
            raise HTTPException(
                status_code=403,
                detail="Patients can only cancel their own appointments"
            )

        if appointment.status in {
            "Cancelled", "Completed", "Rejected"
        }:
            raise HTTPException(
                status_code=400,
                detail="This appointment cannot be cancelled"
            )

    elif role == "doctor":
        doctor = db.query(Doctor).filter(
            Doctor.user_id == int(user_id)
        ).first()

        if not doctor or doctor.doctor_id != appointment.doctor_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to update this appointment"
            )

        if status_data.status == "Cancelled":
            raise HTTPException(
                status_code=403,
                detail="Doctors cannot use this endpoint to cancel appointments"
            )

    else:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to update appointments"
        )

    appointment.status = status_data.status

    try:
        db.commit()
        db.refresh(appointment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update appointment status"
        )

    return {
        "message": "Appointment status updated successfully",
        "appointment_id": appointment.appointment_id,
        "status": appointment.status
    }
