import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from xgboost import XGBClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "saved_models")
os.makedirs(MODEL_DIR, exist_ok=True)

print(f"\n Models will be saved in: {MODEL_DIR}")


class DigitalAddictionMLSystem:

    def __init__(self):
        self.psychological_model = None
        self.behavioral_model = None
        self.clustering_model = None
        self.scaler = StandardScaler()
    def train_psychological_model(self, dataset_path):
        print("\nTraining Psychological XGBoost Model...")

        data = pd.read_csv(dataset_path)

        X = data[
            [
                "Depression_Score",
                "Anxiety_Score",
                "Stress_Score",
                "Self-Esteem_Score"
            ]
        ]

        y_raw = (
            data["Internet_Addiction_Level"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        mask = y_raw.isin(["normal", "moderate", "addicted"])
        X = X.loc[mask]
        y_raw = y_raw.loc[mask]

        labels = sorted(y_raw.unique())
        label_map = {lbl: i for i, lbl in enumerate(labels)}
        y = y_raw.map(label_map).astype(int)

        print(" Detected classes:", label_map)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        objective = "binary:logistic" if len(label_map) == 2 else "multi:softmax"

        self.psychological_model = XGBClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.1,
            objective=objective,
            num_class=None if len(label_map) == 2 else len(label_map),
            eval_metric="mlogloss",
            random_state=42
        )

        self.psychological_model.fit(X_train, y_train)

        acc = accuracy_score(y_test, self.psychological_model.predict(X_test))
        print(f"Psychological Model Accuracy: {acc:.2f}")

        joblib.dump(
            {"model": self.psychological_model, "label_map": label_map},
            os.path.join(MODEL_DIR, "psychological_xgboost.pkl")
        )

        print("Saved: psychological_xgboost.pkl")
    def train_behavioral_model(self, dataset_path):
        print("\n Training Behavioral Model...")

        data = pd.read_csv(dataset_path)

        feature_cols = [
            "App Usage Time (min/day)",
            "Screen On Time (hours/day)",
            "Data Usage (MB/day)",
            "Age"
        ]

        target_col = "User Behavior Class"

        X = data[feature_cols]
        y_raw = data[target_col].astype(str).str.strip().str.lower()

        labels = sorted(y_raw.unique())
        label_map = {lbl: i for i, lbl in enumerate(labels)}
        y = y_raw.map(label_map).astype(int)

        print(" Behavioral classes:", label_map)

        X_scaled = self.scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )

        self.behavioral_model = RandomForestClassifier(
            n_estimators=150,
            random_state=42
        )

        self.behavioral_model.fit(X_train, y_train)

        acc = accuracy_score(y_test, self.behavioral_model.predict(X_test))
        print(f" Behavioral Model Accuracy: {acc:.2f}")

        joblib.dump(
            {"model": self.behavioral_model, "label_map": label_map},
            os.path.join(MODEL_DIR, "behavioral_model.pkl")
        )

        joblib.dump(
            self.scaler,
            os.path.join(MODEL_DIR, "scaler.pkl")
        )

        print(" Saved: behavioral_model.pkl & scaler.pkl")

    def train_clustering_model(self, dataset_path):
        print("\n Training Clustering Model...")

        data = pd.read_csv(dataset_path)

        cluster_features = [
            "App Usage Time (min/day)",
            "Screen On Time (hours/day)",
            "Data Usage (MB/day)"
        ]

        X = data[cluster_features]
        X_scaled = self.scaler.fit_transform(X)

        self.clustering_model = KMeans(
            n_clusters=3,
            random_state=42,
            n_init=10
        )

        self.clustering_model.fit(X_scaled)

        joblib.dump(
            self.clustering_model,
            os.path.join(MODEL_DIR, "clustering_model.pkl")
        )

        print(" Saved: clustering_model.pkl")

    def train_models(self, psychological_dataset, behavioral_dataset):
        self.train_psychological_model(psychological_dataset)
        self.train_behavioral_model(behavioral_dataset)
        self.train_clustering_model(behavioral_dataset)


if __name__ == "__main__":
    print("\n Starting Digital Addiction ML Training Pipeline")

    system = DigitalAddictionMLSystem()

    system.train_models(
        psychological_dataset="data/digital_addiction_dataset.csv",
        behavioral_dataset="data/user_behavior_dataset.csv"
    )

    print("\n ALL MODELS TRAINED AND SAVED SUCCESSFULLY")
