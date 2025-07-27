"""
TalentScout Hiring Assistant - Enhanced Streamlit Application

A comprehensive AI-powered chatbot for initial candidate screening with advanced features.
"""
import uuid
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.conversation import ConversationManager
import config

# Set page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="👨‍💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for better UI
st.markdown("""
<style>
    /* Main container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Chat message styling */
    .stChatMessageContent {
        background-color: rgba(240, 242, 246, 0.1) !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Hide footer */
    footer {
        visibility: hidden;
    }
    
    /* Language selector styling */
    .language-selector {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def init_session():
    """Initialize session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "conversation_manager" not in st.session_state:
        st.session_state.conversation_manager = ConversationManager(st.session_state.session_id)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add initial greeting
        conversation_manager = st.session_state.conversation_manager
        initial_message = conversation_manager.process_message("Hello")
        st.session_state.messages.append({"role": "assistant", "content": initial_message})
    
    if "show_analytics" not in st.session_state:
        st.session_state.show_analytics = False
    
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "en"

def display_language_selector():
    """Display language selection interface."""
    st.markdown("### 🌍 Language Selection")
    
    # Get languages from the language manager
    from utils.language_manager import LanguageManager
    lang_manager = LanguageManager()
    supported_languages = lang_manager.get_supported_languages()
    
    # Create language options with flags and native names
    languages = {}
    for code, info in supported_languages.items():
        languages[code] = f"{info['flag']} {info['native_name']} ({info['name']})"
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_lang = st.selectbox(
            "Choose your preferred language:",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=list(languages.keys()).index(st.session_state.selected_language)
        )
    
    with col2:
        if st.button("Apply Language", type="secondary"):
            if selected_lang != st.session_state.selected_language:
                st.session_state.selected_language = selected_lang
                conversation_manager = st.session_state.conversation_manager
                conversation_manager.update_language(selected_lang)
                st.success(f"Language changed to {languages[selected_lang]}")
                st.rerun()
    
    st.markdown("---")

def display_conversation_progress():
    """Display conversation progress and analytics."""
    conversation_manager = st.session_state.conversation_manager
    analytics = conversation_manager.get_conversation_analytics()
    
    st.markdown("### 📊 Conversation Progress")
    
    # Progress bar
    progress = analytics['completion_percentage'] / 100
    st.progress(progress)
    st.caption(f"Progress: {analytics['completion_percentage']:.1f}% complete")
    
    # Current stage indicator
    stage_emojis = {
        "greeting": "👋",
        "name": "📝", 
        "contact_info": "📧",
        "experience": "💼",
        "position": "🎯",
        "location": "📍",
        "tech_stack": "💻",
        "technical_questions": "🔧",
        "farewell": "👋",
        "complete": "✅"
    }
    
    current_stage = analytics['stage_name']
    stage_emoji = stage_emojis.get(current_stage, "📋")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Current Stage",
            value=f"{stage_emoji} {current_stage.replace('_', ' ').title()}",
            delta=f"Stage {analytics['current_stage'] + 1}/10"
        )
    
    with col2:
        st.metric(
            label="Messages",
            value=analytics['conversation_length'],
            delta=f"Language: {analytics['language'].upper()}"
        )
    
    with col3:
        st.metric(
            label="Technical Questions",
            value=f"{analytics['technical_answers_count']}/{analytics['technical_questions_count']}",
            delta="Answered"
        )
    
    st.markdown("---")

def display_candidate_summary():
    """Display comprehensive candidate summary."""
    conversation_manager = st.session_state.conversation_manager
    summary = conversation_manager.get_candidate_summary()
    
    st.markdown("### 👤 Candidate Summary")
    
    # Basic Information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📋 Basic Information**")
        basic_info = summary['basic_info']
        
        info_data = {
            "Name": basic_info['name'],
            "Email": basic_info['email'],
            "Phone": basic_info['phone'],
            "Position": basic_info['position'],
            "Location": basic_info['location'],
            "Experience": f"{basic_info['years_experience']} years"
        }
        
        for key, value in info_data.items():
            if value != "Not provided":
                st.markdown(f"**{key}:** {value}")
    
    with col2:
        st.markdown("**💻 Technical Information**")
        tech_info = summary['technical_info']
        
        if tech_info['tech_stack']:
            st.markdown("**Tech Stack:**")
            for tech in tech_info['tech_stack']:
                st.markdown(f"• {tech}")
        else:
            st.markdown("*No tech stack provided yet*")
        
        st.markdown(f"**Questions Answered:** {len(tech_info['technical_answers'])}/{len(tech_info['technical_questions'])}")
    
    # Sentiment Analysis
    if 'sentiment_analysis' in summary:
        st.markdown("**😊 Sentiment Analysis**")
        sentiment = summary['sentiment_analysis']
        
        if 'feedback' in sentiment:
            st.info(sentiment['feedback'])
    
    st.markdown("---")

def display_advanced_analytics():
    """Display advanced analytics and insights."""
    try:
        conversation_manager = st.session_state.conversation_manager
        analytics = conversation_manager.get_conversation_analytics()
        
        st.markdown("### 📈 Advanced Analytics")
        
        # Missing fields
        if analytics.get('missing_fields'):
            st.warning(f"**Missing Information:** {', '.join(analytics['missing_fields'])}")
        
        # Collected fields
        if analytics.get('collected_fields'):
            st.success(f"**Collected Information:** {len(analytics['collected_fields'])} fields")
        
        # Sentiment analysis chart
        try:
            if 'sentiment_analysis' in analytics and analytics['sentiment_analysis'].get('total_analyses', 0) > 0:
                st.markdown("**😊 Emotional Progression**")
                
                # Create sentiment chart
                sentiment_data = conversation_manager.candidate_data.get('sentiment_history', [])
                if sentiment_data and len(sentiment_data) > 0:
                    df = pd.DataFrame(sentiment_data)
                    
                    # Check if 'emotion' column exists and has data
                    if 'emotion' in df.columns and len(df['emotion'].dropna()) > 0:
                        # Create emotion distribution chart
                        emotion_counts = df['emotion'].value_counts().reset_index()
                        emotion_counts.columns = ['emotion', 'count']
                        
                        fig = px.bar(
                            emotion_counts,
                            x='emotion',
                            y='count',
                            title="Emotion Distribution",
                            labels={'emotion': 'Emotion', 'count': 'Count'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No emotion data available yet.")
                else:
                    st.info("No sentiment history available yet.")
        except Exception as e:
            st.warning(f"Sentiment chart error: {str(e)}")
        
        # Conversation flow visualization
        st.markdown("**🔄 Conversation Flow**")
        
        try:
            # Create stage progression chart
            conversation_stages = [
                'greeting', 'name', 'contact_info', 'experience', 
                'position', 'location', 'tech_stack', 'technical_questions', 'farewell', 'complete'
            ]
            stage_progress = []
            
            for i, stage in enumerate(conversation_stages):
                if i <= analytics.get('current_stage', 0):
                    stage_progress.append(1)
                else:
                    stage_progress.append(0)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=[stage.replace('_', ' ').title() for stage in conversation_stages],
                    y=stage_progress,
                    marker_color=['#4CAF50' if p == 1 else '#E0E0E0' for p in stage_progress]
                )
            ])
            
            fig.update_layout(
                title="Stage Completion",
                xaxis_title="Stages",
                yaxis_title="Status",
                showlegend=False,
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Conversation flow chart error: {str(e)}")
            
    except Exception as e:
        st.error(f"Analytics error: {str(e)}")
        st.info("Analytics temporarily unavailable.")

def display_chat():
    """Display enhanced chat interface."""
    # Display chat messages with better formatting
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(message["content"])
    
    # Enhanced chat input with language indicator
    current_lang = st.session_state.selected_language
    from utils.language_manager import LanguageManager
    lang_manager = LanguageManager()
    lang_info = lang_manager.get_language_info(current_lang)
    lang_name = lang_info['native_name'] if lang_info else current_lang.upper()
    
    placeholder_text = f"Type your message in {lang_name}..."
    if prompt := st.chat_input(placeholder_text):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get conversation manager
        conversation_manager = st.session_state.conversation_manager
        
        # Process message and get response
        with st.spinner("🤖 TalentScout is thinking..."):
            response = conversation_manager.process_message(prompt)
            
            # Add bot response to chat
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Force UI refresh
        st.rerun()

def display_sidebar():
    """Display enhanced sidebar with all new features."""
    with st.sidebar:
        st.title("🎯 " + config.APP_TITLE)
        st.caption(config.APP_DESCRIPTION)
        
        st.markdown("---")
        
        # Language Selection
        display_language_selector()
        
        # Conversation Progress
        if "conversation_manager" in st.session_state:
            display_conversation_progress()
            
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Show Analytics", use_container_width=True):
                st.session_state.show_analytics = not st.session_state.show_analytics
        
        with col2:
            if st.button("🔄 Reset Chat", use_container_width=True):
                if "conversation_manager" in st.session_state:
                    st.session_state.conversation_manager.reset_conversation()
                st.session_state.messages = []
                st.session_state.show_analytics = False
                # Add initial greeting after reset
                conversation_manager = st.session_state.conversation_manager
                initial_message = conversation_manager.process_message("Hello")
                st.session_state.messages.append({"role": "assistant", "content": initial_message})
                st.rerun()
        
        # Candidate Summary Toggle
        if st.button("👤 Toggle Summary", use_container_width=True):
            if "show_summary" not in st.session_state:
                st.session_state.show_summary = True
            else:
                st.session_state.show_summary = not st.session_state.show_summary
        
        st.markdown("---")
        
        # About Section
        st.subheader("ℹ️ About TalentScout")
        st.markdown("""
        **Enhanced Features:**
        - 🌍 Multi-language support
        - 📊 Real-time analytics
        - 😊 Sentiment analysis
        - 💻 Smart tech stack detection
        - 🔧 Personalized technical questions
        - ⚡ Performance optimization
        """)
        
        # Supported Technologies
        st.subheader("🛠️ Supported Technologies")
        
        for category, techs in config.TECH_CATEGORIES.items():
            with st.expander(f"{category.replace('_', ' ').title()} ({len(techs)})"):
                cols = st.columns(2)
                for i, tech in enumerate(techs):
                    cols[i % 2].markdown(f"• {tech}")
        
        st.markdown("---")
        
        # Footer
        st.caption("© 2025 TalentScout Inc. All rights reserved.")
        st.caption("For support: support@talentscout.com")

def main():
    """Main application function with enhanced features."""
    try:
        # Initialize session
        init_session()
        
        # Display sidebar
        display_sidebar()
        
        # Main content area
        st.markdown("<h1 style='text-align: center;'>🎯 TalentScout Hiring Assistant</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px; color: #666;'>AI-Powered Candidate Screening with Advanced Analytics</p>", unsafe_allow_html=True)
    
        # Main content columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Chat interface
            try:
                display_chat()
            except Exception as e:
                st.error(f"Chat error: {str(e)}")
                st.info("Please refresh the page to continue.")
        
        with col2:
            # Analytics and Summary Panel
            try:
                if st.session_state.show_analytics:
                    display_advanced_analytics()
                
                if "show_summary" in st.session_state and st.session_state.show_summary:
                    display_candidate_summary()
                
                # Sentiment Alert
                if "conversation_manager" in st.session_state:
                    candidate_data = st.session_state.conversation_manager.candidate_data
                    if ("sentiment_history" in candidate_data and 
                        any(item.get("emotion") in ["anger", "fear", "sadness"] and item.get("score", 0) > 0.7 
                            for item in candidate_data.get("sentiment_history", []))):
                        st.warning("⚠️ **Candidate Alert:** Strong negative emotions detected. Consider supportive approach.")
            except Exception as e:
                st.warning(f"Analytics error: {str(e)}")
        
        # Full-width analytics (when enabled)
        if st.session_state.show_analytics:
            st.markdown("---")
            try:
                display_advanced_analytics()
            except Exception as e:
                st.warning(f"Full analytics error: {str(e)}")
                
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page to restart the application.")
        st.stop()

if __name__ == "__main__":
    main() 