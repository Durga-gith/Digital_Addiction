import base64
import requests
import os

API = "http://localhost:8000"

def main():
    # Login test user (create if needed)
    reg = {
        "username": "video_tester",
        "password": "password123",
        "email": "video@test.com",
        "full_name": "Video Tester",
        "age": 25
    }
    try:
        requests.post(f"{API}/api/auth/register", json=reg, timeout=5)
    except Exception:
        pass
    token_res = requests.post(f"{API}/api/auth/login", data={"username": reg["username"], "password": reg["password"]})
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Read a sample image and encode
    img_path = os.path.join("simple-ui", "assets", "girl-mobile.jpg")
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64}"

    # Call video analysis endpoint
    res = requests.post(f"{API}/api/assessment/video", json={"image": data_url}, headers=headers)
    print("Analysis status:", res.status_code)
    print("Analysis body:", res.text)

    if res.ok:
        j = res.json()
        # Save assessment via standard endpoint to ensure DB history
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
        save = requests.post(f"{API}/api/assessments", json=payload, headers=headers)
        print("Save status:", save.status_code)
        print("Save body:", save.text)
        # Fetch history to verify
        hist = requests.get(f"{API}/api/assessments", headers=headers)
        print("History status:", hist.status_code)
        if hist.ok:
            items = hist.json()
            videos = [a for a in items if a.get("assessment_type") == "VIDEO"]
            print(f"Total assessments: {len(items)}; VIDEO count: {len(videos)}")
            if videos:
                last = videos[0]
                print(f"Latest VIDEO: level={last['addiction_level']}, risk={last['risk_score']}, created_at={last['created_at']}")

if __name__ == "__main__":
    main()
