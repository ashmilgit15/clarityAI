import streamlit as st
from streamlit_oauth import OAuth2Component
from groq import Groq
import hashlib
import requests
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Page configuration
st.set_page_config(
    page_title="Clarity - Your AI Wellness Companion",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Firebase (only once)
if not firebase_admin._apps:
    try:
        if "firebase_credentials" in st.secrets:
            cred_dict = {
                "type": st.secrets["firebase_credentials"]["type"],
                "project_id": st.secrets["firebase_credentials"]["project_id"],
                "private_key_id": st.secrets["firebase_credentials"]["private_key_id"],
                "private_key": st.secrets["firebase_credentials"]["private_key"],
                "client_email": st.secrets["firebase_credentials"]["client_email"],
                "client_id": st.secrets["firebase_credentials"]["client_id"],
                "auth_uri": st.secrets["firebase_credentials"]["auth_uri"],
                "token_uri": st.secrets["firebase_credentials"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["firebase_credentials"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["firebase_credentials"]["client_x509_cert_url"],
            }
            if "universe_domain" in st.secrets["firebase_credentials"]:
                cred_dict["universe_domain"] = st.secrets["firebase_credentials"]["universe_domain"]
            cred = credentials.Certificate(cred_dict)
        else:
            cred_path = st.secrets.get("firebase_credentials_path", "firebase-credentials.json")
            cred = credentials.Certificate(cred_path)
        
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        st.error(f"Firebase initialization error: {str(e)}")
        st.info("Please complete Firebase setup")
        st.stop()
else:
    db = firestore.client()

# Comprehensive Redesign - Clarity UI/UX
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* === DESIGN SYSTEM: 8PX GRID & COLOR PALETTE === */
    :root {
        --bg-primary: #1E293B;
        --bg-secondary: #2A3A50;
        --bg-elevated: #334155;
        --text-primary: #F1F5F9;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --accent-teal: #4FD1C5;
        --accent-teal-hover: #38B2AC;
        --accent-coral: #F59E0B;
        --border-subtle: #475569;
        --spacing-unit: 8px;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu, footer, header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    /* === MAIN APP BACKGROUND === */
    .stApp {
        background: linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%) !important;
        min-height: 100vh;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: var(--bg-elevated) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding: calc(var(--spacing-unit) * 3) calc(var(--spacing-unit) * 2) !important;
    }
    
    /* Custom Clarity Logo */
    .clarity-logo {
        text-align: center;
        padding: calc(var(--spacing-unit) * 3) 0;
        margin-bottom: calc(var(--spacing-unit) * 3);
        border-bottom: 1px solid var(--border-subtle);
    }
    
    .clarity-logo-icon {
        width: 48px;
        height: 48px;
        margin: 0 auto 12px;
        background: linear-gradient(135deg, var(--accent-teal) 0%, var(--accent-teal-hover) 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 16px rgba(79, 209, 197, 0.25);
    }
    
    .clarity-logo-text {
        font-size: 20px;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }
    
    /* Sidebar Buttons */
    [data-testid="stSidebar"] .stButton button {
        background: transparent !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        min-height: 44px !important;
        width: 100% !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: var(--accent-teal) !important;
        border-color: var(--accent-teal) !important;
        transform: translateY(-1px);
    }
    
    /* === MAIN CHAT CONTAINER === */
    .main {
        background: transparent;
    }
    
    .chat-container {
        max-width: 768px;
        margin: 0 auto;
        padding: calc(var(--spacing-unit) * 4) calc(var(--spacing-unit) * 2);
    }
    
    /* === WELCOME SCREEN === */
    .welcome-hero {
        text-align: center;
        padding: calc(var(--spacing-unit) * 8) calc(var(--spacing-unit) * 2);
        max-width: 600px;
        margin: 0 auto;
    }
    
    .welcome-title {
        font-size: 36px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 16px;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    
    .welcome-subtitle {
        font-size: 18px;
        font-weight: 400;
        color: var(--text-secondary);
        margin-bottom: 48px;
        line-height: 1.5;
    }
    
    /* === CONVERSATION STARTERS === */
    .starters-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px;
        margin: calc(var(--spacing-unit) * 4) 0 calc(var(--spacing-unit) * 6);
        max-width: 768px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .starter-button {
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 20px;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .starter-button:hover {
        background: var(--accent-teal);
        border-color: var(--accent-teal);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(79, 209, 197, 0.2);
    }
    
    .starter-button:hover .starter-text {
        color: var(--bg-primary);
    }
    
    .starter-text {
        font-size: 15px;
        font-weight: 500;
        color: var(--text-primary);
        line-height: 1.4;
        transition: color 0.2s ease;
    }
    
    /* === CHAT MESSAGES === */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        padding: calc(var(--spacing-unit) * 2) 0 !important;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: var(--accent-teal) !important;
        color: var(--bg-primary) !important;
        border-radius: 16px 16px 4px 16px !important;
        padding: 16px 20px !important;
        max-width: 75% !important;
        margin-left: auto !important;
        font-size: 15px !important;
        line-height: 1.5 !important;
        box-shadow: 0 2px 8px rgba(79, 209, 197, 0.2);
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
        background: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 16px 16px 16px 4px !important;
        padding: 16px 20px !important;
        max-width: 75% !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
    }
    
    /* === CHAT INPUT === */
    .chat-input-container {
        position: sticky;
        bottom: 0;
        background: linear-gradient(to top, var(--bg-secondary) 0%, transparent 100%);
        padding: calc(var(--spacing-unit) * 3) calc(var(--spacing-unit) * 2);
        z-index: 100;
    }
    
    [data-testid="stChatInputContainer"] {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3) !important;
        max-width: 768px !important;
        margin: 0 auto !important;
    }
    
    .stChatInput textarea {
        background: transparent !important;
        border: none !important;
        color: var(--text-primary) !important;
        font-size: 15px !important;
        padding: 12px 16px !important;
        min-height: 52px !important;
        line-height: 1.5 !important;
    }
    
    .stChatInput textarea::placeholder {
        color: var(--text-secondary) !important;
    }
    
    .stChatInput textarea:focus {
        outline: none !important;
        box-shadow: 0 0 0 2px var(--accent-teal) inset !important;
        border-radius: 8px !important;
    }
    
    /* === AUTH SCREEN === */
    .auth-hero {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 80vh;
        padding: calc(var(--spacing-unit) * 4);
        text-align: center;
    }
    
    .auth-logo {
        width: 64px;
        height: 64px;
        margin: 0 auto 24px;
        background: linear-gradient(135deg, var(--accent-teal) 0%, var(--accent-teal-hover) 100%);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 32px rgba(79, 209, 197, 0.3);
    }
    
    .auth-title {
        font-size: 32px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 16px;
        letter-spacing: -0.02em;
    }
    
    .auth-subtitle {
        font-size: 16px;
        color: var(--text-secondary);
        margin-bottom: 48px;
        line-height: 1.5;
    }
    
    .auth-form {
        max-width: 400px;
        margin: 0 auto;
        width: 100%;
    }
    
    .stTextInput input {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        padding: 12px 16px !important;
        min-height: 48px !important;
        font-size: 15px !important;
    }
    
    .stTextInput input:focus {
        border-color: var(--accent-teal) !important;
        box-shadow: 0 0 0 3px rgba(79, 209, 197, 0.1) !important;
    }
    
    .stButton button[kind="primary"] {
        background: var(--accent-teal) !important;
        color: var(--bg-primary) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px 24px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        min-height: 48px !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button[kind="primary"]:hover {
        background: var(--accent-teal-hover) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(79, 209, 197, 0.3) !important;
    }
    
    /* === MOBILE RESPONSIVE === */
    @media (max-width: 768px) {
        .welcome-title {
            font-size: 28px;
        }
        
        .welcome-subtitle {
            font-size: 16px;
        }
        
        .starters-grid {
            grid-template-columns: 1fr;
            gap: 12px;
        }
        
        .starter-button {
            min-height: 80px;
            padding: 16px;
        }
        
        .chat-input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: calc(var(--spacing-unit) * 2);
            background: var(--bg-secondary);
        }
        
        .auth-title {
            font-size: 24px;
        }
        
        [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
            max-width: 90% !important;
        }
    }
    
    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-subtle);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
</style>
""", unsafe_allow_html=True)

# System prompt
SYSTEM_PROMPT = """You are 'Clarity', an expert AI Wellness Companion designed to provide emotional support, stress relief, and promote mental clarity. Your persona is warm, empathetic, calm, and reassuring."""

# Helper Functions
def create_user_in_firestore(user_id, email, name, photo_url):
    """Create user document in Firestore"""
    user_ref = db.collection('users').document(user_id)
    user_ref.set({
        'email': email,
        'name': name,
        'photo_url': photo_url,
        'created_at': firestore.SERVER_TIMESTAMP,
        'last_login': firestore.SERVER_TIMESTAMP
    }, merge=True)

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "client" not in st.session_state:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        st.session_state.client = Groq(api_key=api_key)
    except:
        st.error("⚠️ Groq API Key Missing")
        st.stop()

# Authentication Screen
def show_auth_screen():
    """Display beautiful, serene login screen"""
    st.markdown("""
    <div class="auth-hero">
        <div class="auth-logo">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #1E293B;">
                <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z"/>
                <circle cx="12" cy="12" r="3"/>
            </svg>
        </div>
        <h1 class="auth-title">Welcome to Clarity</h1>
        <p class="auth-subtitle">A quiet space for your thoughts</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-form">', unsafe_allow_html=True)
        
        login_email = st.text_input(
            "Email",
            placeholder="Enter your email address",
            key="login_email"
        )
        
        login_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        if st.button("Sign In", use_container_width=True, type="primary"):
            if login_email and login_password:
                user_id = hashlib.md5(login_email.encode()).hexdigest()
                
                st.session_state.user = {
                    'id': user_id,
                    'email': login_email,
                    'name': login_email.split('@')[0].capitalize(),
                    'photo_url': f"https://ui-avatars.com/api/?name={login_email.split('@')[0]}&background=4FD1C5&color=1E293B"
                }
                
                create_user_in_firestore(
                    user_id,
                    st.session_state.user['email'],
                    st.session_state.user['name'],
                    st.session_state.user['photo_url']
                )
                
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Main App
if st.session_state.user is None:
    show_auth_screen()
else:
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="clarity-logo">
            <div class="clarity-logo-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z"/>
                    <circle cx="12" cy="12" r="3"/>
                </svg>
            </div>
            <div class="clarity-logo-text">Clarity</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ New Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()
    
    # Main Chat Area
    if len(st.session_state.messages) == 0:
        st.markdown(f"""
        <div class="welcome-hero">
            <h1 class="welcome-title">Find your calm</h1>
            <p class="welcome-subtitle">I'm here to listen. What's on your mind?</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Conversation Starters
        st.markdown('<div class="starters-grid">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        starters = [
            "Practice a 5-minute mindfulness exercise",
            "Help me calm my anxiety",
            "I want to improve my sleep",
            "Talk about my feelings"
        ]
        
        with col1:
            if st.button(starters[0], key="starter_1", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": starters[0]})
                st.rerun()
            if st.button(starters[2], key="starter_3", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": starters[2]})
                st.rerun()
        
        with col2:
            if st.button(starters[1], key="starter_2", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": starters[1]})
                st.rerun()
            if st.button(starters[3], key="starter_4", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": starters[3]})
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Display messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat Input - Sticky on mobile
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    if prompt := st.chat_input("Share what's on your mind..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner(""):
                try:
                    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                    for msg in st.session_state.messages:
                        messages.append({"role": msg["role"], "content": msg["content"]})
                    
                    response = st.session_state.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=200
                    )
                    assistant_response = response.choices[0].message.content
                    
                    st.markdown(assistant_response)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
