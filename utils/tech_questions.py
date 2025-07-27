"""Generate technical questions based on candidate's tech stack."""
from typing import List, Dict, Any, Optional
import random

import config
from utils.llm_router import LLMRouter

class TechQuestionGenerator:
    """Generates technical questions based on candidate's tech stack."""
    
    def __init__(self):
        """Initialize the technical question generator."""
        self.llm_router = LLMRouter()
        self.question_cache: Dict[str, List[str]] = {}  # Cache questions by tech
    
    def generate_questions(self, tech_stack: List[str], years_experience: int, 
                           num_questions: Optional[int] = None) -> List[str]:
        """
        Generate technical questions based on the candidate's tech stack.
        
        Args:
            tech_stack: List of technologies the candidate is proficient in
            years_experience: Years of experience to adjust difficulty
            num_questions: Number of questions to generate (defaults to config)
            
        Returns:
            List of technical questions
        """
        if not tech_stack:
            return self._generate_general_questions()
            
        if num_questions is None:
            # Use the minimum and maximum from config to determine range
            min_q = config.MIN_TECHNICAL_QUESTIONS
            max_q = config.MAX_TECHNICAL_QUESTIONS
            num_questions = min(max(min_q, len(tech_stack)), max_q)
        
        return self._generate_tech_specific_questions(tech_stack, years_experience, num_questions)
    
    def _generate_general_questions(self) -> List[str]:
        """Generate general technical questions when no tech stack is provided."""
        general_questions = [
            "Can you describe your experience with programming languages?",
            "What software development methodologies are you familiar with?",
            "How do you approach debugging complex technical issues?",
            "Describe a challenging technical project you worked on recently.",
            "How do you stay updated with industry trends and new technologies?",
            "What tools do you use for version control and why?",
            "How do you ensure code quality and maintainability?",
            "Describe your experience with testing and QA processes.",
            "How do you approach technical documentation?",
            "What's your process for learning a new technology quickly?"
        ]
        
        # Select a random subset of questions
        count = min(config.MIN_TECHNICAL_QUESTIONS, len(general_questions))
        return random.sample(general_questions, count)
    
    def _generate_tech_specific_questions(self, tech_stack: List[str], 
                                         years_experience: int, 
                                         num_questions: int) -> List[str]:
        """Generate technology-specific questions."""
        # Determine difficulty based on experience
        difficulty = self._determine_difficulty(years_experience)
        
        # Try to get questions from the LLM router
        questions = self.llm_router.generate_technical_questions(tech_stack, years_experience)
        
        # If we got enough questions, return them
        if questions and len(questions) >= num_questions:
            return questions[:num_questions]
            
        # Fallback: generate questions ourselves using templates
        return self._generate_fallback_questions(tech_stack, difficulty, num_questions)
    
    def _determine_difficulty(self, years_experience: int) -> str:
        """Determine question difficulty based on years of experience."""
        if years_experience < 2:
            return "entry-level"
        elif years_experience < 5:
            return "intermediate"
        else:
            return "advanced"
    
    def _generate_fallback_questions(self, tech_stack: List[str], 
                                    difficulty: str, 
                                    num_questions: int) -> List[str]:
        """Generate fallback questions using templates if LLM fails."""
        questions = []
        templates = self._get_question_templates(difficulty)
        
        # Try to generate at least one question per tech, up to num_questions
        techs_to_use = tech_stack.copy()
        random.shuffle(techs_to_use)  # Randomize tech order
        
        # Limit to num_questions techs
        techs_to_use = techs_to_use[:num_questions]
        
        for tech in techs_to_use:
            # Try to find a question from cache first
            cache_key = f"{tech}_{difficulty}"
            if cache_key in self.question_cache and self.question_cache[cache_key]:
                # Get and remove a question from cache
                questions.append(self.question_cache[cache_key].pop(0))
                continue
                
            # No cached question, generate a new one
            template = random.choice(templates)
            question = template.format(tech=tech)
            questions.append(question)
            
        return questions
    
    def _get_question_templates(self, difficulty: str) -> List[str]:
        """Get question templates based on difficulty level."""
        templates = {
            "entry-level": [
                "What are the basic features of {tech}?",
                "Can you explain the main use cases for {tech}?",
                "What are some advantages of using {tech} compared to alternatives?",
                "How would you set up a simple project using {tech}?",
                "What resources did you use to learn {tech}?",
                "Can you describe a simple project you built using {tech}?"
            ],
            "intermediate": [
                "What are some best practices when working with {tech}?",
                "How would you optimize performance in a {tech} application?",
                "Can you explain the architecture of a {tech} application you've built?",
                "What are some common pitfalls to avoid when using {tech}?",
                "How do you handle error management in {tech}?",
                "How would you implement testing for a {tech} application?"
            ],
            "advanced": [
                "Can you describe a complex technical challenge you solved using {tech}?",
                "How would you architect a scalable system using {tech}?",
                "What are the internals of {tech} and how does it work under the hood?",
                "How have you extended or customized {tech} for specific requirements?",
                "Can you discuss the tradeoffs involved in different {tech} implementation strategies?",
                "How would you debug a complex issue in a {tech} application?"
            ]
        }
        
        return templates.get(difficulty, templates["intermediate"])
    
    def cache_questions(self, tech: str, difficulty: str, questions: List[str]) -> None:
        """Cache questions for a specific technology and difficulty level."""
        cache_key = f"{tech}_{difficulty}"
        self.question_cache[cache_key] = questions 