"""Sentiment analysis for TalentScout Hiring Assistant using Hugging Face API."""
import logging
import requests
import json
from typing import Dict, List, Any, Tuple
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Analyzes candidate sentiment during interview using HuggingFace API."""
    
    def __init__(self):
        """Initialize sentiment analyzer with HuggingFace API."""
        self.api_token = os.getenv("HUGGINGFACE_API_KEY")
        self.api_url = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
        self.headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
        self.emotion_history = []
    
        # Test API connection
        self._test_api_connection()
    
    def _test_api_connection(self):
        """Test the HuggingFace API connection."""
        if not self.api_token:
            logger.warning("HuggingFace API key not provided. Sentiment analysis will not be available.")
            return
            
        try:
            # Simple test request
            test_data = {"inputs": "Hello, I'm excited about this opportunity!"}
            response = requests.post(self.api_url, headers=self.headers, json=test_data, timeout=10)
            
            if response.status_code == 200:
                logger.info("HuggingFace API connection successful")
            else:
                logger.warning(f"HuggingFace API test failed with status code: {response.status_code}")
            logger.warning("Sentiment analysis will not be available")
                
        except Exception as e:
            logger.warning(f"Error testing HuggingFace API connection: {e}")
            logger.warning("Sentiment analysis will not be available")
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze the sentiment of the given text using HuggingFace API.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary of emotions and their scores
        """
        if not self.api_token:
            logger.warning("HuggingFace API key not provided")
            return {"neutral": 1.0}
            
        try:
            # Prepare request data
            data = {"inputs": text}
            
            # Make API request
            response = requests.post(self.api_url, headers=self.headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                # Parse the response
                if isinstance(result, list) and len(result) > 0:
                    emotions = result[0]
                    
                    # Convert to dictionary format
                    emotion_dict = {}
                    for emotion_data in emotions:
                        if isinstance(emotion_data, dict) and 'label' in emotion_data and 'score' in emotion_data:
                            emotion_dict[emotion_data['label']] = emotion_data['score']
            
            # Store in history
                    self.emotion_history.append(emotion_dict)
                    
                    return emotion_dict
                else:
                    logger.warning(f"Unexpected API response format: {result}")
                    return {"neutral": 1.0}
                    
            else:
                logger.error(f"API request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {"neutral": 1.0}
                
        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            return {"neutral": 1.0}
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return {"neutral": 1.0}
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"neutral": 1.0}
    
    def get_dominant_emotion(self, text: str) -> Tuple[str, float]:
        """
        Get the dominant emotion from the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Tuple of (emotion name, confidence score)
        """
        emotions = self.analyze_sentiment(text)
        if emotions:
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            return dominant_emotion
        return ("neutral", 1.0)
    
    def get_candidate_emotional_state(self) -> Dict[str, Any]:
        """
        Get the overall emotional state of the candidate based on history.
        
        Returns:
            Dictionary with emotional state analysis
        """
        if not self.emotion_history:
            return {"overall_state": "neutral", "confidence": 1.0}
            
        # Aggregate emotions across history
        emotion_totals = {}
        for emotions in self.emotion_history:
            for emotion, score in emotions.items():
                if emotion in emotion_totals:
                    emotion_totals[emotion] += score
                else:
                    emotion_totals[emotion] = score
                    
        # Find dominant emotion overall
        total_entries = len(self.emotion_history)
        for emotion in emotion_totals:
            emotion_totals[emotion] /= total_entries
            
        dominant_emotion = max(emotion_totals.items(), key=lambda x: x[1])
        
        # Check for emotional shifts
        emotional_shifts = []
        if len(self.emotion_history) > 1:
            for i in range(1, len(self.emotion_history)):
                prev_dominant = max(self.emotion_history[i-1].items(), key=lambda x: x[1])[0]
                curr_dominant = max(self.emotion_history[i].items(), key=lambda x: x[1])[0]
                if prev_dominant != curr_dominant:
                    emotional_shifts.append((prev_dominant, curr_dominant))
        
        return {
            "overall_state": dominant_emotion[0],
            "confidence": dominant_emotion[1],
            "emotional_shifts": emotional_shifts,
            "emotion_distribution": emotion_totals
        }
    
    def get_feedback_based_on_emotion(self, emotion: str, score: float) -> str:
        """
        Get interviewer feedback based on detected emotion.
        
        Args:
            emotion: The dominant emotion
            score: The confidence score for that emotion
            
        Returns:
            Feedback text for the interviewer
        """
        if score < 0.5:
            # Low confidence, don't provide specific feedback
            return ""
            
        # Provide feedback based on emotion
        if emotion == "neutral":
            return ""
        elif emotion == "joy":
            return "Candidate appears enthusiastic and positive about the opportunity."
        elif emotion == "sadness":
            return "Candidate seems hesitant or uncertain. Consider asking encouraging follow-up questions to boost confidence."
        elif emotion == "anger":
            return "Candidate may be frustrated with the process. Consider a more supportive approach or clarify any confusing questions."
        elif emotion == "fear":
            return "Candidate appears nervous or anxious. Consider a more reassuring tone and provide clear expectations."
        elif emotion == "surprise":
            return "Candidate seems surprised by the questions. Consider providing more context about the interview process."
        elif emotion == "disgust":
            return "Candidate may be uncomfortable with the current topic. Consider shifting to a different area of discussion."
        else:
            return ""
            
    def analyze_interview_progress(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze the emotional progression throughout the interview.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Analysis of emotional progression
        """
        # Reset history
        self.emotion_history = []
        
        # Analyze each user message
        user_emotions = []
        for message in messages:
            if message["role"] == "user":
                emotion, score = self.get_dominant_emotion(message["content"])
                user_emotions.append((message["content"], emotion, score))
                
        # Get overall emotional state
        emotional_state = self.get_candidate_emotional_state()
        
        # Generate interview feedback
        feedback = []
        if emotional_state["emotional_shifts"]:
            significant_shifts = [shift for shift in emotional_state["emotional_shifts"] 
                                 if shift[0] != "neutral" and shift[1] != "neutral"]
            if significant_shifts:
                feedback.append(f"Candidate's emotional state shifted from {significant_shifts[0][0]} to {significant_shifts[-1][1]} during the interview.")
        
        # Add feedback based on overall emotion
        overall_feedback = self.get_feedback_based_on_emotion(
            emotional_state["overall_state"], 
            emotional_state["confidence"]
        )
        if overall_feedback:
            feedback.append(overall_feedback)
            
        # Add confidence level information
        if emotional_state["confidence"] > 0.8:
            feedback.append("High confidence in emotional assessment.")
        elif emotional_state["confidence"] < 0.6:
            feedback.append("Low confidence in emotional assessment - consider manual review.")
            
        return {
            "emotional_state": emotional_state["overall_state"],
            "confidence": emotional_state["confidence"],
            "feedback": " ".join(feedback),
            "detailed_analysis": user_emotions,
            "emotion_distribution": emotional_state["emotion_distribution"]
        }
        
    def is_available(self) -> bool:
        """Check if sentiment analysis is available."""
        return self.api_token is not None and len(self.headers) > 0
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get the status of the HuggingFace API connection."""
        return {
            "api_key_provided": self.api_token is not None,
            "headers_configured": len(self.headers) > 0,
            "api_url": self.api_url,
            "available": self.is_available()
        } 