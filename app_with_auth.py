import streamlit as st
from streamlit_oauth import OAuth2Component
from groq import Groq
import json
import re
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth
import hashlib
import os
import requests

# Page configuration
st.set_page_config(
    page_title="Clarity - Your AI Wellness Companion",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Firebase (only once)
if not firebase_admin._apps:
    try:
        # Check if running on Streamlit Cloud (secrets has firebase_credentials section)
        if "firebase_credentials" in st.secrets:
            # Load from Streamlit Cloud secrets
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
            # Load from local file (development)
            cred_path = st.secrets.get("firebase_credentials_path", "firebase-credentials.json")
            cred = credentials.Certificate(cred_path)
        
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        st.error(f"Firebase initialization error: {str(e)}")
        st.info("Please complete Firebase setup. See FIREBASE_SETUP.md")
        st.stop()
else:
    db = firestore.client()

# Stylish Mobile-First Design with Beautiful Gradients
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * { 
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
        box-sizing: border-box;
    }
    
    #MainMenu, footer, header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    
    :root {
        --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --gradient-purple: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-pink: linear-gradient(135deg, #f857a6 0%, #ff5858 100%);
        --background: #0a0a1e;
        --surface: rgba(255, 255, 255, 0.05);
        --surface-hover: rgba(255, 255, 255, 0.1);
        --text-primary: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.7);
        --border: rgba(255, 255, 255, 0.1);
        --glow: rgba(102, 126, 234, 0.5);
    }
    
    /* Global Styles */
    .stApp { 
        background: var(--background) !important;
    }
    
    .block-container { 
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Mobile-First: Base mobile styles */
    @media (max-width: 768px) {
        .stApp {
            padding-bottom: 80px !important;
        }
    }
    
    /* ==========================================
       AUTH SCREEN - MOBILE RESPONSIVE
    ========================================== */
    .auth-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 1.5rem;
        background: radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.1) 0%, transparent 60%);
    }
    
    @media (max-width: 480px) {
        .auth-container {
            padding: 1rem;
        }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    /* ==========================================
       PROFESSIONAL SIDEBAR
    ========================================== */
    
    /* Stylish Sidebar with Glassmorphism */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 10, 30, 0.95) 0%, rgba(15, 15, 35, 0.98) 100%) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(102, 126, 234, 0.2) !important;
        box-shadow: 4px 0 24px rgba(102, 126, 234, 0.1) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding: 1.25rem !important;
    }
    
    /* Gorgeous User Profile Card with Gradient */
    .user-profile-card {
        background: var(--gradient-1);
        padding: 1.25rem;
        border-radius: 16px;
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .user-profile-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .user-profile-card:hover::before {
        opacity: 1;
    }
    
    .user-profile-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(102, 126, 234, 0.4);
    }
    
    .user-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid rgba(255, 255, 255, 0.9);
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        position: relative;
        z-index: 1;
    }
    
    .user-info {
        flex: 1;
        min-width: 0;
        position: relative;
        z-index: 1;
    }
    
    .user-name {
        font-size: 1rem;
        font-weight: 600;
        color: white;
        margin: 0 0 0.25rem 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .user-email {
        font-size: 0.8125rem;
        color: rgba(255, 255, 255, 0.9);
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    /* Stylish Gradient Buttons */
    [data-testid="stSidebar"] .stButton button {
        background: var(--surface) !important;
        color: white !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 12px !important;
        padding: 0.875rem 1.25rem !important;
        font-size: 0.9375rem !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        min-height: 48px !important;
        backdrop-filter: blur(10px) !important;
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stSidebar"] .stButton button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s ease;
    }
    
    [data-testid="stSidebar"] .stButton button:hover::before {
        left: 100%;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: var(--surface-hover) !important;
        border-color: rgba(102, 126, 234, 0.6) !important;
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }
    
    /* New Chat Button - Beautiful Gradient */
    [data-testid="stSidebar"] .stButton:first-of-type button {
        background: var(--gradient-1) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
    }
    
    [data-testid="stSidebar"] .stButton:first-of-type button:hover {
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.6);
        transform: translateY(-3px) scale(1.03);
    }
    
    /* Sign Out Button - Pink Gradient */
    [data-testid="stSidebar"] .stButton:last-of-type button {
        background: transparent !important;
        border-color: rgba(248, 87, 166, 0.4) !important;
        color: #f857a6 !important;
    }
    
    [data-testid="stSidebar"] .stButton:last-of-type button:hover {
        background: var(--gradient-pink) !important;
        border-color: transparent !important;
        color: white !important;
        box-shadow: 0 8px 24px rgba(248, 87, 166, 0.4);
    }
    
    /* Sidebar Elements */
    [data-testid="stSidebar"] hr {
        border-color: var(--border) !important;
        margin: 1rem 0 !important;
    }
    
    [data-testid="stSidebar"] h3 {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin: 1rem 0 0.75rem 0 !important;
    }
    
    /* ==========================================
       CHAT INTERFACE - MOBILE OPTIMIZED
    ========================================== */
    .stChatMessage {
        background: transparent !important;
        padding: 1rem 0.5rem !important;
    }
    
    /* User Messages - Beautiful Gradient */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: var(--gradient-1) !important;
        color: white !important;
        border-radius: 20px 20px 4px 20px !important;
        padding: 1rem 1.25rem !important;
        max-width: 85% !important;
        font-size: 0.9375rem !important;
        line-height: 1.6 !important;
        word-wrap: break-word !important;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        position: relative;
        animation: slideInRight 0.3s ease-out;
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
    
    /* Assistant Messages - Glassmorphism */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px 20px 20px 4px !important;
        padding: 1rem 1.25rem !important;
        max-width: 85% !important;
        font-size: 0.9375rem !important;
        line-height: 1.6 !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        animation: slideInLeft 0.3s ease-out;
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
    
    /* Stylish Chat Input with Gradient Border */
    .stChatInputContainer {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid transparent !important;
        background-image: linear-gradient(rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.05)), 
                          var(--gradient-1) !important;
        background-origin: border-box !important;
        background-clip: padding-box, border-box !important;
        border-radius: 28px !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }
    
    .stChatInputContainer:focus-within {
        background-image: linear-gradient(rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.08)), 
                          var(--gradient-1) !important;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3) !important;
        transform: translateY(-2px);
    }
    
    .stChatInput input {
        background: transparent !important;
        color: white !important;
        border: none !important;
        font-size: 1rem !important;
        min-height: 48px !important;
        font-weight: 400;
    }
    
    .stChatInput input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* ==========================================
       MOBILE RESPONSIVE
    ========================================== */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] > div:first-child {
            padding: 0.75rem !important;
        }
        
        .user-profile-card {
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .user-avatar {
            width: 40px;
            height: 40px;
        }
        
        [data-testid="stSidebar"] .stButton button {
            padding: 0.875rem 1rem !important;
            min-height: 48px !important;
        }
        
        [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
            max-width: 90% !important;
            font-size: 1rem !important;
        }
        
        .stChatInput input {
            font-size: 16px !important;
            min-height: 48px !important;
        }
    }
    
    @media (max-width: 480px) {
        .user-name {
            font-size: 0.875rem !important;
        }
        
        .user-email {
            font-size: 0.6875rem !important;
        }
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

def save_chat_to_firestore(user_id, messages):
    """Save chat session to Firestore"""
    if not messages:
        return
    
    chat_ref = db.collection('users').document(user_id).collection('chats').document()
    chat_ref.set({
        'messages': messages,
        'created_at': firestore.SERVER_TIMESTAMP,
        'updated_at': firestore.SERVER_TIMESTAMP,
        'message_count': len(messages)
    })
    return chat_ref.id

def load_user_chats(user_id, limit=10):
    """Load user's recent chats from Firestore"""
    chats_ref = db.collection('users').document(user_id).collection('chats')
    chats = chats_ref.order_by('updated_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
    
    chat_list = []
    for chat in chats:
        chat_data = chat.to_dict()
        chat_list.append({
            'id': chat.id,
            'messages': chat_data.get('messages', []),
            'created_at': chat_data.get('created_at'),
            'preview': chat_data['messages'][0]['content'][:50] + "..." if chat_data.get('messages') else "Empty chat"
        })
    return chat_list

def update_chat_in_firestore(user_id, chat_id, messages):
    """Update existing chat session"""
    chat_ref = db.collection('users').document(user_id).collection('chats').document(chat_id)
    chat_ref.update({
        'messages': messages,
        'updated_at': firestore.SERVER_TIMESTAMP,
        'message_count': len(messages)
    })

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "client" not in st.session_state:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        st.session_state.client = Groq(api_key=api_key)
    except:
        st.error("⚠️ Groq API Key Missing")
        st.stop()

# Real Google OAuth Sign-in
def show_auth_screen():
    """Display authentication screen with real Google OAuth"""
    # Add spacer to push content to center vertically
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Centered auth card and form
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem; animation: float 3s ease-in-out infinite;">🧘</div>
            <h1 style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                Welcome to Clarity
            </h1>
            <p style="color: rgba(255,255,255,0.6); font-size: 1.1rem; margin-bottom: 2rem;">
                Your AI-powered wellness companion
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; color: white; margin-bottom: 1.5rem;'>Sign in with Google</h3>", unsafe_allow_html=True)
        
        # Initialize OAuth component
        oauth2 = OAuth2Component(
            st.secrets["oauth"]["client_id"],
            st.secrets["oauth"]["client_secret"],
            "https://accounts.google.com/o/oauth2/v2/auth",
            "https://oauth2.googleapis.com/token",
            "https://oauth2.googleapis.com/token"
        )
        
        # Create OAuth button
        result = oauth2.authorize_button(
            name="Sign in with Google",
            redirect_uri=st.secrets["oauth"]["redirect_uri"],
            scope="openid email profile",
            key="google_oauth",
            extras_params={"prompt": "consent", "access_type": "offline"},
            use_container_width=True,
            pkce='S256',
        )
        
        # Handle OAuth callback
        if result and "token" in result:
            # Get user info from Google
            headers = {"Authorization": f"Bearer {result['token']['access_token']}"}
            user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers).json()
            
            # Create user ID from Google ID
            user_id = user_info.get("id", hashlib.md5(user_info["email"].encode()).hexdigest())
            
            # Store user info in session
            st.session_state.user = {
                'id': user_id,
                'email': user_info.get("email", ""),
                'name': user_info.get("name", "User"),
                'photo_url': user_info.get("picture", f"https://ui-avatars.com/api/?name={user_info.get('name', 'User')}&background=667eea&color=fff")
            }
            
            # Create user in Firestore
            create_user_in_firestore(
                user_id,
                st.session_state.user['email'],
                st.session_state.user['name'],
                st.session_state.user['photo_url']
            )
            
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.5); font-size: 0.9rem;'>🔒 Secure authentication with Google</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.5); font-size: 0.9rem;'>📱 Your chats are saved and synced across devices</p>", unsafe_allow_html=True)

# Main App (after authentication)
if st.session_state.user is None:
    show_auth_screen()
else:
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        # User Profile
        st.markdown(f"""
        <div class="user-profile-card">
            <img src="{user['photo_url']}" class="user-avatar" alt="User Avatar">
            <div class="user-info">
                <p class="user-name">{user['name']}</p>
                <p class="user-email">{user['email']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # New Chat Button
        if st.button("🔄 New Conversation", use_container_width=True):
            # Save current chat if it has messages
            if st.session_state.messages and st.session_state.current_chat_id:
                update_chat_in_firestore(user['id'], st.session_state.current_chat_id, st.session_state.messages)
            elif st.session_state.messages:
                st.session_state.current_chat_id = save_chat_to_firestore(user['id'], st.session_state.messages)
            
            # Clear for new chat
            st.session_state.messages = []
            st.session_state.current_chat_id = None
            st.rerun()
        
        st.divider()
        
        # Load chat history
        st.subheader("💬 Chat History")
        user_chats = load_user_chats(user['id'])
        
        if user_chats:
            for chat in user_chats:
                if st.button(chat['preview'], key=f"chat_{chat['id']}", use_container_width=True):
                    st.session_state.messages = chat['messages']
                    st.session_state.current_chat_id = chat['id']
                    st.rerun()
        else:
            st.caption("No chat history yet")
        
        st.divider()
        
        # Sign out
        if st.button("🚪 Sign Out", use_container_width=True):
            # Save current chat before signing out
            if st.session_state.messages:
                if st.session_state.current_chat_id:
                    update_chat_in_firestore(user['id'], st.session_state.current_chat_id, st.session_state.messages)
                else:
                    save_chat_to_firestore(user['id'], st.session_state.messages)
            
            st.session_state.user = None
            st.session_state.messages = []
            st.session_state.current_chat_id = None
            st.rerun()
    
    # Main Chat Area
    st.markdown('<div style="max-width: 900px; margin: 0 auto; padding: 2rem;">', unsafe_allow_html=True)
    
    if len(st.session_state.messages) == 0:
        st.markdown(f"""
        <div style="text-align: center; padding: 4rem 2rem;">
            <h1 style="font-size: 3rem; color: white; margin-bottom: 1rem;">
                Hello, {user['name']}! 👋
            </h1>
            <p style="font-size: 1.2rem; color: #a0a0b0;">
                How can I support your wellness journey today?
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat Input
    if prompt := st.chat_input("Share your thoughts..."):
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
                    
                    # Auto-save to Firestore
                    if st.session_state.current_chat_id:
                        update_chat_in_firestore(user['id'], st.session_state.current_chat_id, st.session_state.messages)
                    else:
                        st.session_state.current_chat_id = save_chat_to_firestore(user['id'], st.session_state.messages)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
