import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import json
import os

class MLDigitalWellnessAssistant:
    def __init__(self, model_path="ml_models/chatbot_model.pkl"):
        self.vectorizer = None
        self.trained_model = None
        self.model_path = model_path
        self.load_model()
        
    def load_model(self):
        """Load pre-trained model or train new one"""
        try:
            if os.path.exists(self.model_path):
                self.trained_model = joblib.load(self.model_path)
                self.vectorizer = self.trained_model['vectorizer']
                print("Chatbot model loaded successfully")
            else:
                print("No pre-trained model found, training new model...")
                self.train_model()
        except Exception as e:
            print(f"Error loading model: {e}")
            self.train_model()
    
    def train_model(self):
        """Train the chatbot model with digital wellness data"""
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
                "how to focus better",
                "reduce phone notifications",
                "work life balance digital",
                "eye strain from screens",
                "technology and relationships",
                "digital minimalism",
                "internet addiction help",
                "gaming addiction symptoms",
                "social media detox",
                "productivity apps"
            ],
            "answers": [
                "To reduce screen time: 1. Set daily limits 2. Enable grayscale mode 3. Schedule tech-free hours 4. Find offline hobbies 5. Use app timers",
                "Digital addiction is compulsive technology use interfering with daily life. Symptoms: anxiety without devices, neglecting responsibilities, sleep disruption.",
                "Digital stress management: 1. Practice mindfulness 2. Take regular breaks 3. Set notification boundaries 4. Digital sabbaths 5. Physical exercise",
                "Recommended apps: Forest (focus), Moment/Screen Time (tracking), Headspace/Calm (meditation), Freedom/Cold Turkey (blocking), Space (balance).",
                "Improve mental health: 1. Limit social media 2. Practice gratitude journaling 3. Connect with nature 4. Maintain sleep hygiene 5. Seek support when needed.",
                "Digital detox strategies: 1. Weekend without devices 2. Delete unused apps 3. Turn off notifications 4. Read physical books 5. Outdoor activities",
                "Phone addiction signs: Constant checking, anxiety without phone, neglecting responsibilities, sleep issues, physical discomfort (text neck, eye strain).",
                "Healthy social media: Set time limits, curate your feed, take regular breaks, engage meaningfully, avoid comparison, disable notifications.",
                "Sleep & tech: Avoid screens 1 hour before bed, use night mode/blue light filters, charge phone outside bedroom, establish tech-free bedtime routine.",
                "Mindfulness apps: Headspace, Calm, Insight Timer, Ten Percent Happier, Waking Up, Healthy Minds Program.",
                "Better focus: Use Pomodoro technique, eliminate distractions, single-tasking, focus apps, regular breaks, designated focus times.",
                "Reduce notifications: Turn off non-essential alerts, batch notifications, use Do Not Disturb, categorize importance, schedule notification checks.",
                "Work-life balance: Set clear boundaries, designated work hours, separate devices, digital disconnection time, prioritize offline activities.",
                "Reduce eye strain: 20-20-20 rule (every 20 minutes, look 20 feet away for 20 seconds), proper lighting, screen distance, blue light glasses, regular breaks.",
                "Tech & relationships: Designated device-free time, active listening, shared offline activities, communication about tech usage, quality time without screens.",
                "Digital minimalism: Intentional tech use, essential apps only, regular digital decluttering, value-based usage, mindful consumption.",
                "Internet addiction: Set strict limits, use blocking software, seek professional help, join support groups, develop offline interests.",
                "Gaming addiction: Loss of control over gaming, prioritizing gaming over responsibilities, withdrawal symptoms, continued use despite problems.",
                "Social media detox: Delete apps temporarily, limit usage, unfollow negative accounts, engage in real-world activities, track usage patterns.",
                "Productivity apps: Todoist/Things (tasks), Notion/Evernote (notes), Rescue Time/Forest (focus), Trello/Asana (projects), Google Calendar (scheduling)."
            ]
        }
        
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        question_vectors = self.vectorizer.fit_transform(training_data["questions"])
        
        self.trained_model = {
            "questions": training_data["questions"],
            "answers": training_data["answers"],
            "vectors": question_vectors,
            "vectorizer": self.vectorizer
        }
        
        joblib.dump(self.trained_model, self.model_path)
        print("Chatbot model trained and saved")
    
    def get_response(self, query, user_context=None):
        """Get response for user query"""

        query_processed = query.lower().strip()
        

        try:
            query_vector = self.vectorizer.transform([query_processed])
        except Exception as e:
            print(f"Vectorization error: {e}")
            return self.get_fallback_response(query_processed, user_context)
        

        similarities = cosine_similarity(
            query_vector, 
            self.trained_model["vectors"]
        )[0]
        

        best_match_idx = np.argmax(similarities)
        similarity_score = similarities[best_match_idx]
        
        if similarity_score > 0.25:  
            response = self.trained_model["answers"][best_match_idx]
            
           
            if user_context:
                response = self.personalize_response(response, user_context)
            
            return {
                "response": response,
                "confidence": float(similarity_score),
                "matched_question": self.trained_model["questions"][best_match_idx]
            }
        else:
        
            return self.get_fallback_response(query_processed, user_context)
    
    def personalize_response(self, response, context):
        """Add personalization based on user context"""
        personalized_response = response
        
        if "latest_assessment" in context:
            assessment = context["latest_assessment"]
            
        
            if assessment["risk_score"] > 0.7:
                personalized_response += "\n\n⚠️ Given your high risk score, consider seeking professional guidance for personalized support."
            elif assessment["risk_score"] > 0.4:
                personalized_response += "\n\n📊 Your moderate risk indicates implementing changes now can prevent escalation."
        
        if "predictions" in context:
            predictions = context["predictions"]
            if predictions.get("trend") == "Increasing":
                personalized_response += "\n\n📈 Your trend shows increasing risk - proactive measures are recommended."
        
        return personalized_response
    
    def get_fallback_response(self, query, context):
        """Provide fallback response when no good match"""
        fallback_responses = {
            "en": [
                "I understand you're asking about digital wellness. Could you please rephrase or ask about specific topics like screen time, stress management, or assessment results?",
                "I specialize in digital addiction and wellness topics. You can ask me about: assessment results, screen time reduction, stress management, or digital detox techniques.",
                "For more specific advice, try asking about: 'How to reduce my screen time?' or 'What do my assessment results mean?' or 'Digital stress management tips'."
            ],
            "fr": [
                "Je comprends que vous posez des questions sur le bien-être numérique. Pourriez-vous reformuler ou poser des questions sur des sujets spécifiques comme le temps d'écran, la gestion du stress ou les résultats d'évaluation?",
                "Je me spécialise dans la dépendance numérique et le bien-être. Vous pouvez me poser des questions sur: les résultats d'évaluation, la réduction du temps d'écran, la gestion du stress ou les techniques de détox numérique.",
                "Pour des conseils plus spécifiques, essayez de demander: 'Comment réduire mon temps d'écran?' ou 'Que signifient mes résultats d'évaluation?' ou 'Conseils de gestion du stress numérique'."
            ]
        }
        
        language = "en"
        if context and context.get("language"):
            language = context["language"]
        
        import random
        response = random.choice(fallback_responses.get(language, fallback_responses["en"]))
        
        return {
            "response": response,
            "confidence": 0.1,
            "matched_question": None
        }

chatbot_instance = MLDigitalWellnessAssistant()