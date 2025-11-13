# 🧘 Clarity - AI Wellness Companion

A modern, AI-powered mental wellness chatbot with Google authentication and persistent chat history.

## ✨ Features

- 🔐 **Google Authentication** - Secure sign-in with Firebase
- 💾 **Chat History** - All conversations saved to Firestore
- 🔄 **Multi-Device Sync** - Access your chats from anywhere
- 🎨 **Modern UI** - Beautiful Tailwind CSS design
- 🤖 **AI-Powered** - Using Groq's Llama 3.3 70B model
- 🌙 **Dark Theme** - Easy on the eyes
- ⚡ **100% FREE** - Firebase free tier + Groq free API

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Firebase
Follow the detailed guide in **`FIREBASE_SETUP.md`**

Quick steps:
1. Create Firebase project
2. Enable Google Authentication
3. Enable Firestore Database
4. Download credentials
5. Update `.streamlit/secrets.toml`

### 3. Configure Secrets

Create/update `.streamlit/secrets.toml`:

```toml
# Groq API Key
GROQ_API_KEY = "your-groq-api-key"

# Firebase Web Config
[firebase]
apiKey = "AIzaSy..."
authDomain = "clarity-xxxxx.firebaseapp.com"
projectId = "clarity-xxxxx"
storageBucket = "clarity-xxxxx.appspot.com"
messagingSenderId = "123456789"
appId = "1:123456789:web:xxxxx"

# Firebase Service Account
firebase_credentials_path = "firebase-credentials.json"
```

### 4. Run the App

**Without Authentication (original):**
```bash
streamlit run app.py
```

**With Authentication & Chat History:**
```bash
streamlit run app_with_auth.py
```

## 📁 Project Structure

```
clarity/
├── app.py                      # Main app (no auth)
├── app_with_auth.py            # App with Firebase auth
├── requirements.txt            # Python dependencies
├── FIREBASE_SETUP.md          # Detailed Firebase setup guide
├── README.md                  # This file
├── .streamlit/
│   └── secrets.toml           # API keys and config (gitignored)
├── firebase-credentials.json  # Firebase service account (gitignored)
└── .gitignore                 # Git ignore rules
```

## 🔒 Security

- ✅ API keys stored in `.streamlit/secrets.toml` (gitignored)
- ✅ Firebase credentials in separate file (gitignored)
- ✅ Firestore security rules restrict access to user's own data
- ✅ No passwords stored (uses Firebase Auth)

## 💰 Cost (FREE!)

### Firebase Free Tier:
- ✅ **Authentication:** Unlimited
- ✅ **Firestore:** 1GB storage, 50K reads/day, 20K writes/day
- ✅ **Hosting:** 10GB/month

### Groq API:
- ✅ Free tier available
- ✅ Fast inference

**Result:** Can support hundreds of users for FREE! 🎉

## 🎨 Available App Versions

- **`app.py`** - Modern UI, no authentication
- **`app_with_auth.py`** - Full authentication + chat history
- **`app_dark.py`** - ChatGPT-style dark theme
- **`app_old.py`** - Original design (backup)

## 🛠️ Tech Stack

- **Frontend:** Streamlit + Tailwind CSS
- **AI:** Groq (Llama 3.3 70B)
- **Auth:** Firebase Authentication
- **Database:** Cloud Firestore
- **Hosting:** Streamlit Cloud (optional)

## 📝 Features in Detail

### Authentication Flow
1. User enters email and name
2. Account created/logged in via Firebase
3. User profile displayed in sidebar
4. All chats auto-saved to Firestore

### Chat History
- 💾 Auto-saves after each message
- 📜 Recent chats shown in sidebar
- 🔄 Click to load previous conversations
- ✏️ Continue where you left off

### AI Capabilities
- 🧘 Emotional support
- 💭 Stress relief techniques
- 🌬️ Breathing exercises
- 😴 Sleep improvement tips
- 🆘 Crisis detection & resources

## 🚀 Deployment

### Streamlit Cloud (Free)
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in dashboard
4. Deploy!

### Manual Deployment
Works on any server with Python 3.8+

## 🤝 Contributing

Feel free to fork and customize for your needs!

## 📄 License

MIT License - Use freely!

## 💡 Tips

- Start with `app_with_auth.py` for full features
- Firebase free tier is generous - perfect for personal use
- Chat history syncs across devices automatically
- Sign in with any email (demo mode) or integrate real Google OAuth

## 🆘 Support

If you encounter issues:
1. Check `FIREBASE_SETUP.md` for Firebase configuration
2. Verify all secrets are in `.streamlit/secrets.toml`
3. Make sure Firebase credentials JSON is in the root folder
4. Check Firebase Console for any auth/database errors

---

**Made with ❤️ for mental wellness**
