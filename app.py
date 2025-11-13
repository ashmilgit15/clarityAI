import streamlit as st
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="Clarity: Your Wellness Companion",
    page_icon="🧘",
    layout="centered"
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

if "model" not in st.session_state:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        st.session_state.model = genai.GenerativeModel(
            model_name="gemini-pro",
            system_instruction=SYSTEM_PROMPT
        )
    except Exception as e:
        st.error(f"Failed to initialize Gemini API: {str(e)}")
        st.stop()

# UI Header
st.title("🧘 Clarity: Your Wellness Companion")
st.markdown("*A safe space for emotional support and mental clarity*")
st.divider()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Share what's on your mind..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Clarity is thinking..."):
            try:
                # Build conversation history for Gemini
                chat_history = []
                for msg in st.session_state.messages[:-1]:
                    chat_history.append({
                        "role": msg["role"],
                        "parts": [msg["content"]]
                    })
                
                # Start chat with history
                chat = st.session_state.model.start_chat(history=chat_history)
                
                # Get response
                response = chat.send_message(prompt)
                assistant_response = response.text
                
                # Display response
                st.markdown(assistant_response)
                
                # Add assistant response to history
                st.session_state.messages.append({
                    "role": "model",
                    "content": assistant_response
                })
                
            except Exception as e:
                error_msg = f"I'm having trouble connecting right now. Please try again in a moment."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "model",
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
    
    st.header("Crisis Resources")
    st.warning(
        "**If you're in crisis:**\n\n"
        "🇺🇸 National Suicide Prevention Lifeline: 988\n\n"
        "🌍 International: findahelpline.com"
    )
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
