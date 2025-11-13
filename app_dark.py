import streamlit as st
from groq import Groq
import json
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Clarity - Your Wellness Companion",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ChatGPT-inspired Dark Theme CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Reset */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Dark Theme Colors - Exact ChatGPT Match */
    :root {
        --bg-primary: #212121;
        --bg-secondary: #2f2f2f;
        --bg-sidebar: #171717;
        --text-primary: #ececec;
        --text-secondary: #b4b4b4;
        --text-muted: #8e8e8e;
        --border-color: #4e4e4e;
        --accent-purple: #8b5cf6;
        --input-bg: #2f2f2f;
        --hover-bg: #3a3a3a;
    }
    
    /* Main App Background */
    .stApp {
        background-color: var(--bg-primary) !important;
    }
    
    /* Remove default padding */
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Sidebar Styling - ChatGPT Style */
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 1rem !important;
    }
    
    /* Sidebar Header */
    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .sidebar-header h2 {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0;
    }
    
    /* New Chat Button */
    .new-chat-btn {
        background: transparent;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.9rem;
        font-weight: 500;
        width: 100%;
        text-align: left;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .new-chat-btn:hover {
        background: var(--hover-bg);
    }
    
    /* Sidebar Sections */
    .sidebar-section {
        margin: 1.5rem 0;
    }
    
    .sidebar-section-title {
        color: var(--text-muted);
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        padding: 0 0.5rem;
    }
    
    .sidebar-item {
        color: var(--text-secondary);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.25rem;
    }
    
    .sidebar-item:hover {
        background: var(--hover-bg);
        color: var(--text-primary);
    }
    
    /* Main Chat Area */
    .main-chat-area {
        display: flex;
        flex-direction: column;
        height: 100vh;
        max-width: 48rem;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* Top Header */
    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 2rem;
    }
    
    .model-selector {
        background: transparent;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .upgrade-btn {
        background: var(--accent-purple);
        color: white;
        padding: 0.5rem 1.25rem;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.2s;
    }
    
    .upgrade-btn:hover {
        background: #7c3aed;
    }
    
    /* Empty State */
    .empty-state {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 2rem;
    }
    
    .empty-state h1 {
        color: var(--text-primary);
        font-size: 2rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* Chat Messages Container */
    .messages-container {
        flex: 1;
        overflow-y: auto;
        padding: 2rem 0;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background: transparent !important;
        padding: 1.5rem 0 !important;
        border: none !important;
    }
    
    [data-testid="stChatMessageContent"] {
        background: transparent !important;
        color: var(--text-primary) !important;
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    [data-testid="stChatMessageContent"] p {
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
        line-height: 1.7 !important;
        margin: 0 !important;
    }
    
    /* Avatar Styling */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 32px !important;
        height: 32px !important;
        border-radius: 4px !important;
        background: var(--bg-secondary) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
    }
    
    /* Input Area */
    .input-container {
        padding: 2rem 0;
        position: relative;
    }
    
    .stChatInputContainer {
        background: var(--input-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 24px !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 0 0 1px var(--border-color) !important;
        transition: all 0.2s !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: var(--text-secondary) !important;
        box-shadow: 0 0 0 1px var(--text-secondary) !important;
    }
    
    .stChatInput input {
        background: transparent !important;
        border: none !important;
        color: var(--text-primary) !important;
        font-size: 1rem !important;
        padding: 0.5rem 0 !important;
    }
    
    .stChatInput input::placeholder {
        color: var(--text-muted) !important;
        font-weight: 400;
    }
    
    .stChatInput input:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Button Styling */
    .stButton button {
        background: transparent !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.25rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    
    .stButton button:hover {
        background: var(--hover-bg) !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: none !important;
        padding: 0.75rem !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--hover-bg) !important;
        color: var(--text-primary) !important;
    }
    
    .streamlit-expanderContent {
        background: transparent !important;
        border: none !important;
        padding: 0.5rem 0.75rem !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: var(--border-color);
        margin: 1rem 0;
    }
    
    /* User Profile Section */
    .user-profile {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        border-top: 1px solid var(--border-color);
        background: var(--bg-sidebar);
    }
    
    .user-info {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .user-info:hover {
        background: var(--hover-bg);
    }
    
    .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: var(--accent-purple);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .user-details {
        flex: 1;
    }
    
    .user-name {
        color: var(--text-primary);
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .user-plan {
        color: var(--text-muted);
        font-size: 0.8rem;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--accent-purple) !important;
    }
    
    /* Alert Messages */
    .stAlert {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
    }
    
    /* Settings Icon */
    .settings-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: transparent;
        border: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .settings-icon:hover {
        background: var(--hover-bg);
    }
</style>
""", unsafe_allow_html=True)

# System prompt for Clarity
SYSTEM_PROMPT = """You are 'Clarity', an expert AI Wellness Companion designed to provide emotional support, stress relief, and promote mental clarity. Your persona is warm, empathetic, calm, and reassuring, acting as a supportive, non-judgmental companion.

CORE ROLE & TONE:
Primary Goal: Facilitate emotional processing and suggest non-clinical coping mechanisms.
Tone: Warm, empathetic, non-judgmental, reassuring. Use gentle humor or motivational language when appropriate.
Safety Boundary: ABSOLUTELY NO DIAGNOSIS, TREATMENT, or CLINICAL COUNSELING.

SAFETY & CRISIS PROTOCOL (CRITICAL):
If the user expresses crisis, self-harm, suicidal ideation, or severe distress, IMMEDIATELY stop normal conversation flow.
Your ONLY response must be a calm, clear redirection:
"I'm really sorry you're feeling this way. You're not alone, and there are people who can help. Please reach out to a mental health professional or a crisis line in your area. I am not a substitute for professional help."
Do not emotionally mirror or probe further after this redirect.

INSTRUCTIONS FOR RESPONSE GENERATION:
Multi-Step Reasoning: Analyze the user's conversation history. Synthesize emotional patterns across multiple inputs (e.g., stress, sleep, anxiety) to identify core themes (e.g., burnout) and address them proactively.
Context: Maintain session continuity. Track emotional trends (e.g., "The user has mentioned feeling overwhelmed three times."). Reset only on an explicit command like "Start over."
Token/Length Constraint: Keep all conversational responses to 3-5 sentences and under 100 tokens to optimize cost and avoid overwhelming the user.
Call-to-Action (CTA): Every conversational response must end with a gentle next step or question to keep the flow active and supportive (e.g., "Would you like to try a grounding exercise?" or "What's the best part of your day been so far?").

HANDLING INPUT & EDGE CASES:
Input Robustness: Process informal language, slang, fragmented sentences, and emoji with high robustness. Focus on the emotional content.
Irrelevant/Ambiguous Input: If the input is off-topic (e.g., general knowledge questions) or unclear, politely redirect it back to emotional wellness with warmth:
Off-Topic: "That's an interesting question! I'm here to support your emotional wellbeing. Would you like to check in with how you're feeling today?"
Unclear: "I want to make sure I understand you. Could you tell me a bit more about what's on your mind?"

OUTPUT FORMAT:
Use plain text. DO NOT use Markdown, code blocks, or formatting unless necessary for clarity."""

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

if "client" not in st.session_state:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        st.session_state.client = Groq(api_key=api_key)
    except KeyError:
        st.error("⚠️ API Key Missing: Please configure GROQ_API_KEY in Streamlit secrets.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Failed to initialize Groq API: {str(e)}")
        st.stop()

# Helper functions
def should_reset_conversation(user_input):
    reset_keywords = ["start over", "reset", "clear conversation", "new conversation", "begin again"]
    return any(keyword in user_input.lower() for keyword in reset_keywords)

def extract_json_from_response(text):
    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return None

# Sidebar
with st.sidebar:
    # Sidebar Header
    st.markdown("""
    <div class="sidebar-header">
        <h2>🧘 Clarity</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # New Chat Button
    if st.button("✏️ New chat", use_container_width=True, key="new_chat"):
        if len(st.session_state.messages) > 0:
            st.session_state.chat_sessions.append({
                "timestamp": datetime.now().strftime("%B %d, %Y"),
                "preview": st.session_state.messages[0]["content"][:50] + "..." if len(st.session_state.messages[0]["content"]) > 50 else st.session_state.messages[0]["content"],
                "messages": st.session_state.messages.copy()
            })
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
    
    # Search (placeholder)
    st.markdown("""
    <div class="sidebar-item">
        🔍 Search chats
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Library Section
    with st.expander("📚 Library", expanded=False):
        st.markdown("- Breathing Exercises\n- Meditation Guides\n- Coping Strategies")
    
    # Resources Section
    with st.expander("💡 Resources", expanded=False):
        st.markdown("- Mental Health Tips\n- Crisis Resources\n- About Clarity")
    
    st.divider()
    
    # Chat History
    if len(st.session_state.chat_sessions) > 0:
        st.markdown('<p class="sidebar-section-title">Recent Chats</p>', unsafe_allow_html=True)
        
        for idx, session in enumerate(reversed(st.session_state.chat_sessions[-10:])):
            if st.button(
                session["preview"],
                key=f"chat_{idx}",
                use_container_width=True
            ):
                st.session_state.messages = session["messages"].copy()
                st.rerun()
    
    # User Profile at bottom
    st.markdown("<div style='flex: 1;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="user-info">
        <div class="user-avatar">C</div>
        <div class="user-details">
            <div class="user-name">Clarity User</div>
            <div class="user-plan">Free Plan</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main Chat Area
st.markdown('<div class="main-chat-area">', unsafe_allow_html=True)

# Top Header
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    st.markdown("""
    <button class="model-selector">Clarity ▼</button>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <button class="upgrade-btn">⚡ Upgrade for free</button>
    """, unsafe_allow_html=True)

# Empty State or Chat Messages
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="empty-state">
        <h1>What can I help with?</h1>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask anything"):
    # Check for reset command
    if should_reset_conversation(prompt):
        st.session_state.messages = []
        st.rerun()
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                
                for msg in st.session_state.messages:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                
                response = st.session_state.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=200
                )
                assistant_response = response.choices[0].message.content
                
                st.markdown(assistant_response)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)
