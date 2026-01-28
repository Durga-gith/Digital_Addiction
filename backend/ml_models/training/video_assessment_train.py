import os
import csv
from pathlib import Path
from typing import List, Tuple
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
from xgboost import XGBClassifier
import joblib

ROOT = Path(__file__).resolve().parents[3]
DATA_CSV = ROOT / "ml_models" / "training" / "data" / "video_dataset.csv"
MODEL_OUT = ROOT / "ml_models" / "video_xgb.pkl"

def load_dataset() -> Tuple[np.ndarray, np.ndarray]:
    X: List[np.ndarray] = []
    y: List[int] = []
    with open(DATA_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            img_path = ROOT / row["image_path"]
            label = int(row["label"])
            if not img_path.exists():
                continue
            img = Image.open(img_path).convert("L")
            arr = np.array(img)
            hist = np.histogram(arr, bins=64, range=(0, 255))[0].astype(np.float32)
            hist = hist / (hist.sum() + 1e-6)
            X.append(hist)
            y.append(label)
    return np.stack(X), np.array(y)

def train():
    X, y = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        n_jobs=4
    )
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    auc = roc_auc_score(y_test, proba)
    acc = accuracy_score(y_test, pred)
    joblib.dump(model, MODEL_OUT)
    print({"AUC": round(auc, 4), "ACC": round(acc, 4), "model": str(MODEL_OUT)})

if __name__ == "__main__":
    train()
