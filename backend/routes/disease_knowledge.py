from fastapi import APIRouter, HTTPException
import pandas as pd
from pathlib import Path

router = APIRouter(
    prefix="/disease-knowledge",
    tags=["Disease Knowledge"]
)

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data" / "processed" / "disease_knowledge.csv"

try:
    disease_df = pd.read_csv(DATA_PATH)
    disease_df["Disease"] = disease_df["Disease"].astype(str).str.strip()
except Exception as e:
    disease_df = None
    print("Disease knowledge dataset could not be loaded:", e)


@router.get("/{disease_name}")
def get_disease_knowledge(disease_name: str):

    if disease_df is None:
        raise HTTPException(
            status_code=500,
            detail="Disease knowledge dataset is not available"
        )

    disease_name_clean = disease_name.strip().lower()

    matches = disease_df[
        disease_df["Disease"].str.lower() == disease_name_clean
    ]

    if matches.empty:
        raise HTTPException(
            status_code=404,
            detail="Disease information not found"
        )

    row = matches.iloc[0]

    precautions = []

    if "Precautions" in disease_df.columns:
        if pd.notna(row["Precautions"]):
            precautions = [
                p.strip()
                for p in str(row["Precautions"]).split(";")
                if p.strip()
            ]

    description = ""
    if "Description" in disease_df.columns:
        if pd.notna(row["Description"]):
            description = str(row["Description"])

    return {
        "disease": str(row["Disease"]),
        "description": description,
        "precautions": precautions,
        "notice": (
            "This information is for educational purposes only "
            "and is not a medical diagnosis or treatment plan."
        )
    }

    