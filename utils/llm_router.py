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
    """Routes LLM requests to appropriate provider based on availability and use case."""
    
    def __init__(self):
        """Initialize the LLM router with API clients."""
        # Set up Groq client
        self.groq_client = groq.Groq(api_key=config.GROQ_API_KEY) if config.GROQ_API_KEY else None
        
        # OpenRouter uses the OpenAI client with a different base URL
        if config.OPENROUTER_API_KEY:
            self.openrouter_client = openai.OpenAI(
                api_key=config.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
        else:
            self.openrouter_client = None
            
        if not self.groq_client and not self.openrouter_client:
            logger.warning("No API keys provided. LLM functionality will be limited.")
    
    def _call_groq(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> Optional[str]:
        """Call the Groq API and return the response."""
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
    
    def _call_openrouter(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> Optional[str]:
        """Call the OpenRouter API and return the response."""
        if not self.openrouter_client:
            logger.warning("OpenRouter API key not provided.")
            return None
        
        try:
            response = self.openrouter_client.chat.completions.create(
                model=config.OPENROUTER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return None
    
    def get_response(self, prompt: str, use_case: str = "general", 
                    temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Get a response from the appropriate LLM based on use case.
        
        Args:
            prompt: The input prompt for the LLM
            use_case: What the response is being used for (general, tech_questions, etc.)
            temperature: Model temperature parameter
            max_tokens: Maximum tokens in response
            
        Returns:
            Model response as string, or error message if both APIs fail
        """
        # For technical questions, prioritize Groq for speed
        if use_case == "tech_questions":
            start_time = time.time()
            response = self._call_groq(prompt, temperature, max_tokens)
            
            # If Groq fails or times out after 5 seconds, use OpenRouter
            if not response and (time.time() - start_time > 5 or not self.groq_client):
                logger.info("Falling back to OpenRouter for technical questions")
                response = self._call_openrouter(prompt, temperature, max_tokens)
        else:
            # For general conversation, try OpenRouter first for accuracy
            response = self._call_openrouter(prompt, temperature, max_tokens)
            
            # Fallback to Groq if OpenRouter fails
            if not response:
                logger.info("Falling back to Groq for general conversation")
                response = self._call_groq(prompt, temperature, max_tokens)
        
        # Final fallback message if both APIs fail
        if not response:
            return "I apologize, but I'm currently having trouble connecting to my knowledge base. Could you please try again in a moment?"
            
        return response
            
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