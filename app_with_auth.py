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
        st.info("Please complete Firebase setup. See FIREBASE_SETUP.md")
        st.stop()
else:
    db = firestore.client()

# Professional ChatGPT-Style UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-sizing: border-box;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    /* Global Reset */
    .stApp { 
        background: #343541 !important;
    }
    
    .block-container { 
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* ==========================================
       SIDEBAR - ChatGPT Style
    ========================================== */
    [data-testid="stSidebar"] {
        background: #202123 !important;
        border-right: none !important;
        padding: 0 !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding: 0.5rem !important;
    }
    
    /* User Profile Section */
    .user-profile {
        padding: 0.75rem;
        margin: 0.5rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .user-profile:hover {
        background: rgba(255, 255, 255, 0.08);
    }
    
    .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 6px;
        object-fit: cover;
        flex-shrink: 0;
    }
    
    .user-info {
        flex: 1;
        min-width: 0;
        overflow: hidden;
    }
    
    .user-name {
        font-size: 0.875rem;
        font-weight: 600;
        color: #ececf1;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .user-email {
        font-size: 0.75rem;
        color: #8e8ea0;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Sidebar Buttons */
    [data-testid="stSidebar"] .stButton button {
        background: transparent !important;
        color: #ececf1 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 6px !important;
        padding: 0.625rem 0.75rem !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
        text-align: left !important;
        width: 100% !important;
        min-height: 42px !important;
        margin: 0.25rem 0 !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* New Chat Button */
    [data-testid="stSidebar"] .stButton:first-of-type button {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] .stButton:first-of-type button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Chat History */
    [data-testid="stSidebar"] h3 {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: #8e8ea0 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin: 1.5rem 0.75rem 0.5rem 0.75rem !important;
        padding: 0 !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
        margin: 0.75rem 0.5rem !important;
    }
    
    /* Sign Out Button */
    [data-testid="stSidebar"] .stButton:last-of-type button {
        color: #ef4444 !important;
        border-color: rgba(239, 68, 68, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .stButton:last-of-type button:hover {
        background: rgba(239, 68, 68, 0.1) !important;
        border-color: rgba(239, 68, 68, 0.5) !important;
    }
    
    /* ==========================================
       CHAT INTERFACE - ChatGPT Style
    ========================================== */
    
    /* Main Chat Container */
    .main {
        background: #343541;
    }
    
    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* User Messages */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background: #343541 !important;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: transparent !important;
        padding: 1.5rem 1rem !important;
        max-width: 48rem !important;
        margin: 0 auto !important;
        color: #ececf1 !important;
        font-size: 1rem !important;
        line-height: 1.75 !important;
        border: none !important;
        border-radius: 0 !important;
    }
    
    /* Assistant Messages */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background: #444654 !important;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
        background: transparent !important;
        padding: 1.5rem 1rem !important;
        max-width: 48rem !important;
        margin: 0 auto !important;
        color: #ececf1 !important;
        font-size: 1rem !important;
        line-height: 1.75 !important;
        border: none !important;
        border-radius: 0 !important;
    }
    
    /* Message Content Styling */
    [data-testid="stChatMessageContent"] p {
        margin: 0.5rem 0 !important;
        color: inherit !important;
    }
    
    /* Chat Input Container */
    [data-testid="stChatInputContainer"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        position: relative !important;
    }
    
    .stChatInput {
        max-width: 48rem !important;
        margin: 0 auto 1.5rem auto !important;
        padding: 0 1rem !important;
    }
    
    .stChatInput textarea {
        background: #40414f !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.75rem 3rem 0.75rem 1rem !important;
        font-size: 1rem !important;
        color: #ececf1 !important;
        min-height: 52px !important;
        max-height: 200px !important;
        resize: none !important;
        box-shadow: 0 0 0 0 transparent !important;
    }
    
    .stChatInput textarea:focus {
        border-color: rgba(255, 255, 255, 0.2) !important;
        outline: none !important;
        box-shadow: 0 0 0 0 transparent !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #8e8ea0 !important;
    }
    
    /* Send Button */
    .stChatInput button {
        background: transparent !important;
        border: none !important;
        color: #8e8ea0 !important;
        position: absolute !important;
        right: 0.5rem !important;
        bottom: 0.5rem !important;
    }
    
    .stChatInput button:hover {
        color: #ececf1 !important;
    }
    
    /* ==========================================
       WELCOME SCREEN
    ========================================== */
    .welcome-screen {
        max-width: 48rem;
        margin: 0 auto;
        padding: 4rem 1rem;
        text-align: center;
    }
    
    .welcome-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 600;
        color: #ececf1;
        margin-bottom: 0.5rem;
    }
    
    .welcome-subtitle {
        font-size: 1.125rem;
        color: #8e8ea0;
    }
    
    /* ==========================================
       AUTH SCREEN - PERFECTLY CENTERED
    ========================================== */
    .auth-container {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh !important;
        width: 100vw !important;
        padding: 2rem !important;
        background: #343541 !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        z-index: 10000 !important;
    }
    
    .auth-card {
        max-width: 420px;
        width: 100%;
        text-align: center;
        background: rgba(32, 33, 35, 0.8);
        backdrop-filter: blur(20px);
        padding: 3rem 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .auth-icon {
        font-size: 4.5rem;
        margin-bottom: 1.5rem;
        filter: drop-shadow(0 4px 12px rgba(102, 126, 234, 0.3));
    }
    
    .auth-title {
        font-size: 2.25rem;
        font-weight: 700;
        color: #ececf1;
        margin-bottom: 0.75rem;
        letter-spacing: -0.02em;
    }
    
    .auth-subtitle {
        font-size: 1.0625rem;
        color: #8e8ea0;
        margin-bottom: 2.5rem;
        line-height: 1.6;
    }
    
    /* ==========================================
       MOBILE MENU - Always Define
    ========================================== */
    
    /* Mobile Menu Button - Hidden by default */
    .mobile-menu-btn {
        display: none;
        position: fixed;
        top: 0.75rem;
        left: 0.75rem;
        z-index: 9999;
        width: 44px;
        height: 44px;
        background: #202123;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        cursor: pointer;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    .mobile-menu-btn:active {
        transform: scale(0.92);
        background: #2c2d30;
    }
    
    .mobile-menu-btn svg {
        width: 22px;
        height: 22px;
        stroke: #ececf1;
        stroke-width: 2.5;
        stroke-linecap: round;
        fill: none;
    }
    
    /* Sidebar Overlay */
    .sidebar-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.6);
        z-index: 9997;
        backdrop-filter: blur(4px);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .sidebar-overlay.active {
        display: block;
        opacity: 1;
    }
    
    /* ==========================================
       MOBILE RESPONSIVE
    ========================================== */
    
    @media (max-width: 768px) {
        /* Show Mobile Menu Button */
        .mobile-menu-btn {
            display: flex !important;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            position: fixed !important;
            left: -100% !important;
            top: 0 !important;
            height: 100vh !important;
            width: 80vw !important;
            max-width: 300px !important;
            z-index: 9998 !important;
            transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.6) !important;
        }
        
        [data-testid="stSidebar"][data-visible="true"] {
            left: 0 !important;
        }
        
        /* Main Content */
        .main {
            padding-top: 3.5rem !important;
        }
        
        .main .block-container {
            padding: 0 !important;
        }
        
        /* Chat Messages */
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"],
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
            padding: 1.25rem 1rem !important;
        }
        
        /* Chat Input */
        .stChatInput {
            padding: 0 0.75rem !important;
            margin-bottom: 1rem !important;
        }
        
        .stChatInput textarea {
            font-size: 16px !important;
        }
        
        /* Welcome Screen */
        .welcome-screen {
            padding: 3rem 1rem !important;
        }
        
        .welcome-title {
            font-size: 1.75rem !important;
        }
        
        .welcome-subtitle {
            font-size: 1rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .mobile-menu-btn {
            top: 0.5rem;
            left: 0.5rem;
        }
        
        [data-testid="stSidebar"] {
            width: 85vw !important;
        }
        
        .welcome-screen {
            padding: 2rem 0.75rem !important;
        }
        
        .welcome-icon, .auth-icon {
            font-size: 3rem !important;
        }
        
        .welcome-title, .auth-title {
            font-size: 1.5rem !important;
        }
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Mobile Menu Script - Enhanced with Better Initialization
st.markdown("""
<div class="mobile-menu-btn" id="mobileMenuBtn" onclick="toggleSidebar()">
    <svg viewBox="0 0 24 24">
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
    </svg>
</div>
<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<script>
// Toggle sidebar function
function toggleSidebar() {
    console.log('Toggle sidebar called');
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (!sidebar || !overlay) {
        console.error('Sidebar or overlay not found');
        return;
    }
    
    const isVisible = sidebar.getAttribute('data-visible') === 'true';
    
    if (isVisible) {
        sidebar.setAttribute('data-visible', 'false');
        overlay.classList.remove('active');
        console.log('Sidebar closed');
    } else {
        sidebar.setAttribute('data-visible', 'true');
        overlay.classList.add('active');
        console.log('Sidebar opened');
    }
}

// Initialize sidebar state
function initSidebar() {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    
    if (!sidebar) {
        setTimeout(initSidebar, 100);
        return;
    }
    
    if (window.innerWidth <= 768) {
        sidebar.setAttribute('data-visible', 'false');
        console.log('Mobile: Sidebar initialized as hidden');
    }
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSidebar);
} else {
    initSidebar();
}

// Also run after a short delay (for Streamlit's dynamic loading)
setTimeout(initSidebar, 500);

// Handle window resize
window.addEventListener('resize', () => {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (window.innerWidth > 768) {
        if (sidebar) sidebar.removeAttribute('data-visible');
        if (overlay) overlay.classList.remove('active');
    } else {
        if (sidebar && !sidebar.hasAttribute('data-visible')) {
            sidebar.setAttribute('data-visible', 'false');
        }
    }
});

// Close sidebar when clicking outside
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const menuBtn = document.getElementById('mobileMenuBtn');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebar && menuBtn && sidebar.getAttribute('data-visible') === 'true') {
            const clickedInside = sidebar.contains(e.target) || menuBtn.contains(e.target);
            
            if (!clickedInside) {
                sidebar.setAttribute('data-visible', 'false');
                if (overlay) overlay.classList.remove('active');
            }
        }
    }
});
</script>
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

# Authentication Screen
def show_auth_screen():
    """Display authentication screen"""
    st.markdown("""
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-icon">🧘</div>
            <h1 class="auth-title">Welcome to Clarity</h1>
            <p class="auth-subtitle">Your AI-powered wellness companion</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
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
            extras_params={"access_type": "offline"},
            use_container_width=True,
            pkce='S256',
        )
        
        # Handle OAuth callback
        if result and "token" in result:
            headers = {"Authorization": f"Bearer {result['token']['access_token']}"}
            user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers).json()
            
            user_id = user_info.get("id", hashlib.md5(user_info["email"].encode()).hexdigest())
            
            st.session_state.user = {
                'id': user_id,
                'email': user_info.get("email", ""),
                'name': user_info.get("name", "User"),
                'photo_url': user_info.get("picture", f"https://ui-avatars.com/api/?name={user_info.get('name', 'User')}&background=667eea&color=fff")
            }
            
            create_user_in_firestore(
                user_id,
                st.session_state.user['email'],
                st.session_state.user['name'],
                st.session_state.user['photo_url']
            )
            
            st.rerun()

# Main App
if st.session_state.user is None:
    show_auth_screen()
else:
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        # User Profile
        st.markdown(f"""
        <div class="user-profile">
            <img src="{user['photo_url']}" class="user-avatar" alt="Avatar">
            <div class="user-info">
                <p class="user-name">{user['name']}</p>
                <p class="user-email">{user['email']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # New Chat Button
        if st.button("➕ New chat", use_container_width=True):
            if st.session_state.messages and st.session_state.current_chat_id:
                update_chat_in_firestore(user['id'], st.session_state.current_chat_id, st.session_state.messages)
            elif st.session_state.messages:
                st.session_state.current_chat_id = save_chat_to_firestore(user['id'], st.session_state.messages)
            
            st.session_state.messages = []
            st.session_state.current_chat_id = None
            st.rerun()
        
        st.divider()
        
        # Chat History
        st.subheader("Recent Chats")
        user_chats = load_user_chats(user['id'])
        
        if user_chats:
            for chat in user_chats:
                if st.button(chat['preview'], key=f"chat_{chat['id']}", use_container_width=True):
                    st.session_state.messages = chat['messages']
                    st.session_state.current_chat_id = chat['id']
                    st.rerun()
        else:
            st.caption("No previous chats")
        
        st.divider()
        
        # Sign Out
        if st.button("🚪 Sign out", use_container_width=True):
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
    if len(st.session_state.messages) == 0:
        st.markdown(f"""
        <div class="welcome-screen">
            <div class="welcome-icon">🧘</div>
            <h1 class="welcome-title">Hello, {user['name']}!</h1>
            <p class="welcome-subtitle">How can I support your wellness journey today?</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat Input
    if prompt := st.chat_input("Send a message..."):
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
                    
                    if st.session_state.current_chat_id:
                        update_chat_in_firestore(user['id'], st.session_state.current_chat_id, st.session_state.messages)
                    else:
                        st.session_state.current_chat_id = save_chat_to_firestore(user['id'], st.session_state.messages)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")