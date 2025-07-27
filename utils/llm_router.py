"""LLM Router to handle multiple API providers and model selection."""
import time
import logging
from typing import Dict, List, Any, Optional

import groq
import openai
import requests
from requests.exceptions import RequestException

import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMRouter:
    """Routes LLM requests to Groq (primary) and OpenRouter (fallback, best 2025 models)."""
    def __init__(self):
        """Initialize the LLM router with Groq client and OpenRouter fallback."""
        self.groq_client = groq.Groq(api_key=config.GROQ_API_KEY) if config.GROQ_API_KEY else None
        # OpenRouter fallback client (only initialized if API key is present)
        self.openrouter_client = None
        if config.OPENROUTER_API_KEY:
            try:
                import openai
                self.openrouter_client = openai.OpenAI(
                    api_key=config.OPENROUTER_API_KEY,
                    base_url="https://openrouter.ai/api/v1"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize OpenRouter client: {e}")
                self.openrouter_client = None
        if not self.groq_client and not self.openrouter_client:
            logger.warning("No API keys provided. LLM functionality will be limited.")

    def _call_groq(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> Optional[str]:
        """Call the Groq API and return the response using the best free model."""
        if not self.groq_client:
            logger.warning("Groq API key not provided.")
            return None
        try:
            response = self.groq_client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return None

    def _call_openrouter_fallback(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> Optional[str]:
        """Try each OpenRouter 2025 model in order until one succeeds."""
        if not self.openrouter_client:
            logger.warning("OpenRouter API key not provided or client not initialized.")
            return None
        for model in config.OPENROUTER_MODELS_2025:
            try:
                response = self.openrouter_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=2.0
                )
                if response.choices and response.choices[0].message.content:
                    logger.info(f"OpenRouter fallback succeeded with model: {model}")
                    return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenRouter model {model} failed: {e}")
                continue
        logger.error("All OpenRouter fallback models failed.")
        return None

    def get_response(self, prompt: str, use_case: str = "general", temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Get a response from Groq LLM (llama3-8b-8192). If unavailable, fallback to OpenRouter best 2025 models. If all fail, return a user-friendly fallback.
        """
        response = self._call_groq(prompt, temperature, max_tokens)
        if response:
            return response
        # Fallback to OpenRouter best 2025 models
        response = self._call_openrouter_fallback(prompt, temperature, max_tokens)
        if response:
            return response
        return self._get_fallback_response(use_case)

    def _get_fallback_response(self, use_case: str) -> str:
        """Get a fallback response when all APIs fail."""
        fallback_responses = {
            "greeting": "Hello! I'm here to help you with your application. Could you please tell me your name?",
            "name": "Thank you for sharing your name. Could you please provide your email address and phone number?",
            "contact_info": "Great! Now could you tell me how many years of experience you have in the industry?",
            "experience": "Thank you. What type of position are you looking for?",
            "position": "Could you tell me your current location?",
            "location": "What technologies and programming languages are you proficient in?",
            "tech_stack": "Thank you for sharing your technical background. I'll now ask you some technical questions.",
            "technical_questions": "Thank you for your answer. Here's the next question.",
            "farewell": "Thank you for completing the interview. We'll review your responses and get back to you soon.",
            "general": "I apologize, but I'm having trouble connecting to my knowledge base. Could you please try again in a moment?"
        }

        return fallback_responses.get(use_case, fallback_responses["general"])

    def generate_technical_questions(self, tech_stack: List[str], experience_years: int) -> List[str]:
        """
        Generate technical questions based on candidate's tech stack.

        Args:
            tech_stack: List of technologies the candidate is proficient in
            experience_years: Years of experience (to adjust difficulty)

        Returns:
            List of technical questions
        """
        difficulty = "entry-level" if experience_years < 2 else "intermediate" if experience_years < 5 else "advanced"

        prompt = f"""
        Generate {config.MIN_TECHNICAL_QUESTIONS}-{config.MAX_TECHNICAL_QUESTIONS} technical interview questions for a candidate with {experience_years} years of experience.
        Focus on the following technologies: {', '.join(tech_stack)}.
        The questions should be {difficulty} difficulty and test practical knowledge.
        Each question should be specific to one technology and require more than a yes/no answer.
        Format the output as a JSON array of strings containing only the questions.
        Example output format: ["Question 1?", "Question 2?", "Question 3?"]
        """

        # Use higher temperature for more diverse questions
        response = self.get_response(prompt, use_case="tech_questions", temperature=0.8, max_tokens=1000)

        try:
            # Try to extract JSON array from response
            import json
            import re

            # Find anything that looks like a JSON array in the response
            json_match = re.search(r'\[\s*".*"\s*(,\s*".*"\s*)*\]', response, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group(0))
                # Ensure we have at least MIN_TECHNICAL_QUESTIONS
                if len(questions) >= config.MIN_TECHNICAL_QUESTIONS:
                    return questions[:config.MAX_TECHNICAL_QUESTIONS]  # Limit to max questions

            # Fallback: Try to extract questions line by line if JSON parsing fails
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            questions = []
            for line in lines:
                # Remove numbering and other formatting
                clean_line = re.sub(r'^[0-9]+[\.\)]\s*', '', line)
                if '?' in clean_line:
                    questions.append(clean_line)

            if len(questions) >= config.MIN_TECHNICAL_QUESTIONS:
                return questions[:config.MAX_TECHNICAL_QUESTIONS]

            # If we still don't have enough questions, return generic ones
            return [
                f"Please explain your experience with {tech}?" for tech in tech_stack[:config.MIN_TECHNICAL_QUESTIONS]
            ]
        except Exception as e:
            logger.error(f"Error parsing technical questions: {e}")
            return [
                f"Could you describe your experience with {tech}?" for tech in tech_stack[:config.MIN_TECHNICAL_QUESTIONS]
            ]
    
    def get_multilingual_response(self, prompt: str, language: str, context: Dict = None, use_case: str = "general", temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Get a response from LLM with language-specific handling.
        
        Args:
            prompt: The prompt to send to the LLM
            language: Target language code (e.g., 'es', 'fr', 'de')
            context: Optional context dictionary with conversation history
            use_case: Use case for fallback responses
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response
            
        Returns:
            Response in the target language
        """
        if language == "en":
            # For English, use the standard method
            return self.get_response(prompt, use_case, temperature, max_tokens)
        
        # For non-English languages, add translation instructions
        multilingual_prompt = self.translate_prompt(prompt, language, context)
        
        # Try to get response
        response = self._call_groq(multilingual_prompt, temperature, max_tokens)
        if response:
            return response
        
        # Fallback to OpenRouter
        response = self._call_openrouter_fallback(multilingual_prompt, temperature, max_tokens)
        if response:
            return response
        
        # Final fallback with localized response
        return self._get_localized_fallback_response(use_case, language)
    
    def translate_prompt(self, prompt: str, target_language: str, context: Dict = None) -> str:
        """
        Add translation instructions to a prompt for non-English languages.
        
        Args:
            prompt: Original prompt in English
            target_language: Target language code
            context: Optional context for better translation
            
        Returns:
            Enhanced prompt with translation instructions
        """
        if target_language == "en":
            return prompt
        
        # Import here to avoid circular imports
        from utils.language_manager import LanguageManager
        lang_manager = LanguageManager()
        
        # Get language info
        lang_info = lang_manager.get_language_info(target_language)
        if not lang_info:
            return prompt  # Fallback to original if language not supported
        
        language_name = lang_info['name']
        native_name = lang_info['native_name']
        
        # Get cultural context for better translation
        cultural_context = lang_manager.get_cultural_context(target_language)
        
        # Build context-aware translation instruction
        translation_instruction = f"""
You are a professional hiring assistant. Please respond in {language_name} ({native_name}).

Cultural Context:
- Communication style: {cultural_context['communication_style']}
- Formality level: {cultural_context['formality_level']}
- Professional expectations: {cultural_context['interview_expectations']}

Instructions:
1. Translate and respond to the following request in {native_name}
2. Maintain professional tone appropriate for {cultural_context['formality_level']} formality
3. Use {cultural_context['communication_style']} communication style
4. Keep technical terms in their commonly used form (may be English if that's standard)
5. Be culturally sensitive and appropriate

Original request:
{prompt}

Please respond in {native_name}:
"""
        
        # Add conversation context if provided
        if context and 'conversation_history' in context:
            history_summary = self._summarize_conversation_history(context['conversation_history'])
            translation_instruction = f"""
Previous conversation context: {history_summary}

{translation_instruction}
"""
        
        return translation_instruction
    
    def preserve_context_across_languages(self, history: List[Dict], new_language: str) -> List[Dict]:
        """
        Preserve conversation context when switching languages.
        
        Args:
            history: Conversation history list
            new_language: New language to switch to
            
        Returns:
            Updated history with language context preserved
        """
        if not history:
            return history
        
        # Add language switch marker to history
        language_switch_entry = {
            "role": "system",
            "content": f"Language switched to {new_language}",
            "language": new_language,
            "timestamp": time.time()
        }
        
        # Keep recent history and add language switch marker
        preserved_history = history[-10:] if len(history) > 10 else history
        preserved_history.append(language_switch_entry)
        
        return preserved_history
    
    def handle_translation_failure(self, original_prompt: str, error: Exception, fallback_language: str = "en") -> str:
        """
        Handle translation failures gracefully.
        
        Args:
            original_prompt: The original prompt that failed
            error: The exception that occurred
            fallback_language: Language to fall back to (default: English)
            
        Returns:
            Fallback response
        """
        logger.error(f"Translation failure: {error}")
        
        # Try to get response in fallback language
        try:
            if fallback_language == "en":
                return self.get_response(original_prompt, "general")
            else:
                return self.get_multilingual_response(original_prompt, fallback_language)
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            return self._get_localized_fallback_response("general", fallback_language)
    
    def optimize_for_language(self, language: str) -> Dict[str, Any]:
        """
        Get optimization settings for a specific language.
        
        Args:
            language: Language code
            
        Returns:
            Dictionary with optimization settings
        """
        # Language-specific optimizations
        optimizations = {
            "en": {
                "temperature": 0.7,
                "max_tokens": 500,
                "model_preference": "groq_primary"
            },
            "es": {
                "temperature": 0.8,  # Slightly higher for more natural Spanish
                "max_tokens": 600,   # Spanish can be more verbose
                "model_preference": "groq_primary"
            },
            "fr": {
                "temperature": 0.7,
                "max_tokens": 600,   # French can be more verbose
                "model_preference": "groq_primary"
            },
            "de": {
                "temperature": 0.6,  # German tends to be more structured
                "max_tokens": 550,   # German compound words
                "model_preference": "groq_primary"
            },
            "ja": {
                "temperature": 0.8,
                "max_tokens": 700,   # Japanese can require more tokens
                "model_preference": "groq_primary"
            },
            "zh": {
                "temperature": 0.8,
                "max_tokens": 600,
                "model_preference": "groq_primary"
            },
            "hi": {
                "temperature": 0.8,
                "max_tokens": 650,
                "model_preference": "groq_primary"
            },
            "ar": {
                "temperature": 0.8,
                "max_tokens": 650,
                "model_preference": "groq_primary"
            }
        }
        
        # Default optimization for unsupported languages
        default_optimization = {
            "temperature": 0.7,
            "max_tokens": 500,
            "model_preference": "groq_primary"
        }
        
        return optimizations.get(language, default_optimization)
    
    def _get_localized_fallback_response(self, use_case: str, language: str) -> str:
        """
        Get a localized fallback response when all APIs fail.
        
        Args:
            use_case: The use case for the fallback
            language: Target language code
            
        Returns:
            Localized fallback response
        """
        # Import here to avoid circular imports
        from utils.language_manager import LanguageManager
        lang_manager = LanguageManager()
        
        # Get localized fallback responses
        localized_fallbacks = {
            "en": {
                "greeting": "Hello! I'm here to help you with your application. Could you please tell me your name?",
                "general": "I apologize, but I'm having trouble connecting to my knowledge base. Could you please try again in a moment?"
            },
            "es": {
                "greeting": "¡Hola! Estoy aquí para ayudarte con tu solicitud. ¿Podrías decirme tu nombre?",
                "general": "Me disculpo, pero tengo problemas para conectarme a mi base de conocimientos. ¿Podrías intentarlo de nuevo en un momento?"
            },
            "fr": {
                "greeting": "Bonjour ! Je suis ici pour vous aider avec votre candidature. Pourriez-vous me dire votre nom ?",
                "general": "Je m'excuse, mais j'ai des difficultés à me connecter à ma base de connaissances. Pourriez-vous réessayer dans un moment ?"
            },
            "de": {
                "greeting": "Hallo! Ich bin hier, um Ihnen bei Ihrer Bewerbung zu helfen. Könnten Sie mir Ihren Namen sagen?",
                "general": "Entschuldigung, aber ich habe Probleme beim Verbinden mit meiner Wissensdatenbank. Könnten Sie es in einem Moment noch einmal versuchen?"
            },
            "it": {
                "greeting": "Ciao! Sono qui per aiutarti con la tua candidatura. Potresti dirmi il tuo nome?",
                "general": "Mi scuso, ma ho problemi a connettermi alla mia base di conoscenze. Potresti riprovare tra un momento?"
            },
            "pt": {
                "greeting": "Olá! Estou aqui para ajudá-lo com sua candidatura. Você poderia me dizer seu nome?",
                "general": "Peço desculpas, mas estou tendo problemas para me conectar à minha base de conhecimento. Você poderia tentar novamente em um momento?"
            },
            "hi": {
                "greeting": "नमस्ते! मैं आपके आवेदन में मदद करने के लिए यहाँ हूँ। क्या आप मुझे अपना नाम बता सकते हैं?",
                "general": "मुझे खेद है, लेकिन मुझे अपने ज्ञान आधार से जुड़ने में समस्या हो रही है। क्या आप कृपया एक क्षण में फिर से कोशिश कर सकते हैं?"
            }
        }
        
        # Get fallback for the language, or use English as ultimate fallback
        language_fallbacks = localized_fallbacks.get(language, localized_fallbacks["en"])
        return language_fallbacks.get(use_case, language_fallbacks.get("general", "I apologize for the technical difficulty. Please try again."))
    
    def _summarize_conversation_history(self, history: List[Dict]) -> str:
        """
        Summarize conversation history for context preservation.
        
        Args:
            history: List of conversation messages
            
        Returns:
            Summary string
        """
        if not history:
            return "No previous conversation."
        
        # Get last few messages for context
        recent_messages = history[-5:] if len(history) > 5 else history
        
        summary_parts = []
        for msg in recent_messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100]  # Truncate long messages
            summary_parts.append(f"{role}: {content}")
        
        return " | ".join(summary_parts)