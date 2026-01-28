import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import joblib

df = pd.read_csv("data/recommendation_data.csv")

X = df[[
    "screen_time",
    "app_usage",
    "depression",
    "stress"
]]

model = KMeans(n_clusters=3, random_state=42)
model.fit(X)

joblib.dump(model, "../saved_models/recommendation.pkl")

print(" Recommendation model trained & saved")
