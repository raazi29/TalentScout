"""
TalentScout Hiring Assistant - Streamlit Application

A chatbot-based hiring assistant for initial candidate screening.
"""
import uuid
import streamlit as st
from utils.conversation import ConversationManager
import config

# Set page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="👨‍💼",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Add minimal CSS for spacing fixes only
st.markdown("""
<style>
    /* Fix padding and margins */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Fix message appearance */
    .stChatMessageContent {
        background-color: rgba(240, 242, 246, 0.1) !important;
    }
    
    /* Fix footer */
    footer {
        visibility: hidden;
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

def display_chat():
    """Display chat interface using Streamlit's built-in chat components."""
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get conversation manager
        conversation_manager = st.session_state.conversation_manager
        
        # Process message and get response
        with st.spinner("TalentScout is typing..."):
            response = conversation_manager.process_message(prompt)
            
            # Add bot response to chat
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Force UI refresh
        st.rerun()

def display_sidebar():
    """Display sidebar with information and controls."""
    with st.sidebar:
        st.title(config.APP_TITLE)
        st.caption(config.APP_DESCRIPTION)
        
        st.markdown("---")
        
        st.subheader("About TalentScout")
        st.markdown("""
        TalentScout is an AI-powered chatbot that assists in the initial screening of candidates for technical roles.
        
        The chatbot will:
        1. Collect your basic information
        2. Ask about your technical skills
        3. Pose relevant technical questions
        
        Your responses will be reviewed by the TalentScout team for potential opportunities.
        """)
        
        # Sentiment Analysis Section (if available)
        if "conversation_manager" in st.session_state and st.session_state.conversation_manager.sentiment_analysis_enabled:
            st.markdown("---")
            st.subheader("Interview Insights")
            
            # Check if we have sentiment data
            candidate_data = st.session_state.conversation_manager.candidate_data
            if "sentiment_history" in candidate_data and len(candidate_data["sentiment_history"]) > 0:
                # Get the latest emotion
                latest = candidate_data["sentiment_history"][-1]
                emotion = latest["emotion"]
                score = latest["score"]
                
                # Display emotion with appropriate emoji
                emotion_emojis = {
                    "joy": "😊",
                    "sadness": "😔",
                    "anger": "😠",
                    "fear": "😨",
                    "surprise": "😮",
                    "disgust": "😒",
                    "neutral": "😐"
                }
                
                emoji = emotion_emojis.get(emotion, "😐")
                
                # Only show if score is above threshold
                if score > 0.6:
                    st.markdown(f"**Current Mood:** {emoji} {emotion.capitalize()} ({score:.2f})")
                
                # Show emotional progression if we have enough data
                if len(candidate_data["sentiment_history"]) >= 3:
                    try:
                        import pandas as pd
                        import matplotlib.pyplot as plt
                        
                        # Extract emotions for chart
                        emotions_data = []
                        for item in candidate_data["sentiment_history"]:
                            emotions_data.append({
                                "emotion": item["emotion"],
                                "score": item["score"]
                            })
                        
                        # Create dataframe
                        df = pd.DataFrame(emotions_data)
                        
                        # Display as line chart if we have more than 3 data points
                        if len(df) > 3:
                            st.write("**Emotional Progression:**")
                            st.line_chart(df.groupby("emotion").size().reset_index(name="count"))
                    except Exception as e:
                        st.write("Could not display emotion chart")
        
        st.markdown("---")
        st.subheader("Supported Technologies")
        
        # Display tech categories from config in collapsible sections
        for category, techs in config.TECH_CATEGORIES.items():
            with st.expander(f"{category.replace('_', ' ').title()}"):
                for tech in techs:
                    st.markdown(f"- {tech}")
        
        st.markdown("---")
        
        # Reset button
        if st.button("Reset Conversation", type="primary", use_container_width=True):
            if "conversation_manager" in st.session_state:
                st.session_state.conversation_manager.reset_conversation()
            st.session_state.messages = []
            # Add initial greeting after reset
            conversation_manager = st.session_state.conversation_manager
            initial_message = conversation_manager.process_message("Hello")
            st.session_state.messages.append({"role": "assistant", "content": initial_message})
            st.rerun()
        
        # Footer
        st.markdown("---")
        st.caption("© 2025 TalentScout Inc. All rights reserved.")
        st.caption("For support, contact support@talentscout.com")

def main():
    """Main application function."""
    # Initialize session
    init_session()
    
    # Display sidebar
    display_sidebar()
    
    # Main content area
    st.markdown("<h2 style='text-align: center;'>Chat with TalentScout</h2>", unsafe_allow_html=True)
    
    # Display sentiment alert for recruiter if strong negative emotions detected
    if "conversation_manager" in st.session_state:
        candidate_data = st.session_state.conversation_manager.candidate_data
        if ("sentiment_history" in candidate_data and 
            any(item["emotion"] in ["anger", "fear", "sadness"] and item["score"] > 0.7 
                for item in candidate_data.get("sentiment_history", []))):
            st.warning("⚠️ Candidate may be experiencing stress or negative emotions. Consider a more supportive approach.")
    
    # Chat interface
    display_chat()

if __name__ == "__main__":
    main() 