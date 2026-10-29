from fastapi import APIRouter, HTTPException
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path


router = APIRouter(
    prefix="/emergency-knowledge",
    tags=["Emergency & First-Aid Knowledge"]
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

FAISS_PATH = (
    BASE_DIR
    / "models"
    / "faiss"
    / "emergency_first_aid.index"
)

METADATA_PATH = (
    BASE_DIR
    / "models"
    / "faiss"
    / "emergency_first_aid_metadata.csv"
)


# --------------------------------------------------
# Load FAISS + Metadata + Embedding Model
# --------------------------------------------------

try:

    index = faiss.read_index(str(FAISS_PATH))

    metadata = pd.read_csv(METADATA_PATH)

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    print("Emergency & First-Aid Knowledge Base loaded successfully")

    print(
        "Total topics:",
        len(metadata)
    )

    print(
        "Total FAISS vectors:",
        index.ntotal
    )

except Exception as e:

    print(
        "Error loading Emergency & First-Aid Knowledge Base:",
        e
    )

    index = None
    metadata = None
    model = None


# --------------------------------------------------
# Medical / Emergency Safety Notice
# --------------------------------------------------

EMERGENCY_NOTICE = (
    "🚨 Emergency Notice: If you are experiencing severe symptoms "
    "or a medical emergency, contact local emergency services or "
    "visit the nearest hospital immediately. Do not rely only on "
    "this application."
)


# --------------------------------------------------
# Get All Emergency Topics
# --------------------------------------------------

@router.get("/")
def get_all_emergency_topics():

    if metadata is None:

        raise HTTPException(
            status_code=500,
            detail="Emergency Knowledge Base is not available"
        )

    records = (
        metadata
        .fillna("")
        .to_dict(orient="records")
    )

    return {

        "message": (
            "Emergency & First-Aid Knowledge Base "
            "fetched successfully"
        ),

        "total_topics": len(records),

        "topics": records,

        "emergency_notice": EMERGENCY_NOTICE
    }


# --------------------------------------------------
# Search Emergency Knowledge
# IMPORTANT: This route is before /{topic_id}
# --------------------------------------------------

@router.get("/search/query")
def search_emergency_knowledge(
    query: str,
    top_k: int = 5
):

    if (
        index is None
        or metadata is None
        or model is None
    ):

        raise HTTPException(
            status_code=500,
            detail=(
                "Emergency Knowledge Base "
                "is not available"
            )
        )

    if not query.strip():

        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    if top_k < 1:
        top_k = 1

    if top_k > 10:
        top_k = 10

    # Convert user query into embedding
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    # Search FAISS
    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for rank, idx in enumerate(
        indices[0],
        start=1
    ):

        if idx < 0 or idx >= len(metadata):
            continue

        record = (
            metadata
            .iloc[idx]
            .fillna("")
            .to_dict()
        )

        results.append({

            "rank": rank,

            "similarity_distance": float(
                distances[0][rank - 1]
            ),

            "topic": record
        })

    return {

        "message": (
            "Emergency & First-Aid "
            "knowledge search completed"
        ),

        "query": query,

        "results_found": len(results),

        "results": results,

        "emergency_notice": EMERGENCY_NOTICE
    }


# --------------------------------------------------
# Get Topic By ID
# --------------------------------------------------

@router.get("/{topic_id}")
def get_emergency_topic(
    topic_id: int
):

    if metadata is None:

        raise HTTPException(
            status_code=500,
            detail=(
                "Emergency Knowledge Base "
                "is not available"
            )
        )

    result = metadata[
        metadata["topic_id"] == topic_id
    ]

    if result.empty:

        raise HTTPException(
            status_code=404,
            detail="Emergency topic not found"
        )

    topic = (
        result
        .iloc[0]
        .fillna("")
        .to_dict()
    )

    return {

        "message": (
            "Emergency topic fetched successfully"
        ),

        "topic": topic,

        "emergency_notice": EMERGENCY_NOTICE
    }