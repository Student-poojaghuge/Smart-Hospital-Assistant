from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Hospital


router = APIRouter(
    prefix="/hospitals",
    tags=["Hospitals"]
)


# =========================
# GET ALL HOSPITALS
# =========================

@router.get("/")
def get_all_hospitals(
    db: Session = Depends(get_db)
):
    hospitals = db.query(Hospital).all()

    return {
        "message": "Hospitals fetched successfully",
        "total_hospitals": len(hospitals),
        "hospitals": [
            {
                "hospital_id": hospital.hospital_id,
                "hospital_name": hospital.hospital_name,
                "location": hospital.location,
                "address": hospital.address,
                "phone": hospital.phone,
                "hospital_type": hospital.hospital_type,
                "specialization": hospital.specialization,
                "emergency_available": hospital.emergency_available,
                "consultation_available": hospital.consultation_available
            }
            for hospital in hospitals
        ]
    }


# =========================
# GET HOSPITAL BY ID
# =========================

@router.get("/{hospital_id}")
def get_hospital_details(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    hospital = db.query(Hospital).filter(
        Hospital.hospital_id == hospital_id
    ).first()

    if not hospital:
        raise HTTPException(
            status_code=404,
            detail="Hospital not found"
        )

    return {
        "message": "Hospital details fetched successfully",
        "hospital": {
            "hospital_id": hospital.hospital_id,
            "hospital_name": hospital.hospital_name,
            "location": hospital.location,
            "address": hospital.address,
            "phone": hospital.phone,
            "hospital_type": hospital.hospital_type,
            "specialization": hospital.specialization,
            "emergency_available": hospital.emergency_available,
            "consultation_available": hospital.consultation_available
        }
    }


# =========================
# SEARCH HOSPITALS
# =========================

@router.get("/search/")
def search_hospitals(
    specialization: str = None,
    location: str = None,
    emergency_available: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Hospital)

    if specialization:
        query = query.filter(
            Hospital.specialization.ilike(
                f"%{specialization}%"
            )
        )

    if location:
        query = query.filter(
            Hospital.location.ilike(
                f"%{location}%"
            )
        )

    if emergency_available:
        query = query.filter(
            Hospital.emergency_available.ilike(
                emergency_available
            )
        )

    hospitals = query.all()

    return {
        "message": "Hospital search completed",
        "total_hospitals": len(hospitals),
        "hospitals": [
            {
                "hospital_id": hospital.hospital_id,
                "hospital_name": hospital.hospital_name,
                "location": hospital.location,
                "address": hospital.address,
                "phone": hospital.phone,
                "hospital_type": hospital.hospital_type,
                "specialization": hospital.specialization,
                "emergency_available": hospital.emergency_available,
                "consultation_available": hospital.consultation_available
            }
            for hospital in hospitals
        ]
    }