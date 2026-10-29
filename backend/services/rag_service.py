from pathlib import Path

import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

FAISS_DIR = BASE_DIR / "models" / "faiss"


# --------------------------------------------------
# File paths
# --------------------------------------------------

MEDICAL_INDEX_PATH = (
    FAISS_DIR / "medical_knowledge.index"
)

MEDICAL_METADATA_PATH = (
    FAISS_DIR / "medical_knowledge_metadata.csv"
)

EMERGENCY_INDEX_PATH = (
    FAISS_DIR / "emergency_first_aid.index"
)

EMERGENCY_METADATA_PATH = (
    FAISS_DIR / "emergency_first_aid_metadata.csv"
)


# --------------------------------------------------
# Load embedding model
# --------------------------------------------------

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# --------------------------------------------------
# Load Medical Knowledge Base
# --------------------------------------------------

medical_index = faiss.read_index(
    str(MEDICAL_INDEX_PATH)
)

medical_metadata = pd.read_csv(
    MEDICAL_METADATA_PATH
)


# --------------------------------------------------
# Load Emergency & First-Aid Knowledge Base
# --------------------------------------------------

emergency_index = faiss.read_index(
    str(EMERGENCY_INDEX_PATH)
)

emergency_metadata = pd.read_csv(
    EMERGENCY_METADATA_PATH
)


print("RAG Knowledge Bases loaded successfully!")

print(
    "Medical vectors:",
    medical_index.ntotal
)

print(
    "Emergency vectors:",
    emergency_index.ntotal
)


# --------------------------------------------------
# Search Medical Knowledge
# --------------------------------------------------

def search_medical(
    query: str,
    top_k: int = 3
):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    distances, indices = medical_index.search(
        query_embedding,
        top_k
    )

    results = []

    for rank, idx in enumerate(
        indices[0],
        start=1
    ):

        if idx < 0 or idx >= len(medical_metadata):
            continue

        record = (
            medical_metadata
            .iloc[idx]
            .fillna("")
            .to_dict()
        )

        results.append({
            "rank": rank,
            "distance": float(
                distances[0][rank - 1]
            ),
            "topic": record
        })

    return results


# --------------------------------------------------
# Search Emergency & First-Aid Knowledge
# --------------------------------------------------

def search_emergency(
    query: str,
    top_k: int = 3
):

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    distances, indices = emergency_index.search(
        query_embedding,
        top_k
    )

    results = []

    for rank, idx in enumerate(
        indices[0],
        start=1
    ):

        if idx < 0 or idx >= len(emergency_metadata):
            continue

        record = (
            emergency_metadata
            .iloc[idx]
            .fillna("")
            .to_dict()
        )

        results.append({
            "rank": rank,
            "distance": float(
                distances[0][rank - 1]
            ),
            "topic": record
        })

    return results


# --------------------------------------------------
# Combined RAG Search
# --------------------------------------------------

def search_knowledge(
    query: str,
    top_k: int = 3
):

    if not query or not query.strip():
        return {
            "medical_results": [],
            "emergency_results": []
        }

    query = query.strip()

    medical_results = search_medical(
        query,
        top_k
    )

    emergency_results = search_emergency(
        query,
        top_k
    )

    return {
        "medical_results": medical_results,
        "emergency_results": emergency_results
    }
# --------------------------------------------------
# Query Classification
# --------------------------------------------------

EMERGENCY_KEYWORDS = [
    "choking",
    "bleeding",
    "unconscious",
    "not breathing",
    "breathing difficulty",
    "heart attack",
    "stroke",
    "seizure",
    "burn",
    "electric shock",
    "poisoning",
    "snake bite",
    "drowning",
    "anaphylaxis",
    "severe allergic reaction",
    "fainting",
    "fracture",
    "head injury",
    "spinal injury",
    "heat stroke",
    "hypothermia",
    "cpr",
    "cardiac arrest",
    "emergency",
    "first aid"
]


def classify_query(query: str):

    query_lower = query.lower().strip()

    for keyword in EMERGENCY_KEYWORDS:

        if keyword in query_lower:

            return "emergency"

    return "medical"
# --------------------------------------------------
# Query Classification
# --------------------------------------------------

EMERGENCY_KEYWORDS = [
    "choking",
    "bleeding",
    "unconscious",
    "not breathing",
    "breathing difficulty",
    "heart attack",
    "stroke",
    "seizure",
    "burn",
    "electric shock",
    "poisoning",
    "snake bite",
    "drowning",
    "anaphylaxis",
    "severe allergic reaction",
    "fainting",
    "fracture",
    "head injury",
    "spinal injury",
    "heat stroke",
    "hypothermia",
    "cpr",
    "cardiac arrest",
    "emergency",
    "first aid"
]


def classify_query(query: str):

    query_lower = query.lower().strip()

    for keyword in EMERGENCY_KEYWORDS:

        if keyword in query_lower:
            return "emergency"

    return "medical"


# --------------------------------------------------
# Classified RAG Search
# --------------------------------------------------

def classified_search(
    query: str,
    top_k: int = 3
):

    query_type = classify_query(query)

    if query_type == "emergency":

        emergency_results = search_emergency(
            query,
            top_k
        )

        return {
            "query_type": "emergency",
            "medical_results": [],
            "emergency_results": emergency_results
        }

    medical_results = search_medical(
        query,
        top_k
    )

    return {
        "query_type": "medical",
        "medical_results": medical_results,
        "emergency_results": []
    }