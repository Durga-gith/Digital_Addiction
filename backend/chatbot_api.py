from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from datetime import datetime
import os

app = FastAPI(title="Digital Wellness Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    user_id: Optional[str] = None
    context: Optional[Dict] = None
    chat_history: Optional[List] = None

class ChatResponse(BaseModel):
    response: str
    confidence: float
    suggestions: Optional[List[str]] = None

class WellnessChatbot:
    def __init__(self):
        self.model_path = "ml_models/chatbot_model.pkl"
        self.vectorizer = None
        self.model_data = None
        self.load_model()
    
    def load_model(self):
        """Load or train chatbot model"""
        try:
            if os.path.exists(self.model_path):
                self.model_data = joblib.load(self.model_path)
                self.vectorizer = self.model_data['vectorizer']
                print("Chatbot model loaded")
            else:
                print("Training chatbot model...")
                self.train_model()
        except Exception as e:
            print(f"Model load error: {e}")
            self.train_model()
    
    def train_model(self):
        """Train chatbot with digital wellness data"""
        training_data = {
            "questions": [
                "how to reduce screen time",
                "what is digital addiction",
                "stress management techniques",
                "best apps for digital wellness",
                "how to improve mental health",
                "digital detox methods",
                "phone addiction symptoms",
                "healthy social media usage",
                "sleep and technology",
                "mindfulness meditation apps",
                "assessment results explained",
                "understanding my risk score",
                "what does moderate addiction mean",
                "how to use the assessment tool",
                "future prediction explanation"
            ],
            "answers": [
                "To reduce screen time: 1. Set daily limits (max 2-3 hours) 2. Enable grayscale mode 3. Schedule tech-free hours 4. Find offline hobbies 5. Use app timers like Forest or Screen Time.",
                "Digital addiction is compulsive technology use interfering with daily life. Symptoms include anxiety without devices, neglecting responsibilities, sleep disruption, and physical discomfort.",
                "Digital stress management: 1. Practice mindfulness meditation 2. Take regular breaks (20-20-20 rule) 3. Set notification boundaries 4. Implement digital sabbaths 5. Physical exercise daily.",
                "Recommended wellness apps: Forest (focus), Moment (tracking), Headspace (meditation), Freedom (blocking), Space (balance), Habitica (gamification).",
                "Improve mental health: 1. Limit social media to 30 min/day 2. Practice gratitude journaling 3. Connect with nature weekly 4. Maintain 7-9 hours sleep 5. Seek professional support if needed.",
                "Digital detox strategies: 1. Weekend without devices 2. Delete unused apps monthly 3. Turn off non-essential notifications 4. Read physical books 5. Outdoor activities and hobbies.",
                "Phone addiction signs: Constant checking (>100x/day), anxiety without phone, neglecting responsibilities, sleep issues, physical discomfort (text neck, eye strain).",
                "Healthy social media: Set 30-min daily limits, curate positive feed, take weekly breaks, engage meaningfully (not passively), disable notifications, avoid bedtime scrolling.",
                "Sleep & tech hygiene: Avoid screens 1 hour before bed, use night mode, charge phone outside bedroom, establish tech-free bedtime routine, keep bedroom dark and cool.",
                "Mindfulness apps: Headspace (beginners), Calm (sleep), Insight Timer (free), Ten Percent Happier (practical), Waking Up (philosophical).",
                "Your assessment measures digital addiction risk (0-100%). Factors: psychological (depression, anxiety), behavioral (screen time, app usage), and demographic (age). Higher score = higher risk.",
                "Risk score interpretation: 0-33% (Normal), 34-66% (Moderate), 67-100% (Addicted). Each 10% increase doubles intervention urgency.",
                "Moderate addiction (34-66%): Early warning stage. Implement preventive measures: set boundaries, track usage, practice mindfulness. Reassess monthly.",
                "Assessment tool guide: 1. Complete manual or voice assessment 2. Review results 3. Check recommendations 4. Track progress in History 5. Use predictions for planning.",
                "Future predictions use ML to forecast your addiction risk trend. Based on historical data, it shows if your risk is increasing, stable, or decreasing over next 3 months."
            ]
        }
        
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
        question_vectors = self.vectorizer.fit_transform(training_data["questions"])
        
        self.model_data = {
            "questions": training_data["questions"],
            "answers": training_data["answers"],
            "vectors": question_vectors,
            "vectorizer": self.vectorizer
        }
        
        os.makedirs("ml_models", exist_ok=True)
        joblib.dump(self.model_data, self.model_path)
        print("Chatbot model trained and saved")
    
    def get_response(self, query, context=None):
        """Get response for user query"""
        query_clean = query.lower().strip()
        
        try:
            query_vec = self.vectorizer.transform([query_clean])
            similarities = cosine_similarity(query_vec, self.model_data["vectors"])[0]
            best_idx = np.argmax(similarities)
            confidence = similarities[best_idx]
            
            if confidence > 0.2:
                response = self.model_data["answers"][best_idx]
                response = self.personalize_response(response, context)
                
                return {
                    "response": response,
                    "confidence": float(confidence),
                    "matched": self.model_data["questions"][best_idx]
                }
        except Exception as e:
            print(f"Model error: {e}")
        return {
            "response": self.get_fallback_response(context),
            "confidence": 0.1,
            "matched": None
        }
    
    def personalize_response(self, response, context):
        """Add personalization based on user data"""
        if not context:
            return response
        
        personalized = response
        
        if "assessment" in context:
            score = context["assessment"].get("risk_score", 0)
            level = context["assessment"].get("addiction_level", "NORMAL")
            
            personalized += f"\n\nYour current assessment: {level} (Score: {score:.0%})"
            
            if score > 0.7:
                personalized += "\nHigh risk detected! Consider professional guidance and immediate intervention."
            elif score > 0.4:
                personalized += "\nModerate risk: Implement recommended changes to prevent escalation."
            else:
                personalized += "\nLow risk: Maintain healthy habits and monitor regularly."
        
        if "prediction" in context and context["prediction"].get("trend") == "Increasing":
            personalized += "\nTrend alert: Your risk is increasing. Proactive measures recommended."
        
        return personalized
    
    def get_fallback_response(self, context):
        """Default response when no match"""
        fallbacks = {
            "en": [
                "I specialize in digital wellness. Ask me about: assessment results, screen time reduction, stress management, or digital detox.",
                "For specific advice, try: 'How to reduce screen time?' or 'What do my assessment results mean?'",
                "I can help with digital addiction topics. What would you like to know about your digital wellness?"
            ],
            "fr": [
                "Je me spécialise dans le bien-être numérique. Demandez-moi: résultats d'évaluation, réduction du temps d'écran, gestion du stress, ou détox numérique.",
                "Pour des conseils spécifiques, essayez: 'Comment réduire le temps d'écran?' ou 'Que signifient mes résultats d'évaluation?'",
                "Je peux aider avec les sujets de dépendance numérique. Que voudriez-vous savoir sur votre bien-être numérique?"
            ]
        }
        
        lang = context.get("language", "en") if context else "en"
        import random
        return random.choice(fallbacks.get(lang, fallbacks["en"]))


chatbot = WellnessChatbot()

@app.post("/api/chatbot/query", response_model=ChatResponse)
async def query_chatbot(request: ChatRequest):
    try:
        print(f"Chatbot query: {request.message[:50]}...")
        

        ml_result = chatbot.get_response(request.message, request.context)
        

        suggestions = []
        query_lower = request.message.lower()
        
        if any(word in query_lower for word in ["result", "score", "assessment"]):
            suggestions = ["How to improve my score?", "Compare with last assessment", "What factors affect my risk?"]
        elif any(word in query_lower for word in ["screen", "time", "phone", "usage"]):
            suggestions = ["Best tracking apps", "Setting limits", "Reducing dependency"]
        elif any(word in query_lower for word in ["stress", "anxiety", "pressure"]):
            suggestions = ["Mindfulness techniques", "Breathing exercises", "Digital boundaries"]
        
        if request.language == "fr":
            suggestions = ["Comment améliorer mon score?", "Applications de suivi", "Techniques de relaxation"]
        
        return ChatResponse(
            response=ml_result["response"],
            confidence=ml_result["confidence"],
            suggestions=suggestions[:3]
        )
        
    except Exception as e:
        print(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chatbot/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "digital_wellness_chatbot",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {"message": "Digital Wellness Chatbot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)