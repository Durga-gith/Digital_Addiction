import numpy as np
from sklearn.linear_model import LinearRegression
import joblib

y = np.array([0.3, 0.4, 0.5, 0.55, 0.6])
X = np.arange(len(y)).reshape(-1,1)

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "../saved_models/future_model.pkl")
print("Future prediction model trained")
