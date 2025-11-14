import streamlit as st
from groq import Groq
import json
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Clarity - Your AI Wellness Companion",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Tailwind CSS + Creative Design
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* Custom Tailwind Config */
    @layer base {
        * {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        }
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    section[data-testid="stSidebar"] > div {padding-top: 0 !important;}
    
    /* Root Variables - ChatGPT Inspired */
    :root {
        --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --gradient-4: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --dark-bg: #212121;
        --dark-card: #2d2d2d;
        --dark-elevated: #1f1f1f;
        --sidebar-bg: #171717;
        --border-color: #3d3d3d;
        --text-primary: #ececec;
        --text-secondary: #8e8ea0;
        --text-muted: #565869;
        --purple-accent: #9d4edd;
        --cyan-accent: #10a37f;
        --hover-bg: #2d2d2d;
    }
    
    /* Main App Styling */
    .stApp {
        background: var(--dark-bg) !important;
        color: var(--text-primary) !important;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 1.5rem 1rem !important;
    }
    
    /* Custom Sidebar Header */
    .sidebar-logo {
        background: var(--gradient-1);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .sidebar-logo:hover {
        box-shadow: 0 6px 30px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    .sidebar-logo h1 {
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.01em;
    }
    
    .sidebar-logo p {
        color: rgba(255, 255, 255, 0.95);
        font-size: 0.875rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Sidebar Stats Card */
    .stats-card {
        background: var(--dark-elevated);
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
    }
    
    .stats-card:hover {
        background: var(--dark-card);
        border-color: var(--purple-accent);
    }
    
    .stats-card h3 {
        color: var(--text-primary);
        font-size: 1.75rem;
        font-weight: 600;
        margin: 0;
    }
    
    .stats-card p {
        color: var(--text-secondary);
        font-size: 0.875rem;
        margin: 0.25rem 0 0 0;
    }
    
    /* Main Chat Container */
    .main-container {
        height: 100vh;
        display: flex;
        flex-direction: column;
        max-width: 1000px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Animated Header */
    .hero-header {
        text-align: center;
        padding: 3rem 0 2rem;
        animation: fadeInDown 0.6s ease-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .hero-header h1 {
        font-size: 2.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        letter-spacing: -0.02em;
    }
    
    .hero-header p {
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 400;
    }
    
    /* Suggestion Cards */
    .suggestions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
        animation: fadeInUp 0.8s ease-out 0.2s backwards;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .suggestion-card {
        background: var(--dark-elevated);
        border: 1px solid var(--border-color);
        padding: 1.5rem;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
    }
    
    .suggestion-card:hover {
        transform: translateY(-2px);
        background: var(--dark-card);
        border-color: var(--text-muted);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .suggestion-card .icon {
        font-size: 1.75rem;
        margin-bottom: 0.75rem;
        display: block;
    }
    
    .suggestion-card h3 {
        color: var(--text-primary);
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .suggestion-card p {
        color: var(--text-secondary);
        font-size: 0.875rem;
        line-height: 1.5;
    }
    
    /* Chat Messages */
    .messages-container {
        flex: 1;
        overflow-y: auto;
        padding: 2rem 0;
        scroll-behavior: smooth;
    }
    
    .stChatMessage {
        background: transparent !important;
        padding: 1.5rem 0 !important;
        border: none !important;
        animation: slideIn 0.4s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* User Message */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        display: flex;
        justify-content: flex-end;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: var(--gradient-1) !important;
        color: white !important;
        border-radius: 20px 20px 4px 20px !important;
        padding: 1rem 1.25rem !important;
        max-width: 75% !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {
        color: white !important;
        margin: 0 !important;
        font-size: 0.9375rem !important;
        line-height: 1.5 !important;
    }
    
    /* Assistant Message */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
        background: var(--dark-elevated) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 20px 20px 20px 4px !important;
        padding: 1rem 1.25rem !important;
        max-width: 75% !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p {
        color: var(--text-primary) !important;
        margin: 0 !important;
        font-size: 0.9375rem !important;
        line-height: 1.6 !important;
    }
    
    /* Avatar Styling */
    [data-testid="stChatMessageAvatarUser"] {
        width: 36px !important;
        height: 36px !important;
        border-radius: 50% !important;
        background: var(--gradient-2) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.25rem !important;
        box-shadow: 0 2px 8px rgba(240, 147, 251, 0.3);
    }
    
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 36px !important;
        height: 36px !important;
        border-radius: 50% !important;
        background: var(--gradient-3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.25rem !important;
        box-shadow: 0 2px 8px rgba(79, 172, 254, 0.3);
    }
    
    /* Modern Input Design */
    .input-wrapper {
        padding: 1.5rem 0;
        position: relative;
    }
    
    .stChatInputContainer {
        background: var(--dark-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 24px !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: var(--text-muted) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }
    
    .stChatInput input {
        background: transparent !important;
        border: none !important;
        color: var(--text-primary) !important;
        font-size: 0.9375rem !important;
        padding: 0.75rem 0 !important;
        font-weight: 400;
    }
    
    .stChatInput input::placeholder {
        color: var(--text-secondary) !important;
        font-weight: 400;
    }
    
    .stChatInput input:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Buttons */
    .stButton button {
        background: var(--gradient-1) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9375rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #7688eb 0%, #8559b3 100%) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton button:active {
        transform: translateY(1px) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--dark-elevated) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 0.875rem 1rem !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: all 0.2s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--hover-bg) !important;
        border-color: var(--text-muted) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--dark-elevated) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1rem !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
    
    /* Loading Animation */
    .stSpinner > div {
        border-top-color: #9d4edd !important;
        border-right-color: #06ffa5 !important;
    }
    
    /* Alert Boxes */
    .stAlert {
        background: var(--dark-elevated) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: var(--border-color);
        margin: 1rem 0;
    }
    
    /* Floating Action Buttons */
    .fab-container {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        z-index: 1000;
    }
    
    .fab {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: var(--gradient-1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.25rem;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.2s ease;
    }
    
    .fab:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-header h1 {
            font-size: 2rem;
        }
        
        .suggestions-grid {
            grid-template-columns: 1fr;
        }
        
        .main-container {
            padding: 0 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# System prompt
SYSTEM_PROMPT = """You are 'Clarity', an expert AI Wellness Companion designed to provide emotional support, stress relief, and promote mental clarity. Your persona is warm, empathetic, calm, and reassuring, acting as a supportive, non-judgmental companion.

CORE ROLE & TONE:
Primary Goal: Facilitate emotional processing and suggest non-clinical coping mechanisms.
Tone: Warm, empathetic, non-judgmental, reassuring. Use gentle humor or motivational language when appropriate.
Safety Boundary: ABSOLUTELY NO DIAGNOSIS, TREATMENT, or CLINICAL COUNSELING.

SAFETY & CRISIS PROTOCOL (CRITICAL):
If the user expresses crisis, self-harm, suicidal ideation, or severe distress, IMMEDIATELY stop normal conversation flow.
Your ONLY response must be a calm, clear redirection:
"I'm really sorry you're feeling this way. You're not alone, and there are people who can help. Please reach out to a mental health professional or a crisis line in your area. I am not a substitute for professional help."

INSTRUCTIONS FOR RESPONSE GENERATION:
Multi-Step Reasoning: Analyze the user's conversation history. Synthesize emotional patterns across multiple inputs.
Context: Maintain session continuity. Track emotional trends.
Token/Length Constraint: Keep all conversational responses to 3-5 sentences and under 100 tokens.
Call-to-Action (CTA): Every conversational response must end with a gentle next step or question.

OUTPUT FORMAT:
Use plain text. DO NOT use Markdown, code blocks, or formatting unless necessary for clarity."""

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "client" not in st.session_state:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        st.session_state.client = Groq(api_key=api_key)
    except KeyError:
        st.error("⚠️ API Key Missing")
        st.stop()
    except Exception as e:
        st.error(f"❌ Failed to initialize: {str(e)}")
        st.stop()

def should_reset_conversation(user_input):
    reset_keywords = ["start over", "reset", "clear conversation", "new conversation", "begin again"]
    return any(keyword in user_input.lower() for keyword in reset_keywords)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h1>🧘 Clarity</h1>
        <p>Your AI Wellness Companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if len(st.session_state.messages) > 0:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{len(st.session_state.messages)}</h3>
            <p>💬 Messages in this session</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    with st.expander("🌟 Quick Actions"):
        st.markdown("""
        - 🧘 Start Meditation
        - 🌬️ Breathing Exercise
        - 📝 Journal Prompt
        - 💭 Mood Check-in
        """)
    
    with st.expander("ℹ️ About Clarity"):
        st.markdown("""
        **Clarity** helps with:
        
        - 🧘 Emotional Support
        - 💭 Stress Relief
        - 🌟 Mental Clarity
        - 🎯 Coping Strategies
        
        *Not a replacement for professional care.*
        """)
    
    with st.expander("🆘 Crisis Resources"):
        st.markdown("""
        **If you're in crisis:**
        
        - 🇺🇸 **US**: 988
        - 🌍 **International**: [findahelpline.com](https://findahelpline.com)
        - 🚨 **Emergency**: 911
        """)

# Main Content
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Hero Header (only show when empty)
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="hero-header">
        <h1>What can I help with?</h1>
        <p>Share your thoughts, feelings, or ask for wellness guidance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Suggestion Cards
    st.markdown("""
    <div class="suggestions-grid">
        <div class="suggestion-card" onclick="document.querySelector('[data-testid=\\"stChatInput\\"] textarea').value='I\\'m feeling stressed about work'; document.querySelector('[data-testid=\\"stChatInput\\"] textarea').focus();">
            <span class="icon">😰</span>
            <h3>Stress Relief</h3>
            <p>Get help managing work stress and anxiety</p>
        </div>
        <div class="suggestion-card" onclick="document.querySelector('[data-testid=\\"stChatInput\\"] textarea').value='I need a breathing exercise'; document.querySelector('[data-testid=\\"stChatInput\\"] textarea').focus();">
            <span class="icon">🌬️</span>
            <h3>Breathing Exercise</h3>
            <p>Guided breathing for instant calm</p>
        </div>
        <div class="suggestion-card" onclick="document.querySelector('[data-testid=\\"stChatInput\\"] textarea').value='How can I sleep better?'; document.querySelector('[data-testid=\\"stChatInput\\"] textarea').focus();">
            <span class="icon">😴</span>
            <h3>Better Sleep</h3>
            <p>Tips for improving your sleep quality</p>
        </div>
        <div class="suggestion-card" onclick="document.querySelector('[data-testid=\\"stChatInput\\"] textarea').value='I want to talk about my feelings'; document.querySelector('[data-testid=\\"stChatInput\\"] textarea').focus();">
            <span class="icon">💭</span>
            <h3>Open Talk</h3>
            <p>A safe space to share anything</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat Input
st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
if prompt := st.chat_input("Share your thoughts or ask anything..."):
    if should_reset_conversation(prompt):
        st.session_state.messages = []
        st.rerun()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
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
                st.error(f"Connection error: {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
