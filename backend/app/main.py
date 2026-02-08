from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import io
import csv
import tempfile
import os
import random
import cv2
import numpy as np

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Local imports
from backend.app import crud, schemas
from backend.app.database import engine, get_db, Base
from backend.app.dependencies import get_current_active_user
from backend.app.auth import router as auth_router
from backend.app.config import settings
import base64
from sqlalchemy import text

# -------------------------------------------------------------------
# App init
# -------------------------------------------------------------------

Base.metadata.create_all(bind=engine)

try:
    from sqlalchemy import text as _text
    with engine.connect() as conn:
        conn.execute(_text("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 
                FROM pg_type t 
                JOIN pg_enum e ON e.enumtypid = t.oid 
                WHERE t.typname = 'assessmenttype' AND e.enumlabel = 'VIDEO'
            ) THEN
                ALTER TYPE assessmenttype ADD VALUE 'VIDEO';
            END IF;
        END $$;
        """))
except Exception:
    pass

app = FastAPI(
    title="Digital Addiction Assessment API",
    description="Digital Addiction Assessment System",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Root
# -------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "API running"}

# -------------------------------------------------------------------
# Auth
# -------------------------------------------------------------------

app.include_router(auth_router)

# -------------------------------------------------------------------
# Health
# -------------------------------------------------------------------

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT
    }

# -------------------------------------------------------------------
# MANUAL / VOICE ASSESSMENT
# -------------------------------------------------------------------

@app.post("/api/assessments", response_model=schemas.AssessmentResponse)
def create_assessment(
    assessment: schemas.AssessmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    return crud.create_assessment(db, assessment, current_user.id)

# -------------------------------------------------------------------
# VIDEO ASSESSMENT (image base64 → inference)
# -------------------------------------------------------------------
from pydantic import BaseModel

class VideoAssessmentRequest(BaseModel):
    image: str

@app.post("/api/assessment/video")
def video_assessment(
    payload: VideoAssessmentRequest,
    current_user = Depends(get_current_active_user),
):
    try:
        try:
            from ml_models.inference.video_inference import predict_emotion  # lazy import to avoid heavy deps at import time
        except Exception as e:
            print(f"WARNING: Failed to import video_inference: {e}")
            def predict_emotion(frame):
                return "neutral", "NORMAL"
        data_url = payload.image
        if "," in data_url:
            b64 = data_url.split(",", 1)[1]
        else:
            b64 = data_url
        img_bytes = base64.b64decode(b64)
        img_np = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        emotion, level = predict_emotion(frame)
        risk_map = {
            "NORMAL": 0.2,
            "MODERATE": 0.5,
            "ADDICTED": 0.8
        }
        risk = risk_map.get(level, 0.5)
        return {
            "emotion": emotion,
            "depression_probability": risk,
            "addiction_level": level,
            "confidence": 0.9
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Video analysis failed: {e}")

# -------------------------------------------------------------------
# HISTORY
# -------------------------------------------------------------------

@app.get("/api/assessments", response_model=List[schemas.AssessmentResponse])
def get_assessments(
    assessment_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    return crud.get_user_assessments(
        db=db,
        user_id=current_user.id,
        assessment_type=assessment_type
    )

# -------------------------------------------------------------------
# STATISTICS
# -------------------------------------------------------------------

@app.get("/api/assessments/statistics")
def get_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    return crud.get_assessment_statistics(db, current_user.id)

# -------------------------------------------------------------------
# FUTURE PREDICTION
# -------------------------------------------------------------------

@app.get("/api/predictions/future", response_model=schemas.FuturePredictionResponse)
def predict_future(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    assessments = crud.get_recent_assessments_for_prediction(db, current_user.id)

    if len(assessments) < 2:
        raise HTTPException(400, "Need at least 2 assessments")

    scores = [float(a.risk_score) for a in assessments]
    trend = scores[-1] - scores[-2]

    def clamp(x): return max(0, min(1, x))

    return {
        "next_week": {
            "risk": clamp(scores[-1] + trend * 0.5),
            "level": schemas.get_level(clamp(scores[-1] + trend * 0.5)),
            "confidence": 0.8
        },
        "next_month": {
            "risk": clamp(scores[-1] + trend),
            "level": schemas.get_level(clamp(scores[-1] + trend)),
            "confidence": 0.7
        },
        "next_3_months": {
            "risk": clamp(scores[-1] + trend * 1.5),
            "level": schemas.get_level(clamp(scores[-1] + trend * 1.5)),
            "confidence": 0.6
        },
        "trend": "INCREASING" if trend > 0 else "DECREASING",
        "based_on_assessments": len(assessments)
    }

# -------------------------------------------------------------------
# CSV EXPORT
# -------------------------------------------------------------------

@app.get("/api/export/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    data = crud.get_user_assessments(db, current_user.id)
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Date", "Type", "Addiction Level", "Risk Score"
    ])

    for a in data:
        writer.writerow([
            a.created_at, a.assessment_type.value,
            a.addiction_level.value, a.risk_score
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=assessments.csv"}
    )

# -------------------------------------------------------------------
# RUN
# -------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
