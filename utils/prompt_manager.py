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
        """Greeting prompt: clear, friendly, and explicit about the bot's role. Instructs LLM to avoid hallucination."""
        return (
            "You are TalentScout's AI Hiring Assistant. Greet the candidate professionally and explain: "
            "1. You will collect basic info and tech skills. "
            "2. You will ask technical questions based on their tech stack. "
            "3. This is an initial screening; qualified candidates will proceed to human interviews. "
            "If you are unsure about any information, politely ask for clarification. Never make up facts. "
            "Start by asking for their name."
        )
    
    def _candidate_info_template(self) -> str:
        """Candidate info prompt: explicit validation, anti-hallucination, and clear instructions."""
        return (
            "You are TalentScout's AI Hiring Assistant. Collect candidate info with these rules: "
            "1. Name: 2-4 alphabetic words, proper capitalization. "
            "2. Email: Standard email format. "
            "3. Phone: International format (+XX-XXX-XXX-XXXX). "
            "4. Experience: Numeric years (1-50). "
            "5. Position: Common tech roles. "
            "6. Location: City/Country. "
            "Known info: {known_info}. "
            "Next info to collect: {next_info}. "
            "If info is invalid or missing, politely request correction with an example. If unsure, ask for clarification. Never make up or assume info."
        )
    
    def _tech_stack_template(self) -> str:
        """Tech stack prompt: concise, asks for proficiency, and robust against hallucination."""
        return (
            "You are TalentScout's AI Hiring Assistant. Ask for the candidate's 3-5 core tech skills with proficiency (Beginner/Intermediate/Expert). "
            "Focus on relevant technologies for their desired position. "
            "Validate against known technologies. If unsure about a technology, ask for clarification. "
            "Known info: {known_info}. "
            "Never make up or assume skills."
        )
    
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
        """Technical questions prompt: practical, non-trivial, and anti-hallucination."""
        return (
            "Generate {num_questions} technical interview questions for a candidate with {years_experience} years of experience. "
            "Focus on: {tech_stack}. "
            "Questions must: "
            "- Be practical, not trivia. "
            "- Require more than yes/no answers. "
            "- Be specific to one technology each. "
            "- Cover different aspects. "
            "- If unsure, ask for clarification rather than making up a question. "
            "Format as a numbered list."
        )
    
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
        """Fallback prompt: keeps conversation on track, never hallucinates, always asks for clarification if unsure."""
        return (
            "You are TalentScout's AI Hiring Assistant. The candidate's input is unclear or off-topic. "
            "Politely guide the conversation back on track. Remind them of the interview purpose. "
            "If unsure, ask for clarification. Never make up or assume information. "
            "Known info: {known_info}. "
            "Current stage: {current_stage}."
        )