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

# Dark Theme CSS with Fixed Colors
st.markdown("""
<style>
    /* Global dark theme styling */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: #0f172a !important;
        color: #e2e8f0 !important;
    }
    
    /* Main container styling */
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 1rem;
        max-width: 1000px;
        background-color: #0f172a !important;
    }
    
    /* Header styling */
    .main-header {
        background: #1e293b;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #f1f5f9;
        text-align: center;
        border: 1px solid #334155;
    }
    
    .main-header h1 {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: #f1f5f9 !important;
    }
    
    .main-header p {
        font-size: 0.9rem;
        margin-bottom: 0;
        color: #cbd5e1 !important;
    }
    
    /* Chat message styling */
    .stChatMessage {
        margin-bottom: 0.5rem;
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        background: #3b82f6 !important;
        color: #ffffff !important;
        padding: 0.75rem !important;
        margin-left: 10% !important;
        border: 1px solid #2563eb !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        padding: 0.75rem !important;
        margin-right: 10% !important;
        border-left: 3px solid #3b82f6 !important;
        border: 1px solid #334155 !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: #3b82f6 !important;
        height: 6px !important;
    }
    
    .stProgress > div > div {
        background: #334155 !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        padding: 1rem !important;
        min-width: 250px;
        max-width: 280px;
        border-right: 1px solid #334155 !important;
    }
    
    .sidebar-section {
        background: #0f172a;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #334155;
        color: #e2e8f0 !important;
    }
    
    .sidebar-section h3, .sidebar-section h4, .sidebar-section h5 {
        color: #f1f5f9 !important;
        font-weight: 600;
        margin-bottom: 0.5rem;
        margin-top: 0;
        font-size: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: #3b82f6 !important;
        color: #ffffff !important;
        border: 1px solid #2563eb !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.875rem !important;
        width: 100% !important;
        margin-bottom: 0.25rem !important;
    }
    
    .stButton > button:hover {
        background: #2563eb !important;
        color: #ffffff !important;
    }
    
    /* Language selector styling */
    .language-selector {
        background: #0f172a;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #334155;
        color: #e2e8f0 !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: #0f172a !important;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #334155;
        color: #e2e8f0 !important;
    }
    
    .metric-card h4 {
        color: #f1f5f9 !important;
        margin-bottom: 0.5rem;
    }
    
    /* Status indicators */
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 4px;
        display: inline-block;
    }
    
    .status-active { background-color: #10b981; }
    .status-warning { background-color: #f59e0b; }
    .status-error { background-color: #ef4444; }
    
    /* Interview stage indicator */
    .stage-indicator {
        background: #3b82f6;
        color: #ffffff;
        padding: 0.25rem 0.5rem;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 0.5rem;
        border: 1px solid #2563eb;
    }
    
    /* Analytics cards */
    .analytics-card {
        background: #0f172a !important;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #3b82f6;
        border: 1px solid #334155;
        color: #e2e8f0 !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
        padding: 0.5rem !important;
        font-size: 0.875rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        background: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div > div {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
    }
    
    .stSelectbox label {
        color: #e2e8f0 !important;
    }
    
    /* Text and label colors - CRITICAL FIX */
    .stMarkdown, .stText, p, span, div {
        color: #e2e8f0 !important;
    }
    
    label {
        color: #e2e8f0 !important;
    }
    
    /* Metric styling */
    .stMetric {
        background: #1e293b !important;
        padding: 1rem !important;
        border: 1px solid #334155 !important;
    }
    
    .stMetric label {
        color: #cbd5e1 !important;
    }
    
    .stMetric [data-testid="metric-value"] {
        color: #f1f5f9 !important;
    }
    
    .stMetric [data-testid="metric-delta"] {
        color: #94a3b8 !important;
    }
    
    /* Expander styling */
    .stExpander {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
    }
    
    .stExpander > div > div > div > div {
        color: #e2e8f0 !important;
    }
    
    .stExpander summary {
        color: #f1f5f9 !important;
    }
    
    /* Tab styling for dark theme */
    .stTabs [data-baseweb="tab-list"] {
        background: #1e293b !important;
        border-bottom: 1px solid #334155 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #0f172a !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        margin-right: 2px !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #1e293b !important;
        color: #f1f5f9 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: #ffffff !important;
        border-color: #2563eb !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background: #0f172a !important;
        color: #e2e8f0 !important;
        padding: 1rem !important;
    }
    
    /* Caption and small text */
    .stCaption {
        color: #94a3b8 !important;
    }
    
    /* Success/Error messages */
    .success-message {
        background: #064e3b;
        color: #6ee7b7;
        padding: 0.75rem;
        border-left: 3px solid #10b981;
        margin: 0.5rem 0;
        border: 1px solid #065f46;
    }
    
    .error-message {
        background: #7f1d1d;
        color: #fca5a5;
        padding: 0.75rem;
        border-left: 3px solid #ef4444;
        margin: 0.5rem 0;
        border: 1px solid #991b1b;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #475569;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    /* Loading animation */
    .loading-spinner {
        border: 2px solid #334155;
        border-top: 2px solid #3b82f6;
        border-radius: 50%;
        width: 16px;
        height: 16px;
        animation: spin 1s linear infinite;
        display: inline-block;
        margin-right: 8px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Fix for Streamlit elements */
    .stApp > div {
        background-color: #0f172a !important;
    }
    
    /* Chat input styling */
    .stChatInput > div > div > div > div {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
    }
    
    .stChatInput input {
        background: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    /* Additional text color fixes */
    .stDataFrame {
        background: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    .stDataFrame table {
        background: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    .stDataFrame th {
        background: #334155 !important;
        color: #f1f5f9 !important;
    }
    
    .stDataFrame td {
        background: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    /* JSON display */
    .stJson {
        background: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    /* Code blocks */
    .stCode {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
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
        if st.button("Apply", type="secondary"):
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
    """Display enhanced sidebar with all new features and modern UI."""
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.title("🎯 " + config.APP_TITLE)
        st.caption(config.APP_DESCRIPTION)
        st.markdown('</div>', unsafe_allow_html=True)
        # Language Selection
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🌍 Language Selection")
        from utils.language_manager import LanguageManager
        lang_manager = LanguageManager()
        supported_languages = lang_manager.get_supported_languages()
        languages = {code: f"{info['flag']} {info['native_name']} ({info['name']})" for code, info in supported_languages.items()}
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_lang = st.selectbox(
                "Choose your preferred language:",
                options=list(languages.keys()),
                format_func=lambda x: languages[x],
                index=list(languages.keys()).index(st.session_state.selected_language)
            )
        with col2:
            if st.button("🌐 Apply", key="apply_language_btn"):
                if selected_lang != st.session_state.selected_language:
                    st.session_state.selected_language = selected_lang
                    conversation_manager = st.session_state.conversation_manager
                    conversation_manager.update_language(selected_lang)
                    st.success(f"Language changed to {languages[selected_lang]}")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        # Conversation Progress
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        if "conversation_manager" in st.session_state:
            display_conversation_progress()
        st.markdown('</div>', unsafe_allow_html=True)
        # Quick Actions
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### ⚡ Quick Actions")
        # Modern buttons with icons
        if st.button("📊 Show Analytics"):
            st.session_state.show_analytics = not st.session_state.show_analytics
        if st.button("🔄 Reset Chat"):
            if "conversation_manager" in st.session_state:
                st.session_state.conversation_manager.reset_conversation()
            st.session_state.messages = []
            st.session_state.show_analytics = False
            conversation_manager = st.session_state.conversation_manager
            initial_message = conversation_manager.process_message("Hello")
            st.session_state.messages.append({"role": "assistant", "content": initial_message})
            st.rerun()
        if st.button("👤 Toggle Summary"):
            if "show_summary" not in st.session_state:
                st.session_state.show_summary = True
            else:
                st.session_state.show_summary = not st.session_state.show_summary
        st.markdown('</div>', unsafe_allow_html=True)
        # About Section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)
        # Supported Technologies
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.subheader("🛠️ Supported Technologies")
        for category, techs in config.TECH_CATEGORIES.items():
            with st.expander(f"{category.replace('_', ' ').title()} ({len(techs)})"):
                cols = st.columns(2)
                for i, tech in enumerate(techs):
                    cols[i % 2].markdown(f"• {tech}")
        st.markdown('</div>', unsafe_allow_html=True)
        # Footer
        st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
        st.caption("© 2025 TalentScout Inc. All rights reserved.")
        st.caption("For support: support@talentscout.com")
        st.markdown('</div>', unsafe_allow_html=True)

def display_enhanced_sidebar():
    """Display enhanced sidebar with modern design."""
    with st.sidebar:
        # App title and description
        st.markdown("""
        <div class="sidebar-section">
            <h3>🎯 TalentScout</h3>
            <p style="color: #bdc3c7; font-size: 0.9rem;">
                AI-Powered Hiring Assistant with Advanced Analytics
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Language Selection
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🌍 Language")
        
        from utils.language_manager import LanguageManager
        lang_manager = LanguageManager()
        supported_languages = lang_manager.get_supported_languages()
        languages = {code: f"{info['flag']} {info['native_name']}" for code, info in supported_languages.items()}
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_lang = st.selectbox(
                "Language:",
                options=list(languages.keys()),
                format_func=lambda x: languages[x],
                index=list(languages.keys()).index(st.session_state.selected_language),
                label_visibility="collapsed"
            )
        with col2:
            if st.button("🌐", help="Apply Language"):
                if selected_lang != st.session_state.selected_language:
                    st.session_state.selected_language = selected_lang
                    conversation_manager = st.session_state.conversation_manager
                    conversation_manager.update_language(selected_lang)
                    st.success("✅ Language updated!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Interview Progress
        if "conversation_manager" in st.session_state:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("### 📊 Progress")
            
            cm = st.session_state.conversation_manager
            analytics = cm.get_conversation_analytics()
            
            # Progress bar
            progress = analytics['completion_percentage'] / 100
            st.progress(progress)
            st.caption(f"Interview {analytics['completion_percentage']:.0f}% complete")
            
            # Current stage
            stage_name = analytics['stage_name'].replace('_', ' ').title()
            st.markdown(f"**Current:** {stage_name}")
            
            # Message count
            st.markdown(f"**Messages:** {analytics['conversation_length']}")
            
            # Technical Questions Progress
            if 'technical_questions' in cm.candidate_data:
                total_questions = len(cm.candidate_data['technical_questions'])
                answered_questions = len(cm.candidate_data.get('technical_answers', []))
                st.markdown(f"**Questions:** {answered_questions}/{total_questions}")
                
                # Question limits info
                import config
                st.caption(f"Limit: {config.MIN_TECHNICAL_QUESTIONS}-{config.MAX_TECHNICAL_QUESTIONS} questions")
            elif analytics['stage_name'] == 'technical_questions':
                import config
                st.markdown(f"**Questions:** Generating...")
                st.caption(f"Limit: {config.MIN_TECHNICAL_QUESTIONS}-{config.MAX_TECHNICAL_QUESTIONS} questions")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### ⚡ Actions")
        
        if st.button("📊 Toggle Analytics"):
            st.session_state.show_analytics = not st.session_state.get('show_analytics', False)
            st.rerun()
        
        if st.button("🔄 Reset Interview"):
            if "conversation_manager" in st.session_state:
                st.session_state.conversation_manager.reset_conversation()
            st.session_state.messages = []
            st.session_state.show_analytics = False
            conversation_manager = st.session_state.conversation_manager
            initial_message = conversation_manager.process_message("Hello")
            st.session_state.messages.append({"role": "assistant", "content": initial_message})
            st.rerun()
        
        if st.button("💾 Export Data"):
            if "conversation_manager" in st.session_state:
                summary = st.session_state.conversation_manager.get_candidate_summary()
                st.download_button(
                    label="📥 Download JSON",
                    data=str(summary),
                    file_name=f"candidate_data_{st.session_state.session_id[:8]}.json",
                    mime="application/json"
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # System Status
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🔧 System Status")
        
        # Check system components
        status_items = [
            ("🤖 LLM Router", "active"),
            ("🌍 Language Manager", "active"),
            ("💭 Sentiment Analysis", "warning"),
            ("📊 Analytics", "active"),
            ("💾 Data Storage", "active")
        ]
        
        for item, status in status_items:
            status_color = {"active": "#2ecc71", "warning": "#f39c12", "error": "#e74c3c"}[status]
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span class="status-indicator" style="background-color: {status_color};"></span>
                <span style="color: #ecf0f1; font-size: 0.9rem;">{item}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Test Inputs - For Development/Testing (Collapsed by default)
        with st.expander("🧪 Quick Test Inputs", expanded=False):
            display_quick_test_inputs()
        
        # About
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### ℹ️ About")
        st.markdown("""
        <div style="color: #bdc3c7; font-size: 0.85rem; line-height: 1.4;">
            <strong>Features:</strong><br>
            • 🌍 21+ Languages<br>
            • 🧠 Smart Data Extraction<br>
            • 😊 Sentiment Analysis<br>
            • 💻 Tech Stack Matching<br>
            • 📊 Real-time Analytics<br>
            • 🔧 Advanced Prompting
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def display_enhanced_header():
    """Display enhanced header with modern design."""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 TalentScout Hiring Assistant</h1>
        <p>AI-Powered Candidate Screening with Advanced Analytics & Multilingual Support</p>
    </div>
    """, unsafe_allow_html=True)

def display_interview_status():
    """Display current interview status and progress."""
    # Removed progress bar and stage indicator from main page
    pass

def display_enhanced_chat():
    """Display enhanced chat interface with better styling."""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display interview status
    display_interview_status()
    
    # Chat messages
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
    
    placeholder_text = f"Type your message in {lang_name}... 💬"
    
    if prompt := st.chat_input(placeholder_text):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get conversation manager
        conversation_manager = st.session_state.conversation_manager
        
        # Process message with loading indicator
        with st.spinner("🤖 TalentScout is analyzing your response..."):
            response = conversation_manager.process_message(prompt)
            
            # Add bot response to chat
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Force UI refresh
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_quick_test_inputs():
    """Display quick test inputs for easy testing."""
    st.markdown("### 🧪 Quick Test Inputs")
    st.markdown("*Click any button to quickly test the chatbot:*")
    
    test_inputs = {
        "👋 Start Interview": "Hello, I'd like to start the interview",
        "📝 Provide Name": "My name is John Smith",
        "📧 Contact Info": "My email is john.smith@example.com and phone is +1-555-123-4567",
        "💼 Experience": "I have 5 years of experience in software development",
        "🎯 Position": "I'm looking for a Senior Software Engineer position",
        "📍 Location": "New York, USA",
        "💻 Tech Stack": "I work with Python, JavaScript, React, Django, PostgreSQL, and AWS",
        "🔧 Technical Answer": "I would use React hooks like useState and useEffect to manage component state and side effects",
        "🌍 Spanish Test": "Hola, mi nombre es Carlos Rodriguez. Tengo 4 años de experiencia en desarrollo web",
        "🇫🇷 French Test": "Bonjour, je m'appelle Pierre Dubois et j'ai 6 ans d'expérience en développement logiciel"
    }
    
    cols = st.columns(2)
    for i, (label, message) in enumerate(test_inputs.items()):
        with cols[i % 2]:
            if st.button(label, key=f"test_{i}"):
                # Add user message
                st.session_state.messages.append({"role": "user", "content": message})
                
                # Process message
                conversation_manager = st.session_state.conversation_manager
                response = conversation_manager.process_message(message)
                
                # Add bot response
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                st.rerun()

def display_enhanced_analytics():
    """Display enhanced analytics with better visualization."""
    if "conversation_manager" not in st.session_state:
        return
    
    cm = st.session_state.conversation_manager
    analytics = cm.get_conversation_analytics()
    
    st.markdown("## 📊 Interview Analytics")
    
    # Key metrics using Streamlit metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        stage_name = analytics['stage_name'].replace('_', ' ').title()
        st.metric("📋 Current Stage", stage_name)
    
    with col2:
        st.metric("💬 Messages", analytics['conversation_length'])
    
    with col3:
        current_lang = analytics['language'].upper()
        st.metric("🌍 Language", current_lang)
    
    with col4:
        completion = analytics['completion_percentage']
        st.metric("✅ Progress", f"{completion:.0f}%")
    
    # Progress bar
    st.markdown("### 📈 Interview Progress")
    st.progress(completion / 100)
    
    # Stage details
    st.markdown("### 🔄 Stage Information")
    stage_descriptions = {
        'greeting': '👋 Initial greeting and introduction',
        'name': '📝 Collecting candidate name',
        'contact_info': '📧 Gathering contact information', 
        'experience': '💼 Discussing work experience',
        'position': '🎯 Understanding desired position',
        'location': '📍 Confirming location details',
        'tech_stack': '💻 Exploring technical skills',
        'technical_questions': '🔧 Technical assessment',
        'farewell': '👋 Interview conclusion',
        'complete': '✅ Interview completed'
    }
    
    current_stage_key = analytics['stage_name']
    stage_description = stage_descriptions.get(current_stage_key, 'Unknown stage')
    st.info(f"**Current Stage:** {stage_description}")
    
    # Collected information with better organization
    if analytics.get('collected_fields'):
        st.markdown("### 📝 Collected Information")
        candidate_data = cm.candidate_data
        
        # Personal Information Section
        personal_info = []
        if 'name' in analytics['collected_fields'] and candidate_data.get('name'):
            personal_info.append(('👤 **Name**', candidate_data.get('name')))
        if 'email' in analytics['collected_fields'] and candidate_data.get('email'):
            personal_info.append(('📧 **Email**', candidate_data.get('email')))
        if 'phone' in analytics['collected_fields'] and candidate_data.get('phone'):
            personal_info.append(('📱 **Phone**', candidate_data.get('phone')))
        if 'location' in analytics['collected_fields'] and candidate_data.get('location'):
            personal_info.append(('📍 **Location**', candidate_data.get('location')))
        
        # Professional Information Section
        professional_info = []
        if 'years_experience' in analytics['collected_fields'] and candidate_data.get('years_experience'):
            professional_info.append(('💼 **Experience**', f"{candidate_data.get('years_experience')} years"))
        if 'position' in analytics['collected_fields'] and candidate_data.get('position'):
            professional_info.append(('🎯 **Position**', candidate_data.get('position')))
        
        # Technical Information Section
        technical_info = []
        if 'tech_stack' in analytics['collected_fields'] and candidate_data.get('tech_stack'):
            tech_stack = candidate_data.get('tech_stack', [])
            if tech_stack:
                technical_info.append(('💻 **Tech Stack**', ', '.join(tech_stack)))
        
        # Display sections with better formatting
        if personal_info or professional_info or technical_info:
            col1, col2 = st.columns(2)
            
            with col1:
                if personal_info:
                    st.markdown("**👤 Personal Details**")
                    for label, value in personal_info:
                        st.markdown(f"{label}: {value}")
                    
                if professional_info:
                    st.markdown("")  # Add spacing
                    st.markdown("**💼 Professional Details**")
                    for label, value in professional_info:
                        st.markdown(f"{label}: {value}")
            
            with col2:
                if technical_info:
                    st.markdown("**💻 Technical Skills**")
                    for label, value in technical_info:
                        # Format tech stack as bullet points for better readability
                        if label.startswith('💻'):
                            tech_list = value.split(', ')
                            st.markdown(f"{label}:")
                            for tech in tech_list:
                                st.markdown(f"• {tech}")
                        else:
                            st.markdown(f"{label}: {value}")
        else:
            st.info("No information collected yet. Start the interview to see candidate details here.")

def main():
    """Enhanced main application function with modern UI."""
    try:
        # Initialize session
        init_session()
        
        # Display enhanced header
        display_enhanced_header()
        
        # Main layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Enhanced chat interface
            try:
                display_enhanced_chat()
            except Exception as e:
                st.error(f"💥 Chat Error: {str(e)}")
                st.info("🔄 Please refresh the page to continue.")
        
        with col2:
            # Enhanced sidebar content
            display_enhanced_sidebar()
            

            # Analytics
            if st.session_state.get('show_analytics', False):
                with st.expander("📊 Analytics", expanded=True):
                    display_enhanced_analytics()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
            🚀 TalentScout Hiring Assistant v2.0 
        </div>
        """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"💥 Application Error: {str(e)}")
        st.info("🔄 Please refresh the page to restart the application.")
        st.stop()

if __name__ == "__main__":
    main() 