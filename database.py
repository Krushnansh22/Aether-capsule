import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv(override=True)

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL', '').replace('DATABASE_URL=', '').strip("'\"")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL, 
    pool_size=5, 
    max_overflow=10, 
    pool_pre_ping=True, 
    connect_args={"connect_timeout": 10}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Capsule(Base):
    __tablename__ = "capsules"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    send_date = Column(DateTime, nullable=False)
    delivered = Column(Boolean, default=False)
    delivered_at = Column(DateTime, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized on Supabase PostgreSQL.")

def save_capsule(email: str, message: str, file_path: str | None, send_date: datetime) -> int:
    db = SessionLocal()
    try:
        new_capsule = Capsule(
            email=email,
            message=message,
            file_path=file_path,
            created_at=datetime.now(),
            send_date=send_date,
            delivered=False
        )
        db.add(new_capsule)
        db.commit()
        db.refresh(new_capsule)
        return new_capsule.id
    finally:
        db.close()

def get_due_capsules(as_of: datetime) -> list[dict]:
    db = SessionLocal()
    try:
        due = db.query(Capsule).filter(Capsule.delivered == False, Capsule.send_date <= as_of).all()
        return [{
            "id": c.id,
            "email": c.email,
            "message": c.message,
            "file_path": c.file_path,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "send_date": c.send_date.isoformat() if c.send_date else None,
            "delivered": 1 if c.delivered else 0,
            "delivered_at": c.delivered_at.isoformat() if c.delivered_at else None
        } for c in due]
    finally:
        db.close()

def mark_delivered(capsule_id: int):
    db = SessionLocal()
    try:
        capsule = db.query(Capsule).filter(Capsule.id == capsule_id).first()
        if capsule:
            capsule.delivered = True
            capsule.delivered_at = datetime.now()
            db.commit()
            logger.info(f"Capsule {capsule_id} marked as delivered.")
    finally:
        db.close()