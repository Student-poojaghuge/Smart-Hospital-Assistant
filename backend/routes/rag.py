from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from backend.services.rag_service import classified_search
from backend.services.response_generator import (
    generate_medical_response,
    generate_emergency_response
)
from backend.services.chat_service import save_chat_history
from backend.services.auth_dependency import get_current_user


router = APIRouter(
    prefix="/rag",
    tags=["RAG Medical Assistant"]
)


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 3


# ============================================================
# RAG KNOWLEDGE RETRIEVAL
# ============================================================

@router.post("/query")
def rag_query(
    request: RAGQueryRequest,
    current_user: dict = Depends(get_current_user)
):

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    top_k = request.top_k

    if top_k < 1:
        top_k = 1

    if top_k > 5:
        top_k = 5

    results = classified_search(
        query=query,
        top_k=top_k
    )

    return {
        "message": "RAG knowledge retrieval completed successfully",
        "query": query,
        "query_type": results["query_type"],
        "medical_results": results["medical_results"],
        "emergency_results": results["emergency_results"],

        "medical_information_notice": (
            "⚠️ Medical Information Notice: "
            "This information is for educational purposes only. "
            "It is not a medical diagnosis or personalized prescription. "
            "Consult a qualified healthcare professional before taking "
            "any medicine or making health-related decisions."
        ),

        "emergency_notice": (
            "🚨 Emergency Notice: "
            "If you are experiencing severe symptoms or a medical emergency, "
            "contact local emergency services or visit the nearest hospital "
            "immediately. Do not rely only on this application."
        )
    }


# ============================================================
# JWT PROTECTED RAG ASSISTANT
# ============================================================

@router.post("/assistant")
def rag_assistant(
    request: RAGQueryRequest,
    current_user: dict = Depends(get_current_user)
):

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    top_k = request.top_k

    if top_k < 1:
        top_k = 1

    if top_k > 5:
        top_k = 5

    # Get user ID directly from JWT
    user_id = current_user["user_id"]

    # Search knowledge bases
    results = classified_search(
        query=query,
        top_k=top_k
    )

    query_type = results["query_type"]

    # ========================================================
    # EMERGENCY RESPONSE
    # ========================================================

    if query_type == "emergency":

        response = generate_emergency_response(
            query=query,
            results=results["emergency_results"]
        )

        assistant_type = "Emergency & First-Aid Assistant"

    # ========================================================
    # MEDICAL RESPONSE
    # ========================================================

    else:

        response = generate_medical_response(
            query=query,
            results=results["medical_results"]
        )

        assistant_type = "Medical Knowledge Assistant"

    # ========================================================
    # SAVE CHAT HISTORY
    # ========================================================

    chat_response = save_chat_history(
        user_id=user_id,
        query=query,
        assistant_response=response,
        query_type=query_type
    )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "message": "RAG assistant response generated successfully",
        "assistant_type": assistant_type,
        "user_id": user_id,
        "chat": chat_response,
        "emergency": query_type == "emergency"
    }