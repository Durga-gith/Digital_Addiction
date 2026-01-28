"""
Chatbot Inference Module
Uses trained model to generate responses
"""
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

class ChatbotInference:
    def __init__(self, model_path: str = None, kb_path: str = None):
        """Initialize chatbot inference engine"""
        self.base_dir = Path(__file__).parent.parent
        
        if model_path is None:
            model_path = self.base_dir / "saved_models" / "chatbot_model.pkl"
        if kb_path is None:
            kb_path = self.base_dir / "chatbot_knowledge_base.json"
        
        self.model_path = Path(model_path)
        self.kb_path = Path(kb_path)
        
        self.model = None
        self.knowledge_base = None
        self.vectorizer = None
        
        self.load_model()
        self.load_knowledge_base()
        
    def load_model(self):
        """Load trained chatbot model"""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                self.vectorizer = self.model.get('vectorizer')
                print(f"   Loaded chatbot model from {self.model_path}")
                print(f"   Samples: {len(self.model['questions'])}")
                print(f"   Version: {self.model['metadata'].get('model_version', '1.0')}")
            else:
                print(f" Model not found at {self.model_path}")
                print(" Run: python training/train_chatbot.py to train model")
        except Exception as e:
            print(f" Error loading model: {e}")
            self.model = None
    
    def load_knowledge_base(self):
        """Load knowledge base for fallback responses"""
        try:
            if self.kb_path.exists():
                with open(self.kb_path, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
                print(f" Loaded knowledge base from {self.kb_path}")
            else:
                print(f" Knowledge base not found at {self.kb_path}")
                self.knowledge_base = None
        except Exception as e:
            print(f" Error loading knowledge base: {e}")
            self.knowledge_base = None
    
    def preprocess_query(self, query: str) -> str:
        """Preprocess user query for matching"""
        if not query:
            return ""
        
        query = query.lower()
        
        
        query = re.sub(r'[^\w\s?]', '', query)
        
        
        query = ' '.join(query.split())
        
        return query
    
    def get_response(self, query: str, context: Optional[Dict] = None, 
                    language: str = "en") -> Dict:
        """
        Get response for user query
        
        Args:
            query: User's question
            context: User context (assessment data, history, etc.)
            language: Response language ('en' or 'fr')
            
        Returns:
            Dict with response, confidence, and metadata
        """
        if not self.model or not self.vectorizer:
            return self.get_fallback_response(query, context, language, 0.0)
        
        
        processed_query = self.preprocess_query(query)
        
        
        if self.is_greeting(processed_query, language):
            return self.get_greeting_response(language)
        
        
        if self.is_farewell(processed_query, language):
            return self.get_farewell_response(language)
        
        try:
            
            query_vector = self.vectorizer.transform([processed_query])
            
            
            similarities = cosine_similarity(
                query_vector, 
                self.model["vectors"]
            )[0]
            
            
            best_idx = np.argmax(similarities)
            confidence = similarities[best_idx]
            
            
            if confidence > 0.1:  
                print(f"🔍 Query: '{query[:50]}...'")
                print(f"   Match: '{self.model['questions'][best_idx][:50]}...'")
                print(f"   Confidence: {confidence:.3f}")
                print(f"   Category: {self.model['categories'][best_idx]}")
            
            if confidence > 0.25:  
                response = self.model["answers"][best_idx]
                category = self.model["categories"][best_idx]
                
                response = self.personalize_response(response, context, category, language)
                
                suggestions = self.get_suggestions(category, language)
                
                return {
                    "response": response,
                    "confidence": float(confidence),
                    "category": category,
                    "matched_question": self.model["questions"][best_idx],
                    "suggestions": suggestions,
                    "source": "ml_model",
                    "requires_followup": confidence < 0.4
                }
            else:
                return self.get_knowledge_base_response(query, context, language, confidence)
                
        except Exception as e:
            print(f" Inference error: {e}")
            return self.get_fallback_response(query, context, language, 0.0)
    
    def is_greeting(self, query: str, language: str) -> bool:
        """Check if query is a greeting"""
        if not self.knowledge_base:
            return False
        
        greetings = self.knowledge_base.get("greetings", {}).get("patterns", {}).get(language, [])
        return any(greeting in query for greeting in greetings)
    
    def is_farewell(self, query: str, language: str) -> bool:
        """Check if query is a farewell"""
        if not self.knowledge_base:
            return False
        
        farewells = ["bye", "goodbye", "see you", "thanks", "thank you"]
        if language == "fr":
            farewells = ["au revoir", "à bientôt", "merci", "adieu"]
        
        return any(farewell in query for farewell in farewells)
    
    def get_greeting_response(self, language: str) -> Dict:
        """Get greeting response"""
        if self.knowledge_base:
            responses = self.knowledge_base.get("greetings", {}).get("responses", {}).get(language, [])
            if responses:
                import random
                return {
                    "response": random.choice(responses),
                    "confidence": 1.0,
                    "category": "greeting",
                    "source": "knowledge_base",
                    "suggestions": self.get_suggestions("greeting", language)
                }
        

        if language == "fr":
            return {
                "response": "Bonjour! 👋 Je suis votre Assistant de Bien-être Numérique. Comment puis-je vous aider aujourd'hui?",
                "confidence": 1.0,
                "category": "greeting",
                "source": "default"
            }
        
        return {
            "response": "Hello! 👋 I'm your Digital Wellness Assistant. How can I help you today?",
            "confidence": 1.0,
            "category": "greeting",
            "source": "default"
        }
    
    def get_farewell_response(self, language: str) -> Dict:
        """Get farewell response"""
        if language == "fr":
            return {
                "response": "Au revoir! N'hésitez pas à revenir si vous avez d'autres questions sur votre bien-être numérique. 👋",
                "confidence": 1.0,
                "category": "farewell",
                "source": "default"
            }
        
        return {
            "response": "Goodbye! Feel free to come back if you have more questions about your digital wellness. 👋",
            "confidence": 1.0,
            "category": "farewell",
            "source": "default"
        }
    
    def personalize_response(self, response: str, context: Optional[Dict], 
                           category: str, language: str) -> str:
        """Add personalization based on user context"""
        if not context:
            return response
        
        personalized = response
        
        if "assessment" in context:
            assessment = context["assessment"]
            score = assessment.get("risk_score", 0)
            level = assessment.get("addiction_level", "NORMAL").upper()
            
            if level == "ADDICTED" and score > 0.7:
                if language == "fr":
                    personalized += "\n\n Votre score élevé indique un besoin d'intervention immédiate. Consultez un professionnel."
                else:
                    personalized += "\n\n Your high score indicates need for immediate intervention. Consult a professional."
            elif level == "MODERATE" and score > 0.4:
                if language == "fr":
                    personalized += "\n\n Votre score modéré suggère des mesures préventives maintenant pour éviter l'escalade."
                else:
                    personalized += "\n\n Your moderate score suggests preventive measures now to prevent escalation."
        
        if "predictions" in context:
            pred = context["predictions"]
            trend = pred.get("trend", "stable")
            
            if trend == "Increasing":
                if language == "fr":
                    personalized += "\n Votre tendance montre une augmentation du risque. Des mesures proactives sont recommandées."
                else:
                    personalized += "\n Your trend shows increasing risk. Proactive measures are recommended."
            elif trend == "Decreasing":
                if language == "fr":
                    personalized += "\n Bonne tendance: Votre risque diminue. Continuez votre bon travail!"
                else:
                    personalized += "\n Good trend: Your risk is decreasing. Keep up the good work!"
        
       
        if self.knowledge_base and "quick_tips" in self.knowledge_base:
            if category in self.knowledge_base["quick_tips"]:
                tip = self.knowledge_base["quick_tips"][category].get(language)
                if tip:
                    personalized += f"\n\n{tip}"
        
        return personalized
    
    def get_knowledge_base_response(self, query: str, context: Optional[Dict], 
                                   language: str, confidence: float) -> Dict:
        """Get response from knowledge base when ML model has low confidence"""
        if not self.knowledge_base:
            return self.get_fallback_response(query, context, language, confidence)
        
        query_lower = query.lower()
        
        
        if "assessment_context" in self.knowledge_base:
            keywords = self.knowledge_base["assessment_context"]["keywords"].get(language, [])
            if any(keyword in query_lower for keyword in keywords):
                
                level = "normal"
                if context and "assessment" in context:
                    score = context["assessment"].get("risk_score", 0)
                    if score > 0.66:
                        level = "addicted"
                    elif score > 0.33:
                        level = "moderate"
                
                explanation = self.knowledge_base["assessment_context"]["explanations"][level].get(language)
                if explanation:
                    return {
                        "response": explanation,
                        "confidence": 0.5,  
                        "category": "assessment",
                        "source": "knowledge_base",
                        "suggestions": self.get_suggestions("assessment", language)
                    }
        
        return self.get_fallback_response(query, context, language, confidence)
    
    def get_fallback_response(self, query: str, context: Optional[Dict], 
                            language: str, confidence: float) -> Dict:
        """Get fallback response when no good match found"""
        if self.knowledge_base and "fallback_responses" in self.knowledge_base:
            responses = self.knowledge_base["fallback_responses"].get(language, [])
            if responses:
                import random
                response = random.choice(responses)
                
                if context and "assessment" in context:
                    score = context["assessment"].get("risk_score", 0)
                    if score > 0:
                        if language == "fr":
                            response += f"\n\n Votre score actuel: {score:.0%}"
                        else:
                            response += f"\n\n Your current score: {score:.0%}"
                
                return {
                    "response": response,
                    "confidence": confidence,
                    "category": "fallback",
                    "source": "knowledge_base",
                    "requires_followup": True,
                    "suggestions": self.get_suggestions("general", language)
                }
        
        if language == "fr":
            return {
                "response": "Je comprends que vous posez des questions sur le bien-être numérique. Pourriez-vous reformuler ou poser des questions sur des sujets spécifiques?",
                "confidence": confidence,
                "category": "fallback",
                "source": "default",
                "requires_followup": True
            }
        
        return {
            "response": "I understand you're asking about digital wellness. Could you please rephrase or ask about specific topics?",
            "confidence": confidence,
            "category": "fallback",
            "source": "default",
            "requires_followup": True
        }
    
    def get_suggestions(self, category: str, language: str) -> List[str]:
        """Get follow-up suggestions based on category"""
        suggestions_map = {
            "assessment": {
                "en": ["How to improve my score?", "Compare with last assessment", "What factors affect my risk?"],
                "fr": ["Comment améliorer mon score?", "Comparer avec la dernière évaluation", "Quels facteurs affectent mon risque?"]
            },
            "screentime": {
                "en": ["Best tracking apps", "Setting daily limits", "Reducing phone dependency"],
                "fr": ["Meilleures applications de suivi", "Définir des limites quotidiennes", "Réduire la dépendance au téléphone"]
            },
            "stress": {
                "en": ["Mindfulness techniques", "Breathing exercises", "Notification management"],
                "fr": ["Techniques de pleine conscience", "Exercices de respiration", "Gestion des notifications"]
            },
            "detox": {
                "en": ["Weekend detox plan", "Social media break", "Device-free activities"],
                "fr": ["Plan de détox de week-end", "Pause des réseaux sociaux", "Activités sans appareil"]
            },
            "greeting": {
                "en": ["Explain my assessment", "Screen time tips", "Stress management"],
                "fr": ["Expliquer mon évaluation", "Conseils temps d'écran", "Gestion du stress"]
            },
            "general": {
                "en": ["Assessment results", "Screen time reduction", "Digital stress help"],
                "fr": ["Résultats d'évaluation", "Réduction du temps d'écran", "Aide stress numérique"]
            }
        }
        
        return suggestions_map.get(category, {}).get(language, [])[:3]
    
    def test_inference(self, test_queries: List[str] = None):
        """Test the inference engine with sample queries"""
        if test_queries is None:
            test_queries = [
                "Hello",
                "How to reduce screen time?",
                "What does my assessment score mean?",
                "Explain future predictions",
                "Best apps for digital wellness",
                "Digital stress management techniques",
                "Goodbye"
            ]
        
        print("\n" + "=" * 60)
        print(" CHATBOT INFERENCE TEST")
        print("=" * 60)
        
        for query in test_queries:
            print(f"\n Query: {query}")
            response = self.get_response(query, language="en")
            print(f"   Response: {response['response'][:80]}...")
            print(f"   Confidence: {response['confidence']:.3f}")
            print(f"   Category: {response['category']}")
            print(f"   Source: {response['source']}")
            if response.get('suggestions'):
                print(f"   Suggestions: {response['suggestions']}")

_chatbot_instance = None

def get_chatbot():
    """Get or create chatbot instance"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = ChatbotInference()
    return _chatbot_instance

def test_chatbot():
    """Test function for quick verification"""
    chatbot = get_chatbot()
    chatbot.test_inference()

if __name__ == "__main__":
    test_chatbot()