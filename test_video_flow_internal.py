import base64
import os
from fastapi.testclient import TestClient
from backend.app.main import app

API = "/api"
client = TestClient(app)

def main():
    # Register user (idempotent)
    reg = {
        "username": "video_tester_internal",
        "password": "password123",
        "email": "video_internal@test.com",
        "full_name": "Video Tester Internal",
        "age": 25
    }
    client.post(f"{API}/auth/register", json=reg)

    # Login to get token
    login = client.post(f"{API}/auth/login", data={"username": reg["username"], "password": reg["password"]})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Prepare image
    img_path = os.path.join("simple-ui", "assets", "girl-mobile.jpg")
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64}"

    # Analyze via video endpoint
    res = client.post(f"{API}/assessment/video", json={"image": data_url}, headers=headers)
    assert res.status_code == 200, res.text
    j = res.json()

    # Save assessment to DB
    payload = {
        "assessment_type": "VIDEO",
        "depression": 0,
        "anxiety": 0,
        "stress": 0,
        "self_esteem": 0,
        "app_usage_min": 0,
        "screen_time_hours": 0.0,
        "data_usage_mb": 0,
        "age": 25,
        "addiction_level": j["addiction_level"],
        "risk_score": j["depression_probability"]
    }
    save = client.post(f"{API}/assessments", json=payload, headers=headers)
    assert save.status_code == 200, save.text

    # Fetch history
    hist = client.get(f"{API}/assessments", headers=headers)
    assert hist.status_code == 200, hist.text
    items = hist.json()
    videos = [a for a in items if a.get("assessment_type") == "VIDEO"]
    print(f"Total assessments: {len(items)}; VIDEO count: {len(videos)}")
    if videos:
        last = videos[0]
        print(f"Latest VIDEO: level={last['addiction_level']}, risk={last['risk_score']}, created_at={last['created_at']}")

if __name__ == "__main__":
    main()
