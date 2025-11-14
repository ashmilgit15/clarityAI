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
    page_title="AuraGlow - Your Skincare Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Firebase (only once) - FIXED
if not firebase_admin._apps:
    try:
        # Try to get credentials from secrets first
        if "firebase_credentials" in st.secrets:
            cred_dict = {
                "type": st.secrets["firebase_credentials"]["type"],
                "project_id": st.secrets["firebase_credentials"]["project_id"],
                "private_key_id": st.secrets["firebase_credentials"]["private_key_id"],
                "private_key": st.secrets["firebase_credentials"]["private_key"].replace('\\n', '\n'),
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
            firebase_admin.initialize_app(cred)
            db = firestore.client()
        elif os.path.exists("firebase-credentials.json"):
            cred = credentials.Certificate("firebase-credentials.json")
            firebase_admin.initialize_app(cred)
            db = firestore.client()
        else:
            # If no credentials available, allow app to run without Firebase (for demo)
            st.warning("⚠️ Firebase credentials not found. Some features may be limited.")
            db = None
    except Exception as e:
        st.warning(f"⚠️ Firebase initialization issue: {str(e)}. App will continue with limited features.")
        db = None
else:
    try:
        db = firestore.client()
    except:
        db = None

# ==========================================
# AURAGLOW DESIGN SYSTEM
# Minimalist, Clean, Luxurious Skincare Brand
# ==========================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');
    
    /* === AURAGLOW COLOR PALETTE === */
    :root {
        --primary-bg: #FAFAF8;
        --secondary-bg: #FFFFFF;
        --accent-gold: #D4AF37;
        --accent-rose: #E8D5C4;
        --accent-sage: #9CAF88;
        --text-primary: #2C2C2C;
        --text-secondary: #6B6B6B;
        --text-muted: #9B9B9B;
        --border-light: #E8E8E6;
        --border-medium: #D4D4D2;
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
        --gradient-primary: linear-gradient(135deg, #D4AF37 0%, #E8D5C4 100%);
        --gradient-subtle: linear-gradient(180deg, #FAFAF8 0%, #FFFFFF 100%);
    }
    
    /* === DARK MODE SUPPORT (Optional) === */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-bg: #1A1A1A;
            --secondary-bg: #242424;
            --text-primary: #F5F5F5;
            --text-secondary: #B0B0B0;
            --text-muted: #808080;
            --border-light: #3A3A3A;
            --border-medium: #4A4A4A;
        }
    }
    
    /* === BASE STYLES === */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        box-sizing: border-box;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu, footer, header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    /* === MAIN APP BACKGROUND === */
    .stApp {
        background: var(--primary-bg) !important;
        color: var(--text-primary) !important;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* === SIDEBAR STYLING (Desktop) === */
    [data-testid="stSidebar"] {
        background: var(--secondary-bg) !important;
        border-right: 1px solid var(--border-light) !important;
        padding: 0 !important;
        min-width: 280px !important;
        max-width: 280px !important;
        box-shadow: var(--shadow-sm);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
        padding: 1.5rem 1rem !important;
    }
    
    /* === AURAGLOW LOGO === */
    .auraglow-logo {
        text-align: center;
        padding: 2rem 1rem 1.5rem;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid var(--border-light);
    }
    
    .auraglow-logo-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
        display: block;
    }
    
    .auraglow-logo-text {
        font-family: 'Playfair Display', serif;
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        margin: 0;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .auraglow-logo-tagline {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.5rem;
    }
    
    /* === USER PROFILE SECTION === */
    .user-profile {
        padding: 1rem;
        margin: 0.5rem 0;
        background: var(--primary-bg);
        border: 1px solid var(--border-light);
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .user-profile:hover {
        background: var(--secondary-bg);
        box-shadow: var(--shadow-sm);
    }
    
    .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        flex-shrink: 0;
        border: 2px solid var(--border-light);
    }
    
    .user-info {
        flex: 1;
        min-width: 0;
        overflow: hidden;
    }
    
    .user-name {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .user-email {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* === SIDEBAR BUTTONS === */
    [data-testid="stSidebar"] .stButton button {
        background: var(--secondary-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
        width: 100% !important;
        min-height: 44px !important;
        margin: 0.25rem 0 !important;
        box-shadow: none !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: var(--primary-bg) !important;
        border-color: var(--accent-gold) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* New Chat Button - Primary Style */
    [data-testid="stSidebar"] .stButton:first-of-type button {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] .stButton:first-of-type button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Chat History Items */
    [data-testid="stSidebar"] h3 {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin: 1.5rem 0.75rem 0.5rem 0.75rem !important;
        padding: 0 !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: var(--border-light) !important;
        margin: 0.75rem 0.5rem !important;
    }
    
    /* Sign Out Button */
    [data-testid="stSidebar"] .stButton:last-of-type button {
        color: #DC2626 !important;
        border-color: rgba(220, 38, 38, 0.2) !important;
    }
    
    [data-testid="stSidebar"] .stButton:last-of-type button:hover {
        background: rgba(220, 38, 38, 0.05) !important;
        border-color: rgba(220, 38, 38, 0.4) !important;
    }
    
    /* === MAIN CHAT INTERFACE === */
    .main-chat-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
        max-width: 1200px;
        margin: 0 auto;
        background: var(--primary-bg);
    }
    
    /* === HEADER (Desktop) === */
    .chat-header {
        background: var(--secondary-bg);
        border-bottom: 1px solid var(--border-light);
        padding: 1rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: var(--shadow-sm);
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .header-logo {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        font-weight: 600;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .header-actions {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .header-btn {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        border: 1px solid var(--border-light);
        background: var(--secondary-bg);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .header-btn:hover {
        background: var(--primary-bg);
        border-color: var(--accent-gold);
    }
    
    /* === CONVERSATION PANE === */
    .conversation-pane {
        flex: 1;
        overflow-y: auto;
        padding: 2rem 2rem;
        scroll-behavior: smooth;
    }
    
    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        padding: 1rem 0 !important;
        margin: 0 !important;
        animation: fadeInUp 0.3s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* User Messages - Right Aligned */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        display: flex;
        justify-content: flex-end;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: var(--gradient-primary) !important;
        color: white !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 1rem 1.25rem !important;
        max-width: 70% !important;
        box-shadow: var(--shadow-md);
        border: none !important;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {
        color: white !important;
        margin: 0 !important;
        font-size: 0.9375rem !important;
        line-height: 1.6 !important;
    }
    
    /* Assistant Messages - Left Aligned */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
        background: var(--secondary-bg) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 18px 18px 18px 4px !important;
        padding: 1rem 1.25rem !important;
        max-width: 70% !important;
        box-shadow: var(--shadow-sm);
    }
    
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) p {
        color: var(--text-primary) !important;
        margin: 0 !important;
        font-size: 0.9375rem !important;
        line-height: 1.7 !important;
    }
    
    /* Avatar Styling */
    [data-testid="stChatMessageAvatarUser"] {
        width: 32px !important;
        height: 32px !important;
        border-radius: 50% !important;
        background: var(--accent-sage) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
        box-shadow: var(--shadow-sm);
    }
    
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 32px !important;
        height: 32px !important;
        border-radius: 50% !important;
        background: var(--accent-rose) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
        box-shadow: var(--shadow-sm);
    }
    
    /* === MESSAGE COMPOSER === */
    .message-composer {
        background: var(--secondary-bg);
        border-top: 1px solid var(--border-light);
        padding: 1.5rem 2rem;
        position: sticky;
        bottom: 0;
        z-index: 100;
        box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.04);
    }
    
    [data-testid="stChatInputContainer"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .stChatInput {
        max-width: 100% !important;
        margin: 0 !important;
    }
    
    .stChatInput textarea {
        background: var(--primary-bg) !important;
        border: 1.5px solid var(--border-light) !important;
        border-radius: 24px !important;
        padding: 0.875rem 3.5rem 0.875rem 1.25rem !important;
        font-size: 0.9375rem !important;
        color: var(--text-primary) !important;
        min-height: 52px !important;
        max-height: 200px !important;
        resize: none !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
    }
    
    .stChatInput textarea:focus {
        border-color: var(--accent-gold) !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1) !important;
    }
    
    .stChatInput textarea::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* Send Button */
    .stChatInput button {
        background: var(--gradient-primary) !important;
        border: none !important;
        color: white !important;
        position: absolute !important;
        right: 0.5rem !important;
        bottom: 0.5rem !important;
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
    }
    
    .stChatInput button:hover {
        transform: scale(1.05);
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Quick Action Buttons */
    .quick-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.75rem;
        flex-wrap: wrap;
    }
    
    .quick-action-btn {
        padding: 0.5rem 1rem;
        background: var(--primary-bg);
        border: 1px solid var(--border-light);
        border-radius: 20px;
        font-size: 0.8125rem;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: nowrap;
    }
    
    .quick-action-btn:hover {
        background: var(--secondary-bg);
        border-color: var(--accent-gold);
        color: var(--text-primary);
    }
    
    /* === WELCOME SCREEN === */
    .welcome-screen {
        max-width: 800px;
        margin: 0 auto;
        padding: 4rem 2rem;
        text-align: center;
    }
    
    .welcome-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        display: block;
    }
    
    .welcome-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    
    .welcome-subtitle {
        font-size: 1.125rem;
        color: var(--text-secondary);
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    
    .suggestion-cards {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .suggestion-card {
        background: var(--secondary-bg);
        border: 1px solid var(--border-light);
        border-radius: 16px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
    }
    
    .suggestion-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--accent-gold);
    }
    
    .suggestion-card-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
        display: block;
    }
    
    .suggestion-card-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .suggestion-card-desc {
        font-size: 0.875rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    /* === AUTHENTICATION SCREEN === */
    .auth-container {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh !important;
        width: 100vw !important;
        padding: 2rem !important;
        background: var(--gradient-subtle) !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        z-index: 10000 !important;
    }
    
    .auth-card {
        max-width: 440px;
        width: 100%;
        text-align: center;
        background: var(--secondary-bg);
        padding: 3rem 2.5rem;
        border-radius: 24px;
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-lg);
    }
    
    .auth-logo {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 600;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .auth-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }
    
    .auth-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .auth-subtitle {
        font-size: 0.9375rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    /* Auth Form Inputs */
    .stTextInput > div > div > input,
    .stTextInput > div > div > input:focus {
        background: var(--primary-bg) !important;
        border: 1.5px solid var(--border-light) !important;
        border-radius: 12px !important;
        padding: 0.875rem 1rem !important;
        color: var(--text-primary) !important;
        font-size: 0.9375rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1) !important;
    }
    
    .stTextInput label {
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Auth Buttons */
    .stButton > button {
        width: 100% !important;
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 1.5rem !important;
        font-size: 0.9375rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        min-height: 48px !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stButton > button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
        box-shadow: var(--shadow-md) !important;
    }
    
    .auth-divider {
        display: flex;
        align-items: center;
        margin: 1.5rem 0;
        color: var(--text-muted);
        font-size: 0.875rem;
    }
    
    .auth-divider::before,
    .auth-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border-light);
    }
    
    .auth-divider::before {
        margin-right: 1rem;
    }
    
    .auth-divider::after {
        margin-left: 1rem;
    }
    
    .auth-toggle {
        margin-top: 1.5rem;
        color: var(--text-secondary);
        font-size: 0.9375rem;
    }
    
    .auth-toggle a {
        color: var(--accent-gold);
        text-decoration: none;
        font-weight: 600;
        cursor: pointer;
    }
    
    .auth-toggle a:hover {
        text-decoration: underline;
    }
    
    /* === MOBILE RESPONSIVE === */
    @media (max-width: 768px) {
        /* Mobile Menu Button */
        .mobile-menu-btn {
            display: flex;
            position: fixed;
            top: 1rem;
            left: 1rem;
            z-index: 9999;
            width: 44px;
            height: 44px;
            background: var(--secondary-bg);
            border: 1px solid var(--border-light);
            border-radius: 12px;
            cursor: pointer;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-md);
        }
        
        .mobile-menu-btn:active {
            transform: scale(0.95);
        }
        
        /* Sidebar - Mobile */
        [data-testid="stSidebar"] {
            position: fixed !important;
            left: -100% !important;
            top: 0 !important;
            height: 100vh !important;
            width: 85vw !important;
            max-width: 320px !important;
            z-index: 9998 !important;
            transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15) !important;
        }
        
        [data-testid="stSidebar"][data-visible="true"] {
            left: 0 !important;
        }
        
        /* Sidebar Overlay */
        .sidebar-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.4);
            z-index: 9997;
            backdrop-filter: blur(4px);
        }
        
        .sidebar-overlay.active {
            display: block;
        }
        
        /* Main Content - Mobile */
        .main-chat-container {
            padding-top: 4rem;
        }
        
        .chat-header {
            padding: 1rem 1rem;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            width: 100%;
        }
        
        .conversation-pane {
            padding: 1rem 1rem !important;
        }
        
        .message-composer {
            padding: 1rem 1rem !important;
        }
        
        /* Chat Messages - Mobile */
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"],
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
            max-width: 85% !important;
            padding: 0.875rem 1rem !important;
        }
        
        /* Welcome Screen - Mobile */
        .welcome-screen {
            padding: 2rem 1rem !important;
        }
        
        .welcome-title {
            font-size: 2rem !important;
        }
        
        .welcome-subtitle {
            font-size: 1rem !important;
        }
        
        .suggestion-cards {
            grid-template-columns: 1fr !important;
        }
        
        /* Auth Screen - Mobile */
        .auth-container {
            padding: 1.5rem !important;
        }
        
        .auth-card {
            padding: 2rem 1.5rem !important;
        }
        
        .auth-title {
            font-size: 1.5rem !important;
        }
        
        .stChatInput textarea {
            min-height: 48px !important;
            font-size: 16px !important; /* Prevents zoom on iOS */
        }
    }
    
    /* === ACCESSIBILITY === */
    /* Focus indicators for keyboard navigation */
    button:focus-visible,
    input:focus-visible,
    textarea:focus-visible {
        outline: 2px solid var(--accent-gold);
        outline-offset: 2px;
    }
    
    /* Screen reader only text */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
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
        background: var(--border-medium);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
</style>
""", unsafe_allow_html=True)

# Mobile Menu Script
st.markdown("""
<div class="mobile-menu-btn" id="mobileMenuBtn" onclick="toggleSidebar()" aria-label="Toggle menu">
    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
    </svg>
</div>
<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()" aria-label="Close menu"></div>

<script>
function toggleSidebar() {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (!sidebar || !overlay) return;
    
    const isVisible = sidebar.getAttribute('data-visible') === 'true';
    
    if (isVisible) {
        sidebar.setAttribute('data-visible', 'false');
        overlay.classList.remove('active');
    } else {
        sidebar.setAttribute('data-visible', 'true');
        overlay.classList.add('active');
    }
}

function initSidebar() {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (!sidebar) {
        setTimeout(initSidebar, 100);
        return;
    }
    
    if (window.innerWidth <= 768) {
        sidebar.setAttribute('data-visible', 'false');
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSidebar);
} else {
    initSidebar();
}

setTimeout(initSidebar, 500);

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
</script>
""", unsafe_allow_html=True)

# ==========================================
# SYSTEM PROMPT - AURAGLOW SKINCARE ASSISTANT
# ==========================================

SYSTEM_PROMPT = """You are an expert skincare assistant for AuraGlow, a premium organic skincare brand. Your role is to help customers with:

1. Product Information: Answer questions about ingredients, usage instructions, and skin type suitability
2. Personalized Recommendations: Suggest products based on customer needs, skin type, and concerns
3. Order Tracking: Help customers track their orders and delivery status
4. Customer Service: Assist with returns, subscription changes, and general inquiries

Your tone should be:
- Warm, professional, and knowledgeable
- Empathetic and understanding of skincare concerns
- Clear and concise in explanations
- Helpful without being pushy

Always prioritize customer satisfaction and provide accurate, helpful information about AuraGlow's organic skincare products."""

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def create_user_in_firestore(user_id, email, name, photo_url):
    """Create user document in Firestore"""
    if db is None:
        return
    try:
        user_ref = db.collection('users').document(user_id)
        user_ref.set({
            'email': email,
            'name': name,
            'photo_url': photo_url,
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_login': firestore.SERVER_TIMESTAMP
        }, merge=True)
    except Exception as e:
        st.warning(f"Could not save user data: {str(e)}")

def save_chat_to_firestore(user_id, messages):
    """Save chat session to Firestore"""
    if db is None or not messages:
        return None
    try:
        chat_ref = db.collection('users').document(user_id).collection('chats').document()
        chat_ref.set({
            'messages': messages,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'message_count': len(messages)
        })
        return chat_ref.id
    except Exception as e:
        st.warning(f"Could not save chat: {str(e)}")
        return None

def load_user_chats(user_id, limit=10):
    """Load user's recent chats from Firestore"""
    if db is None:
        return []
    try:
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
    except Exception as e:
        st.warning(f"Could not load chats: {str(e)}")
        return []

def update_chat_in_firestore(user_id, chat_id, messages):
    """Update existing chat session"""
    if db is None:
        return
    try:
        chat_ref = db.collection('users').document(user_id).collection('chats').document(chat_id)
        chat_ref.update({
            'messages': messages,
            'updated_at': firestore.SERVER_TIMESTAMP,
            'message_count': len(messages)
        })
    except Exception as e:
        st.warning(f"Could not update chat: {str(e)}")

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================

if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "client" not in st.session_state:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        st.session_state.client = Groq(api_key=api_key)
    except:
        st.error("⚠️ Groq API Key Missing")
        st.stop()

# ==========================================
# AUTHENTICATION SCREEN
# ==========================================

def show_auth_screen():
    """Display authentication screen with AuraGlow branding"""
    
    is_signup = st.session_state.auth_mode == "signup"
    
    st.markdown(f"""
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-logo">AuraGlow</div>
            <div class="auth-icon">✨</div>
            <h1 class="auth-title">{'Create Your Account' if is_signup else 'Welcome Back'}</h1>
            <p class="auth-subtitle">
                {'Start your journey to radiant, healthy skin' if is_signup else 'Sign in to continue your skincare journey'}
            </p>
    """, unsafe_allow_html=True)
    
    if is_signup:
        st.markdown("<h3 style='color: var(--text-primary); text-align: center; margin-bottom: 1.5rem; font-size: 1.125rem;'>Create Your Account</h3>", unsafe_allow_html=True)
        
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address",
            key="signup_email",
            label_visibility="visible"
        )
        
        name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            key="signup_name",
            label_visibility="visible"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a strong password (minimum 8 characters)",
            key="signup_password",
            label_visibility="visible"
        )
        
        if st.button("Create Account", use_container_width=True, type="primary"):
            if email and name and password:
                if len(password) < 8:
                    st.error("Password must be at least 8 characters long")
                else:
                    user_id = hashlib.md5(email.encode()).hexdigest()
                    
                    st.session_state.user = {
                        'id': user_id,
                        'email': email,
                        'name': name,
                        'photo_url': f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=D4AF37&color=fff"
                    }
                    
                    create_user_in_firestore(
                        user_id,
                        email,
                        name,
                        st.session_state.user['photo_url']
                    )
                    
                    st.success("Account created successfully! Redirecting...")
                    st.rerun()
            else:
                st.error("Please fill in all fields")
        
        st.markdown("<div class='auth-divider'>OR</div>", unsafe_allow_html=True)
        
        try:
            oauth2 = OAuth2Component(
                st.secrets["oauth"]["client_id"],
                st.secrets["oauth"]["client_secret"],
                "https://accounts.google.com/o/oauth2/v2/auth",
                "https://oauth2.googleapis.com/token",
                "https://oauth2.googleapis.com/token"
            )
            
            result = oauth2.authorize_button(
                name="Continue with Google",
                redirect_uri=st.secrets["oauth"]["redirect_uri"],
                scope="openid email profile",
                key="google_oauth_signup",
                extras_params={"access_type": "offline"},
                use_container_width=True,
                pkce='S256',
            )
            
            if result and "token" in result:
                headers = {"Authorization": f"Bearer {result['token']['access_token']}"}
                user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers).json()
                
                user_id = user_info.get("id", hashlib.md5(user_info["email"].encode()).hexdigest())
                
                st.session_state.user = {
                    'id': user_id,
                    'email': user_info.get("email", ""),
                    'name': user_info.get("name", "User"),
                    'photo_url': user_info.get("picture", f"https://ui-avatars.com/api/?name={user_info.get('name', 'User')}&background=D4AF37&color=fff")
                }
                
                create_user_in_firestore(
                    user_id,
                    st.session_state.user['email'],
                    st.session_state.user['name'],
                    st.session_state.user['photo_url']
                )
                
                st.rerun()
        except Exception as e:
            st.warning(f"OAuth not configured: {str(e)}")
        
        if st.button("Already have an account? Sign in", use_container_width=True, key="switch_to_login"):
            st.session_state.auth_mode = "login"
            st.rerun()
            
    else:  # Login mode
        st.markdown("<h3 style='color: var(--text-primary); text-align: center; margin-bottom: 1.5rem; font-size: 1.125rem;'>Sign In</h3>", unsafe_allow_html=True)
        
        login_email = st.text_input(
            "Email Address",
            placeholder="Enter your registered email address",
            key="login_email",
            label_visibility="visible"
        )
        
        login_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
            label_visibility="visible"
        )
        
        if st.button("Sign In", use_container_width=True, type="primary"):
            if login_email and login_password:
                user_id = hashlib.md5(login_email.encode()).hexdigest()
                
                st.session_state.user = {
                    'id': user_id,
                    'email': login_email,
                    'name': "User",
                    'photo_url': f"https://ui-avatars.com/api/?name=User&background=D4AF37&color=fff"
                }
                
                st.success("Signed in successfully!")
                st.rerun()
            else:
                st.error("Please enter your email and password")
        
        st.markdown("<div class='auth-divider'>OR</div>", unsafe_allow_html=True)
        
        try:
            oauth2 = OAuth2Component(
                st.secrets["oauth"]["client_id"],
                st.secrets["oauth"]["client_secret"],
                "https://accounts.google.com/o/oauth2/v2/auth",
                "https://oauth2.googleapis.com/token",
                "https://oauth2.googleapis.com/token"
            )
            
            result = oauth2.authorize_button(
                name="Sign in with Google",
                redirect_uri=st.secrets["oauth"]["redirect_uri"],
                scope="openid email profile",
                key="google_oauth_login",
                extras_params={"access_type": "offline"},
                use_container_width=True,
                pkce='S256',
            )
            
            if result and "token" in result:
                headers = {"Authorization": f"Bearer {result['token']['access_token']}"}
                user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers).json()
                
                user_id = user_info.get("id", hashlib.md5(user_info["email"].encode()).hexdigest())
                
                st.session_state.user = {
                    'id': user_id,
                    'email': user_info.get("email", ""),
                    'name': user_info.get("name", "User"),
                    'photo_url': user_info.get("picture", f"https://ui-avatars.com/api/?name={user_info.get('name', 'User')}&background=D4AF37&color=fff")
                }
                
                st.rerun()
        except Exception as e:
            st.warning(f"OAuth not configured: {str(e)}")
        
        if st.button("Don't have an account? Sign up", use_container_width=True, key="switch_to_signup"):
            st.session_state.auth_mode = "signup"
            st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# ==========================================
# MAIN APPLICATION
# ==========================================

if st.session_state.user is None:
    show_auth_screen()
else:
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        # AuraGlow Logo
        st.markdown("""
        <div class="auraglow-logo">
            <span class="auraglow-logo-icon">✨</span>
            <div class="auraglow-logo-text">AuraGlow</div>
            <div class="auraglow-logo-tagline">Organic Skincare</div>
        </div>
        """, unsafe_allow_html=True)
        
        # User Profile
        st.markdown(f"""
        <div class="user-profile">
            <img src="{user['photo_url']}" class="user-avatar" alt="User avatar">
            <div class="user-info">
                <p class="user-name">{user['name']}</p>
                <p class="user-email">{user['email']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # New Chat Button
        if st.button("➕ New Chat", use_container_width=True):
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
        if st.button("🚪 Sign Out", use_container_width=True):
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
    st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)
    
    # Header (Desktop)
    st.markdown("""
    <div class="chat-header">
        <div class="header-left">
            <div class="header-logo">AuraGlow</div>
        </div>
        <div class="header-actions">
            <div class="header-btn" title="Settings">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24"></path>
                </svg>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Conversation Pane
    st.markdown('<div class="conversation-pane">', unsafe_allow_html=True)
    
    if len(st.session_state.messages) == 0:
        st.markdown(f"""
        <div class="welcome-screen">
            <span class="welcome-icon">✨</span>
            <h1 class="welcome-title">Hello, {user['name']}!</h1>
            <p class="welcome-subtitle">I'm your AuraGlow skincare assistant. How can I help you today?</p>
            
            <div class="suggestion-cards">
                <div class="suggestion-card" onclick="document.querySelector('[data-testid=\\"stChatInput\\"] textarea').value='What products are best for sensitive skin?'; document.querySelector('[data-testid=\\"stChatInput\\"] textarea').focus();">
                    <span class="suggestion-card-icon">🌿</span>
                    <div class="suggestion-card-title">Product Recommendations</div>
                    <div class="suggestion-card-desc">Get personalized skincare recommendations</div>
                </div>
                <div class="suggestion-card" onclick="document.querySelector('[data-testid=\\"stChatInput\\"] textarea').value='Track my order'; document.querySelector('[data-testid=\\"stChatInput\\"] textarea').focus();">
                    <span class="suggestion-card-icon">📦</span>
                    <div class="suggestion-card-title">Track Order</div>
                    <div class="suggestion-card-desc">Check your order status and delivery</div>
                </div>
                <div class="suggestion-card" onclick="document.querySelector('[data-testid=\\"stChatInput\\"] textarea').value='What ingredients are in your products?'; document.querySelector('[data-testid=\\"stChatInput\\"] textarea').focus();">
                    <span class="suggestion-card-icon">🧪</span>
                    <div class="suggestion-card-title">Product Ingredients</div>
                    <div class="suggestion-card-desc">Learn about our organic ingredients</div>
                </div>
                <div class="suggestion-card" onclick="document.querySelector('[data-testid=\\"stChatInput\\"] textarea').value='I need help with a return'; document.querySelector('[data-testid=\\"stChatInput\\"] textarea').focus();">
                    <span class="suggestion-card-icon">🔄</span>
                    <div class="suggestion-card-title">Customer Service</div>
                    <div class="suggestion-card-desc">Returns, exchanges, and support</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Display messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close conversation-pane
    
    # Message Composer
    st.markdown('<div class="message-composer">', unsafe_allow_html=True)
    
    if prompt := st.chat_input("Ask about products, ingredients, orders, or skincare advice..."):
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
                        max_tokens=300
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
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close message-composer
    st.markdown('</div>', unsafe_allow_html=True)  # Close main-chat-container

