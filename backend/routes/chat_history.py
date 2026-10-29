from fastapi import APIRouter, Depends, HTTPException, Query

from database.database import SessionLocal
from database.models import ChatHistory
from backend.services.auth_dependency import get_current_user


router = APIRouter(
    prefix="/chat-history",
    tags=["Chat History"]
)


# ============================================================
# JWT PROTECTED - CURRENT USER CHAT HISTORY
# ============================================================

@router.get("/my-history")
def get_my_chat_history(
    current_user: dict = Depends(get_current_user)
):
    db = SessionLocal()

    try:
        user_id = current_user["user_id"]

        chats = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.chat_id.desc())
            .all()
        )

        history = []

        for chat in chats:
            history.append({
                "chat_id": chat.chat_id,
                "user_id": chat.user_id,
                "query": chat.query,
                "query_type": chat.query_type,
                "response": chat.response,
                "created_at": chat.created_at
            })

        return {
            "message": "My chat history fetched successfully",
            "user_id": user_id,
            "total_chats": len(history),
            "history": history
        }

    finally:
        db.close()


# ============================================================
# JWT PROTECTED - GET USER CHAT HISTORY
# ============================================================

@router.get("/{user_id}")
def get_chat_history(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    # Check logged-in user
    logged_in_user_id = current_user["user_id"]

    if logged_in_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access another user's chat history"
        )

    db = SessionLocal()

    try:
        total_chats = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .count()
        )

        chats = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.chat_id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        history = []

        for chat in chats:
            history.append({
                "chat_id": chat.chat_id,
                "user_id": chat.user_id,
                "query": chat.query,
                "query_type": chat.query_type,
                "response": chat.response,
                "created_at": chat.created_at
            })

        return {
            "message": "Chat history fetched successfully",
            "user_id": user_id,
            "total_chats": total_chats,
            "limit": limit,
            "offset": offset,
            "returned_chats": len(history),
            "history": history
        }

    finally:
        db.close()


# ============================================================
# JWT PROTECTED - GET SINGLE CHAT
# ============================================================

@router.get("/{user_id}/{chat_id}")
def get_single_chat(
    user_id: int,
    chat_id: int,
    current_user: dict = Depends(get_current_user)
):
    logged_in_user_id = current_user["user_id"]

    if logged_in_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access another user's chat"
        )

    db = SessionLocal()

    try:
        chat = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.chat_id == chat_id,
                ChatHistory.user_id == user_id
            )
            .first()
        )

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat history not found for this user"
            )

        return {
            "message": "Chat fetched successfully",
            "chat": {
                "chat_id": chat.chat_id,
                "user_id": chat.user_id,
                "query": chat.query,
                "query_type": chat.query_type,
                "response": chat.response,
                "created_at": chat.created_at
            }
        }

    finally:
        db.close()


# ============================================================
# JWT PROTECTED - DELETE CHAT
# ============================================================

@router.delete("/{user_id}/{chat_id}")
def delete_chat_history(
    user_id: int,
    chat_id: int,
    current_user: dict = Depends(get_current_user)
):
    logged_in_user_id = current_user["user_id"]

    if logged_in_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete another user's chat"
        )

    db = SessionLocal()

    try:
        chat = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.chat_id == chat_id,
                ChatHistory.user_id == user_id
            )
            .first()
        )

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat history not found for this user"
            )

        db.delete(chat)
        db.commit()

        return {
            "message": "Chat history deleted successfully",
            "user_id": user_id,
            "chat_id": chat_id
        }

    finally:
        db.close()