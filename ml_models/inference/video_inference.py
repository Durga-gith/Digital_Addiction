import tensorflow as tf
import cv2
import numpy as np

model = tf.keras.models.load_model("video_emotion_model.h5")

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
    image = cv2.resize(image, (48,48))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = image / 255.0
    image = np.reshape(image, (1,48,48,1))

    preds = model.predict(image)
    emotion_idx = np.argmax(preds)
    emotion = EMOTION_MAP[emotion_idx]

    return emotion, FINAL_MAP[emotion]
