from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    Text, Boolean, ForeignKey, Enum, CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.database import Base
import enum

# Enums for better data integrity
class AddictionLevel(str, enum.Enum):
    NORMAL = "NORMAL"
    MODERATE = "MODERATE"
    ADDICTED = "ADDICTED"

class AssessmentType(str, enum.Enum):
    MANUAL = "MANUAL"
    VOICE = "VOICE"
    ML_SURVEY = "ML_SURVEY"
    HEALTH = "HEALTH"
    VIDEO = "VIDEO"

class Language(str, enum.Enum):
    EN = "EN"
    FR = "FR"

class ReportType(str, enum.Enum):
    PDF = "PDF"
    CSV = "CSV"
    SUMMARY = "SUMMARY"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    age = Column(Integer, CheckConstraint("age >= 12 AND age <= 100"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    downloads = relationship("DownloadHistory", back_populates="user", cascade="all, delete-orphan")

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Assessment metadata
    assessment_type = Column(Enum(AssessmentType), default=AssessmentType.MANUAL)
    
    # Psychological factors (0-30)
    depression = Column(Integer, CheckConstraint("depression >= 0 AND depression <= 30"))
    anxiety = Column(Integer, CheckConstraint("anxiety >= 0 AND anxiety <= 30"))
    stress = Column(Integer, CheckConstraint("stress >= 0 AND stress <= 30"))
    self_esteem = Column(Integer, CheckConstraint("self_esteem >= 0 AND self_esteem <= 30"))
    
    # Behavioral factors
    app_usage_min = Column(Integer, CheckConstraint("app_usage_min >= 0"), default=0)
    screen_time_hours = Column(Float, CheckConstraint("screen_time_hours >= 0"), default=0.0)
    data_usage_mb = Column(Integer, CheckConstraint("data_usage_mb >= 0"), default=0)
    age = Column(Integer, CheckConstraint("age >= 12 AND age <= 100"))
    
    # Results
    addiction_level = Column(Enum(AddictionLevel), nullable=False)
    risk_score = Column(Float, CheckConstraint("risk_score >= 0 AND risk_score <= 1"), nullable=False)
    
    # Additional info
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    
    # Indexes for better query performance
    __table_args__ = (
        CheckConstraint("depression IS NOT NULL"),
        CheckConstraint("anxiety IS NOT NULL"),
        CheckConstraint("stress IS NOT NULL"),
        CheckConstraint("self_esteem IS NOT NULL"),
        CheckConstraint("risk_score IS NOT NULL"),
    )

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Chat content
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    
    # Metadata
    language = Column(Enum(Language), default=Language.EN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_history")

class DownloadHistory(Base):
    __tablename__ = "download_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Download info
    report_type = Column(Enum(ReportType), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)  # in bytes
    file_format = Column(String(10))
    
    # Metadata
    download_date = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45))  # IPv6 compatible
    
    # Relationships
    user = relationship("User", back_populates="downloads")

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, nullable=False)
    model_version = Column(String(20), nullable=False)
    model_path = Column(String(255), nullable=False)
    accuracy = Column(Float)
    trained_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
