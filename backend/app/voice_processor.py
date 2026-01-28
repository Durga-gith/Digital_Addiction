import speech_recognition as sr
import io
import wave
import tempfile
import os
import re
from typing import Optional, Tuple, List
import numpy as np

class VoiceProcessor:
    def __init__(self, language="en"):
        self.language = language
        self.recognizer = sr.Recognizer()
        self.language_codes = {"en": "en-US", "fr": "fr-FR"}
        
    def process_audio_bytes(self, audio_bytes: io.BytesIO) -> Optional[sr.AudioData]:
        """Convert bytes to AudioData for speech recognition"""
        try:

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_bytes.getvalue())
                tmp_path = tmp_file.name
            

            with sr.AudioFile(tmp_path) as source:
                audio = self.recognizer.record(source)
            

            os.unlink(tmp_path)
            
            return audio
            
        except Exception as e:
            print(f"Error processing audio bytes: {e}")
            return None
    
    def speech_to_text(self, audio_data) -> Tuple[Optional[str], Optional[str]]:
        """
        Convert speech to text with error handling
        Returns: (text, error_message)
        """
        try:

            text = self.recognizer.recognize_google(
                audio_data, 
                language=self.language_codes.get(self.language, "en-US")
            )
            return text, None
            
        except sr.UnknownValueError:
            return None, "Could not understand audio"
        except sr.RequestError as e:
           
            try:
                
                text = self.recognizer.recognize_sphinx(audio_data)
                return text, None
            except:
                return None, f"Speech recognition error: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
    
    def extract_number(self, text: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Extract numeric value from speech text
        Returns: (number, error_message)
        """
        if not text:
            return None, "No speech detected"
        
        text_lower = text.lower()
        if ("don't know" in text_lower or 
            "dont know" in text_lower or 
            "unsure" in text_lower or 
            "not sure" in text_lower):
            return None, "USER_UNSURE"
        
        numbers = re.findall(r'\b\d+\b', text)
        
        if numbers:
            try:
                return int(numbers[0]), None
            except ValueError:
                pass
        
        word_to_num = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
            'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
            'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
            'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
            'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
            'hundred': 100
        }
        
        words = text_lower.split()
        total = 0
        current = 0
        
        for word in words:
            if word in word_to_num:
                value = word_to_num[word]
                if value >= 100:
                    current *= value
                elif value >= 20:
                    current = value
                else:
                    current += value
            elif word == 'and':
                continue
        
        if current > 0:
            return current, None
        
        return None, "No number found in speech"
    
    def validate_number_range(self, number: int, min_val: int, max_val: int) -> bool:
        """Validate if number is within acceptable range"""
        return min_val <= number <= max_val

class VoiceAssessmentHandler:
    def __init__(self, language="en"):
        self.voice_processor = VoiceProcessor(language)
        self.questions_en = [
            ("What is your depression level? Say a number between 0 and 30.", 0, 30),
            ("What is your anxiety level? Say a number between 0 and 30.", 0, 30),
            ("What is your stress level? Say a number between 0 and 30.", 0, 30),
            ("What is your self-esteem level? Say a number between 0 and 30.", 0, 30),
            ("What is your daily app usage in minutes? Say a number.", 0, 1440),
            ("What is your daily screen time in hours? Say a number.", 0, 24),
            ("How old are you? Say your age.", 12, 100)
        ]
        
        self.questions_fr = [
            ("Quel est votre niveau de dépression ? Dites un nombre entre 0 et 30.", 0, 30),
            ("Quel est votre niveau d'anxiété ? Dites un nombre entre 0 et 30.", 0, 30),
            ("Quel est votre niveau de stress ? Dites un nombre entre 0 et 30.", 0, 30),
            ("Quel est votre niveau d'estime de soi ? Dites un nombre entre 0 et 30.", 0, 30),
            ("Quelle est votre utilisation quotidienne des applications en minutes ? Dites un nombre.", 0, 1440),
            ("Quel est votre temps d'écran quotidien en heures ? Dites un nombre.", 0, 24),
            ("Quel âge avez-vous ? Dites votre âge.", 12, 100)
        ]
    
    def get_questions(self, language="en"):
        return self.questions_en if language == "en" else self.questions_fr
    
    def process_voice_response(self, audio_bytes, current_question_idx, language="en"):
        """Process voice response for current question"""
        audio_data = self.voice_processor.process_audio_bytes(audio_bytes)
        if not audio_data:
            return {
                "success": False,
                "error": "Could not process audio data",
                "retry_question": True,
                "message": "Audio processing failed. Please try again."
            }
        
        text, error = self.voice_processor.speech_to_text(audio_data)
        
        if error:
            return {
                "success": False,
                "error": error,
                "retry_question": True,
                "message": "Could not understand audio. Please try again."
            }
        
        number, num_error = self.voice_processor.extract_number(text)
        
        if num_error == "USER_UNSURE":
            return {
                "success": False,
                "error": "USER_UNSURE",
                "retry_question": False,
                "message": "Switching to fallback assessment...",
                "recognized_text": text
            }
        
        if num_error:
            return {
                "success": False,
                "error": num_error,
                "retry_question": True,
                "message": f"I heard: '{text}'. Please say a number.",
                "recognized_text": text
            }
        
        questions = self.get_questions(language)
        _, min_val, max_val = questions[current_question_idx]
        
        if not self.voice_processor.validate_number_range(number, min_val, max_val):
            return {
                "success": False,
                "error": f"Number {number} out of range {min_val}-{max_val}",
                "retry_question": True,
                "message": f"Please say a number between {min_val} and {max_val}. You said {number}.",
                "recognized_text": text,
                "value": number
            }
        
        return {
            "success": True,
            "value": number,
            "message": f"Got {number}.",
            "recognized_text": text
        }