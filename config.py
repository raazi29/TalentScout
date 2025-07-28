"""Configuration settings for TalentScout Hiring Assistant."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys with validation
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("⚠️  Warning: GROQ_API_KEY not found. Please check your .env file.")

# OpenRouter fallback configuration (for use only if Groq is unavailable)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("⚠️  Warning: OPENROUTER_API_KEY not found. Fallback may not work.")
# List of working OpenRouter models for 2025 (tested and verified)
# Ordered by reliability and performance for hiring assistant use case
OPENROUTER_MODELS_2025 = [
    "google/gemma-2-9b-it:free",                 # Gemma 2 9B (Google, tested working ✅)
    "mistralai/mistral-7b-instruct:free",       # Mistral 7B (good performance, free)
    "google/gemma-7b-it:free",                   # Gemma 7B (Google, reliable backup)
    "huggingface/zephyr-7b-beta:free",          # Zephyr 7B (conversational, free)
    "meta-llama/llama-3-8b-instruct:free",      # Llama 3 8B (if available)
    "openchat/openchat-7b:free",                 # OpenChat 7B (conversational fallback)
]
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Check API key status and provide feedback
if not GROQ_API_KEY and not OPENROUTER_API_KEY:
    print("❌ ERROR: No API keys found! Please set at least GROQ_API_KEY or OPENROUTER_API_KEY")
    print("   Add these to your Render environment variables.")
    print("   Get Groq API key: https://console.groq.com/")
    print("   Get OpenRouter API key: https://openrouter.ai/")
elif GROQ_API_KEY and OPENROUTER_API_KEY:
    print("✅ Both Groq and OpenRouter API keys found - full fallback enabled")
    print("   Primary: Groq (fastest) → Fallback: OpenRouter (reliable)")
elif GROQ_API_KEY:
    print("✅ Groq API key found - primary service enabled")
    print("⚠️  OpenRouter fallback disabled (no API key)")
    print("   Consider adding OPENROUTER_API_KEY for better reliability")
elif OPENROUTER_API_KEY:
    print("✅ OpenRouter API key found - using as primary service")
    print("⚠️  Consider adding GROQ_API_KEY for better performance")
    print("   Groq is faster but OpenRouter has more model options")

# Model configuration: Use only Groq's llama3-8b-8192 for all LLM calls (fastest, most reliable, least hallucination among free models)
GROQ_MODEL = "llama3-8b-8192"

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
APP_VERSION = "2.0.0"
APP_AUTHOR = "AI/ML Intern Assignment"