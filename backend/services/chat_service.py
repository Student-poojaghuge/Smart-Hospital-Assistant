from datetime import datetime

from database.database import SessionLocal
from database.models import ChatHistory


def save_chat_history(
    user_id: int,
    query: str,
    assistant_response: str,
    query_type: str
):
    db = SessionLocal()

    try:
        chat = ChatHistory(
            user_id=user_id,
            query=query,
            query_type=query_type,
            response=assistant_response,
            created_at=datetime.now().isoformat()
        )

        db.add(chat)
        db.commit()
        db.refresh(chat)

        return {
            "chat_id": chat.chat_id,
            "user_id": chat.user_id,
            "query": chat.query,
            "query_type": chat.query_type,
            "response": chat.response,
            "created_at": chat.created_at
        }

    finally:
        db.close()