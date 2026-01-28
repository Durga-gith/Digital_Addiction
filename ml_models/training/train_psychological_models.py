import numpy as np
from sklearn.multioutput import MultiOutputRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)

print(f"\n📁 Models will be saved in: {MODEL_DIR}")

# Training data
X = np.array([
    [5, 5, 5, 5],     # [depression, anxiety, stress, self_esteem]
    [10, 10, 10, 10],
    [15, 15, 15, 15],
    [20, 20, 20, 20],
    [25, 25, 25, 25],
    [5, 15, 25, 15],
    [25, 15, 5, 10],
])

# Target: [depression_score, anxiety_score, stress_score, screen_time_hours]
y = np.array([
    [5, 6, 7, 22],
    [10, 12, 11, 20],
    [15, 16, 18, 18],
    [20, 21, 22, 15],
    [25, 26, 27, 10],
    [15, 18, 20, 17],
    [18, 14, 16, 19],
])

print(f"📊 Training data shape: X={X.shape}, y={y.shape}")

# 1. Create and fit scaler for input features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 2. Create and train the model
model = MultiOutputRegressor(LinearRegression())
model.fit(X_scaled, y)

# 3. Save both scaler and model
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
joblib.dump(model, os.path.join(MODEL_DIR, "psych_model.pkl"))

print("✅ Psychological ML model trained and saved successfully!")
print(f"   - Scaler saved as: scaler.pkl")
print(f"   - Model saved as: psych_model.pkl")

# 4. Test the model
print("\n🧪 Testing the model:")
test_input = np.array([[12, 18, 22, 20]])  # Sample input
test_scaled = scaler.transform(test_input)
prediction = model.predict(test_scaled)
print(f"   Input: {test_input[0]}")
print(f"   Predicted: {prediction[0]}")
print(f"   Depression: {prediction[0][0]:.1f}")
print(f"   Anxiety: {prediction[0][1]:.1f}")
print(f"   Stress: {prediction[0][2]:.1f}")
print(f"   Screen Time: {prediction[0][3]:.1f} hours")