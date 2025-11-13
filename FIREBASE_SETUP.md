# Firebase Setup Guide for Clarity

## Step 1: Create Firebase Project (100% FREE)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Enter project name: **"Clarity"**
4. Disable Google Analytics (optional)
5. Click **"Create project"**

## Step 2: Enable Google Authentication

1. In Firebase Console, go to **Authentication** → **Get Started**
2. Click **Sign-in method** tab
3. Enable **Google** provider
4. Add support email (your email)
5. Click **Save**

## Step 3: Enable Firestore Database

1. Go to **Firestore Database** → **Create database**
2. Choose **Start in test mode** (for development)
3. Select location closest to you
4. Click **Enable**

**Security Rules (for development):**
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

## Step 4: Get Firebase Credentials

### A. Get Web App Config (for frontend)
1. Go to **Project Settings** (gear icon) → **General**
2. Scroll to **Your apps** → Click **Web app** icon (</>)
3. Register app name: **"Clarity Web"**
4. Copy the `firebaseConfig` object

### B. Get Service Account Key (for backend)
1. Go to **Project Settings** → **Service accounts**
2. Click **Generate new private key**
3. Download the JSON file
4. Rename it to `firebase-credentials.json`
5. Move it to your `clarity` folder

**⚠️ IMPORTANT: Add to `.gitignore`:**
```
firebase-credentials.json
```

## Step 5: Configure Streamlit Secrets

Add to `.streamlit/secrets.toml`:

```toml
# Groq API (already exists)
GROQ_API_KEY = "your-groq-key"

# Firebase Web Config (from Step 4A)
[firebase]
apiKey = "AIzaSy..."
authDomain = "clarity-xxxxx.firebaseapp.com"
projectId = "clarity-xxxxx"
storageBucket = "clarity-xxxxx.appspot.com"
messagingSenderId = "123456789"
appId = "1:123456789:web:xxxxx"

# Path to service account key (from Step 4B)
firebase_credentials_path = "firebase-credentials.json"
```

## Step 6: Install Dependencies

```bash
pip install firebase-admin streamlit-oauth
```

## Free Tier Limits (More than enough!)

✅ **Authentication:** Unlimited sign-ins
✅ **Firestore:** 
  - 1GB storage
  - 50,000 reads/day
  - 20,000 writes/day
  - 20,000 deletes/day

**Perfect for personal use and hundreds of users!**

## Next Steps

After completing these steps, run:
```bash
streamlit run app_with_auth.py
```

Your app will have:
- ✅ Google Sign-in
- ✅ User profiles
- ✅ Chat history storage
- ✅ Persistent conversations
- ✅ Multi-device sync
