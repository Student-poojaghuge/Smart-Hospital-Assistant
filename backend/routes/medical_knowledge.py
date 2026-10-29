from fastapi import APIRouter, HTTPException
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path


router = APIRouter(
    prefix="/medical-knowledge",
    tags=["Medical Knowledge Base"]
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

FAISS_PATH = BASE_DIR / "models" / "faiss" / "medical_knowledge.index"
METADATA_PATH = BASE_DIR / "models" / "faiss" / "medical_knowledge_metadata.csv"


# --------------------------------------------------
# Load FAISS index and metadata
# --------------------------------------------------

try:
    index = faiss.read_index(str(FAISS_PATH))

    metadata = pd.read_csv(METADATA_PATH)

    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Medical Knowledge Base loaded successfully")
    print("Total records:", len(metadata))

except Exception as e:
    print("Error loading Medical Knowledge Base:", e)
    index = None
    metadata = None
    model = None


# --------------------------------------------------
# Get all medical knowledge
# --------------------------------------------------

@router.get("/")
def get_all_medical_knowledge():

    if metadata is None:
        raise HTTPException(
            status_code=500,
            detail="Medical Knowledge Base is not available"
        )

    records = metadata.fillna("").to_dict(orient="records")

    return {
        "message": "Medical Knowledge Base fetched successfully",
        "total_topics": len(records),
        "topics": records
    }


# --------------------------------------------------
# Get topic by ID
# --------------------------------------------------

@router.get("/{topic_id}")
def get_medical_topic(topic_id: int):

    if metadata is None:
        raise HTTPException(
            status_code=500,
            detail="Medical Knowledge Base is not available"
        )

    result = metadata[
        metadata["topic_id"] == topic_id
    ]

    if result.empty:
        raise HTTPException(
            status_code=404,
            detail="Medical topic not found"
        )

    topic = result.iloc[0].fillna("").to_dict()

    return {
        "message": "Medical topic fetched successfully",
        "topic": topic
    }


# --------------------------------------------------
# Semantic Search
# --------------------------------------------------

@router.get("/search/query")
def search_medical_knowledge(
    query: str,
    top_k: int = 5
):

    if index is None or metadata is None or model is None:
        raise HTTPException(
            status_code=500,
            detail="Medical Knowledge Base is not available"
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

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for rank, idx in enumerate(indices[0], start=1):

        if idx < 0 or idx >= len(metadata):
            continue

        record = metadata.iloc[idx].fillna("").to_dict()

        results.append({
            "rank": rank,
            "similarity_distance": float(
                distances[0][rank - 1]
            ),
            "topic": record
        })

    return {
        "message": "Medical knowledge search completed",
        "query": query,
        "results_found": len(results),
        "results": results
    }