import tensorflow as tf
import cv2
import numpy as np

import os
from pathlib import Path

# Get the absolute path to the current file
current_file_path = Path(__file__).resolve()
# Go up to ml_models directory
ml_models_dir = current_file_path.parent.parent

# Construct path to the model
# Based on find command: ./ml_models/training/ml_models/saved_models/video_emotion_model.h5
model_path = ml_models_dir / "training" / "ml_models" / "saved_models" / "video_emotion_model.h5"

if not model_path.exists():
    # Fallback to check if it's in the current directory or other common locations
    if Path("video_emotion_model.h5").exists():
        model_path = Path("video_emotion_model.h5")
    else:
        print(f"Warning: Model file not found at {model_path}")

try:
    model = tf.keras.models.load_model(str(model_path))
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

EMOTION_MAP = {
    0: "angry",
    1: "disgust",
    2: "fear",
    3: "happy",
    4: "sad",
    5: "surprise",
    6: "neutral"
}

FINAL_MAP = {
    "happy": "NORMAL",
    "neutral": "NORMAL",
    "surprise": "MODERATE",
    "angry": "MODERATE",
    "fear": "MODERATE",
    "sad": "ADDICTED",
    "disgust": "ADDICTED"
}

def predict_emotion(image):
    if model is None:
        raise RuntimeError("Video emotion model failed to load. Please check server logs for details.")

    image = cv2.resize(image, (48,48))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = image / 255.0
    image = np.reshape(image, (1,48,48,1))

    preds = model.predict(image)
    emotion_idx = np.argmax(preds)
    emotion = EMOTION_MAP[emotion_idx]

    return emotion, FINAL_MAP[emotion]
