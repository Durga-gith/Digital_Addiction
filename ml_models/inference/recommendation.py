import numpy as np
import joblib

model = joblib.load("../saved_models/recommendation.pkl")

def recommend(data):
    X = np.array([[
        data["screen_time"],
        data["app_usage"],
        data["depression"],
        data["stress"]
    ]])

    cluster = model.predict(X)[0]

    return {
        0: ["Maintain healthy habits"],
        1: ["Reduce screen time", "Use app limits"],
        2: ["Digital detox", "Seek professional help"]
    }[cluster]
