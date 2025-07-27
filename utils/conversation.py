"""Manages conversation flow for TalentScout Hiring Assistant."""
from typing import Dict, List, Any, Optional, Tuple
import uuid
import re
import time
import json

from utils.prompt_manager import PromptManager
from utils.data_handler import DataHandler
from utils.llm_router import LLMRouter
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.language_manager import LanguageManager
from utils.personalization_manager import PersonalizationManager
from utils.performance_manager import PerformanceManager
from utils.tech_questions import TechQuestionGenerator

# Import config here to avoid circular imports
import config

class ConversationManager:
    """Manages conversation flow for the TalentScout Hiring Assistant."""
    
    # Conversation stages
    STAGES = {
        "greeting": 0,
        "name": 1,
        "contact_info": 2,
        "experience": 3,
        "position": 4,
        "location": 5,
        "tech_stack": 6,
        "technical_questions": 7,
        "farewell": 8,
        "complete": 9
    }
    
    # Fields required for each stage
    REQUIRED_FIELDS = {
        "name": ["name"],
        "contact_info": ["email", "phone"],
        "experience": ["years_experience"],
        "position": ["position"],
        "location": ["location"],
        "tech_stack": ["tech_stack"],
    }
    
    # Keywords that indicate the user wants to end the conversation
    EXIT_KEYWORDS = ["exit", "quit", "end interview", "stop", "bye", "goodbye"]
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize conversation manager.
        
        Args:
            session_id: Optional session ID (generated if not provided)
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.prompt_manager = PromptManager()
        self.data_handler = DataHandler()
        self.llm_router = LLMRouter()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Initialize new managers
        self.language_manager = LanguageManager()
        self.personalization_manager = PersonalizationManager()
        self.performance_manager = PerformanceManager()
        self.tech_question_generator = TechQuestionGenerator()
        
        # Load existing session or create new one
        self.candidate_data = self.data_handler.load_candidate_data(self.session_id) or {}
        self.stage = self._determine_current_stage()
        self.history: List[Dict[str, str]] = self.candidate_data.get("conversation_history", [])
        self.technical_questions: List[str] = []
        
        # Track sentiment analysis status
        self.sentiment_analysis_enabled = self.sentiment_analyzer.is_available()
        if not self.sentiment_analysis_enabled:
            print("Sentiment analysis is not available. Using fallback mode.")
        
        # Initialize user ID and language
        self.user_id = self.personalization_manager.get_user_id(self.session_id, self.candidate_data)
        self.current_language = self.candidate_data.get("language", "en")
        
        # Preload common responses for performance
        self.performance_manager.preload_common_responses()
        
        # Load existing technical questions if available
        if "technical_questions" in self.candidate_data:
            self.technical_questions = self.candidate_data["technical_questions"]
    
    def _determine_current_stage(self) -> int:
        """Determine the current conversation stage based on collected data."""
        if not self.candidate_data:
            return self.STAGES["greeting"]
            
        # Check if conversation is already complete
        if self.candidate_data.get("conversation_complete", False):
            return self.STAGES["complete"]
            
        # Check each stage's required fields
        for stage_name, stage_index in self.STAGES.items():
            if stage_name in self.REQUIRED_FIELDS:
                required_fields = self.REQUIRED_FIELDS[stage_name]
                if not all(field in self.candidate_data for field in required_fields):
                    return stage_index
        
        # If technical questions haven't been asked yet
        if "technical_questions" not in self.candidate_data:
            return self.STAGES["technical_questions"]
            
        # If we have technical questions but not all have been answered
        if "technical_answers" not in self.candidate_data or len(self.candidate_data["technical_answers"]) < len(self.candidate_data["technical_questions"]):
            return self.STAGES["technical_questions"]
            
        # Default to farewell if everything else is complete
        return self.STAGES["farewell"]
    
    def process_message(self, user_message: str) -> str:
        """
        Process user message and return appropriate response.
        
        Args:
            user_message: Message from the user/candidate
            
        Returns:
            Response message
        """
        start_time = time.time()
        
        # Check for exit keywords
        if any(keyword in user_message.lower() for keyword in self.EXIT_KEYWORDS):
            return self._handle_exit()
        
        # Detect language if not already set
        if self.current_language == "en" and len(self.history) < 3:
            detected_language = self.language_manager.detect_language(user_message)
            if detected_language != "en":
                self.current_language = detected_language
                self.candidate_data["language"] = detected_language
                self.language_manager.update_language_preference(self.session_id, detected_language)
        
        # Update conversation history
        self._update_history("user", user_message)
        
        # Extract information from user message
        self._extract_info(user_message)
        
        # Analyze sentiment if available
        if self.sentiment_analysis_enabled:
            sentiment = self.sentiment_analyzer.get_dominant_emotion(user_message)
            if "sentiment_history" not in self.candidate_data:
                self.candidate_data["sentiment_history"] = []
            self.candidate_data["sentiment_history"].append({
                "message": user_message,
                "emotion": sentiment[0],
                "score": sentiment[1]
            })
        
        # Generate response based on current stage
        response = self._generate_response(user_message)
        
        # Update conversation history with response
        self._update_history("assistant", response)
        
        # Record interaction for personalization
        response_time = time.time() - start_time
        self.personalization_manager.record_interaction(self.user_id, {
            "message": user_message,
            "response": response,
            "response_time": response_time,
            "stage": self.stage,
            "language": self.current_language
        })
        
        # Save updated candidate data
        self._save_session()
        
        return response
    
    def _extract_info(self, message: str) -> None:
        """
        Extract candidate information from message.
        
        Args:
            message: User message to extract info from
        """
        # Extract name if in name stage
        if self.stage == self.STAGES["name"] and "name" not in self.candidate_data:
            name_match = re.search(r"my name is\s+([A-Za-z\s]+)", message, re.IGNORECASE)
            if name_match:
                self.candidate_data["name"] = name_match.group(1).strip()
            elif len(message.split()) <= 5:  # Short message likely containing just the name
                self.candidate_data["name"] = message.strip()
        
        # Extract email if in contact info stage
        if self.stage == self.STAGES["contact_info"] and "email" not in self.candidate_data:
            email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", message)
            if email_match:
                self.candidate_data["email"] = email_match.group(0)
        
        # Name validation (2-4 alphabetic names)
        if self.stage == self.STAGES["name"] and "name" not in self.candidate_data:
            name_match = re.search(r"^\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*$", message)
            if name_match:
                self.candidate_data["name"] = name_match.group(1).strip()

        # Extract phone if in contact info stage
        if self.stage == self.STAGES["contact_info"] and "phone" not in self.candidate_data:
            phone_match = re.search(r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}", message)
            if phone_match and len(phone_match.group()) >= 7:
                self.candidate_data["phone"] = phone_match.group().strip()

        # Extract years of experience
        if self.stage == self.STAGES["experience"] and "years_experience" not in self.candidate_data:
            experience_match = re.search(r"(\d+)(?:\s+years|\s+year|\s+yr|\s*\+\s*years|\s*\+)", message, re.IGNORECASE)
            if experience_match:
                try:
                    self.candidate_data["years_experience"] = int(experience_match.group(1))
                except ValueError:
                    pass
        
        # Extract position
        if self.stage == self.STAGES["position"] and "position" not in self.candidate_data:
            # This is more complex, use the full message
            # Validate position title
            position_match = re.search(r"\b(senior|junior|lead|manager|director|developer|engineer)\b", 
                message, re.IGNORECASE)
            if position_match:
                self.candidate_data["position"] = position_match.group(1).title()
            else:
                self.candidate_data["position"] = message.strip()
        
        # Extract location
        if self.stage == self.STAGES["location"] and "location" not in self.candidate_data:
            location_match = re.search(r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b", message)
            if location_match:
                self.candidate_data["location"] = location_match.group().strip()
        
        # Extract tech stack
        if self.stage == self.STAGES["tech_stack"] and "tech_stack" not in self.candidate_data:
            # Parse tech stack from free text by checking against known technologies
            tech_stack = []
            all_technologies = []
            
            # Combine all technologies from the configuration
            for category, techs in config.TECH_CATEGORIES.items():
                all_technologies.extend(techs)
            
            # Look for matches in the message
            for tech in all_technologies:
                if re.search(r"\b" + re.escape(tech) + r"\b", message, re.IGNORECASE):
                    tech_stack.append(tech)
            
            # If we found technologies, save them
            if tech_stack:
                self.candidate_data["tech_stack"] = tech_stack
    
    def _generate_response(self, user_message: str) -> str:
        """
        Generate response based on current conversation stage.
        
        Args:
            user_message: User's message
            
        Returns:
            Response message
        """
        # Check if we need to advance to the next stage
        self.stage = self._determine_current_stage()
        
        # Handle different conversation stages
        if self.stage == self.STAGES["greeting"]:
            response = self._handle_greeting()
            self.stage = self.STAGES["name"]
        
        elif self.stage == self.STAGES["name"]:
            response = self._handle_name_collection(user_message)
        
        elif self.stage == self.STAGES["contact_info"]:
            response = self._handle_contact_collection(user_message)
        
        elif self.stage == self.STAGES["experience"]:
            response = self._handle_experience_collection(user_message)
        
        elif self.stage == self.STAGES["position"]:
            response = self._handle_position_collection(user_message)
        
        elif self.stage == self.STAGES["location"]:
            response = self._handle_location_collection(user_message)
        
        elif self.stage == self.STAGES["tech_stack"]:
            response = self._handle_tech_stack_collection(user_message)
        
        elif self.stage == self.STAGES["technical_questions"]:
            response = self._handle_technical_questions(user_message)
        
        elif self.stage == self.STAGES["farewell"]:
            response = self._handle_farewell()
            self.candidate_data["conversation_complete"] = True
            self.stage = self.STAGES["complete"]
        
        else:  # Complete or unknown stage
            response = "Thank you for completing the initial interview process. The TalentScout team will be in touch if your profile matches their requirements."
        
        return response
    
    def _handle_greeting(self) -> str:
        """Handle the greeting stage."""
        # Check for cached response first
        cache_key = self.performance_manager.generate_cache_key("greeting", {
            "language": self.current_language,
            "user_id": self.user_id
        })
        
        cached_response = self.performance_manager.get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Get personalized greeting
        if self.current_language != "en":
            response = self.language_manager.get_localized_greeting(self.current_language)
        else:
            response = self.personalization_manager.get_personalized_greeting(self.user_id, self.current_language)
        
        # Cache the response
        self.performance_manager.cache_response(cache_key, response)
        
        return response
    
    def _handle_name_collection(self, user_message: str) -> str:
        """Handle the name collection stage."""
        if "name" in self.candidate_data:
            # Name already collected, move to next stage
            self.stage = self.STAGES["contact_info"]
            known_info = f"Name: {self.candidate_data['name']}"
            prompt = self.prompt_manager.get_prompt("candidate_info", 
                known_info=known_info,
                next_info="email address and phone number"
            )
        else:
            # Still need to collect name
            prompt = self.prompt_manager.get_prompt("candidate_info",
                known_info="No information collected yet.",
                next_info="name"
            )
        
        response = self.llm_router.get_response(prompt)
        return response
    
    def _handle_contact_collection(self, user_message: str) -> str:
        """Handle the contact information collection stage."""
        known_info = f"Name: {self.candidate_data.get('name', 'Not provided')}"
        
        if "email" in self.candidate_data:
            known_info += f"\nEmail: {self.candidate_data['email']}"
            
        if "phone" in self.candidate_data:
            known_info += f"\nPhone: {self.candidate_data['phone']}"
        
        # Check if both email and phone are collected
        if "email" in self.candidate_data and "phone" in self.candidate_data:
            # Move to next stage
            self.stage = self.STAGES["experience"]
            prompt = self.prompt_manager.get_prompt("candidate_info",
                known_info=known_info,
                next_info="years of experience in the industry"
            )
        else:
            # Still need one or both contact info
            missing = []
            if "email" not in self.candidate_data:
                missing.append("email address")
            if "phone" not in self.candidate_data:
                missing.append("phone number")
                
            prompt = self.prompt_manager.get_prompt("candidate_info",
                known_info=known_info,
                next_info=" and ".join(missing)
            )
        
        response = self.llm_router.get_response(prompt)
        return response
    
    def _handle_experience_collection(self, user_message: str) -> str:
        """Handle the experience collection stage."""
        known_info = f"Name: {self.candidate_data.get('name', 'Not provided')}\n"
        known_info += f"Email: {self.candidate_data.get('email', 'Not provided')}\n"
        known_info += f"Phone: {self.candidate_data.get('phone', 'Not provided')}"
        
        if "years_experience" in self.candidate_data:
            # Move to next stage
            known_info += f"\nYears of Experience: {self.candidate_data['years_experience']}"
            self.stage = self.STAGES["position"]
            prompt = self.prompt_manager.get_prompt("candidate_info",
                known_info=known_info,
                next_info="desired position or role"
            )
        else:
            # Still need experience info
            prompt = self.prompt_manager.get_prompt("candidate_info",
                known_info=known_info,
                next_info="years of experience in the industry"
            )
        
        response = self.llm_router.get_response(prompt)
        return response
    
    def _handle_position_collection(self, user_message: str) -> str:
        """Handle the position collection stage."""
        known_info = f"Name: {self.candidate_data.get('name', 'Not provided')}\n"
        known_info += f"Email: {self.candidate_data.get('email', 'Not provided')}\n"
        known_info += f"Phone: {self.candidate_data.get('phone', 'Not provided')}\n"
        known_info += f"Years of Experience: {self.candidate_data.get('years_experience', 'Not provided')}"
        
        if "position" in self.candidate_data:
            # Move to next stage
            known_info += f"\nDesired Position: {self.candidate_data['position']}"
            self.stage = self.STAGES["location"]
            prompt = self.prompt_manager.get_prompt("candidate_info",
                known_info=known_info,
                next_info="current location"
            )
        else:
            # Still need position info
            prompt = self.prompt_manager.get_prompt("candidate_info",
                known_info=known_info,
                next_info="desired position or role"
            )
        
        response = self.llm_router.get_response(prompt)
        return response
    
    def _handle_location_collection(self, user_message: str) -> str:
        """Handle the location collection stage."""
        known_info = f"Name: {self.candidate_data.get('name', 'Not provided')}\n"
        known_info += f"Email: {self.candidate_data.get('email', 'Not provided')}\n"
        known_info += f"Phone: {self.candidate_data.get('phone', 'Not provided')}\n"
        known_info += f"Years of Experience: {self.candidate_data.get('years_experience', 'Not provided')}\n"
        known_info += f"Desired Position: {self.candidate_data.get('position', 'Not provided')}"
        
        if "location" in self.candidate_data:
            # Move to next stage
            known_info += f"\nLocation: {self.candidate_data['location']}"
            self.stage = self.STAGES["tech_stack"]
            prompt = self.prompt_manager.get_prompt("tech_stack", known_info=known_info)
        else:
            # Still need location info
            prompt = self.prompt_manager.get_prompt("candidate_info",
                known_info=known_info,
                next_info="current location"
            )
        
        response = self.llm_router.get_response(prompt)
        return response
    
    def _handle_tech_stack_collection(self, user_message: str) -> str:
        """Handle the tech stack collection stage."""
        known_info = f"Name: {self.candidate_data.get('name', 'Not provided')}\n"
        known_info += f"Email: {self.candidate_data.get('email', 'Not provided')}\n"
        known_info += f"Phone: {self.candidate_data.get('phone', 'Not provided')}\n"
        known_info += f"Years of Experience: {self.candidate_data.get('years_experience', 'Not provided')}\n"
        known_info += f"Desired Position: {self.candidate_data.get('position', 'Not provided')}\n"
        known_info += f"Location: {self.candidate_data.get('location', 'Not provided')}"
        
        # First, try to extract tech stack from the message using regex patterns
        if "tech_stack" not in self.candidate_data:
            tech_stack = []
            all_technologies = []
            
            # Combine all technologies from the configuration
            for category, techs in config.TECH_CATEGORIES.items():
                all_technologies.extend(techs)
            
            # Look for matches in the message
            for tech in all_technologies:
                if re.search(r"\b" + re.escape(tech) + r"\b", user_message, re.IGNORECASE):
                    tech_stack.append(tech)
            
            # If we found technologies, save them
            if tech_stack:
                self.candidate_data["tech_stack"] = tech_stack
        
        # If still no tech stack, try LLM extraction (but only once to prevent loops)
        if "tech_stack" not in self.candidate_data and "tech_extraction_attempted" not in self.candidate_data:
            self.candidate_data["tech_extraction_attempted"] = True
            
            # Use LLM to extract tech stack
            prompt = f"""
            Based on the following message, identify the technologies, programming languages, frameworks, 
            databases, and tools mentioned. Return ONLY a comma-separated list of technologies.
            
            Message: {user_message}
            """
            tech_stack_response = self.llm_router.get_response(prompt, use_case="general")
            
            # Parse the response into a list
            techs = [tech.strip() for tech in tech_stack_response.split(',') if tech.strip()]
            if techs:
                self.candidate_data["tech_stack"] = techs
            
        # If we have tech stack, move to technical questions
        if "tech_stack" in self.candidate_data and self.candidate_data["tech_stack"]:
            # Move to technical questions
            known_info += "\nTech Stack: " + ", ".join(self.candidate_data["tech_stack"])
            self.stage = self.STAGES["technical_questions"]
            
            # Generate technical questions
            self._generate_technical_questions()
            
            # Create response with first question
            if self.technical_questions:
                response = f"Thank you for sharing your technical background. Now, I'd like to ask you a few technical questions based on your skills.\n\nHere's the first question:\n\n{self.technical_questions[0]}"
                
                # Initialize technical answers array
                self.candidate_data["technical_answers"] = []
                
                return response
        
        # If we still don't have tech stack, ask for it directly
        if "tech_stack" not in self.candidate_data:
            return "Could you please tell me what technologies, programming languages, frameworks, and tools you're proficient in? For example: Python, JavaScript, React, PostgreSQL, AWS, etc."
        
        # Fallback response
        return "Thank you for the information. Let me ask you some technical questions now."
    
    def _handle_technical_questions(self, user_message: str) -> str:
        """Handle the technical questions stage."""
        # If no technical questions generated yet, generate them
        if not self.technical_questions and "technical_questions" not in self.candidate_data:
            self._generate_technical_questions()
        
        # Use questions from data handler if available
        if not self.technical_questions and "technical_questions" in self.candidate_data:
            self.technical_questions = self.candidate_data["technical_questions"]
        
        # Initialize technical answers if needed
        if "technical_answers" not in self.candidate_data:
            self.candidate_data["technical_answers"] = []
        
        # Store the answer to the current question
        self.candidate_data["technical_answers"].append(user_message)
        
        # Check if we've asked all questions
        current_question_idx = len(self.candidate_data["technical_answers"]) - 1
        
        # If we have more questions
        if current_question_idx < len(self.technical_questions) - 1:
            next_question_idx = current_question_idx + 1
            response = f"Thank you for your answer. Here's the next question:\n\n{self.technical_questions[next_question_idx]}"
        else:
            # All questions asked, move to farewell
            self.stage = self.STAGES["farewell"]
            response = "Thank you for answering all the technical questions. Your responses have been recorded."
        
        return response
    
    def _handle_farewell(self) -> str:
        """Handle the farewell stage."""
        # Create candidate info summary for the farewell message
        candidate_info = self.data_handler.get_candidate_summary(self.session_id)
        
        # Add sentiment analysis if available
        if self.sentiment_analysis_enabled and "sentiment_history" in self.candidate_data:
            sentiment_analysis = self.sentiment_analyzer.analyze_interview_progress(self.history)
            self.candidate_data["sentiment_analysis"] = sentiment_analysis
            
            # Add sentiment info to the candidate summary for the recruiter
            if sentiment_analysis["feedback"]:
                candidate_info += f"\n\nSentiment Analysis:\n{sentiment_analysis['feedback']}"
        
        prompt = self.prompt_manager.get_prompt("farewell", candidate_info=candidate_info)
        response = self.llm_router.get_response(prompt)
        return response
    
    def _handle_exit(self) -> str:
        """Handle user request to exit the conversation."""
        self.candidate_data["conversation_complete"] = True
        self.stage = self.STAGES["complete"]
        
        # Generate farewell response
        farewell = "Thank you for your time. The interview has been concluded. The TalentScout team will review your information and will be in touch if there's a match for your profile. Have a great day!"
        
        # Save the final state
        self._save_session()
        
        return farewell
    
    def _generate_technical_questions(self) -> None:
        """Generate technical questions based on candidate's tech stack."""
        tech_stack = self.candidate_data.get("tech_stack", [])
        years_experience = self.candidate_data.get("years_experience", 0)
        
        # Check for cached questions first
        cache_key = self.performance_manager.generate_cache_key("technical_questions", {
            "tech_stack": tech_stack,
            "years_experience": years_experience,
            "user_id": self.user_id
        })
        
        cached_questions = self.performance_manager.get_cached_response(cache_key)
        if cached_questions:
            self.technical_questions = json.loads(cached_questions)
        else:
            # Use the new TechQuestionGenerator to generate questions
            self.technical_questions = self.tech_question_generator.generate_questions(
                tech_stack=tech_stack,
                years_experience=years_experience,
                num_questions=None  # Use default from config
                )
            
            # Cache the questions
            self.performance_manager.cache_response(cache_key, json.dumps(self.technical_questions))
            
        # Store the questions in candidate data
        self.candidate_data["technical_questions"] = self.technical_questions
        
        # Store questions in data handler for persistence
        self.data_handler.store_technical_questions(self.session_id, self.technical_questions)
    
    def _update_history(self, role: str, message: str) -> None:
        """
        Update conversation history.
        
        Args:
            role: Either 'user' or 'assistant'
            message: The message content
        """
        self.history.append({
            "role": role,
            "content": message
        })
        
        # Keep history within limits
        if len(self.history) > config.MAX_HISTORY_LENGTH * 2:  # * 2 for pairs of messages
            self.history = self.history[-config.MAX_HISTORY_LENGTH * 2:]
        
        # Update history in candidate data
        self.candidate_data["conversation_history"] = self.history
    
    def _save_session(self) -> None:
        """Save current session data."""
        self.data_handler.save_candidate_data(self.session_id, self.candidate_data)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.history
    
    def reset_conversation(self) -> None:
        """Reset the conversation to the beginning."""
        self.candidate_data = {}
        self.history = []
        self.stage = self.STAGES["greeting"]
        self.technical_questions = []
        self.current_language = "en"
        self._save_session()
        
        # Clear performance cache for this user
        self.performance_manager.clear_cache()

    def get_conversation_analytics(self) -> Dict[str, Any]:
        """Get analytics about the current conversation."""
        analytics = {
            "session_id": self.session_id,
            "current_stage": self.stage,
            "stage_name": [k for k, v in self.STAGES.items() if v == self.stage][0],
            "conversation_length": len(self.history),
            "language": self.current_language,
            "user_id": self.user_id,
            "completion_percentage": self._calculate_completion_percentage(),
            "collected_fields": list(self.candidate_data.keys()),
            "missing_fields": self._get_missing_fields(),
            "technical_questions_count": len(self.technical_questions),
            "technical_answers_count": len(self.candidate_data.get("technical_answers", [])),
        }
        
        # Add sentiment analysis if available
        if self.sentiment_analysis_enabled and "sentiment_history" in self.candidate_data:
            analytics["sentiment_analysis"] = {
                "total_analyses": len(self.candidate_data["sentiment_history"]),
                "recent_emotions": [entry["emotion"] for entry in self.candidate_data["sentiment_history"][-5:]]
            }
        
        return analytics
    
    def _calculate_completion_percentage(self) -> float:
        """Calculate the completion percentage of the conversation."""
        total_stages = len(self.STAGES) - 2  # Exclude 'complete' and 'farewell'
        completed_stages = 0
        
        for stage_name, stage_index in self.STAGES.items():
            if stage_name in ["complete", "farewell"]:
                continue
                
            if stage_name in self.REQUIRED_FIELDS:
                required_fields = self.REQUIRED_FIELDS[stage_name]
                if all(field in self.candidate_data for field in required_fields):
                    completed_stages += 1
            elif stage_name == "technical_questions":
                if "technical_questions" in self.candidate_data and "technical_answers" in self.candidate_data:
                    if len(self.candidate_data["technical_answers"]) >= len(self.candidate_data["technical_questions"]):
                        completed_stages += 1
        
        return (completed_stages / total_stages) * 100
    
    def _get_missing_fields(self) -> List[str]:
        """Get list of missing required fields."""
        missing_fields = []
        
        for stage_name, required_fields in self.REQUIRED_FIELDS.items():
            for field in required_fields:
                if field not in self.candidate_data:
                    missing_fields.append(field)
        
        return missing_fields
    
    def get_candidate_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the candidate's information."""
        summary = {
            "session_id": self.session_id,
            "basic_info": {
                "name": self.candidate_data.get("name", "Not provided"),
                "email": self.candidate_data.get("email", "Not provided"),
                "phone": self.candidate_data.get("phone", "Not provided"),
                "position": self.candidate_data.get("position", "Not provided"),
                "location": self.candidate_data.get("location", "Not provided"),
                "years_experience": self.candidate_data.get("years_experience", "Not provided"),
            },
            "technical_info": {
                "tech_stack": self.candidate_data.get("tech_stack", []),
                "technical_questions": self.candidate_data.get("technical_questions", []),
                "technical_answers": self.candidate_data.get("technical_answers", []),
            },
            "conversation_meta": {
                "language": self.current_language,
                "conversation_complete": self.candidate_data.get("conversation_complete", False),
                "total_messages": len(self.history),
                "completion_percentage": self._calculate_completion_percentage(),
            }
        }
        
        # Add sentiment analysis if available
        if "sentiment_analysis" in self.candidate_data:
            summary["sentiment_analysis"] = self.candidate_data["sentiment_analysis"]
        
        return summary
    
    def update_language(self, new_language: str) -> None:
        """Update the conversation language."""
        self.current_language = new_language
        self.candidate_data["language"] = new_language
        self.language_manager.update_language_preference(self.session_id, new_language)
        self._save_session()
    
    def get_next_question(self) -> Optional[str]:
        """Get the next technical question to ask."""
        if not self.technical_questions:
            return None
            
        answered_count = len(self.candidate_data.get("technical_answers", []))
        if answered_count < len(self.technical_questions):
            return self.technical_questions[answered_count]
        
        return None