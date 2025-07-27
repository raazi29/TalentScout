"""Manages conversation flow for TalentScout Hiring Assistant."""
from typing import Dict, List, Any, Optional, Tuple
import uuid
import re

from utils.prompt_manager import PromptManager
from utils.data_handler import DataHandler
from utils.llm_router import LLMRouter
from utils.sentiment_analyzer import SentimentAnalyzer  # Add import for sentiment analyzer

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
        self.sentiment_analyzer = SentimentAnalyzer()  # Initialize sentiment analyzer
        
        # Load existing session or create new one
        self.candidate_data = self.data_handler.load_candidate_data(self.session_id) or {}
        self.stage = self._determine_current_stage()
        self.history: List[Dict[str, str]] = self.candidate_data.get("conversation_history", [])
        self.technical_questions: List[str] = []
        
        # Track sentiment analysis status
        self.sentiment_analysis_enabled = self.sentiment_analyzer.is_available()
        if not self.sentiment_analysis_enabled:
            print("Sentiment analysis is not available. Using fallback mode.")
    
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
        # Check for exit keywords
        if any(keyword in user_message.lower() for keyword in self.EXIT_KEYWORDS):
            return self._handle_exit()
            
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
        
        # Extract phone if in contact info stage
        if self.stage == self.STAGES["contact_info"] and "phone" not in self.candidate_data:
            phone_match = re.search(r"\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", message)
            if phone_match:
                self.candidate_data["phone"] = phone_match.group(0)
        
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
            self.candidate_data["position"] = message.strip()
        
        # Extract location
        if self.stage == self.STAGES["location"] and "location" not in self.candidate_data:
            self.candidate_data["location"] = message.strip()
        
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
        prompt = self.prompt_manager.get_prompt("greeting")
        response = self.llm_router.get_response(prompt)
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
        
        # If no tech stack is extracted, try to extract using LLM
        if "tech_stack" not in self.candidate_data:
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
        
        # Still need tech stack info or additional clarification
        prompt = self.prompt_manager.get_prompt("tech_stack", known_info=known_info)
        response = self.llm_router.get_response(prompt)
        return response
    
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
        
        if not tech_stack:
            # No tech stack provided, generate general questions
            self.technical_questions = [
                "Can you describe your experience with programming languages?",
                "What development methodologies are you familiar with?",
                "How do you approach debugging complex issues?",
                "Describe a challenging technical project you worked on.",
                "How do you stay updated with industry trends and new technologies?"
            ]
        else:
            # Generate tech-specific questions
            self.technical_questions = self.llm_router.generate_technical_questions(
                tech_stack, years_experience
            )
            
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
        self._save_session()

# Import config here to avoid circular imports
import config 