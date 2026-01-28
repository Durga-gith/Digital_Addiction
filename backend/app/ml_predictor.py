import joblib
import numpy as np
from typing import Dict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = PROJECT_ROOT / "ml_models" / "saved_models"

class MLPredictor:
    def __init__(self):
        self.models_loaded = False

        self.psychological_model = None
        self.psych_label_map = None

        self.behavioral_model = None
        self.behavior_label_map = None

        self.clustering_model = None
        self.recommendation_model = None
        self.future_model = None
        self.scaler = None

    def load_models(self):
        try:
            print(f"📂 Loading ML models from: {MODEL_DIR}")

            psych_bundle = joblib.load(MODEL_DIR / "psychological_xgboost.pkl")
            self.psychological_model = psych_bundle["model"]
            self.psych_label_map = psych_bundle["label_map"]

            behav_bundle = joblib.load(MODEL_DIR / "behavioral_model.pkl")
            self.behavioral_model = behav_bundle["model"]
            self.behavior_label_map = behav_bundle["label_map"]

            self.clustering_model = joblib.load(MODEL_DIR / "clustering_model.pkl")
            self.scaler = joblib.load(MODEL_DIR / "scaler.pkl")

            self.recommendation_model = joblib.load(MODEL_DIR / "recommendation.pkl")
            self.future_model = joblib.load(MODEL_DIR / "future_model.pkl")

            self.models_loaded = True
            print("All ML models loaded successfully")

        except Exception as e:
            print(f"ML model loading failed: {e}")
            print("⚠️ Switching to rule-based logic")
            self.models_loaded = False

    def predict(self, input_data: Dict) -> Dict:
        if not self.models_loaded:
            return self._rule_based_prediction(input_data)

        psych_features = np.array([[
            input_data["depression"],
            input_data["anxiety"],
            input_data["stress"],
            input_data["self_esteem"]
        ]])

        psych_pred = self.psychological_model.predict(psych_features)[0]
        psych_level = self._reverse_lookup(self.psych_label_map, psych_pred)

        behav_features = np.array([[
            input_data["app_usage_min"],
            input_data["screen_time_hours"],
            input_data["data_usage_mb"],
            input_data["age"]
        ]])

        behav_scaled = self.scaler.transform(behav_features)
        behav_pred = self.behavioral_model.predict(behav_scaled)[0]
        behav_level = self._reverse_lookup(self.behavior_label_map, behav_pred)


        cluster_features = np.array([[
            input_data["screen_time_hours"],
            input_data["app_usage_min"],
            input_data["depression"],
            input_data["stress"]
        ]])

        cluster_id = int(self.clustering_model.predict(cluster_features)[0])

        recommendations = self._get_recommendations(cluster_features)

        final_level = self._fusion_logic(psych_level, behav_level)

        future_risk = float(self.future_model.predict([[0]])[0])

        return {
            "final_scores": input_data,
            "final_prediction": {
                "addiction_level": final_level,
                "future_risk_score": round(future_risk, 2)
            },
            "recommendations": recommendations,
            "meta": {
                "psychological_level": psych_level.upper(),
                "behavioral_level": behav_level.upper(),
                "cluster_id": cluster_id,
                "confidence": "ML_MODELS"
            }
        }

    def _reverse_lookup(self, label_map, value):
        for k, v in label_map.items():
            if v == value:
                return k
        return "unknown"

    def _fusion_logic(self, psych, behav):
        if psych == "addicted":
            return "ADDICTED"
        if psych == "moderate" or behav in ["high", "very_high"]:
            return "MODERATE"
        return "NORMAL"

    def _get_recommendations(self, features):
        cluster = int(self.recommendation_model.predict(features)[0])
        return {
            0: [
                "Maintain healthy digital habits",
                "Continue regular breaks"
            ],
            1: [
                "Reduce daily screen time",
                "Use app usage limits"
            ],
            2: [
                "Consider a digital detox",
                "Seek professional guidance"
            ]
        }.get(cluster, ["Maintain balanced usage"])

    def _rule_based_prediction(self, input_data: Dict) -> Dict:
        return {
            "final_scores": input_data,
            "final_prediction": {
                "addiction_level": "MODERATE"
            },
            "recommendations": [
                "Limit screen time",
                "Take regular breaks",
                "Practice digital mindfulness"
            ],
            "meta": {
                "confidence": "RULE_BASED"
            }
        }


predictor = MLPredictor()
predictor.load_models()


def predict_addiction(input_data: Dict) -> Dict:
    """
    ONLY function to be imported by FastAPI routes
    """
    return predictor.predict(input_data)
