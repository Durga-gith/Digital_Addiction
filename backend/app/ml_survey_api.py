from fastapi import APIRouter
from pydantic import BaseModel
from .ml_predictor import predict_addiction

router = APIRouter(prefix="/ml-survey", tags=["ML Survey"])

class PsychologicalSurvey(BaseModel):
    depression: int
    anxiety: int
    stress: int
    self_esteem: int
    app_usage_min: int
    screen_time_hours: float
    data_usage_mb: int
    age: int

@router.post("/predict")
def predict_from_survey(data: PsychologicalSurvey):
    payload = data.dict()

    print("ML Survey Payload:", payload) 

    result = predict_addiction(payload)

    return result
