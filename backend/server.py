from chatbot_api import app as chatbot_app
from fastapi.mount import Mount
app.mount("/chatbot", chatbot_app)
@app.post("/api/chatbot/query")
async def chatbot_query(request: dict):
    pass

@app.get("/api/chatbot/health")
async def chatbot_health():
    return {"status": "connected"}