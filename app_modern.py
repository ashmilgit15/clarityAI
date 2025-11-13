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
    
    /* Root Variables */
    :root {
        --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --gradient-4: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --dark-bg: #0f0f1e;
        --dark-card: #1a1a2e;
        --dark-elevated: #16213e;
        --purple-accent: #9d4edd;
        --cyan-accent: #06ffa5;
    }
    
    /* Main App Styling */
    .stApp {
        background: var(--dark-bg) !important;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1e 100%) !important;
        border-right: 1px solid rgba(157, 78, 221, 0.1) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: 1.5rem 1rem !important;
    }
    
    /* Custom Sidebar Header */
    .sidebar-logo {
        background: var(--gradient-1);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        animation: glow 3s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3); }
        50% { box-shadow: 0 12px 48px rgba(102, 126, 234, 0.5); }
    }
    
    .sidebar-logo h1 {
        color: white;
        font-size: 1.75rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .sidebar-logo p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.85rem;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* Sidebar Stats Card */
    .stats-card {
        background: var(--gradient-2);
        padding: 1.25rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(240, 147, 251, 0.3);
    }
    
    .stats-card h3 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .stats-card p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
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
        padding: 3rem 0;
        background: radial-gradient(circle at 50% 0%, rgba(157, 78, 221, 0.1) 0%, transparent 50%);
        animation: fadeInDown 0.8s ease-out;
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
        font-size: 3rem;
        font-weight: 800;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.3); }
    }
    
    .hero-header p {
        color: #a0a0b0;
        font-size: 1.2rem;
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
        background: var(--dark-card);
        border: 1px solid rgba(157, 78, 221, 0.2);
        padding: 1.5rem;
        border-radius: 16px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .suggestion-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--gradient-1);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .suggestion-card:hover {
        transform: translateY(-5px);
        border-color: rgba(157, 78, 221, 0.5);
        box-shadow: 0 12px 40px rgba(157, 78, 221, 0.3);
    }
    
    .suggestion-card:hover::before {
        opacity: 0.1;
    }
    
    .suggestion-card .icon {
        font-size: 2rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .suggestion-card h3 {
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .suggestion-card p {
        color: #a0a0b0;
        font-size: 0.9rem;
        line-height: 1.5;
        position: relative;
        z-index: 1;
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
        border-radius: 24px 24px 4px 24px !important;
        padding: 1.25rem 1.5rem !important;
        max-width: 75% !important;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {
        color: white !important;
        margin: 0 !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    /* Assistant Message */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
        background: var(--dark-card) !important;
        border: 1px solid rgba(157, 78, 221, 0.2) !important;
        border-radius: 24px 24px 24px 4px !important;
        padding: 1.25rem 1.5rem !important;
        max-width: 75% !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p {
        color: #e0e0e0 !important;
        margin: 0 !important;
        font-size: 1rem !important;
        line-height: 1.7 !important;
    }
    
    /* Avatar Styling */
    [data-testid="stChatMessageAvatarUser"] {
        width: 45px !important;
        height: 45px !important;
        border-radius: 50% !important;
        background: var(--gradient-2) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.5rem !important;
        box-shadow: 0 4px 20px rgba(240, 147, 251, 0.4);
    }
    
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 45px !important;
        height: 45px !important;
        border-radius: 50% !important;
        background: var(--gradient-3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.5rem !important;
        box-shadow: 0 4px 20px rgba(79, 172, 254, 0.4);
    }
    
    /* Modern Input Design */
    .input-wrapper {
        padding: 2rem 0;
        position: relative;
    }
    
    .stChatInputContainer {
        background: var(--dark-card) !important;
        border: 2px solid rgba(157, 78, 221, 0.3) !important;
        border-radius: 28px !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }
    
    .stChatInputContainer::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: var(--gradient-1);
        border-radius: 28px;
        opacity: 0;
        transition: opacity 0.3s;
        z-index: -1;
    }
    
    .stChatInputContainer:focus-within {
        border-color: transparent !important;
        box-shadow: 0 8px 40px rgba(157, 78, 221, 0.4) !important;
        transform: translateY(-2px);
    }
    
    .stChatInputContainer:focus-within::before {
        opacity: 1;
    }
    
    .stChatInput input {
        background: transparent !important;
        border: none !important;
        color: white !important;
        font-size: 1rem !important;
        padding: 0.75rem 0 !important;
        font-weight: 400;
    }
    
    .stChatInput input::placeholder {
        color: #6b6b7b !important;
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
        border-radius: 16px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        letter-spacing: 0.02em;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.5) !important;
    }
    
    .stButton button:active {
        transform: translateY(0) scale(1) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--dark-card) !important;
        border: 1px solid rgba(157, 78, 221, 0.2) !important;
        border-radius: 12px !important;
        padding: 1rem 1.25rem !important;
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(157, 78, 221, 0.5) !important;
        background: var(--dark-elevated) !important;
        transform: translateX(5px);
    }
    
    .streamlit-expanderContent {
        background: var(--dark-card) !important;
        border: 1px solid rgba(157, 78, 221, 0.2) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1.25rem !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--dark-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #764ba2, #667eea);
    }
    
    /* Loading Animation */
    .stSpinner > div {
        border-top-color: #9d4edd !important;
        border-right-color: #06ffa5 !important;
    }
    
    /* Alert Boxes */
    .stAlert {
        background: var(--dark-card) !important;
        border: 1px solid rgba(157, 78, 221, 0.3) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(157, 78, 221, 0.5), transparent);
        margin: 1.5rem 0;
    }
    
    /* Floating Action Buttons */
    .fab-container {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        z-index: 1000;
    }
    
    .fab {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: var(--gradient-1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .fab:hover {
        transform: scale(1.1) rotate(10deg);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6);
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
