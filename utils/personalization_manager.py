"""
Personalization Manager for TalentScout Hiring Assistant.

Handles user preferences, history tracking, and personalized responses.
"""
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib

class PersonalizationManager:
    """Manages personalization features for the TalentScout chatbot."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the personalization manager.
        
        Args:
            data_dir: Directory to store user data
        """
        self.data_dir = data_dir
        self.user_profiles_file = os.path.join(data_dir, "user_profiles.json")
        self.interaction_history_file = os.path.join(data_dir, "interaction_history.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing data
        self.user_profiles = self._load_user_profiles()
        self.interaction_history = self._load_interaction_history()
    
    def _load_user_profiles(self) -> Dict:
        """Load user profiles from file."""
        try:
            if os.path.exists(self.user_profiles_file):
                with open(self.user_profiles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading user profiles: {e}")
        return {}
    
    def _save_user_profiles(self) -> None:
        """Save user profiles to file."""
        try:
            with open(self.user_profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving user profiles: {e}")
    
    def _load_interaction_history(self) -> Dict:
        """Load interaction history from file."""
        try:
            if os.path.exists(self.interaction_history_file):
                with open(self.interaction_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading interaction history: {e}")
        return {}
    
    def _save_interaction_history(self) -> None:
        """Save interaction history to file."""
        try:
            with open(self.interaction_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.interaction_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving interaction history: {e}")
    
    def get_user_id(self, session_id: str, candidate_data: Dict) -> str:
        """
        Generate a unique user ID based on session and candidate data.
        
        Args:
            session_id: Session identifier
            candidate_data: Candidate information
            
        Returns:
            Unique user ID
        """
        # Try to create ID from email if available
        if "email" in candidate_data and candidate_data["email"]:
            return hashlib.md5(candidate_data["email"].encode()).hexdigest()
        
        # Fallback to session ID
        return hashlib.md5(session_id.encode()).hexdigest()
    
    def get_user_profile(self, user_id: str) -> Dict:
        """
        Get user profile by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile dictionary
        """
        return self.user_profiles.get(user_id, {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_interaction": None,
            "preferences": {
                "communication_style": "professional",
                "response_length": "detailed",
                "technical_depth": "intermediate",
                "language": "en"
            },
            "interaction_count": 0,
            "favorite_technologies": [],
            "interview_completions": 0,
            "average_response_time": 0,
            "preferred_interview_times": [],
            "feedback_ratings": []
        })
    
    def update_user_profile(self, user_id: str, updates: Dict) -> None:
        """
        Update user profile with new information.
        
        Args:
            user_id: User identifier
            updates: Dictionary of updates to apply
        """
        profile = self.get_user_profile(user_id)
        profile.update(updates)
        profile["last_interaction"] = datetime.now().isoformat()
        
        self.user_profiles[user_id] = profile
        self._save_user_profiles()
    
    def record_interaction(self, user_id: str, interaction_data: Dict) -> None:
        """
        Record a new interaction for the user.
        
        Args:
            user_id: User identifier
            interaction_data: Interaction details
        """
        if user_id not in self.interaction_history:
            self.interaction_history[user_id] = []
        
        interaction_data["timestamp"] = datetime.now().isoformat()
        self.interaction_history[user_id].append(interaction_data)
        
        # Keep only last 50 interactions per user
        if len(self.interaction_history[user_id]) > 50:
            self.interaction_history[user_id] = self.interaction_history[user_id][-50:]
        
        self._save_interaction_history()
        
        # Update user profile
        profile = self.get_user_profile(user_id)
        profile["interaction_count"] += 1
        profile["last_interaction"] = datetime.now().isoformat()
        self.update_user_profile(user_id, profile)
    
    def get_personalized_greeting(self, user_id: str, language_code: str = "en") -> str:
        """
        Generate a personalized greeting based on user history.
        
        Args:
            user_id: User identifier
            language_code: Language code
            
        Returns:
            Personalized greeting message
        """
        profile = self.get_user_profile(user_id)
        
        # Check if returning user
        if profile["interaction_count"] > 1:
            if language_code == "en":
                return f"Welcome back! It's great to see you again. I remember you from our previous conversation. How can I assist you today?"
            elif language_code == "es":
                return f"¡Bienvenido de nuevo! Es genial verte otra vez. Te recuerdo de nuestra conversación anterior. ¿Cómo puedo ayudarte hoy?"
            elif language_code == "fr":
                return f"Bon retour ! C'est formidable de vous revoir. Je me souviens de vous de notre conversation précédente. Comment puis-je vous aider aujourd'hui ?"
            else:
                return f"Welcome back! It's great to see you again. I remember you from our previous conversation. How can I assist you today?"
        
        # First-time user
        if language_code == "en":
            return "Hello! Welcome to TalentScout. I'm here to help you with your initial screening interview. Let's get started!"
        elif language_code == "es":
            return "¡Hola! Bienvenido a TalentScout. Estoy aquí para ayudarte con tu entrevista de preselección inicial. ¡Empecemos!"
        elif language_code == "fr":
            return "Bonjour ! Bienvenue chez TalentScout. Je suis ici pour vous aider avec votre entretien de présélection initial. Commençons !"
        else:
            return "Hello! Welcome to TalentScout. I'm here to help you with your initial screening interview. Let's get started!"
    
    def get_personalized_questions(self, user_id: str, tech_stack: List[str], years_experience: int) -> List[str]:
        """
        Generate personalized technical questions based on user history.
        
        Args:
            user_id: User identifier
            tech_stack: User's technology stack
            years_experience: Years of experience
            
        Returns:
            List of personalized questions
        """
        profile = self.get_user_profile(user_id)
        history = self.interaction_history.get(user_id, [])
        
        # Analyze previous interactions to understand user's comfort level
        comfort_level = self._analyze_comfort_level(history)
        
        # Adjust question difficulty based on experience and comfort level
        if years_experience >= 5 and comfort_level == "high":
            difficulty = "advanced"
        elif years_experience >= 3 or comfort_level == "medium":
            difficulty = "intermediate"
        else:
            difficulty = "beginner"
        
        # Check if user has been asked similar questions before
        previous_questions = self._get_previous_questions(history)
        
        # Generate questions avoiding repetition
        questions = []
        for tech in tech_stack[:3]:  # Focus on top 3 technologies
            question = self._generate_tech_question(tech, difficulty, previous_questions)
            if question:
                questions.append(question)
        
        # Add general questions if needed
        if len(questions) < 3:
            general_questions = [
                "How do you approach learning new technologies?",
                "Describe a challenging project you worked on recently.",
                "What development methodologies are you most comfortable with?"
            ]
            questions.extend(general_questions[:3-len(questions)])
        
        return questions[:5]  # Return max 5 questions
    
    def _analyze_comfort_level(self, history: List[Dict]) -> str:
        """
        Analyze user's comfort level based on interaction history.
        
        Args:
            history: User's interaction history
            
        Returns:
            Comfort level: 'low', 'medium', or 'high'
        """
        if not history:
            return "medium"
        
        # Analyze response patterns
        response_times = []
        completion_rates = []
        
        for interaction in history[-10:]:  # Last 10 interactions
            if "response_time" in interaction:
                response_times.append(interaction["response_time"])
            if "completed" in interaction:
                completion_rates.append(interaction["completed"])
        
        # Calculate average response time
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            if avg_response_time < 30:  # Less than 30 seconds
                return "high"
            elif avg_response_time < 60:  # Less than 1 minute
                return "medium"
            else:
                return "low"
        
        return "medium"
    
    def _get_previous_questions(self, history: List[Dict]) -> List[str]:
        """
        Extract previously asked questions from history.
        
        Args:
            history: User's interaction history
            
        Returns:
            List of previous questions
        """
        previous_questions = []
        for interaction in history:
            if "questions_asked" in interaction:
                previous_questions.extend(interaction["questions_asked"])
        return previous_questions
    
    def _generate_tech_question(self, technology: str, difficulty: str, previous_questions: List[str]) -> Optional[str]:
        """
        Generate a technology-specific question.
        
        Args:
            technology: Technology name
            difficulty: Question difficulty level
            previous_questions: Previously asked questions
            
        Returns:
            Generated question or None
        """
        # Question templates by difficulty
        templates = {
            "beginner": [
                f"What is {technology} and what is it commonly used for?",
                f"Can you explain the basic concepts of {technology}?",
                f"How would you describe {technology} to someone new to programming?"
            ],
            "intermediate": [
                f"What are the key features and advantages of {technology}?",
                f"Can you describe a project where you used {technology}?",
                f"What challenges have you faced while working with {technology}?"
            ],
            "advanced": [
                f"What are the advanced features and best practices for {technology}?",
                f"Can you explain the architecture and design patterns in {technology}?",
                f"How would you optimize performance in a {technology} application?"
            ]
        }
        
        # Get available templates for the difficulty level
        available_templates = templates.get(difficulty, templates["intermediate"])
        
        # Find a question that hasn't been asked before
        for template in available_templates:
            if template not in previous_questions:
                return template
        
        # If all templates have been used, return a generic one
        return f"Can you share your experience with {technology}?"
    
    def update_preferences(self, user_id: str, preferences: Dict) -> None:
        """
        Update user preferences.
        
        Args:
            user_id: User identifier
            preferences: New preferences
        """
        profile = self.get_user_profile(user_id)
        profile["preferences"].update(preferences)
        self.update_user_profile(user_id, profile)
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """
        Get user statistics and analytics.
        
        Args:
            user_id: User identifier
            
        Returns:
            User statistics dictionary
        """
        profile = self.get_user_profile(user_id)
        history = self.interaction_history.get(user_id, [])
        
        # Calculate statistics
        total_interactions = len(history)
        completion_rate = 0
        avg_response_time = 0
        
        if history:
            completed_interviews = sum(1 for h in history if h.get("completed", False))
            completion_rate = (completed_interviews / total_interactions) * 100
            
            response_times = [h.get("response_time", 0) for h in history if h.get("response_time")]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "total_interactions": total_interactions,
            "completion_rate": completion_rate,
            "average_response_time": avg_response_time,
            "favorite_technologies": profile.get("favorite_technologies", []),
            "interview_completions": profile.get("interview_completions", 0),
            "last_interaction": profile.get("last_interaction"),
            "preferences": profile.get("preferences", {})
        }
    
    def record_feedback(self, user_id: str, rating: int, feedback: str = "") -> None:
        """
        Record user feedback and rating.
        
        Args:
            user_id: User identifier
            rating: Rating (1-5)
            feedback: Optional feedback text
        """
        profile = self.get_user_profile(user_id)
        
        if "feedback_ratings" not in profile:
            profile["feedback_ratings"] = []
        
        profile["feedback_ratings"].append({
            "rating": rating,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        })
        
        self.update_user_profile(user_id, profile)
    
    def get_recommendations(self, user_id: str) -> List[str]:
        """
        Get personalized recommendations for the user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of recommendations
        """
        profile = self.get_user_profile(user_id)
        stats = self.get_user_statistics(user_id)
        
        recommendations = []
        
        # Based on completion rate
        if stats["completion_rate"] < 50:
            recommendations.append("Consider completing more interviews to improve your profile visibility.")
        
        # Based on favorite technologies
        if profile.get("favorite_technologies"):
            recommendations.append(f"Focus on highlighting your expertise in {', '.join(profile['favorite_technologies'][:3])}.")
        
        # Based on interaction frequency
        if stats["total_interactions"] < 3:
            recommendations.append("Regular participation helps recruiters better understand your skills and preferences.")
        
        # Based on response time
        if stats["average_response_time"] > 120:  # More than 2 minutes
            recommendations.append("Consider preparing your responses in advance to improve interview flow.")
        
        return recommendations 