"""Sentiment analysis for TalentScout Hiring Assistant using Hugging Face models."""
import logging
from typing import Dict, List, Any, Tuple
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Analyzes candidate sentiment during interview using HuggingFace models."""
    
    def __init__(self):
        """Initialize sentiment analyzer with appropriate models."""
        self.model = None
        self.tokenizer = None
        self._initialize_model()
        self.emotion_history = []
    
    def _initialize_model(self):
        """Initialize the HuggingFace model for sentiment analysis."""
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            
            # Use j-hartmann's emotion-english-distilroberta-base model
            # This model can detect 7 emotions: anger, disgust, fear, joy, neutral, sadness, surprise
            model_name = "j-hartmann/emotion-english-distilroberta-base"
            
            logger.info(f"Loading sentiment analysis model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            logger.info("Sentiment analysis model loaded successfully")
            
        except ImportError as e:
            logger.warning(f"Could not import transformers library: {e}")
            logger.warning("Sentiment analysis will not be available")
        except Exception as e:
            logger.warning(f"Error loading sentiment analysis model: {e}")
            logger.warning("Sentiment analysis will not be available")
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze the sentiment of the given text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary of emotions and their scores
        """
        if not self.model or not self.tokenizer:
            logger.warning("Sentiment analysis model not available")
            return {"neutral": 1.0}
            
        try:
            import torch
            
            # Tokenize and predict
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                
            # Get predicted emotions
            scores = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
            emotion_labels = self.model.config.id2label
            emotions = {emotion_labels[i]: float(scores[i]) for i in range(len(emotion_labels))}
            
            # Store in history
            self.emotion_history.append(emotions)
            
            return emotions
            
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
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        return dominant_emotion
    
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
            return "Candidate appears enthusiastic and positive."
        elif emotion == "sadness":
            return "Candidate seems hesitant or uncertain. Consider asking encouraging follow-up questions."
        elif emotion == "anger":
            return "Candidate may be frustrated. Consider a more supportive approach or clarify questions."
        elif emotion == "fear":
            return "Candidate appears nervous. Consider a more reassuring tone."
        elif emotion == "surprise":
            return "Candidate seems surprised by questions. Consider providing more context."
        elif emotion == "disgust":
            return "Candidate may be uncomfortable with the current topic. Consider shifting direction."
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
                feedback.append(f"Candidate's emotions shifted from {significant_shifts[0][0]} to {significant_shifts[-1][1]}.")
        
        # Add feedback based on overall emotion
        overall_feedback = self.get_feedback_based_on_emotion(
            emotional_state["overall_state"], 
            emotional_state["confidence"]
        )
        if overall_feedback:
            feedback.append(overall_feedback)
            
        return {
            "emotional_state": emotional_state["overall_state"],
            "confidence": emotional_state["confidence"],
            "feedback": " ".join(feedback),
            "detailed_analysis": user_emotions
        }
        
    def is_available(self) -> bool:
        """Check if sentiment analysis is available."""
        return self.model is not None and self.tokenizer is not None 