import streamlit as st
import google.generativeai as genai
import json
import re

# Page configuration
st.set_page_config(
    page_title="Clarity: Your Wellness Companion",
    page_icon="🧘",
    layout="centered",
    initial_sidebar_state="expanded"
)

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

if "chat" not in st.session_state:
    st.session_state.chat = None

if "model" not in st.session_state:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        st.session_state.model = genai.GenerativeModel(
            model_name="gemini-pro",
            system_instruction=SYSTEM_PROMPT
        )
        # Initialize chat session
        st.session_state.chat = st.session_state.model.start_chat(history=[])
    except KeyError:
        st.error("⚠️ **API Key Missing**: Please configure GEMINI_API_KEY in Streamlit secrets.")
        st.stop()
    except Exception as e:
        st.error(f"❌ **Failed to initialize Gemini API**: {str(e)}")
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

# UI Header
st.title("🧘 Clarity: Your Wellness Companion")
st.markdown("*A safe space for emotional support and mental clarity*")
st.divider()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Check if it's JSON and format accordingly
        content = message["content"]
        json_data = extract_json_from_response(content)
        if json_data:
            st.json(json_data)
        else:
            st.markdown(content)

# Chat input
if prompt := st.chat_input("Share what's on your mind..."):
    # Check for reset command
    if should_reset_conversation(prompt):
        st.session_state.messages = []
        st.session_state.chat = st.session_state.model.start_chat(history=[])
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
                # Send message to chat
                response = st.session_state.chat.send_message(prompt)
                assistant_response = response.text
                
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

# Sidebar with information
with st.sidebar:
    st.header("About Clarity")
    st.info(
        "Clarity is your AI wellness companion, here to provide emotional support "
        "and help you find mental clarity. Remember, I'm not a replacement for "
        "professional mental health care."
    )
    
    st.divider()
    
    st.header("Crisis Resources")
    st.warning(
        "**If you're in crisis:**\n\n"
        "🇺🇸 National Suicide Prevention Lifeline: **988**\n\n"
        "🌍 International: **findahelpline.com**"
    )
    
    st.divider()
    
    st.header("Conversation Tools")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat = st.session_state.model.start_chat(history=[])
        st.rerun()
    
    # Display conversation stats
    if len(st.session_state.messages) > 0:
        st.caption(f"**Messages**: {len(st.session_state.messages)}")
        st.caption("Type 'start over' or 'reset' to clear the conversation history.")
    
    st.divider()
    
    st.caption("💡 **Tip**: Clarity understands informal language, emojis, and emotional cues. Just share what's on your mind.")