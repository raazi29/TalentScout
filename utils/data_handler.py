"""Handles data processing and storage for TalentScout Hiring Assistant."""
import json
import os
from typing import Dict, List, Any, Optional
import datetime

class DataHandler:
    """Manages candidate data storage and retrieval."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize data handler.
        
        Args:
            data_dir: Directory for storing data files
        """
        self.data_dir = data_dir
        self._ensure_data_dir()
    
    def _ensure_data_dir(self) -> None:
        """Ensure data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def save_candidate_data(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        Save candidate data to file.
        
        Args:
            session_id: Unique session identifier
            data: Candidate data to save
        """
        self._ensure_data_dir()
        
        # Add timestamp
        data["timestamp"] = datetime.datetime.now().isoformat()
        
        file_path = os.path.join(self.data_dir, f"candidate_{session_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving candidate data: {e}")
    
    def load_candidate_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load candidate data from file.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Candidate data dict or None if not found
        """
        file_path = os.path.join(self.data_dir, f"candidate_{session_id}.json")
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading candidate data: {e}")
            return None
    
    def update_candidate_data(self, session_id: str, 
                             updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update existing candidate data.
        
        Args:
            session_id: Unique session identifier
            updates: New data to update
            
        Returns:
            Updated candidate data or None on error
        """
        current_data = self.load_candidate_data(session_id)
        
        if not current_data:
            # If no existing data, create new
            self.save_candidate_data(session_id, updates)
            return updates
        
        # Update data
        current_data.update(updates)
        
        # Save updated data
        self.save_candidate_data(session_id, current_data)
        
        return current_data
    
    def get_tech_stack(self, session_id: str) -> List[str]:
        """
        Get candidate's tech stack.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of technologies or empty list if not found
        """
        data = self.load_candidate_data(session_id)
        
        if not data or "tech_stack" not in data:
            return []
            
        return data["tech_stack"]
    
    def get_experience_years(self, session_id: str) -> int:
        """
        Get candidate's years of experience.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Years of experience or 0 if not found
        """
        data = self.load_candidate_data(session_id)
        
        if not data or "years_experience" not in data:
            return 0
            
        try:
            return int(data["years_experience"])
        except (ValueError, TypeError):
            # Handle case where experience is not a valid integer
            return 0
    
    def store_technical_questions(self, session_id: str, 
                                 questions: List[str]) -> None:
        """
        Store technical questions asked to candidate.
        
        Args:
            session_id: Unique session identifier
            questions: List of technical questions
        """
        data = self.load_candidate_data(session_id) or {}
        
        # Add questions to data
        data["technical_questions"] = questions
        
        # Save updated data
        self.save_candidate_data(session_id, data)
    
    def get_candidate_summary(self, session_id: str) -> str:
        """
        Get summary of candidate data as formatted string.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Formatted summary string
        """
        data = self.load_candidate_data(session_id)
        
        if not data:
            return "No candidate data found."
            
        # Create formatted summary
        summary_lines = ["Candidate Summary:"]
        
        # Basic info
        if "name" in data:
            summary_lines.append(f"Name: {data.get('name', 'Not provided')}")
        if "email" in data:
            summary_lines.append(f"Email: {data.get('email', 'Not provided')}")
        if "phone" in data:
            summary_lines.append(f"Phone: {data.get('phone', 'Not provided')}")
        if "location" in data:
            summary_lines.append(f"Location: {data.get('location', 'Not provided')}")
        if "years_experience" in data:
            summary_lines.append(f"Experience: {data.get('years_experience', 'Not provided')} years")
        if "position" in data:
            summary_lines.append(f"Desired Position: {data.get('position', 'Not provided')}")
            
        # Tech stack
        if "tech_stack" in data and data["tech_stack"]:
            summary_lines.append("\nTech Stack:")
            for tech in data["tech_stack"]:
                summary_lines.append(f"- {tech}")
                
        # Technical questions
        if "technical_questions" in data and data["technical_questions"]:
            summary_lines.append("\nTechnical Questions Asked:")
            for i, question in enumerate(data["technical_questions"], 1):
                summary_lines.append(f"{i}. {question}")
                
        # Answers if available
        if "technical_answers" in data and data["technical_answers"]:
            summary_lines.append("\nCandidate's Answers:")
            for i, answer in enumerate(data["technical_answers"], 1):
                summary_lines.append(f"Q{i}: {answer[:100]}...")
                
        return "\n".join(summary_lines) 