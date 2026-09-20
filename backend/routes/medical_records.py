from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database.database import get_db
from database.models import MedicalRecord, Patient, Doctor

router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"]
)


class MedicalRecordRequest(BaseModel):
    patient_id: int
    doctor_id: int
    symptoms: str
    diagnosis: str
    allergies: str = ""
    existing_conditions: str = ""
    doctor_notes: str = ""


# Add Medical Record
@router.post("/add")
def add_medical_record(
    record_data: MedicalRecordRequest,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.patient_id == record_data.patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    doctor = db.query(Doctor).filter(
        Doctor.doctor_id == record_data.doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    new_record = MedicalRecord(
        patient_id=record_data.patient_id,
        doctor_id=record_data.doctor_id,
        record_date=datetime.now(),
        symptoms=record_data.symptoms,
        diagnosis=record_data.diagnosis,
        allergies=record_data.allergies,
        existing_conditions=record_data.existing_conditions,
        doctor_notes=record_data.doctor_notes
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {
        "message": "Medical record added successfully",
        "record_id": new_record.record_id,
        "patient_id": new_record.patient_id,
        "doctor_id": new_record.doctor_id
    }


# View Patient Medical Records
@router.get("/patient/{patient_id}")
def get_patient_medical_records(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    records = db.query(MedicalRecord).filter(
        MedicalRecord.patient_id == patient_id
    ).all()

    return {
        "patient_id": patient_id,
        "total_records": len(records),
        "records": [
            {
                "record_id": record.record_id,
                "doctor_id": record.doctor_id,
                "record_date": record.record_date,
                "symptoms": record.symptoms,
                "diagnosis": record.diagnosis,
                "allergies": record.allergies,
                "existing_conditions": record.existing_conditions,
                "doctor_notes": record.doctor_notes
            }
            for record in records
        ]
    }


# View Single Medical Record
@router.get("/{record_id}")
def get_single_medical_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    record = db.query(MedicalRecord).filter(
        MedicalRecord.record_id == record_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found"
        )

    return {
        "record_id": record.record_id,
        "patient_id": record.patient_id,
        "doctor_id": record.doctor_id,
        "record_date": record.record_date,
        "symptoms": record.symptoms,
        "diagnosis": record.diagnosis,
        "allergies": record.allergies,
        "existing_conditions": record.existing_conditions,
        "doctor_notes": record.doctor_notes
    }