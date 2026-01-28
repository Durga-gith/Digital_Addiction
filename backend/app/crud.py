from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Optional, List
from datetime import datetime, timedelta
import bcrypt
from backend.app import models, schemas

# User operations
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    # Hash password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password.decode('utf-8'),
        full_name=user.full_name,
        age=user.age
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        return None
    return user

# Assessment operations
def create_assessment(db: Session, assessment: schemas.AssessmentCreate, user_id: int) -> models.Assessment:
    db_assessment = models.Assessment(
        user_id=user_id,
        **assessment.dict()
    )
    
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

def get_user_assessments(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    assessment_type: Optional[str] = None
) -> List[models.Assessment]:
    query = db.query(models.Assessment).filter(models.Assessment.user_id == user_id)
    
    if assessment_type:
        query = query.filter(models.Assessment.assessment_type == assessment_type)
    
    return query.order_by(desc(models.Assessment.created_at)).offset(skip).limit(limit).all()

def get_assessment_statistics(db: Session, user_id: int) -> dict:
    # Get basic statistics
    stats = db.query(
        func.count(models.Assessment.id).label("total_assessments"),
        func.avg(models.Assessment.risk_score).label("avg_risk"),
        func.min(models.Assessment.risk_score).label("min_risk"),
        func.max(models.Assessment.risk_score).label("max_risk"),
        func.avg(models.Assessment.screen_time_hours).label("avg_screen_time"),
        func.sum(models.Assessment.app_usage_min).label("total_app_usage")
    ).filter(models.Assessment.user_id == user_id).first()
    
    # Get addiction level distribution
    level_dist = db.query(
        models.Assessment.addiction_level,
        func.count(models.Assessment.id).label("count")
    ).filter(models.Assessment.user_id == user_id).group_by(models.Assessment.addiction_level).all()
    
    # Get first and last assessment dates
    dates = db.query(
        func.min(models.Assessment.created_at).label("first_date"),
        func.max(models.Assessment.created_at).label("last_date")
    ).filter(models.Assessment.user_id == user_id).first()
    
    return {
        "total_assessments": stats.total_assessments or 0,
        "average_risk_score": float(stats.avg_risk or 0),
        "min_risk_score": float(stats.min_risk or 0),
        "max_risk_score": float(stats.max_risk or 0),
        "average_screen_time": float(stats.avg_screen_time or 0),
        "total_app_usage": stats.total_app_usage or 0,
        "addiction_level_distribution": {level: count for level, count in level_dist},
        "first_assessment_date": dates.first_date,
        "latest_assessment_date": dates.last_date
    }

def get_recent_assessments_for_prediction(db: Session, user_id: int, limit: int = 5) -> List[models.Assessment]:
    return db.query(models.Assessment).filter(
        models.Assessment.user_id == user_id
    ).order_by(desc(models.Assessment.created_at)).limit(limit).all()

# Chat history operations
def save_chat_message(
    db: Session, 
    user_id: int, 
    user_message: str, 
    bot_response: str,
    language: str = "EN"
) -> models.ChatHistory:
    chat = models.ChatHistory(
        user_id=user_id,
        user_message=user_message,
        bot_response=bot_response,
        language=language
    )
    
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def get_chat_history(db: Session, user_id: int, limit: int = 20) -> List[models.ChatHistory]:
    return db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == user_id
    ).order_by(desc(models.ChatHistory.created_at)).limit(limit).all()

# Download history operations
def save_download_record(
    db: Session,
    user_id: int,
    report_type: str,
    file_name: str,
    file_size: Optional[int] = None,
    file_format: Optional[str] = None,
    ip_address: Optional[str] = None
) -> models.DownloadHistory:
    download = models.DownloadHistory(
        user_id=user_id,
        report_type=report_type,
        file_name=file_name,
        file_size=file_size,
        file_format=file_format,
        ip_address=ip_address
    )
    
    db.add(download)
    db.commit()
    db.refresh(download)
    return download