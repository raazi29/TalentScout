#!/usr/bin/env python3
"""
Health check script for TalentScout deployment
"""
import sys
import os

def check_imports():
    """Check if all required modules can be imported."""
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
        
        import config
        print("✅ Config imported successfully")
        
        from utils.conversation import ConversationManager
        print("✅ ConversationManager imported successfully")
        
        from utils.language_manager import LanguageManager
        print("✅ LanguageManager imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_environment():
    """Check environment variables."""
    required_vars = ['GROQ_API_KEY']
    optional_vars = ['OPENROUTER_API_KEY', 'HUGGINGFACE_API_KEY']
    
    print("\n🔍 Checking environment variables:")
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is missing (required)")
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} is missing (optional)")

def main():
    print("🏥 TalentScout Health Check")
    print("=" * 40)
    
    print("\n📦 Checking imports...")
    imports_ok = check_imports()
    
    check_environment()
    
    if imports_ok:
        print("\n✅ Health check passed!")
        return 0
    else:
        print("\n❌ Health check failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())