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