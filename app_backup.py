import streamlit as st
from groq import Groq
import json
import re

# Page configuration
st.set_page_config(
    page_title="Clarity - AI Wellness Companion",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Tailwind CSS + Custom Modern Styling
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Reset & Variables */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #8b5cf6;
        --success: #10b981;
        --danger: #ef4444;
        --bg-main: #f9fafb;
        --bg-card: #ffffff;
        --text-primary: #111827;
        --text-secondary: #6b7280;
        --border-color: #e5e7eb;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-main: #0f172a;
            --bg-card: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --border-color: #334155;
        }
    }
    
    /* Hide Streamlit Elements */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main App Background */
    .stApp {
        background: var(--bg-main);
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Header Styling */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-xl);
        animation: slideDown 0.5s ease-out;
    }
    
    .app-header h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .app-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Chat Container */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* Chat Messages - Complete Redesign */
    .stChatMessage {
        background: transparent !important;
        padding: 1rem 0 !important;
        border: none !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* User Message */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        display: flex;
        justify-content: flex-end;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 20px 20px 4px 20px !important;
        padding: 1rem 1.25rem !important;
        max-width: 75% !important;
        box-shadow: var(--shadow-md);
        animation: slideInRight 0.3s ease-out;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {
        color: white !important;
        margin: 0 !important;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Assistant Message */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 20px 20px 20px 4px !important;
        padding: 1rem 1.25rem !important;
        max-width: 75% !important;
        box-shadow: var(--shadow-sm);
        animation: slideInLeft 0.3s ease-out;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p {
        color: var(--text-primary) !important;
        margin: 0 !important;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    
    /* Avatar Styling */
    [data-testid="stChatMessageAvatarUser"], 
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.25rem !important;
        box-shadow: var(--shadow-md);
    }
    
    [data-testid="stChatMessageAvatarUser"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
    }
    
    [data-testid="stChatMessageAvatarAssistant"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
    }
    
    /* Chat Input - Modern Design */
    .stChatInputContainer {
        background: var(--bg-card) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 28px !important;
        padding: 0.5rem 1rem !important;
        box-shadow: var(--shadow-lg) !important;
        transition: all 0.3s ease !important;
        margin-top: 2rem !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1), var(--shadow-xl) !important;
    }
    
    .stChatInput input {
        border: none !important;
        background: transparent !important;
        padding: 0.75rem 0.5rem !important;
        font-size: 0.95rem !important;
        color: var(--text-primary) !important;
    }
    
    .stChatInput input::placeholder {
        color: var(--text-secondary) !important;
        font-weight: 400;
    }
    
    .stChatInput input:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Sidebar Modern Design */
    [data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border-color) !important;
        box-shadow: var(--shadow-lg);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        padding: 1rem;
    }
    
    /* Button Styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
        box-shadow: var(--shadow-md);
        letter-spacing: 0.01em;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    .stButton button:active {
        transform: translateY(0) !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
        padding: 1rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--primary) !important;
        background: rgba(99, 102, 241, 0.05) !important;
    }
    
    .streamlit-expanderContent {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1rem !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--primary) !important;
    }
    
    /* Alert/Error boxes */
    .stAlert {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: var(--shadow-sm);
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: var(--border-color);
    }
    
    /* Animations */
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-main);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .app-header h1 {
            font-size: 1.5rem;
        }
        
        .chat-container {
            padding: 0 0.5rem;
        }
        
        [data-testid="stChatMessageContent"] {
            max-width: 90% !important;
        }
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

TOOL CALLS & STRUCTURED DATA:
Tool Usage: When the user explicitly requests an action (e.g., "Start meditation," "Set a reminder"), you MUST respond with only a structured JSON block. DO NOT include any conversational text with a tool call.
Tool Call Format Example: {"tool_call": "start_meditation", "duration": 5, "type": "guided", "theme": "anxiety relief"}
Structured Input/Output: If the user provides structured JSON input (e.g., survey data), you MUST respond with a structured JSON summary and suggested action.
Structured Output Example: {"summary": "User is experiencing high stress and poor sleep...", "suggested_action": "Offer a guided meditation..."}

OUTPUT FORMAT:
If a tool or structured output is required, use JSON only.
Otherwise, use plain text. DO NOT use Markdown, code blocks, or formatting unless necessary for clarity."""

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "client" not in st.session_state:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        st.session_state.client = Groq(api_key=api_key)
    except KeyError:
        st.error("⚠️ **API Key Missing**: Please configure GROQ_API_KEY in Streamlit secrets.")
        st.stop()
    except Exception as e:
        st.error(f"❌ **Failed to initialize Groq API**: {str(e)}")
        st.stop()

# Helper function to check for reset command
def should_reset_conversation(user_input):
    """Check if user wants to start over"""
    reset_keywords = ["start over", "reset", "clear conversation", "new conversation", "begin again"]
    return any(keyword in user_input.lower() for keyword in reset_keywords)

# Helper function to extract JSON from response
def extract_json_from_response(text):
    """Extract JSON block from response if present"""
    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return None

# Create centered container
col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    # Modern Header
    st.markdown("""
    <div class="app-header">
        <h1>🧘 Clarity</h1>
        <p>Your AI-powered wellness companion for emotional support and mental clarity</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            content = message["content"]
            json_data = extract_json_from_response(content)
            if json_data:
                st.json(json_data)
            else:
                st.markdown(content)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("How are you feeling today? Share what's on your mind..."):
        # Check for reset command
        if should_reset_conversation(prompt):
            st.session_state.messages = []
            st.rerun()
        
        # Check if user input is JSON
        user_json = None
        try:
            user_json = json.loads(prompt)
        except json.JSONDecodeError:
            pass
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            if user_json:
                st.json(user_json)
            else:
                st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Clarity is thinking..."):
                try:
                    # Build messages array with system prompt and history
                    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                    
                    # Add conversation history
                    for msg in st.session_state.messages:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    
                    # Send message to Groq
                    response = st.session_state.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=200
                    )
                    assistant_response = response.choices[0].message.content
                    
                    # Display response
                    json_data = extract_json_from_response(assistant_response)
                    if json_data:
                        st.json(json_data)
                    else:
                        st.markdown(assistant_response)
                    
                    # Add assistant response to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                    
                except Exception as e:
                    error_msg = "I'm having trouble connecting right now. Please try again in a moment."
                    st.error(error_msg)
                    st.caption(f"Debug: {str(e)}")

# Modern Sidebar
with st.sidebar:
    # Sidebar header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h2 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 700;">✨ Clarity</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;">Powered by Groq AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # New conversation button
    if st.button("🔄 New Conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Conversation stats
    if len(st.session_state.messages) > 0:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <p style="color: white; margin: 0; font-weight: 600; font-size: 0.9rem; text-align: center;">
                💬 {len(st.session_state.messages)} messages
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # About section
    with st.expander("ℹ️ About Clarity"):
        st.markdown("""
        **Clarity** is your AI wellness companion designed to provide:
        
        - 🧘 **Emotional Support** - A safe space to share your feelings
        - 💭 **Stress Relief** - Techniques and guidance for relaxation
        - 🌟 **Mental Clarity** - Help organizing thoughts and emotions
        
        *Note: I'm not a replacement for professional mental health care.*
        """)
    
    # Crisis resources
    with st.expander("🆘 Crisis Resources"):
        st.markdown("""
        **If you're in crisis, please reach out immediately:**
        
        - 🇺🇸 **US**: Call/Text **988**  
          (National Suicide Prevention Lifeline)
        
        - 🌍 **International**: [findahelpline.com](https://findahelpline.com)
        
        - 🚨 **Emergency**: Call 911 or local emergency services
        """)
    
    # Tips section
    with st.expander("💡 Usage Tips"):
        st.markdown("""
        **Get the most from Clarity:**
        
        - Be open and honest about your feelings
        - Use casual language or emojis 😊
        - Ask for breathing exercises or coping strategies
        - Type 'reset' to start a fresh conversation
        - Take breaks when needed
        """)
    
    st.divider()
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 1rem; color: #9ca3af; font-size: 0.75rem;">
        Made with ❤️ for your wellbeing<br/>
        <span style="font-size: 0.7rem;">© 2024 Clarity AI</span>
    </div>
    """, unsafe_allow_html=True)
