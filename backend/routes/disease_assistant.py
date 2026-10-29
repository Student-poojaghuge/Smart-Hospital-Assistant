
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
from pathlib import Path
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


router = APIRouter(
    prefix="/disease-assistant",
    tags=["Disease Assistant"]
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "disease_prediction_model.pkl"
)

FEATURES_PATH = (
    BASE_DIR
    / "models"
    / "disease_prediction_features.pkl"
)

KNOWLEDGE_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "disease_knowledge.csv"
)


# =========================================================
# LOAD DISEASE MODEL + DATA
# =========================================================

try:

    model = joblib.load(
        MODEL_PATH
    )

    feature_columns = joblib.load(
        FEATURES_PATH
    )

    print(
        "SUPPORTED SYMPTOMS:",
        list(feature_columns)
    )

    disease_df = pd.read_csv(
        KNOWLEDGE_PATH
    )

    disease_df["Disease"] = (
        disease_df["Disease"]
        .astype(str)
        .str.strip()
    )

    print(
        "Disease knowledge base loaded successfully."
    )

except Exception as e:

    model = None
    feature_columns = None
    disease_df = None

    print(
        "Disease Assistant resources could not be loaded:",
        repr(e)
    )


# =========================================================
# LOAD TRANSLATION MODELS
# =========================================================

marathi_tokenizer = None
marathi_model = None

hindi_tokenizer = None
hindi_model = None


# ---------------------------------------------------------
# ENGLISH → MARATHI
# ---------------------------------------------------------

try:

    print(
        "Loading English → Marathi translation model..."
    )

    marathi_model_name = (
        "Helsinki-NLP/opus-mt-en-mr"
    )

    marathi_tokenizer = (
        AutoTokenizer.from_pretrained(
            marathi_model_name
        )
    )

    marathi_model = (
        AutoModelForSeq2SeqLM.from_pretrained(
            marathi_model_name
        )
    )

    print(
        "English → Marathi translator loaded successfully."
    )

except Exception as e:

    marathi_tokenizer = None
    marathi_model = None

    print(
        "Marathi translator could not be loaded:",
        repr(e)
    )


# ---------------------------------------------------------
# ENGLISH → HINDI
# ---------------------------------------------------------

try:

    print(
        "Loading English → Hindi translation model..."
    )

    hindi_model_name = (
        "Helsinki-NLP/opus-mt-en-hi"
    )

    hindi_tokenizer = (
        AutoTokenizer.from_pretrained(
            hindi_model_name
        )
    )

    hindi_model = (
        AutoModelForSeq2SeqLM.from_pretrained(
            hindi_model_name
        )
    )

    print(
        "English → Hindi translator loaded successfully."
    )

except Exception as e:

    hindi_tokenizer = None
    hindi_model = None

    print(
        "Hindi translator could not be loaded:",
        repr(e)
    )


# =========================================================
# REQUEST MODEL
# =========================================================

class DiseaseAssistantRequest(BaseModel):

    symptoms: list[str]

    language: str = "English"


# =========================================================
# SYMPTOM ALIASES
# =========================================================

SYMPTOM_ALIASES = {

    # Fever
    "fever": "high_fever",
    "high fever": "high_fever",
    "high temperature": "high_fever",
    "temperature": "high_fever",
    "having fever": "high_fever",
    "i have fever": "high_fever",

    # Headache
    "headache": "headache",
    "head pain": "headache",
    "head ache": "headache",
    "head is hurting": "headache",
    "my head hurts": "headache",
    "pain in head": "headache",

    # Cough
    "cough": "cough",
    "coughing": "cough",
    "i am coughing": "cough",

    # Cold / Nose
    "cold": "cold_hands_and_feets",
    "runny nose": "runny_nose",
    "running nose": "runny_nose",
    "blocked nose": "congestion",
    "nasal congestion": "congestion",

    # Fatigue / Weakness
    "fatigue": "fatigue",
    "tired": "fatigue",
    "very tired": "fatigue",
    "feeling tired": "fatigue",

    "weakness": "muscle_weakness",
    "weak": "muscle_weakness",
    "feeling weak": "muscle_weakness",

    # Nausea
    "nausea": "nausea",
    "feeling nauseous": "nausea",
    "feel nauseous": "nausea",

    # Vomiting
    "vomiting": "vomiting",
    "vomit": "vomiting",
    "throwing up": "vomiting",
    "throw up": "vomiting",

    # Stomach
    "stomach pain": "stomach_pain",
    "stomach ache": "stomach_pain",
    "pain in stomach": "stomach_pain",
    "abdominal pain": "abdominal_pain",
    "belly pain": "belly_pain",

    # Chest
    "chest pain": "chest_pain",
    "pain in chest": "chest_pain",
    "chest hurts": "chest_pain",

    # Dizziness
    "dizziness": "dizziness",
    "dizzy": "dizziness",
    "feeling dizzy": "dizziness",

    # Breathing
    "difficulty breathing": "breathlessness",
    "breathing difficulty": "breathlessness",
    "shortness of breath": "breathlessness",
    "trouble breathing": "breathlessness",
    "hard to breathe": "breathlessness",
    "breathlessness": "breathlessness",

    # Throat
    "sore throat": "throat_irritation",
    "throat pain": "throat_irritation",
    "painful throat": "throat_irritation",
    "throat irritation": "throat_irritation",

    # Itching
    "itching": "itching",
    "itchy": "itching",
    "skin itching": "itching",

    # Rash
    "rash": "skin_rash",
    "skin rash": "skin_rash",

    # Joint
    "joint pain": "joint_pain",
    "pain in joints": "joint_pain",

    # Back
    "back pain": "back_pain",
    "pain in back": "back_pain",

    # Diarrhoea
    "diarrhea": "diarrhoea",
    "diarrhoea": "diarrhoea",
    "loose motion": "diarrhoea",
    "loose motions": "diarrhoea",
    "loose stools": "diarrhoea",

    # Constipation
    "constipation": "constipation",
    "constipated": "constipation",

    # Appetite
    "loss of appetite": "loss_of_appetite",
    "no appetite": "loss_of_appetite",
    "poor appetite": "loss_of_appetite",

    # Sweating
    "sweating": "sweating",
    "excessive sweating": "sweating",

    # Chills
    "chills": "chills",
    "shivering": "shivering",
    "feeling cold and shivering": "shivering",

    # Muscle pain
    "muscle pain": "muscle_pain",
    "body pain": "muscle_pain",

    # Heartbeat
    "fast heartbeat": "fast_heart_rate",
    "rapid heartbeat": "fast_heart_rate",
    "fast heart rate": "fast_heart_rate",
    "heart beating fast": "fast_heart_rate",

    # Smell
    "loss of smell": "loss_of_smell",

    # Eyes
    "red eyes": "redness_of_eyes",
    "redness of eyes": "redness_of_eyes",
    "watery eyes": "watering_from_eyes",
}


# =========================================================
# NORMALIZE SYMPTOM
# =========================================================

def normalize_symptom(symptom):

    symptom = str(
        symptom
    ).strip().lower()

    symptom = re.sub(
        r"\s+",
        " ",
        symptom
    )

    if symptom in SYMPTOM_ALIASES:

        return SYMPTOM_ALIASES[
            symptom
        ]

    if feature_columns is not None:

        if symptom in feature_columns:

            return symptom

    return None



def translate_text(text, language):

    if not text:
        return text

    if language == "English":
        return text

    # =====================================================
    # FIXED MEDICAL TRANSLATIONS
    # =====================================================

    FIXED_TRANSLATIONS = {

        "Marathi": {

            "The AI could not identify a medical condition reliably from the supplied symptoms.":
                "दिलेल्या लक्षणांच्या आधारे AI कोणतीही वैद्यकीय स्थिती विश्वसनीयपणे ओळखू शकले नाही.",


"Unable to determine reliably":
    "विश्वसनीयपणे निश्चित करता आले नाही",



            "Please consult a qualified doctor.":
                "कृपया पात्र डॉक्टरांचा सल्ला घ्या.",

            "Do not self-medicate.":
                "स्वतःहून औषधे घेऊ नका.",

            "Seek medical attention if your symptoms worsen.":
                "लक्षणे अधिक गंभीर झाल्यास त्वरित वैद्यकीय मदत घ्या.",

            "The AI could not determine the condition reliably from the supplied symptoms. Please consult a qualified doctor for proper diagnosis.":
                "दिलेल्या लक्षणांच्या आधारे AI ही वैद्यकीय स्थिती विश्वसनीयपणे ओळखू शकले नाही. योग्य निदानासाठी कृपया पात्र डॉक्टरांचा सल्ला घ्या.",

            "This result is an AI-based prediction and should not be considered a medical diagnosis. Please consult a qualified doctor.":
                "हा निकाल AI आधारित अंदाज आहे आणि याला वैद्यकीय निदान समजू नये. कृपया पात्र डॉक्टरांचा सल्ला घ्या.",

            "The AI prediction is based on the symptoms provided.":
                "AI चा अंदाज दिलेल्या लक्षणांवर आधारित आहे.",

            "No matching symptoms were found for the AI prediction.":
                "AI अंदाजासाठी कोणतीही जुळणारी लक्षणे आढळली नाहीत.",

            "Please provide more specific symptoms.":
                "कृपया अधिक विशिष्ट लक्षणे द्या.",

            "Consult a qualified doctor if symptoms continue.":
                "लक्षणे कायम राहिल्यास पात्र डॉक्टरांचा सल्ला घ्या."
        },

        "Hindi": {

            "The AI could not identify a medical condition reliably from the supplied symptoms.":
                "दिए गए लक्षणों के आधार पर AI किसी चिकित्सीय स्थिति की विश्वसनीय पहचान नहीं कर सका।",

                "Unable to determine reliably":
    "विश्वसनीय रूप से निर्धारित नहीं किया जा सका",

            "Please consult a qualified doctor.":
                "कृपया योग्य डॉक्टर से परामर्श लें।",

            "Do not self-medicate.":
                "बिना डॉक्टर की सलाह के दवा न लें।",

            "Seek medical attention if your symptoms worsen.":
                "यदि आपके लक्षण अधिक गंभीर हो जाएं, तो तुरंत चिकित्सा सहायता लें।",

            "The AI could not determine the condition reliably from the supplied symptoms. Please consult a qualified doctor for proper diagnosis.":
                "दिए गए लक्षणों के आधार पर AI इस स्थिति की विश्वसनीय पहचान नहीं कर सका। सही निदान के लिए कृपया योग्य डॉक्टर से परामर्श लें।",

            "This result is an AI-based prediction and should not be considered a medical diagnosis. Please consult a qualified doctor.":
                "यह परिणाम AI आधारित अनुमान है और इसे चिकित्सीय निदान नहीं माना जाना चाहिए। कृपया योग्य डॉक्टर से परामर्श लें।",

            "The AI prediction is based on the symptoms provided.":
                "AI का अनुमान दिए गए लक्षणों पर आधारित है।",

            "No matching symptoms were found for the AI prediction.":
                "AI अनुमान के लिए कोई मेल खाने वाले लक्षण नहीं मिले।",

            "Please provide more specific symptoms.":
                "कृपया अधिक विशिष्ट लक्षण बताएं।",

            "Consult a qualified doctor if symptoms continue.":
                "यदि लक्षण बने रहें तो योग्य डॉक्टर से परामर्श लें।"
        }
    }

    # =====================================================
    # USE SAFE FIXED TRANSLATION IF AVAILABLE
    # =====================================================

    if language in FIXED_TRANSLATIONS:

        translated = FIXED_TRANSLATIONS[language].get(text)

        if translated:
            return translated

    # =====================================================
    # FALLBACK TO AI TRANSLATION
    # =====================================================

    try:

        if language == "Marathi":

            if (
                marathi_tokenizer is None
                or marathi_model is None
            ):
                print(
                    "Marathi translator is not available."
                )
                return text

            tokenizer = marathi_tokenizer
            translation_model = marathi_model

        elif language == "Hindi":

            if (
                hindi_tokenizer is None
                or hindi_model is None
            ):
                print(
                    "Hindi translator is not available."
                )
                return text

            tokenizer = hindi_tokenizer
            translation_model = hindi_model

        else:
            return text

        inputs = tokenizer(
            str(text),
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )

        with torch.no_grad():

            translated_tokens = (
                translation_model.generate(
                    **inputs,
                    max_length=512
                )
            )

        translated_text = tokenizer.decode(
            translated_tokens[0],
            skip_special_tokens=True
        )

        return translated_text

    except Exception as e:

        print(
            f"{language} translation failed:",
            repr(e)
        )

        return text


        # -------------------------------------------------
        # TOKENIZE
        # -------------------------------------------------

        inputs = tokenizer(
            str(text),
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )

        # -------------------------------------------------
        # GENERATE TRANSLATION
        # -------------------------------------------------

        with torch.no_grad():

            translated_tokens = (
                translation_model.generate(
                    **inputs,
                    max_length=512
                )
            )

        # -------------------------------------------------
        # DECODE
        # -------------------------------------------------

        translated_text = (
            tokenizer.decode(
                translated_tokens[0],
                skip_special_tokens=True
            )
        )

        return translated_text

    except Exception as e:

        print(
            f"{language} translation failed:",
            repr(e)
        )

        return text


# =========================================================
# TRANSLATE RESPONSE
# =========================================================

def translate_response(
    predicted_disease,
    description,
    precautions,
    notice,
    language
):

    if language == "English":

        return {

            "predicted_disease":
                predicted_disease,

            "description":
                description,

            "precautions":
                precautions,

            "notice":
                notice
        }

    # -----------------------------------------------------
    # DISEASE
    # -----------------------------------------------------

    translated_disease = (
        translate_text(
            predicted_disease,
            language
        )
    )

    # -----------------------------------------------------
    # DESCRIPTION
    # -----------------------------------------------------

    translated_description = (
        translate_text(
            description,
            language
        )
    )

    # -----------------------------------------------------
    # PRECAUTIONS
    # -----------------------------------------------------

    translated_precautions = []

    for precaution in precautions:

        translated_precautions.append(
            translate_text(
                precaution,
                language
            )
        )

    # -----------------------------------------------------
    # NOTICE
    # -----------------------------------------------------

    translated_notice = (
        translate_text(
            notice,
            language
        )
    )

    return {

        "predicted_disease":
            translated_disease,

        "description":
            translated_description,

        "precautions":
            translated_precautions,

        "notice":
            translated_notice
    }


# =========================================================
# DISEASE INFORMATION
# =========================================================

def get_disease_information(
    disease_name
):

    default_description = (
        "The AI prediction is based on "
        "the symptoms provided."
    )

    default_precautions = [

        "Consult a qualified doctor.",

        "Do not self-medicate.",

        "Seek medical attention if symptoms worsen."
    ]

    if disease_df is None:

        return (
            default_description,
            default_precautions
        )

    try:

        rows = disease_df[
            disease_df["Disease"]
            .str.lower()
            ==
            str(disease_name).lower()
        ]

        if rows.empty:

            return (
                default_description,
                default_precautions
            )

        row = rows.iloc[0]

        description = (
            default_description
        )

        precautions = (
            default_precautions
        )

        # -------------------------------------------------
        # DESCRIPTION
        # -------------------------------------------------

        if "Description" in disease_df.columns:

            value = row["Description"]

            if pd.notna(value):

                description = str(
                    value
                )

        # -------------------------------------------------
        # PRECAUTIONS
        # -------------------------------------------------

        if "Precautions" in disease_df.columns:

            value = row["Precautions"]

            if pd.notna(value):

                if isinstance(
                    value,
                    str
                ):

                    precautions = [

                        item.strip()

                        for item in value.split(",")

                        if item.strip()
                    ]

        return (
            description,
            precautions
        )

    except Exception as e:

        print(
            "Disease information error:",
            repr(e)
        )

        return (
            default_description,
            default_precautions
        )


# =========================================================
# ANALYZE DISEASE
# =========================================================

@router.post("/analyze")
def analyze_disease(
    data: DiseaseAssistantRequest
):

    # =====================================================
    # CHECK MODEL
    # =====================================================

    if model is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "Disease prediction model "
                "is not available."
            )
        )

    if feature_columns is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "Disease prediction features "
                "are not available."
            )
        )

    # =====================================================
    # LANGUAGE
    # =====================================================

    language = data.language

    if language not in [
        "English",
        "Marathi",
        "Hindi"
    ]:

        language = "English"

    print(
        "REQUEST LANGUAGE:",
        language
    )

    # =====================================================
    # CHECK SYMPTOMS
    # =====================================================

    if not data.symptoms:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please provide at least "
                "one symptom."
            )
        )

    # =====================================================
    # NORMALIZE SYMPTOMS
    # =====================================================

    matched_symptoms = []

    for symptom in data.symptoms:

        normalized = normalize_symptom(
            symptom
        )

        if normalized is not None:

            if (
                normalized
                not in matched_symptoms
            ):

                matched_symptoms.append(
                    normalized
                )

    # =====================================================
    # NO MATCHING SYMPTOMS
    # =====================================================

    if not matched_symptoms:

        notice = (
            "The supplied symptoms could not "
            "be matched with the AI model. "
            "Please provide symptoms such as "
            "fever, headache, cough, nausea, "
            "vomiting, stomach pain or dizziness."
        )

        description = (
            "No matching symptoms were found "
            "for the AI prediction."
        )

        precautions = [

            "Please provide more specific symptoms.",

            "Consult a qualified doctor "
            "if symptoms continue."
        ]

        translated = translate_response(

            "Unable to determine reliably",

            description,

            precautions,

            notice,

            language
        )

        return {

            "predicted_disease":
                translated[
                    "predicted_disease"
                ],

            "confidence":
                0,

            "matched_symptoms":
                matched_symptoms,

            "description":
                translated[
                    "description"
                ],

            "precautions":
                translated[
                    "precautions"
                ],

            "notice":
                translated[
                    "notice"
                ],

            "language":
                language
        }

    # =====================================================
    # CREATE INPUT VECTOR
    # =====================================================

    input_data = pd.DataFrame(
        0,
        index=[0],
        columns=feature_columns
    )

    for symptom in matched_symptoms:

        if symptom in input_data.columns:

            input_data.loc[
                0,
                symptom
            ] = 1

    # =====================================================
    # PREDICTION
    # =====================================================

    try:

        prediction = model.predict(
            input_data
        )

        predicted_disease = str(
            prediction[0]
        )

    except Exception as e:

        print(
            "Prediction error:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Disease prediction failed."
            )
        )

    # =====================================================
    # CONFIDENCE
    # =====================================================

    confidence = 0.0

    try:

        if hasattr(
            model,
            "predict_proba"
        ):

            probabilities = (
                model.predict_proba(
                    input_data
                )[0]
            )

            confidence = float(
                max(probabilities)
            )

    except Exception as e:

        print(
            "Confidence calculation error:",
            repr(e)
        )

        confidence = 0.0

    # =====================================================
    # LOW CONFIDENCE
    # =====================================================

    if confidence < 0.50:

        displayed_disease = (
            "Unable to determine reliably"
        )

        description = (
            "The AI could not identify "
            "a medical condition reliably "
            "from the supplied symptoms."
        )

        precautions = [

            "Please consult a qualified doctor.",

            "Do not self-medicate.",

            "Seek medical attention if "
            "your symptoms worsen."
        ]

        notice = (
            "The AI could not determine "
            "the condition reliably from "
            "the supplied symptoms. "
            "Please consult a qualified doctor "
            "for proper diagnosis."
        )

    # =====================================================
    # HIGH CONFIDENCE
    # =====================================================

    else:

        displayed_disease = (
            predicted_disease
        )

        (
            description,
            precautions
        ) = get_disease_information(
            predicted_disease
        )

        notice = (
            "This result is an AI-based "
            "prediction and should not be "
            "considered a medical diagnosis. "
            "Please consult a qualified doctor."
        )

    # =====================================================
    # TRANSLATION
    # =====================================================

    translated_response = (
        translate_response(

            displayed_disease,

            description,

            precautions,

            notice,

            language
        )
    )

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    return {

        "predicted_disease":
            translated_response[
                "predicted_disease"
            ],

        "confidence":
            confidence,

        "matched_symptoms":
            matched_symptoms,

        "description":
            translated_response[
                "description"
            ],

        "precautions":
            translated_response[
                "precautions"
            ],

        "notice":
            translated_response[
                "notice"
            ],

        "language":
            language
    }
