# Complete Google OAuth Setup Guide for Clarity

## 🎯 Overview
This guide will help you set up **real Google OAuth authentication** (not demo mode) for your Clarity app.

---

## 📋 Part 1: Firebase Authentication Setup

### Step 1: Enable Google Authentication in Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **clarity-ai-bd1d0**
3. Click **Authentication** in the left sidebar
4. Click **Get Started** (if you haven't already)
5. Go to **Sign-in method** tab
6. Find **Google** in the list and click it
7. Toggle **Enable** to ON
8. **Project support email**: Enter your email address
9. Click **Save**

✅ **Checkpoint**: Google sign-in is now enabled in Firebase!

---

## 📋 Part 2: Register Your Web App with Firebase

### Step 2: Add Web App to Firebase Project

1. In Firebase Console, click the **gear icon** (Settings) → **Project settings**
2. Scroll down to **Your apps** section
3. Click the **</>** (Web) icon to add a web app
4. **App nickname**: Enter "Clarity Web App"
5. ✅ Check **"Also set up Firebase Hosting"** (optional, for deployment later)
6. Click **Register app**
7. **Copy the Firebase SDK configuration** - you'll need this

Example config (yours will be different):
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyDJHlzH4VN5tbvk77GEus_enulG2EuMmKs",
  authDomain: "clarity-ai-bd1d0.firebaseapp.com",
  projectId: "clarity-ai-bd1d0",
  storageBucket: "clarity-ai-bd1d0.firebasestorage.app",
  messagingSenderId: "1002239201452",
  appId: "1:1002239201452:web:a03a57ecc8a142a4d6cf09"
};
```

8. Click **Continue to console**

---

## 📋 Part 3: Get OAuth Client ID & Secret

### Step 3: Get Google OAuth Credentials

1. In Firebase Console, go to **Authentication** → **Sign-in method**
2. Click on **Google** provider
3. Expand the **Web SDK configuration** section
4. You'll see:
   - **Web client ID** (looks like: `123456789-abc123.apps.googleusercontent.com`)
   - **Web client secret** (looks like: `GOCSPX-abc123xyz`)

5. **Copy both of these** - you'll need them!

---

## 📋 Part 4: Configure Authorized Domains

### Step 4: Add Authorized Domains for OAuth

1. Still in **Authentication** → **Sign-in method**
2. Scroll down to **Authorized domains**
3. By default, you'll see:
   - `localhost` ✅ (for development)
   - `clarity-ai-bd1d0.firebaseapp.com` ✅ (Firebase hosting)

4. Click **Add domain** if you need to add:
   - Your production domain (e.g., `clarity.yourdomain.com`)
   - Streamlit Cloud domain (e.g., `yourapp.streamlit.app`)

**For now, `localhost` is enough for development!**

---

## 📋 Part 5: Configure OAuth Consent Screen

### Step 5: Set Up OAuth Consent Screen in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your Firebase project: **clarity-ai-bd1d0**
3. In the left menu, go to **APIs & Services** → **OAuth consent screen**
4. Choose **External** (for public access)
5. Click **Create**

**Fill in the required fields:**

- **App name**: `Clarity - AI Wellness Companion`
- **User support email**: Your email
- **App logo**: (Optional - upload a logo if you have one)
- **Application home page**: `http://localhost:8501` (for now)
- **Application privacy policy**: (Optional for development)
- **Application terms of service**: (Optional for development)
- **Authorized domains**: `firebaseapp.com`
- **Developer contact email**: Your email

6. Click **Save and Continue**

**Scopes (Step 2):**
7. Click **Add or Remove Scopes**
8. Select these scopes:
   - ✅ `.../auth/userinfo.email`
   - ✅ `.../auth/userinfo.profile`
   - ✅ `openid`
9. Click **Update** → **Save and Continue**

**Test Users (Step 3):**
10. Click **Add Users**
11. Add your email address and any other test emails
12. Click **Save and Continue**

13. Review and click **Back to Dashboard**

✅ **Checkpoint**: OAuth Consent Screen is configured!

---

## 📋 Part 6: Configure Redirect URIs

### Step 6: Add Authorized Redirect URIs

1. In [Google Cloud Console](https://console.cloud.google.com/)
2. Go to **APIs & Services** → **Credentials**
3. Find your **OAuth 2.0 Client ID** (should be named something like "Web client (auto created by Google Service)")
4. Click on it to edit
5. Under **Authorized JavaScript origins**, add:
   ```
   http://localhost:8501
   http://localhost:8502
   http://localhost:8503
   http://localhost:8504
   http://localhost:8505
   ```

6. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8501/component/streamlit_oauth.authorize_button/index.html
   http://localhost:8502/component/streamlit_oauth.authorize_button/index.html
   http://localhost:8503/component/streamlit_oauth.authorize_button/index.html
   http://localhost:8504/component/streamlit_oauth.authorize_button/index.html
   http://localhost:8505/component/streamlit_oauth.authorize_button/index.html
   ```

7. Click **Save**

✅ **Checkpoint**: Redirect URIs configured!

---

## 📋 Part 7: SHA-1 Key Generation (For Android/Mobile)

### Step 7: Generate SHA-1 Certificate Fingerprint

**Note**: SHA-1 is primarily needed for **Android apps**. For web apps (Streamlit), you can **skip this step** for now.

If you plan to build an Android app later:

#### On Windows:

1. Open **Command Prompt** or **PowerShell**
2. Navigate to your Java JDK bin folder (usually):
   ```powershell
   cd "C:\Program Files\Java\jdk-XX.X.X\bin"
   ```

3. Run this command:
   ```powershell
   keytool -list -v -keystore "%USERPROFILE%\.android\debug.keystore" -alias androiddebugkey -storepass android -keypass android
   ```

4. Look for **SHA-1** in the output:
   ```
   SHA1: 12:34:56:78:90:AB:CD:EF:12:34:56:78:90:AB:CD:EF:12:34:56:78
   ```

5. Copy this SHA-1 value

#### On Mac/Linux:

```bash
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android
```

### Add SHA-1 to Firebase:

1. Go to Firebase Console → **Project Settings**
2. Scroll to **Your apps**
3. Select your Android app (or add one)
4. Click **Add fingerprint**
5. Paste your SHA-1 key
6. Click **Save**

---

## 📋 Part 8: Update Streamlit Secrets

### Step 8: Update `.streamlit/secrets.toml`

Add your OAuth credentials:

```toml
GROQ_API_KEY = "your-groq-api-key-here"

# Firebase credentials path
firebase_credentials_path = "firebase-credentials.json"

# Google OAuth Configuration
[oauth]
client_id = "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret = "GOCSPX-YOUR_CLIENT_SECRET"
redirect_uri = "http://localhost:8505/component/streamlit_oauth.authorize_button/index.html"

# Firebase Web Config (for frontend)
[firebase_web]
apiKey = "AIzaSyDJHlzH4VN5tbvk77GEus_enulG2EuMmKs"
authDomain = "clarity-ai-bd1d0.firebaseapp.com"
projectId = "clarity-ai-bd1d0"
storageBucket = "clarity-ai-bd1d0.firebasestorage.app"
messagingSenderId = "1002239201452"
appId = "1:1002239201452:web:a03a57ecc8a142a4d6cf09"
```

**Replace:**
- `YOUR_CLIENT_ID` with your actual OAuth Client ID
- `YOUR_CLIENT_SECRET` with your actual OAuth Client Secret

---

## 📋 Part 9: Testing OAuth Flow

### Step 9: Test Your OAuth Setup

Once the code is updated (next step), you should see:

1. **Sign in with Google** button
2. Click it → redirected to Google sign-in page
3. Select your Google account
4. Grant permissions
5. Redirected back to Clarity app
6. Signed in successfully!

---

## 🔐 Security Checklist

Before deploying to production:

- ✅ Keep `firebase-credentials.json` in `.gitignore`
- ✅ Keep `.streamlit/secrets.toml` in `.gitignore`
- ✅ Never commit OAuth secrets to GitHub
- ✅ Use environment variables for production deployment
- ✅ Enable Firebase Security Rules for Firestore
- ✅ Switch OAuth consent screen from "Testing" to "Production"
- ✅ Add proper privacy policy and terms of service
- ✅ Use HTTPS in production (required for OAuth)

---

## 🚀 Next Steps

After completing this guide:
1. ✅ Update the app code to use real OAuth (I'll do this next)
2. ✅ Test the authentication flow
3. ✅ Deploy to Streamlit Cloud or your own server

---

## 📚 Additional Resources

- [Firebase Authentication Docs](https://firebase.google.com/docs/auth/web/google-signin)
- [Google OAuth 2.0 Docs](https://developers.google.com/identity/protocols/oauth2)
- [Streamlit OAuth Component](https://github.com/dnplus/streamlit-oauth)

---

## ❓ Troubleshooting

### Common Issues:

**1. "Redirect URI mismatch" error**
- Solution: Add the exact redirect URI to Google Cloud Console Credentials

**2. "OAuth consent screen not configured"**
- Solution: Complete Part 5 above

**3. "Invalid client ID"**
- Solution: Double-check client_id in secrets.toml matches Google Cloud Console

**4. "Access blocked: This app's request is invalid"**
- Solution: Add your email as a test user in OAuth consent screen

---

Ready to proceed? Let me know when you've completed these steps, and I'll update the code to use real OAuth!
