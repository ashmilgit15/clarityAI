# 🚀 Deployment Guide for Clarity AI

Complete guide to deploy your Clarity app to Streamlit Cloud with Google OAuth.

---

## 📋 Step 1: Push Code to GitHub

**1. Commit your changes:**

```powershell
cd "C:\Users\Ashmil P\Desktop\clarity"
git add app_with_auth.py requirements.txt .gitignore FIREBASE_SETUP.md OAUTH_SETUP_GUIDE.md README.md
git commit -m "Add OAuth authentication with Firebase integration"
git push origin main
```

**⚠️ Important:** Make sure these files are NOT committed (they're in .gitignore):
- `firebase-credentials.json`
- `.streamlit/secrets.toml`

---

## 📋 Step 2: Deploy to Streamlit Cloud

**1. Go to Streamlit Cloud:**
- Visit: https://share.streamlit.io/
- Click **"Sign in"** with your GitHub account

**2. Create New App:**
- Click **"New app"** button
- **Repository**: `ashmilgit15/clarityAI`
- **Branch**: `main`
- **Main file path**: `app_with_auth.py`
- **App URL** (custom): Choose something like `clarity-wellness` or `clarity-ai-app`
- Click **"Deploy"**

**3. Your app will start deploying!** (takes 2-3 minutes)

---

## 📋 Step 3: Add Secrets to Streamlit Cloud

**1. Open App Settings:**
- Click on your deployed app
- Click the **⚙️ (Settings)** button in the top right
- Go to **"Secrets"** section

**2. Copy your local secrets:**

Open your local file: `C:\Users\Ashmil P\Desktop\clarity\.streamlit\secrets.toml`

Copy the entire content and paste it into Streamlit Cloud secrets editor.

**Example format:**
```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

firebase_credentials_path = "firebase-credentials.json"

[oauth]
client_id = "1002239201452-jk5uphjnveqlnbchoh3r291pe9178igs.apps.googleusercontent.com"
client_secret = "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"
redirect_uri = "https://YOUR-APP-NAME.streamlit.app"

[firebase]
projectId = "clarity-ai-bd1d0"
apiKey = "AIzaSyDJHlzH4VN5tbvk77GEus_enulG2EuMmKs"
authDomain = "clarity-ai-bd1d0.firebaseapp.com"
```

**⚠️ Important:** Replace `redirect_uri` with your actual Streamlit app URL!

**3. Add Firebase Credentials:**

You also need to add the Firebase service account JSON. Add this section to secrets:

```toml
[firebase_credentials]
type = "service_account"
project_id = "clarity-ai-bd1d0"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-fbsvc@clarity-ai-bd1d0.iam.gserviceaccount.com"
client_id = "108270400965642207466"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40clarity-ai-bd1d0.iam.gserviceaccount.com"
```

To get these values, open your local `firebase-credentials.json` and copy the values.

**4. Click "Save"** and the app will restart.

---

## 📋 Step 4: Update app_with_auth.py for Firebase Credentials

We need to update the app to read Firebase credentials from secrets in production:

**Add this code after the Firebase initialization section:**

```python
# Initialize Firebase (only once)
if not firebase_admin._apps:
    try:
        # Check if running on Streamlit Cloud (secrets has firebase_credentials)
        if "firebase_credentials" in st.secrets:
            # Load from Streamlit secrets
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
```

---

## 📋 Step 5: Update OAuth Redirect URIs

**Your Streamlit app URL will be something like:**
```
https://YOUR-APP-NAME.streamlit.app
```

**1. Update Google Cloud Console:**

Go to: https://console.cloud.google.com/apis/credentials?project=clarity-ai-bd1d0

- Click on **"Web client (auto created by Google Service)"**
- Click **✏️ Edit**
- Under **Authorized JavaScript origins**, add:
  ```
  https://YOUR-APP-NAME.streamlit.app
  ```
- Under **Authorized redirect URIs**, add:
  ```
  https://YOUR-APP-NAME.streamlit.app
  ```
- Click **SAVE**

**2. Update Firebase Authorized Domains:**

Go to: https://console.firebase.google.com/project/clarity-ai-bd1d0/authentication/settings

- Scroll to **Authorized domains**
- Click **Add domain**
- Add: `YOUR-APP-NAME.streamlit.app`
- Click **Add**

---

## 📋 Step 6: Test Your Deployed App

**1. Visit your app:**
```
https://YOUR-APP-NAME.streamlit.app
```

**2. Test the OAuth flow:**
- Click "Sign in with Google"
- Authenticate with your Google account
- You should be redirected back to the app
- ✅ You're signed in!

**3. Test functionality:**
- Send a message to the AI
- Check if it saves to Firebase
- Sign out and sign back in
- Verify chat history persists

---

## 🔧 Troubleshooting

### "Redirect URI mismatch"
**Solution:** Double-check the redirect URI in Google Cloud Console matches your Streamlit app URL exactly (including https://)

### "Firebase initialization error"
**Solution:** Make sure all Firebase credentials are properly copied to Streamlit Cloud secrets

### "GROQ_API_KEY not found"
**Solution:** Verify GROQ_API_KEY is in Streamlit Cloud secrets

### OAuth consent screen warnings
**Solution:** If you see "This app hasn't been verified", click "Advanced" → "Go to Clarity (unsafe)" during testing. To remove this, publish your OAuth app in Google Cloud Console.

---

## 🎉 You're Live!

Your Clarity AI app is now deployed with:
- ✅ Real Google OAuth authentication
- ✅ Firebase database integration
- ✅ Secure HTTPS connection
- ✅ Global accessibility

**Share your app:**
```
https://YOUR-APP-NAME.streamlit.app
```

---

## 🔐 Security Best Practices

**1. Publish OAuth Consent Screen:**
- Go to Google Cloud Console → OAuth consent screen
- Click "Publish App" to remove the "unverified app" warning
- Add privacy policy and terms of service URLs

**2. Update Firebase Security Rules:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

**3. Monitor Usage:**
- Check Firebase Console for user activity
- Monitor Firestore usage to stay within free tier
- Review OAuth logs in Google Cloud Console

---

## 📊 Free Tier Limits

**Streamlit Cloud (Free):**
- 1 app deployed
- Unlimited public views
- Sleeps after inactivity (wakes up automatically)

**Firebase (Free - Spark Plan):**
- 50,000 reads/day
- 20,000 writes/day
- 1GB storage
- Unlimited authentication

**Groq API:**
- Check your Groq dashboard for current limits

---

## 🚀 Next Steps

**Optional enhancements:**
1. Add custom domain
2. Implement rate limiting
3. Add analytics tracking
4. Create user onboarding flow
5. Add more AI features
6. Implement chat export/download

---

Need help? Check the troubleshooting section or review the setup guides!
