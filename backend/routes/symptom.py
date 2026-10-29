from fastapi import APIRouter, HTTPException
import csv
import os

router = APIRouter(
    prefix="/symptoms",
    tags=["Symptoms"]
)

CSV_FILE = os.path.join(
    "data",
    "symptom_medicine.csv"
)


@router.get("/search/{symptom}")
def search_symptom(symptom: str):

    if not os.path.exists(CSV_FILE):
        raise HTTPException(
            status_code=500,
            detail="Symptom dataset not found"
        )

    results = []

    with open(
        CSV_FILE,
        mode="r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                symptom.lower().strip()
                in row["symptom"].lower().strip()
            ):
                results.append(row)

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No information found for this symptom"
        )

    return {
        "symptom": symptom,
        "results": results,
        "notice": (
            "This information is for educational purposes only. "
            "It is not a medical diagnosis or prescription. "
            "Consult a qualified healthcare professional before "
            "using any medicine."
        )
    }