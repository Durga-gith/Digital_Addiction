import os
import csv
import numpy as np
from PIL import Image
from pathlib import Path

# Setup paths
ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "ml_models" / "training" / "data"
IMAGES_DIR = DATA_DIR / "images"
CSV_PATH = DATA_DIR / "video_dataset.csv"

# Ensure directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)

# Generate dummy images
# We will create 20 images: 10 'normal' (label 0) and 10 'addicted' (label 1)
# To make them distinguishable for the model, we'll make 'normal' images brighter and 'addicted' images darker
# This is just for testing the pipeline, not for real model performance.

data_rows = []

print(f"Generating dummy data in {DATA_DIR}...")

for i in range(20):
    label = i % 2  # 0 or 1
    
    # Create random image
    if label == 0:
        # Normal: Brighter image (mean ~180)
        arr = np.random.normal(180, 30, (224, 224)).clip(0, 255).astype(np.uint8)
    else:
        # Addicted: Darker image (mean ~80)
        arr = np.random.normal(80, 30, (224, 224)).clip(0, 255).astype(np.uint8)
    
    img = Image.fromarray(arr)
    filename = f"img_{i}.jpg"
    img_path = IMAGES_DIR / filename
    img.save(img_path)
    
    # Path relative to ROOT for the CSV, as expected by the training script
    # The training script does: img_path = ROOT / row["image_path"]
    # So we need the path from ROOT
    rel_path = img_path.relative_to(ROOT)
    
    data_rows.append({
        "image_path": str(rel_path),
        "label": label
    })

# Write CSV
with open(CSV_PATH, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["image_path", "label"])
    writer.writeheader()
    writer.writerows(data_rows)

print(f"Created {len(data_rows)} entries in {CSV_PATH}")
