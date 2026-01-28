from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums for schemas
class AddictionLevel(str, Enum):
    NORMAL = "NORMAL"
    MODERATE = "MODERATE"
    ADDICTED = "ADDICTED"

class AssessmentType(str, Enum):
    MANUAL = "MANUAL"
    VOICE = "VOICE"
    ML_SURVEY = "ML_SURVEY"
    HEALTH = "HEALTH"
    VIDEO = "VIDEO"

class VideoAnalysisRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image string")

class VideoAnalysisResponse(BaseModel):
    depression_probability: float
    addiction_level: AddictionLevel
    confidence: float
    emotions: dict = {}

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    age: int = Field(..., ge=12, le=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None

# Assessment schemas
class AssessmentBase(BaseModel):
    assessment_type: AssessmentType = AssessmentType.MANUAL
    depression: int = Field(..., ge=0, le=30)
    anxiety: int = Field(..., ge=0, le=30)
    stress: int = Field(..., ge=0, le=30)
    self_esteem: int = Field(..., ge=0, le=30)
    app_usage_min: int = Field(..., ge=0)
    screen_time_hours: float = Field(..., ge=0, le=24)
    data_usage_mb: int = Field(..., ge=0)
    age: int = Field(..., ge=12, le=100)
    addiction_level: AddictionLevel
    risk_score: float = Field(..., ge=0, le=1)
    notes: Optional[str] = None

class AssessmentCreate(BaseModel):
    assessment_type: str

    depression: Optional[int] = None
    anxiety: Optional[int] = None
    stress: Optional[int] = None
    self_esteem: Optional[int] = None
    app_usage_min: Optional[int] = None
    screen_time_hours: Optional[float] = None
    data_usage_mb: Optional[float] = None
    age: Optional[int] = None

    addiction_level: str
    risk_score: float


class AssessmentResponse(AssessmentBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Prediction schemas
class PredictionData(BaseModel):
    risk: float = Field(..., ge=0, le=1)
    level: AddictionLevel
    confidence: float = Field(..., ge=0, le=1)

class FuturePredictionResponse(BaseModel):
    next_week: PredictionData
    next_month: PredictionData
    next_3_months: PredictionData
    trend: str
    volatility: float
    based_on_assessments: int

# Chatbot schemas
class ChatbotRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    language: str = "EN"

class ChatbotResponse(BaseModel):
    response: str
    language: str
    timestamp: datetime

# Report schemas
class ReportRequest(BaseModel):
    report_type: str = "PDF"
    include_charts: bool = True
    include_predictions: bool = True
    time_period: str = "all"  # all, month, quarter, year

# Statistics schemas
class StatisticsResponse(BaseModel):
    total_assessments: int
    average_risk_score: float
    min_risk_score: float
    max_risk_score: float
    addiction_level_distribution: dict
    first_assessment_date: Optional[datetime]
    latest_assessment_date: Optional[datetime]
    total_screen_time: float  # hours
    total_app_usage: int  # minutes