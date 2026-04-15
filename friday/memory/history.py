# memory/history.py
from memory.database import SessionLocal, Conversation
from config.settings import USER_NAME
import uuid


def new_session_id() -> str:
    return str(uuid.uuid4())


def save_message(session_id: str, role: str, content: str, was_online: bool = False):
    db = SessionLocal()
    try:
        msg = Conversation(
            session_id=session_id,
            role=role,
            content=content,
            was_online=was_online,
        )
        db.add(msg)
        db.commit()
    finally:
        db.close()


def get_recent_history(session_id: str, limit: int = 20) -> list[dict]:
    """Get last N messages from the current session."""
    db = SessionLocal()
    try:
        messages = (
            db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(Conversation.timestamp.desc())
            .limit(limit)
            .all()
        )
        messages.reverse()
        return [{"role": m.role, "content": m.content} for m in messages]
    finally:
        db.close()


def get_all_sessions() -> list[str]:
    db = SessionLocal()
    try:
        sessions = db.query(Conversation.session_id).distinct().all()
        return [s[0] for s in sessions]
    finally:
        db.close()
