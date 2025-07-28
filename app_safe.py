"""
TalentScout Hiring Assistant - Safe Deployment Version
Handles missing environment variables gracefully
"""
import streamlit as st
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """Check if environment is properly configured."""
    issues = []
    
    # Check for API keys
    if not os.getenv("GROQ_API_KEY"):
        issues.append("GROQ_API_KEY is missing")
    
    if not os.getenv("OPENROUTER_API_KEY"):
        issues.append("OPENROUTER_API_KEY is missing (fallback)")
    
    return issues

def display_environment_error(issues):
    """Display environment configuration error."""
    st.error("🚨 **Configuration Error**")
    st.markdown("""
    **The TalentScout Hiring Assistant is not properly configured.**
    
    **Missing Configuration:**
    """)
    
    for issue in issues:
        st.markdown(f"- ❌ {issue}")
    
    st.markdown("""
    **To fix this:**
    1. Go to your Render dashboard
    2. Navigate to your service settings
    3. Add the missing environment variables in the "Environment" section
    4. Redeploy the service
    
    **Required Environment Variables:**
    - `GROQ_API_KEY`: Your Groq API key (required)
    - `OPENROUTER_API_KEY`: Your OpenRouter API key (optional fallback)
    """)
    
    st.info("💡 **For developers:** Check that environment variables are set in Render dashboard, not just in .env file")

def main():
    """Main application with environment checking."""
    st.set_page_config(
        page_title="TalentScout Hiring Assistant",
        page_icon="👨‍💼",
        layout="wide"
    )
    
    # Check environment first
    env_issues = check_environment()
    
    if env_issues:
        display_environment_error(env_issues)
        return
    
    # If environment is OK, try to load the main app
    try:
        import config
        from utils.conversation import ConversationManager
        
        # Import and run the original app
        import app
        app.main()
        
    except ImportError as e:
        st.error(f"🚨 **Import Error**: {str(e)}")
        st.markdown("""
        **Possible solutions:**
        - Check that all required files are present
        - Verify that the build completed successfully
        - Check Render build logs for errors
        """)
        
        if st.checkbox("Show technical details"):
            st.code(f"Error: {str(e)}")
            st.code(f"Python path: {sys.path}")
            st.code(f"Current directory: {os.getcwd()}")
            st.code(f"Files in current directory: {os.listdir('.')}")
    
    except Exception as e:
        st.error(f"🚨 **Application Error**: {str(e)}")
        st.markdown("""
        **Something went wrong with the TalentScout Hiring Assistant.**
        
        **Possible solutions:**
        - 🔄 Refresh the page and try again
        - 🌐 Check your internet connection
        - ⏰ Wait a moment and retry (API might be temporarily unavailable)
        
        If the problem persists, please contact support.
        """)
        
        if st.checkbox("Show technical details"):
            st.code(f"Error: {str(e)}")

if __name__ == "__main__":
    main()