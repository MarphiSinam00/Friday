# memory/user_profile.py
from memory.database import SessionLocal, UserProfile
from datetime import datetime


def set_profile(key: str, value: str):
    db = SessionLocal()
    try:
        existing = db.query(UserProfile).filter(UserProfile.key == key).first()
        if existing:
            existing.value = value
            existing.updated_at = datetime.utcnow()
        else:
            db.add(UserProfile(key=key, value=value))
        db.commit()
    finally:
        db.close()


def get_profile(key: str, default: str = "") -> str:
    db = SessionLocal()
    try:
        record = db.query(UserProfile).filter(UserProfile.key == key).first()
        return record.value if record else default
    finally:
        db.close()


def get_all_profile() -> dict:
    db = SessionLocal()
    try:
        records = db.query(UserProfile).all()
        return {r.key: r.value for r in records}
    finally:
        db.close()
            

def save_name(name: str):
    set_profile("name", name)
    set_profile("preferred_address", "Sir")
