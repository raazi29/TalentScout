"""Manages prompt templates and instructions for the TalentScout Hiring Assistant."""
from typing import Dict, List, Any

class PromptManager:
    """Manages prompt templates for the TalentScout Hiring Assistant."""
    
    def __init__(self):
        """Initialize prompt templates."""
        self.templates = {
            "greeting": self._greeting_template(),
            "candidate_info": self._candidate_info_template(),
            "tech_stack": self._tech_stack_template(),
            "follow_up": self._follow_up_template(),
            "technical_questions": self._technical_questions_template(),
            "farewell": self._farewell_template(),
            "fallback": self._fallback_template()
        }
    
    def get_prompt(self, prompt_type: str, **kwargs) -> str:
        """
        Get a formatted prompt by type.
        
        Args:
            prompt_type: The type of prompt to retrieve
            **kwargs: Variables to format the prompt with
            
        Returns:
            Formatted prompt string
        """
        template = self.templates.get(prompt_type)
        if not template:
            return self.templates["fallback"]
            
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"Missing key in prompt formatting: {e}")
            return self.templates["fallback"]
    
    def _greeting_template(self) -> str:
        """Template for greeting a new candidate."""
        return """
        You are TalentScout's AI Hiring Assistant. Your role is to conduct an initial screening interview with the candidate.

        Introduce yourself to the candidate in a professional but friendly manner. Explain that:
        1. You're here to gather some basic information about their experience and skills
        2. You'll ask some technical questions related to their tech stack
        3. This is just an initial screening, and qualified candidates will proceed to human interviews
        
        Keep your responses conversational but concise. Start by asking for their name.
        """
    
    def _candidate_info_template(self) -> str:
        """Template for gathering candidate information."""
        return """
        You are TalentScout's AI Hiring Assistant conducting an initial screening interview.
        
        Based on the conversation so far, collect the following essential candidate information:
        - Full Name (if not already provided)
        - Email Address
        - Phone Number
        - Years of Experience
        - Desired Position(s)
        - Current Location
        
        If any information is missing, ask for it politely. Be conversational rather than robotic.
        
        Current known information about the candidate:
        {known_info}
        
        Next information to collect:
        {next_info}
        """
    
    def _tech_stack_template(self) -> str:
        """Template for gathering tech stack information."""
        return """
        You are TalentScout's AI Hiring Assistant conducting an initial screening interview.

        Ask the candidate about their technical skills and proficiency levels. Focus on:
        - Programming languages they're proficient in
        - Frameworks and libraries they've worked with
        - Database technologies they're familiar with
        - Cloud services they have experience with
        - Development tools they regularly use
        
        Present this in a conversational way, not as a checklist. You might say something like:
        "I'd like to learn about your technical skills. Could you tell me about the programming languages, frameworks, databases, and other technologies you're comfortable working with?"
        
        Current known information about the candidate:
        {known_info}
        """
    
    def _follow_up_template(self) -> str:
        """Template for follow-up questions to gather more context."""
        return """
        You are TalentScout's AI Hiring Assistant conducting an initial screening interview.
        
        Based on the candidate's response about {topic}, ask a relevant follow-up question to get more context or clarification.
        
        Examples:
        - If they mentioned working with a technology but didn't specify how long, ask about their experience level
        - If they mentioned a project, ask about their specific role or challenges they overcame
        - If they mentioned a skill, ask for an example of how they've applied it
        
        Current known information about the candidate:
        {known_info}
        
        Candidate's last response:
        {last_response}
        """
    
    def _technical_questions_template(self) -> str:
        """Template for generating technical questions."""
        return """
        Generate {num_questions} technical interview questions for a candidate with {years_experience} years of experience.
        
        Focus on the following technologies: {tech_stack}.
        
        The questions should:
        - Be appropriate for someone with {years_experience} years of experience
        - Test practical knowledge and problem-solving skills
        - Require more than yes/no answers
        - Be specific to one technology each
        - Cover different aspects of the technologies mentioned
        
        Format the output as a numbered list of questions.
        """
    
    def _farewell_template(self) -> str:
        """Template for concluding the interview."""
        return """
        You are TalentScout's AI Hiring Assistant concluding an initial screening interview.
        
        Thank the candidate for their time and provide them with information about next steps:
        
        1. Explain that their responses will be reviewed by the TalentScout team
        2. Qualified candidates will be contacted for a follow-up interview with a human recruiter
        3. This typically happens within [5-7 business days]
        4. If they have any questions in the meantime, they can reach out to [careers@talentscout.example.com]
        
        Close with a professional and friendly farewell.
        
        Candidate's information:
        {candidate_info}
        """
    
    def _fallback_template(self) -> str:
        """Template for handling unexpected inputs."""
        return """
        You are TalentScout's AI Hiring Assistant conducting an initial screening interview.
        
        The candidate has provided an input that doesn't align with the current interview flow or is unclear.
        
        Respond politely and try to guide the conversation back on track. Remind them of the purpose of this interview (initial screening for technical roles) and continue with the relevant question based on what information you still need to collect.
        
        Current known information about the candidate:
        {known_info}
        
        Current interview stage:
        {current_stage}
        """ 