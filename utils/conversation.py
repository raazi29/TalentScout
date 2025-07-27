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
            logger.info("Sentiment analysis is not available. Using fallback mode.")
        
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
        
        # Enhanced language detection and switching
        language_switch_message = ""
        new_language, switched, switch_message = self.language_manager.auto_switch_language(
            user_message, self.current_language, self.session_id
        )
        
        if switched:
            # Language was automatically switched
            self.current_language = new_language
            self.candidate_data["language"] = new_language
            language_switch_message = switch_message
            
            # Preserve conversation context across language switch
            self.history = self.llm_router.preserve_context_across_languages(
                self.history, new_language
            )
        elif switch_message:
            # Language switch suggestion (medium confidence)
            # Store the suggestion for potential confirmation
            self.candidate_data["language_suggestion"] = {
                "suggested_language": new_language,
                "message": switch_message,
                "timestamp": time.time()
            }
        
        # Update conversation history
        self._update_history("user", user_message)
        
        # Extract information from user message with language context
        self._extract_multilingual_info(user_message)
        
        # Analyze sentiment if available
        if self.sentiment_analysis_enabled:
            sentiment = self.sentiment_analyzer.get_dominant_emotion(user_message)
            if "sentiment_history" not in self.candidate_data:
                self.candidate_data["sentiment_history"] = []
            self.candidate_data["sentiment_history"].append({
                "message": user_message,
                "emotion": sentiment[0],
                "score": sentiment[1],
                "language": self.current_language
            })
        
        # Generate response based on current stage
        response = self._generate_response(user_message)
        
        # Add language switch message if needed
        if language_switch_message:
            response = f"{language_switch_message}\n\n{response}"
        
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
        Extract candidate information from message (legacy method for backward compatibility).
        
        Args:
            message: User message to extract info from
        """
        # Use the enhanced multilingual extraction method
        self._extract_multilingual_info(message)
    
    def _extract_multilingual_info(self, message: str) -> None:
        """
        Enhanced information extraction with better pattern matching and validation.
        
        Args:
            message: User message to extract info from
        """
        # Extract name with improved patterns
        if self.stage == self.STAGES["name"] and "name" not in self.candidate_data:
            extracted_name = self._extract_name(message)
            if extracted_name:
                self.candidate_data["name"] = extracted_name
        
        # Extract email with validation
        if self.stage == self.STAGES["contact_info"] and "email" not in self.candidate_data:
            extracted_email = self._extract_email(message)
            if extracted_email:
                self.candidate_data["email"] = extracted_email
        
        # Extract phone with international format support
        if self.stage == self.STAGES["contact_info"] and "phone" not in self.candidate_data:
            extracted_phone = self._extract_phone(message)
            if extracted_phone:
                self.candidate_data["phone"] = extracted_phone
        
        # Extract years of experience with better parsing
        if self.stage == self.STAGES["experience"] and "years_experience" not in self.candidate_data:
            extracted_experience = self._extract_experience(message)
            if extracted_experience is not None:
                self.candidate_data["years_experience"] = extracted_experience
        
        # Extract position with better matching
        if self.stage == self.STAGES["position"] and "position" not in self.candidate_data:
            extracted_position = self._extract_position(message)
            if extracted_position:
                self.candidate_data["position"] = extracted_position
        
        # Extract location with better parsing
        if self.stage == self.STAGES["location"] and "location" not in self.candidate_data:
            extracted_location = self._extract_location(message)
            if extracted_location:
                self.candidate_data["location"] = extracted_location
        
        # Extract tech stack with comprehensive matching
        if self.stage == self.STAGES["tech_stack"] and "tech_stack" not in self.candidate_data:
            extracted_tech_stack = self._extract_tech_stack(message)
            if extracted_tech_stack:
                self.candidate_data["tech_stack"] = extracted_tech_stack
    
    def _extract_name(self, message: str) -> Optional[str]:
        """Extract name from message with improved patterns."""
        # Language-specific patterns
        name_patterns = {
            "en": [
                r"my name is\s+([A-Za-z\s\-'\.]+)",
                r"i am\s+([A-Za-z\s\-'\.]+)",
                r"i'm\s+([A-Za-z\s\-'\.]+)",
                r"call me\s+([A-Za-z\s\-'\.]+)"
            ],
            "es": [
                r"mi nombre es\s+([A-Za-z\s\-'\.]+)",
                r"me llamo\s+([A-Za-z\s\-'\.]+)",
                r"soy\s+([A-Za-z\s\-'\.]+)"
            ],
            "fr": [
                r"je m'appelle\s+([A-Za-z\s\-'\.]+)",
                r"mon nom est\s+([A-Za-z\s\-'\.]+)",
                r"je suis\s+([A-Za-z\s\-'\.]+)"
            ]
        }
        
        patterns = name_patterns.get(self.current_language, name_patterns["en"])
        
        # Try pattern matching first
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if self._validate_name(name):
                    return name
        
        # Fallback: if message is short and looks like a name
        if len(message.split()) <= 4:
            clean_name = re.sub(r'[^\w\s\-\']', '', message).strip()
            if self._validate_name(clean_name):
                return clean_name
        
        return None
    
    def _extract_email(self, message: str) -> Optional[str]:
        """Extract email with comprehensive validation."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, message)
        
        if match:
            email = match.group(0)
            # Additional validation
            if self._validate_email(email):
                return email
        
        return None
    
    def _extract_phone(self, message: str) -> Optional[str]:
        """Extract phone number with international format support."""
        # Comprehensive phone patterns
        phone_patterns = [
            r'\+\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',  # US format (555) 123-4567
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # US format 555-123-4567
            r'\d{10,15}'  # Simple digit sequence
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, message)
            if match:
                phone = match.group(0)
                if self._validate_phone(phone):
                    return phone
        
        return None
    
    def _extract_experience(self, message: str) -> Optional[int]:
        """Extract years of experience with better parsing."""
        # Multiple patterns for experience
        experience_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
            r'(\d+(?:\.\d+)?)\s*(?:year|yr)\s*(?:experience|exp)',
            r'experience.*?(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
            r'(\d+(?:\.\d+)?)\s*(?:años?|ans?)',  # Spanish/French
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    years = float(match.group(1))
                    if 0 <= years <= 50:  # Reasonable range
                        return int(years) if years == int(years) else years
                except ValueError:
                    continue
        
        return None
    
    def _extract_position(self, message: str) -> Optional[str]:
        """Extract position with better matching."""
        # Common tech positions
        tech_positions = [
            'software engineer', 'software developer', 'web developer', 'frontend developer',
            'backend developer', 'full stack developer', 'mobile developer', 'data scientist',
            'data analyst', 'data engineer', 'machine learning engineer', 'ai engineer',
            'devops engineer', 'cloud engineer', 'security engineer', 'qa engineer',
            'test engineer', 'product manager', 'technical lead', 'team lead',
            'senior developer', 'junior developer', 'principal engineer', 'architect',
            'ui/ux designer', 'designer', 'scrum master', 'project manager'
        ]
        
        message_lower = message.lower()
        
        # Look for exact matches first
        for position in tech_positions:
            if position in message_lower:
                return position.title()
        
        # Look for partial matches with common prefixes/suffixes
        position_keywords = ['developer', 'engineer', 'analyst', 'scientist', 'manager', 'lead', 'architect']
        for keyword in position_keywords:
            if keyword in message_lower:
                # Extract surrounding context
                pattern = rf'\b\w*\s*{keyword}\b'
                match = re.search(pattern, message_lower)
                if match:
                    return match.group(0).strip().title()
        
        # Fallback: use the whole message if it's short and reasonable
        if len(message.split()) <= 5 and len(message.strip()) > 2:
            return message.strip().title()
        
        return None
    
    def _extract_location(self, message: str) -> Optional[str]:
        """Extract location with enhanced support for Indian states and cities."""
        # Clean the message
        clean_message = message.strip()
        
        # Indian states and major cities for better recognition
        indian_states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 
            'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 
            'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 
            'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 
            'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Delhi', 'Jammu and Kashmir', 
            'Ladakh', 'Puducherry', 'Chandigarh', 'Dadra and Nagar Haveli', 'Daman and Diu',
            'Lakshadweep', 'Andaman and Nicobar Islands'
        ]
        
        indian_cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Bengaluru', 'Hyderabad', 'Chennai', 'Kolkata', 
            'Pune', 'Ahmedabad', 'Surat', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 
            'Thane', 'Bhopal', 'Visakhapatnam', 'Pimpri-Chinchwad', 'Patna', 'Vadodara', 
            'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik', 'Faridabad', 'Meerut', 'Rajkot', 
            'Kalyan-Dombivali', 'Vasai-Virar', 'Varanasi', 'Srinagar', 'Aurangabad', 
            'Dhanbad', 'Amritsar', 'Navi Mumbai', 'Allahabad', 'Prayagraj', 'Ranchi', 
            'Howrah', 'Coimbatore', 'Jabalpur', 'Gwalior', 'Vijayawada', 'Jodhpur', 
            'Madurai', 'Raipur', 'Kota', 'Chandigarh', 'Guwahati', 'Solapur', 'Hubli-Dharwad',
            'Bareilly', 'Moradabad', 'Mysore', 'Mysuru', 'Gurgaon', 'Gurugram', 'Aligarh', 
            'Jalandhar', 'Tiruchirappalli', 'Bhubaneswar', 'Salem', 'Warangal', 'Guntur', 
            'Bhiwandi', 'Saharanpur', 'Gorakhpur', 'Bikaner', 'Amravati', 'Noida', 'Jamshedpur',
            'Bhilai', 'Cuttack', 'Firozabad', 'Kochi', 'Ernakulam', 'Bhavnagar', 'Dehradun',
            'Durgapur', 'Asansol', 'Rourkela', 'Nanded', 'Kolhapur', 'Ajmer', 'Akola',
            'Gulbarga', 'Jamnagar', 'Ujjain', 'Loni', 'Siliguri', 'Jhansi', 'Ulhasnagar',
            'Nellore', 'Jammu', 'Sangli-Miraj & Kupwad', 'Belgaum', 'Mangalore', 'Ambattur',
            'Tirunelveli', 'Malegaon', 'Gaya', 'Jalgaon', 'Udaipur', 'Maheshtala'
        ]
        
        # Check for Indian locations first
        message_lower = clean_message.lower()
        
        # Check for Indian states
        for state in indian_states:
            if state.lower() in message_lower:
                # Look for city, state pattern
                city_state_pattern = rf'([A-Za-z\s]+),\s*{re.escape(state)}'
                match = re.search(city_state_pattern, clean_message, re.IGNORECASE)
                if match:
                    return f"{match.group(1).strip()}, {state}, India"
                else:
                    return f"{state}, India"
        
        # Check for Indian cities
        for city in indian_cities:
            if city.lower() in message_lower:
                # Try to find state context
                for state in indian_states:
                    if state.lower() in message_lower:
                        return f"{city}, {state}, India"
                # If no state found, just return city with India
                return f"{city}, India"
        
        # Check for "India" keyword
        if 'india' in message_lower or 'indian' in message_lower:
            # Extract city/state before India
            india_pattern = r'([A-Za-z\s]+)(?:,\s*)?(?:india|indian)'
            match = re.search(india_pattern, clean_message, re.IGNORECASE)
            if match:
                location_part = match.group(1).strip().rstrip(',')
                return f"{location_part}, India"
        
        # General location patterns
        location_patterns = [
            r'([A-Za-z\s]+),\s*([A-Za-z\s]+)(?:,\s*([A-Za-z\s]+))?',  # City, State, Country
            r'([A-Za-z\s]{2,})'  # Simple location name
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, clean_message)
            if match:
                location = match.group(0).strip()
                if self._validate_location(location):
                    return location
        
        return None
    
    def _extract_tech_stack(self, message: str) -> Optional[List[str]]:
        """Extract tech stack with comprehensive matching."""
        # Get all known technologies from config
        all_technologies = []
        for category, techs in config.TECH_CATEGORIES.items():
            all_technologies.extend(techs)
        
        # Additional common technologies not in config
        additional_techs = [
            'HTML', 'CSS', 'SASS', 'SCSS', 'TypeScript', 'GraphQL', 'REST API',
            'Microservices', 'Agile', 'Scrum', 'TDD', 'CI/CD', 'DevOps',
            'Machine Learning', 'Deep Learning', 'AI', 'Blockchain'
        ]
        all_technologies.extend(additional_techs)
        
        found_technologies = []
        message_lower = message.lower()
        
        # Look for exact matches (case-insensitive)
        for tech in all_technologies:
            if re.search(rf'\b{re.escape(tech.lower())}\b', message_lower):
                found_technologies.append(tech)
        
        # Look for common variations and abbreviations
        tech_variations = {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'py': 'Python',
            'react.js': 'React',
            'vue.js': 'Vue.js',
            'node.js': 'Node.js',
            'express.js': 'Express.js'
        }
        
        for variation, full_name in tech_variations.items():
            if re.search(rf'\b{re.escape(variation)}\b', message_lower):
                if full_name not in found_technologies:
                    found_technologies.append(full_name)
        
        return found_technologies if found_technologies else None
    
    def _validate_name(self, name: str) -> bool:
        """Validate name format."""
        if not name or len(name.strip()) < 2:
            return False
        
        # Check for reasonable name pattern
        name_pattern = r'^[A-Za-z\s\-\'\.]{2,50}$'
        if not re.match(name_pattern, name):
            return False
        
        # Should have 1-4 words
        words = name.split()
        return 1 <= len(words) <= 4
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        if not email or len(email) > 254:
            return False
        
        # More comprehensive email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number."""
        if not phone:
            return False
        
        # Remove all non-digit characters for length check
        digits_only = re.sub(r'\D', '', phone)
        return 7 <= len(digits_only) <= 15
    
    def _validate_location(self, location: str) -> bool:
        """Validate location format with enhanced support for Indian locations."""
        if not location or len(location.strip()) < 2:
            return False
        
        # Should be reasonable length and contain letters
        if len(location) > 100 or not re.search(r'[A-Za-z]', location):
            return False
        
        # Additional validation for common location patterns
        location_lower = location.lower()
        
        # Valid if contains common location indicators
        location_indicators = [
            'city', 'state', 'country', 'india', 'usa', 'uk', 'canada', 'australia',
            'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata', 'pune',
            'new york', 'london', 'toronto', 'sydney', 'singapore', 'dubai'
        ]
        
        # Check for valid location patterns
        has_location_indicator = any(indicator in location_lower for indicator in location_indicators)
        has_comma_separation = ',' in location  # City, State or City, Country format
        is_reasonable_length = 2 <= len(location.split()) <= 6  # Reasonable word count
        
        return has_location_indicator or has_comma_separation or is_reasonable_length
        
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
        Generate response based on current conversation stage with multilingual support.
        
        Args:
            user_message: User's message
            
        Returns:
            Response message in the appropriate language
        """
        # Check if we need to advance to the next stage
        self.stage = self._determine_current_stage()
        
        # Handle different conversation stages
        try:
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
                response = self._get_completion_message()
            
            return response
            
        except Exception as e:
            # Handle errors gracefully with multilingual error messages
            return self._handle_language_error(e)
    
    def _get_completion_message(self) -> str:
        """Get completion message in the appropriate language."""
        completion_messages = {
            "en": "Thank you for completing the initial interview process. The TalentScout team will be in touch if your profile matches their requirements.",
            "es": "Gracias por completar el proceso de entrevista inicial. El equipo de TalentScout se pondrá en contacto si su perfil coincide con nuestros requisitos.",
            "fr": "Merci d'avoir terminé le processus d'entretien initial. L'équipe TalentScout vous contactera si votre profil correspond à nos exigences.",
            "de": "Vielen Dank für die Teilnahme am ersten Vorstellungsgespräch. Das TalentScout-Team wird sich melden, wenn Ihr Profil unseren Anforderungen entspricht.",
            "it": "Grazie per aver completato il processo di colloquio iniziale. Il team TalentScout ti contatterà se il tuo profilo corrisponde ai nostri requisiti.",
            "pt": "Obrigado por completar o processo de entrevista inicial. A equipe TalentScout entrará em contato se seu perfil corresponder aos nossos requisitos.",
            "hi": "प्रारंभिक साक्षात्कार प्रक्रिया पूरी करने के लिए धन्यवाद। यदि आपकी प्रोफ़ाइल हमारी आवश्यकताओं से मेल खाती है तो TalentScout टीम संपर्क करेगी।"
        }
        
        return completion_messages.get(self.current_language, completion_messages["en"])
    
    def _handle_greeting(self) -> str:
        """Handle the greeting stage with cultural adaptation."""
        # Check for cached response first
        cache_key = self.performance_manager.generate_cache_key("greeting", {
            "language": self.current_language,
            "user_id": self.user_id
        })
        
        cached_response = self.performance_manager.get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Get base localized greeting
        base_greeting = self.language_manager.get_localized_greeting(self.current_language)
        
        # Adapt greeting for cultural context
        culturally_adapted_greeting = self.language_manager.adapt_greeting_for_culture(
            self.current_language, base_greeting
        )
        
        # Cache the response
        self.performance_manager.cache_response(cache_key, culturally_adapted_greeting)
        
        return culturally_adapted_greeting
    
    def _handle_name_collection(self, user_message: str) -> str:
        """Handle the name collection stage with enhanced prompts."""
        if "name" in self.candidate_data:
            # Name collected successfully, transition to next stage
            self.stage = self.STAGES["contact_info"]
            
            # Use transition prompt for smooth flow
            transition_prompt = self.prompt_manager.get_prompt("transition",
                completed_stage="name collection",
                next_stage="contact information",
                collected_info=f"Name: {self.candidate_data['name']}"
            )
            
            # Then ask for contact info
            info_prompt = self.prompt_manager.get_prompt("candidate_info",
                known_info=f"Name: {self.candidate_data['name']}",
                next_info="email address and phone number"
            )
            
            combined_prompt = f"{transition_prompt}\n\n{info_prompt}"
            
        else:
            # Still need to collect name - check if validation is needed
            if user_message and len(user_message.strip()) > 0:
                # User provided something, but extraction failed - use validation prompt
                validation_prompt = self.prompt_manager.get_prompt("validation",
                    field_name="name",
                    provided_value=user_message,
                    validation_error="Name format is invalid",
                    expected_format="2-4 alphabetic words with proper capitalization (e.g., 'John Smith')"
                )
                combined_prompt = validation_prompt
            else:
                # Initial request for name
                combined_prompt = self.prompt_manager.get_prompt("candidate_info",
                    known_info="Starting interview process.",
                    next_info="full name"
                )
        
        # Use enhanced LLM routing
        context = {"conversation_history": self.history}
        response = self.llm_router.get_multilingual_response(
            combined_prompt, self.current_language, context, "name"
        )
        return response
    
    def _handle_contact_collection(self, user_message: str) -> str:
        """Handle the contact information collection stage with multilingual support."""
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
        
        # Use multilingual LLM routing
        context = {"conversation_history": self.history}
        response = self.llm_router.get_multilingual_response(
            prompt, self.current_language, context, "contact_info"
        )
        return response
    
    def _handle_experience_collection(self, user_message: str) -> str:
        """Handle the experience collection stage with multilingual support."""
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
        
        # Use multilingual LLM routing
        context = {"conversation_history": self.history}
        response = self.llm_router.get_multilingual_response(
            prompt, self.current_language, context, "experience"
        )
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
        """Handle the tech stack collection stage with enhanced extraction."""
        # Build comprehensive candidate context
        known_info = self._build_candidate_context()
        
        # Use enhanced tech stack extraction
        if "tech_stack" not in self.candidate_data:
            extracted_tech_stack = self._extract_tech_stack(user_message)
            if extracted_tech_stack:
                self.candidate_data["tech_stack"] = extracted_tech_stack
        
        # If we have tech stack, transition to technical questions
        if "tech_stack" in self.candidate_data and self.candidate_data["tech_stack"]:
            # Update known info with tech stack
            known_info += f"\nTech Stack: {', '.join(self.candidate_data['tech_stack'])}"
            
            # Use transition prompt
            transition_prompt = self.prompt_manager.get_prompt("transition",
                completed_stage="technical skills collection",
                next_stage="technical assessment",
                collected_info=f"Tech Stack: {', '.join(self.candidate_data['tech_stack'])}"
            )
            
            # Move to technical questions stage
            self.stage = self.STAGES["technical_questions"]
            
            # Generate technical questions using enhanced method
            self._generate_technical_questions()
            
            # Create comprehensive response
            if self.technical_questions:
                tech_summary = self._create_tech_stack_summary()
                first_question = self.technical_questions[0]
                
                response = f"{transition_prompt}\n\n{tech_summary}\n\nLet's start with the first technical question:\n\n{first_question}"
                
                # Initialize technical answers
                self.candidate_data["technical_answers"] = []
                
                return response
        
        # If no tech stack extracted, use enhanced prompting
        if "tech_stack" not in self.candidate_data:
            if user_message and len(user_message.strip()) > 0:
                # User provided something but extraction failed
                prompt = self.prompt_manager.get_prompt("tech_stack", known_info=known_info)
                fallback_prompt = f"""
                I couldn't identify specific technologies from your response. {prompt}
                
                Please list your technical skills more specifically. For example:
                - Programming Languages: Python, JavaScript, Java
                - Frameworks: React, Django, Spring
                - Databases: PostgreSQL, MongoDB
                - Cloud: AWS, Azure
                - Tools: Git, Docker, Jenkins
                """
                
                context = {"conversation_history": self.history}
                return self.llm_router.get_multilingual_response(
                    fallback_prompt, self.current_language, context, "tech_stack"
                )
            else:
                # Initial tech stack request
                prompt = self.prompt_manager.get_prompt("tech_stack", known_info=known_info)
                context = {"conversation_history": self.history}
                return self.llm_router.get_multilingual_response(
                    prompt, self.current_language, context, "tech_stack"
                )
        
        # Fallback response
        return "Thank you for the information. Let me ask you some technical questions now."
    
    def _build_candidate_context(self) -> str:
        """Build comprehensive candidate context string."""
        context_parts = []
        
        if "name" in self.candidate_data:
            context_parts.append(f"Name: {self.candidate_data['name']}")
        if "email" in self.candidate_data:
            context_parts.append(f"Email: {self.candidate_data['email']}")
        if "phone" in self.candidate_data:
            context_parts.append(f"Phone: {self.candidate_data['phone']}")
        if "years_experience" in self.candidate_data:
            context_parts.append(f"Experience: {self.candidate_data['years_experience']} years")
        if "position" in self.candidate_data:
            context_parts.append(f"Desired Position: {self.candidate_data['position']}")
        if "location" in self.candidate_data:
            context_parts.append(f"Location: {self.candidate_data['location']}")
        
        return "\n".join(context_parts) if context_parts else "No information collected yet."
    
    def _create_tech_stack_summary(self) -> str:
        """Create a summary of the candidate's tech stack."""
        if "tech_stack" not in self.candidate_data:
            return ""
        
        tech_stack = self.candidate_data["tech_stack"]
        
        # Categorize technologies
        categories = {
            "Programming Languages": [],
            "Frameworks": [],
            "Databases": [],
            "Cloud/DevOps": [],
            "Tools": []
        }
        
        # Simple categorization based on known technologies
        for tech in tech_stack:
            tech_lower = tech.lower()
            if any(lang in tech_lower for lang in ['python', 'javascript', 'java', 'c#', 'go', 'ruby', 'php']):
                categories["Programming Languages"].append(tech)
            elif any(fw in tech_lower for fw in ['react', 'angular', 'vue', 'django', 'flask', 'spring']):
                categories["Frameworks"].append(tech)
            elif any(db in tech_lower for db in ['mysql', 'postgresql', 'mongodb', 'redis', 'oracle']):
                categories["Databases"].append(tech)
            elif any(cloud in tech_lower for cloud in ['aws', 'azure', 'gcp', 'docker', 'kubernetes']):
                categories["Cloud/DevOps"].append(tech)
            else:
                categories["Tools"].append(tech)
        
        # Build summary
        summary_parts = []
        for category, techs in categories.items():
            if techs:
                summary_parts.append(f"{category}: {', '.join(techs)}")
        
        if summary_parts:
            return f"Great! I've identified your technical skills:\n" + "\n".join(f"• {part}" for part in summary_parts)
        else:
            return f"I've noted your technical skills: {', '.join(tech_stack)}"
    
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
    
    def switch_conversation_language(self, new_language: str) -> bool:
        """
        Switch the conversation language and update context.
        
        Args:
            new_language: New language code to switch to
            
        Returns:
            True if switch was successful, False otherwise
        """
        try:
            # Validate language is supported
            if new_language not in self.language_manager.SUPPORTED_LANGUAGES:
                return False
            
            # Update language
            old_language = self.current_language
            self.current_language = new_language
            self.candidate_data["language"] = new_language
            
            # Update language preference
            self.language_manager.update_language_preference(self.session_id, new_language)
            
            # Preserve conversation context across language switch
            self.history = self.llm_router.preserve_context_across_languages(
                self.history, new_language
            )
            
            # Update conversation history in candidate data
            self.candidate_data["conversation_history"] = self.history
            
            # Log language switch
            if "language_switches" not in self.candidate_data:
                self.candidate_data["language_switches"] = []
            
            self.candidate_data["language_switches"].append({
                "from_language": old_language,
                "to_language": new_language,
                "timestamp": time.time(),
                "stage": self.stage
            })
            
            # Save updated data
            self._save_session()
            
            return True
            
        except Exception as e:
            # Log error and revert language
            logger.error(f"Error switching language: {e}")
            self.current_language = old_language if 'old_language' in locals() else "en"
            return False
    
    def _handle_language_error(self, error: Exception, fallback_language: str = "en") -> str:
        """
        Handle language-related errors gracefully.
        
        Args:
            error: The exception that occurred
            fallback_language: Language to fall back to
            
        Returns:
            Error response in appropriate language
        """
        try:
            # Try to get error response using LLM router's error handling
            return self.llm_router.handle_translation_failure(
                "I apologize for the technical difficulty. Let me try to help you.",
                error,
                fallback_language
            )
        except Exception as fallback_error:
            # Ultimate fallback - hardcoded error messages
            error_messages = {
                "en": "I apologize for the technical difficulty. Please try again or continue in English.",
                "es": "Me disculpo por la dificultad técnica. Por favor, inténtelo de nuevo o continúe en inglés.",
                "fr": "Je m'excuse pour la difficulté technique. Veuillez réessayer ou continuer en anglais.",
                "de": "Entschuldigung für die technischen Schwierigkeiten. Bitte versuchen Sie es erneut oder setzen Sie auf Englisch fort.",
                "it": "Mi scuso per la difficoltà tecnica. Per favore riprova o continua in inglese.",
                "pt": "Peço desculpas pela dificuldade técnica. Tente novamente ou continue em inglês.",
                "hi": "तकनीकी कठिनाई के लिए मुझे खेद है। कृपया पुनः प्रयास करें या अंग्रेजी में जारी रखें।"
            }
            
            return error_messages.get(self.current_language, error_messages["en"])
    
    def process_multilingual_message(self, message: str, detected_language: str) -> str:
        """
        Process a message with explicit language detection result.
        
        Args:
            message: User message
            detected_language: Pre-detected language code
            
        Returns:
            Response message
        """
        # Update language if different from current
        if detected_language != self.current_language:
            self.switch_conversation_language(detected_language)
        
        # Process message normally
        return self.process_message(message)
    
    def validate_language_specific_data(self, data: Dict, language: str) -> bool:
        """
        Validate data based on language-specific cultural norms.
        
        Args:
            data: Data dictionary to validate
            language: Language code for cultural context
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Validate name format
            if "name" in data:
                is_valid, _ = self.language_manager.validate_cultural_data_format(
                    "name", data["name"], language
                )
                if not is_valid:
                    return False
            
            # Validate phone format
            if "phone" in data:
                is_valid, _ = self.language_manager.validate_cultural_data_format(
                    "phone", data["phone"], language
                )
                if not is_valid:
                    return False
            
            return True
            
        except Exception:
            return False