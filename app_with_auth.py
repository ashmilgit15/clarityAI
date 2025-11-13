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

# Modern Tailwind CSS (same as before, keeping it short here)
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif; }
    #MainMenu, footer, header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    
    :root {
        --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --dark-bg: #0f0f1e;
        --dark-card: #1a1a2e;
    }
    
    .stApp { background: var(--dark-bg) !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    
    /* Auth Screen */
    .auth-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 2rem;
        background: radial-gradient(circle at 50% 50%, rgba(157, 78, 221, 0.1) 0%, transparent 50%);
    }
    
    .auth-card {
        background: var(--dark-card);
        border: 1px solid rgba(157, 78, 221, 0.3);
        border-radius: 24px;
        padding: 3rem;
        max-width: 450px;
        width: 100%;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        animation: fadeInUp 0.8s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .auth-logo {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Center the auth form columns */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    /* Style form inputs on auth screen */
    .auth-container input[type="text"] {
        background: rgba(157, 78, 221, 0.1) !important;
        border: 1px solid rgba(157, 78, 221, 0.3) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    
    .auth-container button {
        background: var(--gradient-1) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
    }
    
    .auth-container button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(157, 78, 221, 0.4) !important;
    }
    
    .auth-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .auth-subtitle {
        color: #a0a0b0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .google-btn {
        background: white !important;
        color: #333 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100%;
        cursor: pointer;
        transition: all 0.3s !important;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
    }
    
    .google-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(255, 255, 255, 0.2) !important;
    }
    
    /* User Profile Display */
    .user-profile-card {
        background: var(--gradient-1);
        padding: 1rem;
        border-radius: 16px;
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    .user-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid white;
    }
    
    .user-info {
        flex: 1;
        color: white;
    }
    
    .user-name {
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
    }
    
    .user-email {
        font-size: 0.8rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Rest of the previous CSS styles... */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1e 100%) !important;
        border-right: 1px solid rgba(157, 78, 221, 0.1) !important;
    }
    
    .stButton button {
        background: var(--gradient-1) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.5) !important;
    }
    
    .stChatMessage {
        background: transparent !important;
        padding: 1.5rem 0 !important;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: var(--gradient-1) !important;
        color: white !important;
        border-radius: 24px 24px 4px 24px !important;
        padding: 1.25rem 1.5rem !important;
        max-width: 75% !important;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
        background: var(--dark-card) !important;
        border: 1px solid rgba(157, 78, 221, 0.2) !important;
        border-radius: 24px 24px 24px 4px !important;
        padding: 1.25rem 1.5rem !important;
        max-width: 75% !important;
    }
    
    .stChatInputContainer {
        background: var(--dark-card) !important;
        border: 2px solid rgba(157, 78, 221, 0.3) !important;
        border-radius: 28px !important;
        padding: 0.75rem 1.5rem !important;
    }
    
    .stChatInput input {
        background: transparent !important;
        color: white !important;
        border: none !important;
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
