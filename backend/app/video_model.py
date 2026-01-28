import io
import base64
from typing import Dict
from PIL import Image
import numpy as np
import joblib
from pathlib import Path
from backend.app.schemas import AddictionLevel

MODEL_PATH = Path(__file__).resolve().parents[2] / "ml_models" / "video_xgb.pkl"

_model = None

def _load_model():
    global _model
    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    return _model

def _extract_features(image: Image.Image) -> np.ndarray:
    gray = image.convert("L")
    arr = np.array(gray)
    hist = np.histogram(arr, bins=64, range=(0, 255))[0].astype(np.float32)
    hist = hist / (hist.sum() + 1e-6)
    return hist.reshape(1, -1)

def predict_from_image(image_base64: str) -> Dict:
    if "," in image_base64:
        _, encoded = image_base64.split(",", 1)
    else:
        encoded = image_base64
    img_bytes = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    features = _extract_features(image)
    model = _load_model()
    if model is None:
        raise RuntimeError("video_xgb.pkl not found")
    prob = float(model.predict_proba(features)[0, 1])
    if prob < 0.33:
        level = AddictionLevel.NORMAL
    elif prob < 0.66:
        level = AddictionLevel.MODERATE
    else:
        level = AddictionLevel.ADDICTED
    return {
        "depression_probability": prob,
        "addiction_level": level,
        "confidence": 0.9,
        "emotions": {
            "neutral": max(0.0, 1.0 - prob),
            "sad": prob * 0.7,
            "anxious": prob * 0.3
        }
    }
