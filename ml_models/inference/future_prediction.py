import joblib
import numpy as np

model = joblib.load("../saved_models/future_model.pkl")

def predict(history):
    start = len(history)
    X_future = np.arange(start, start+3).reshape(-1,1)
    return model.predict(X_future).tolist()
