from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
from pathlib import Path

router = APIRouter(
    prefix="/disease-assistant",
    tags=["Disease Assistant"]
)

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "models" / "disease_prediction_model.pkl"
FEATURES_PATH = BASE_DIR / "models" / "disease_prediction_features.pkl"
KNOWLEDGE_PATH = BASE_DIR / "data" / "processed" / "disease_knowledge.csv"

try:
    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURES_PATH)
    disease_df = pd.read_csv(KNOWLEDGE_PATH)

    disease_df["Disease"] = (
        disease_df["Disease"]
        .astype(str)
        .str.strip()
    )

except Exception as e:
    model = None
    feature_columns = None
    disease_df = None

    print("Disease Assistant resources could not be loaded:", e)


class DiseaseAssistantRequest(BaseModel):
    symptoms: list[str]


@router.post("/analyze")
def analyze_disease(data: DiseaseAssistantRequest):

    if model is None or feature_columns is None or disease_df is None:
        raise HTTPException(
            status_code=500,
            detail="Disease Assistant resources are not available"
        )

    try:
        # -----------------------------
        # Clean user symptoms
        # -----------------------------

        user_symptoms = set()

        for symptom in data.symptoms:

            cleaned = (
                symptom.strip()
                .lower()
                .replace(" ", "_")
            )

            cleaned = "_".join(
                part for part in cleaned.split("_")
                if part
            )

            user_symptoms.add(cleaned)

        # -----------------------------
        # Create model input
        # -----------------------------

        input_data = pd.DataFrame(
            0,
            index=[0],
            columns=feature_columns
        )

        matched_symptoms = []

        for symptom in user_symptoms:

            if symptom in input_data.columns:

                input_data.loc[0, symptom] = 1
                matched_symptoms.append(symptom)

        if not matched_symptoms:

            raise HTTPException(
                status_code=400,
                detail=(
                    "None of the supplied symptoms match "
                    "the supported symptom list."
                )
            )

        # -----------------------------
        # Disease prediction
        # -----------------------------

        prediction = model.predict(input_data)[0]

        confidence = None

        if hasattr(model, "predict_proba"):

            probabilities = model.predict_proba(input_data)[0]

            confidence = float(max(probabilities))

        predicted_disease = str(prediction)

        # -----------------------------
        # Get disease knowledge
        # -----------------------------

        matches = disease_df[
            disease_df["Disease"].str.lower()
            == predicted_disease.lower()
        ]

        description = ""

        precautions = []

        if not matches.empty:

            row = matches.iloc[0]

            if "Description" in disease_df.columns:

                if pd.notna(row["Description"]):

                    description = str(row["Description"])

            if "Precautions" in disease_df.columns:

                if pd.notna(row["Precautions"]):

                    precautions = [
                        precaution.strip()
                        for precaution in str(
                            row["Precautions"]
                        ).split(";")
                        if precaution.strip()
                    ]

        # -----------------------------
        # Final response
        # -----------------------------

        return {
            "predicted_disease": predicted_disease,
            "confidence": confidence,
            "matched_symptoms": matched_symptoms,
            "description": description,
            "precautions": precautions,
            "notice": (
                "This information is for educational purposes only. "
                "The prediction is not a medical diagnosis or "
                "personalized treatment recommendation."
            )
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Disease analysis failed: {str(e)}"
        )