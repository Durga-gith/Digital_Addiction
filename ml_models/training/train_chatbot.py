"""
MINIMAL Chatbot Training - No external dependencies except scikit-learn
"""
import pandas as pd
import numpy as np
import joblib
import json
import re
from pathlib import Path
from datetime import datetime

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    print(" scikit-learn not available. Using simple matching.")
    SKLEARN_AVAILABLE = False

class MinimalChatbotTrainer:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.models_dir = self.base_dir / "saved_models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def simple_match(self, query, questions):
        """Simple keyword matching without ML"""
        query = query.lower()
        best_match = None
        best_score = 0
        
        for i, question in enumerate(questions):
            question_lower = question.lower()
            score = self.calculate_similarity(query, question_lower)
            
            if score > best_score:
                best_score = score
                best_match = i
        
        return best_match, best_score
    
    def calculate_similarity(self, text1, text2):
        """Simple similarity calculation"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0
    
    def create_minimal_model(self):
        """Create a minimal chatbot model"""
        print(" Creating minimal chatbot model...")
        
        qa_pairs = [
            {
                "question": "What do my assessment results mean?",
                "answer": "Your assessment measures digital addiction risk (0-100%). Levels: Normal (0-33%), Moderate (34-66%), Addicted (67-100%).",
                "keywords": ["assessment", "result", "score", "mean", "interpret"],
                "category": "assessment"
            },
            {
                "question": "How to reduce screen time?",
                "answer": "Reduce screen time: 1. Set daily limits 2. Use grayscale mode 3. Schedule tech-free hours 4. Find offline hobbies.",
                "keywords": ["screen", "time", "reduce", "limit", "phone"],
                "category": "screentime"
            },
            {
                "question": "Digital stress management?",
                "answer": "Stress management: 1. Practice mindfulness 2. Take regular breaks 3. Manage notifications 4. Try breathing exercises.",
                "keywords": ["stress", "anxiety", "manage", "relax", "calm"],
                "category": "stress"
            },
            {
                "question": "What is digital detox?",
                "answer": "Digital detox = intentional break from devices. Benefits: Less anxiety, better sleep, improved focus.",
                "keywords": ["detox", "break", "cleanse", "reset", "offline"],
                "category": "detox"
            },
            {
                "question": "Hello",
                "answer": "Hello! I'm your Digital Wellness Assistant. I can help with assessment results, screen time reduction, and stress management.",
                "keywords": ["hello", "hi", "hey", "greetings"],
                "category": "greeting"
            },
            {
                "question": "Help",
                "answer": "I can help with:  Assessment results  Screen time reduction  Stress management  Digital detox",
                "keywords": ["help", "support", "assist", "guide"],
                "category": "help"
            }
        ]
        
        model = {
            "qa_pairs": qa_pairs,
            "metadata": {
                "created_date": datetime.now().isoformat(),
                "model_type": "minimal_keyword_matching",
                "version": "1.0.0",
                "num_pairs": len(qa_pairs)
            }
        }
        

        model_path = self.models_dir / "chatbot_minimal_model.pkl"
        joblib.dump(model, model_path)
        
        print(f"Minimal model saved to: {model_path}")
        

        self.test_minimal_model(model)
        
        return model
    
    def test_minimal_model(self, model):
        """Test the minimal model"""
        print("\n Testing minimal model...")
        
        test_queries = [
            "How to reduce screen time?",
            "What do results mean?",
            "Stress help",
            "Hello",
            "Help me"
        ]
        
        for query in test_queries:
            best_idx, best_score = self.simple_match(
                query, 
                [pair["question"] for pair in model["qa_pairs"]]
            )
            
            print(f"\n Query: '{query}'")
            if best_idx is not None:
                print(f"   Match: '{model['qa_pairs'][best_idx]['question']}'")
                print(f"   Score: {best_score:.3f}")
                print(f"   Category: {model['qa_pairs'][best_idx]['category']}")
                
                if best_score > 0.3:
                    print("    Good match")
                else:
                    print("    Low confidence")
            else:
                print("   No match found")
    
    def run(self):
        """Run minimal training"""
        print("=" * 60)
        print("MINIMAL CHATBOT TRAINING")
        print("=" * 60)
        print(f"scikit-learn available: {SKLEARN_AVAILABLE}")
        
        model = self.create_minimal_model()
        
        print("\n" + "=" * 60)
        print(" MINIMAL MODEL CREATED!")
        print("=" * 60)
        print("\nThis model uses simple keyword matching.")
        print("For better accuracy, install scikit-learn:")
        print("pip install scikit-learn pandas numpy")
        
        return model

def main():
    trainer = MinimalChatbotTrainer()
    trainer.run()

if __name__ == "__main__":
    main()