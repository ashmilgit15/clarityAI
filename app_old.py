import streamlit as st
from groq import Groq
import json
import re

# Page configuration
st.set_page_config(
    page_title="Clarity: Your Wellness Companion",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern UI Styling inspired by Google AI Studio
st.markdown("""
<style>
    /* Global styles */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --accent-color: #667eea;
        --bg-light: #f8f9fa;
        --text-dark: #1a1a1a;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .main-header {
        background: var(--primary-gradient);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    
    /* User message specific */
    [data-testid="stChatMessageContent"] {
        background: transparent;
    }
    
    /* Chat input */
    .stChatInputContainer {
        background: white;
        border-radius: 24px;
        padding: 0.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    .stChatInput input {
        border-radius: 20px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 1rem;
        transition: border-color 0.3s;
    }
    
    .stChatInput input:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: white;
        box-shadow: 4px 0 16px rgba(0,0,0,0.08);
    }
    
    [data-testid="stSidebar"] .stButton button {
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: var(--accent-color) !important;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
    }
    
    /* Caption text */
    .caption {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem;
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
    # Try to find JSON in the response
    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return None

# Helper function to format response
def format_response(response_text):
    """Format the response, handling JSON if present"""
    json_data = extract_json_from_response(response_text)
    if json_data:
        # Display JSON in a formatted way
        return json.dumps(json_data, indent=2)
    return response_text

# Create centered container for chat
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # Modern UI Header
    st.markdown("""
    <div class="main-header">
        <h1>🧘 Clarity</h1>
        <p>Your AI Wellness Companion</p>
    </div>
    """, unsafe_allow_html=True)

# Display chat history in center column
with col2:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Check if it's JSON and format accordingly
            content = message["content"]
            json_data = extract_json_from_response(content)
            if json_data:
                st.json(json_data)
            else:
                st.markdown(content)

# Chat input in center column
with col2:
    if prompt := st.chat_input("Share what's on your mind..."):
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
                    
                    # Format and display response
                    formatted_response = format_response(assistant_response)
                    json_data = extract_json_from_response(assistant_response)
                    
                    if json_data:
                        st.json(json_data)
                    else:
                        st.markdown(formatted_response)
                    
                    # Add assistant response to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                    
                except Exception as e:
                    error_msg = "I'm having trouble connecting right now. Please try again in a moment."
                    st.error(error_msg)
                    st.error(f"Debug info: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

# Modern Sidebar
with st.sidebar:
    # Sidebar header with gradient
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
    ">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">✨ Clarity</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.9rem;">Powered by Groq AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clear conversation button
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
        ">
            <p style="color: white; margin: 0; font-weight: 600; font-size: 0.9rem;">
                💬 Messages: {len(st.session_state.messages)}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # About section
    with st.expander("ℹ️ About Clarity", expanded=False):
        st.markdown("""
        Clarity is your AI wellness companion designed to provide:
        
        - 🧘 **Emotional Support**
        - 💭 **Stress Relief**
        - 🌟 **Mental Clarity**
        
        *Remember: I'm not a replacement for professional mental health care.*
        """)
    
    # Crisis resources
    with st.expander("🆘 Crisis Resources", expanded=False):
        st.markdown("""
        **If you're in crisis, please reach out:**
        
        - 🇺🇸 **US**: Call/Text **988**  
          (National Suicide Prevention Lifeline)
        
        - 🌍 **International**: [findahelpline.com](https://findahelpline.com)
        
        - 🚨 **Emergency**: Call local emergency services
        """)
    
    # Tips section
    with st.expander("💡 Tips for Best Experience", expanded=False):
        st.markdown("""
        - Share your feelings openly and honestly
        - Use informal language or emojis
        - Ask for breathing exercises or coping strategies
        - Type 'reset' to start a new conversation
        """)
    
    st.divider()
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 1rem; color: #888; font-size: 0.8rem;">
        Made with ❤️ for your wellbeing
    </div>
    """, unsafe_allow_html=True)