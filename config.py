"""Configuration settings for TalentScout Hiring Assistant."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Model configurations
GROQ_MODEL = "llama3-70b-8192"  # Fast model for most interactions

# OpenRouter models with multiple selection options
OPENROUTER_MODELS = {
    "primary": "tngtech/deepseek-r1t2-chimera",  # High performance with 20% faster speed than R1-0528
    "alternatives": {
        "deepseek_r1_0528": "deepseek/r1-0528",  # Performance comparable to OpenAI o1, 671B parameters
        "tng_r1t_chimera": "tngtech/deepseek-r1t-chimera",  # Combines R1 reasoning with V3 token efficiency
        "microsoft_mai_ds_r1": "microsoft/mai-ds-r1",  # Enhanced safety profile with strong reasoning capabilities
        "deepseek_r1": "deepseek/r1"  # Original R1 model with 671B parameters, MIT licensed
    }
}
# Default OpenRouter model to use
OPENROUTER_MODEL = OPENROUTER_MODELS["primary"]

# Conversation settings
MAX_TECHNICAL_QUESTIONS = 5
MIN_TECHNICAL_QUESTIONS = 3
MAX_HISTORY_LENGTH = 10  # Number of conversation turns to maintain context

# Tech stack categories
TECH_CATEGORIES = {
    "programming_languages": ["Python", "JavaScript", "Java", "C#", "C++", "Go", "Ruby", "PHP", "Swift", "Kotlin"],
    "frameworks": ["React", "Angular", "Vue.js", "Django", "Flask", "Spring", "ASP.NET", "Laravel", "Ruby on Rails"],
    "databases": ["MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle", "SQL Server", "DynamoDB"],
    "cloud_services": ["AWS", "Azure", "Google Cloud", "Firebase", "Heroku", "Netlify"],
    "tools": ["Docker", "Kubernetes", "Git", "Jenkins", "Travis CI", "Jira", "Confluence"]
}

# App settings
APP_TITLE = "TalentScout Hiring Assistant"
APP_DESCRIPTION = "AI-powered chatbot for initial candidate screening" 