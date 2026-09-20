from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.database import get_db
from database.models import Medicine

router = APIRouter(
    prefix="/medicines",
    tags=["Medicines"]
)


class MedicineRequest(BaseModel):
    medicine_name: str
    generic_name: str = ""
    category: str = ""
    uses: str = ""
    precautions: str = ""
    side_effects: str = ""
    prescription_required: str = "Yes"
    doctor_verified: str = "No"


# Add Medicine
@router.post("/add")
def add_medicine(
    medicine_data: MedicineRequest,
    db: Session = Depends(get_db)
):
    existing_medicine = db.query(Medicine).filter(
        Medicine.medicine_name == medicine_data.medicine_name
    ).first()

    if existing_medicine:
        raise HTTPException(
            status_code=400,
            detail="Medicine already exists"
        )

    new_medicine = Medicine(
        medicine_name=medicine_data.medicine_name,
        generic_name=medicine_data.generic_name,
        category=medicine_data.category,
        uses=medicine_data.uses,
        precautions=medicine_data.precautions,
        side_effects=medicine_data.side_effects,
        prescription_required=medicine_data.prescription_required,
        doctor_verified=medicine_data.doctor_verified
    )

    db.add(new_medicine)
    db.commit()
    db.refresh(new_medicine)

    return {
        "message": "Medicine added successfully",
        "medicine_id": new_medicine.medicine_id
    }


# View All Medicines
@router.get("/")
def get_all_medicines(
    db: Session = Depends(get_db)
):
    medicines = db.query(Medicine).all()

    return {
        "total_medicines": len(medicines),
        "medicines": [
            {
                "medicine_id": medicine.medicine_id,
                "medicine_name": medicine.medicine_name,
                "generic_name": medicine.generic_name,
                "category": medicine.category,
                "uses": medicine.uses,
                "prescription_required": medicine.prescription_required,
                "doctor_verified": medicine.doctor_verified
            }
            for medicine in medicines
        ]
    }


# Search Medicine
@router.get("/search/{medicine_name}")
def search_medicine(
    medicine_name: str,
    db: Session = Depends(get_db)
):
    medicine = db.query(Medicine).filter(
        Medicine.medicine_name.ilike(f"%{medicine_name}%")
    ).all()

    if not medicine:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    return {
        "results": [
            {
                "medicine_id": item.medicine_id,
                "medicine_name": item.medicine_name,
                "generic_name": item.generic_name,
                "category": item.category,
                "uses": item.uses,
                "precautions": item.precautions,
                "side_effects": item.side_effects,
                "prescription_required": item.prescription_required,
                "doctor_verified": item.doctor_verified
            }
            for item in medicine
        ]
    }


# View Medicine Details
@router.get("/{medicine_id}")
def get_medicine_details(
    medicine_id: int,
    db: Session = Depends(get_db)
):
    medicine = db.query(Medicine).filter(
        Medicine.medicine_id == medicine_id
    ).first()

    if not medicine:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    return {
        "medicine_id": medicine.medicine_id,
        "medicine_name": medicine.medicine_name,
        "generic_name": medicine.generic_name,
        "category": medicine.category,
        "uses": medicine.uses,
        "precautions": medicine.precautions,
        "side_effects": medicine.side_effects,
        "prescription_required": medicine.prescription_required,
        "doctor_verified": medicine.doctor_verified
    }