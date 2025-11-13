# Deployment script for Clarity AI
Write-Host "🚀 Deploying Clarity AI to GitHub..." -ForegroundColor Cyan

# Navigate to project directory
cd "C:\Users\Ashmil P\Desktop\clarity"

# Add files
Write-Host "`n📦 Adding files..." -ForegroundColor Yellow
git add app_with_auth.py requirements.txt .gitignore FIREBASE_SETUP.md OAUTH_SETUP_GUIDE.md README.md DEPLOYMENT_GUIDE.md

# Show status
Write-Host "`n📋 Git status:" -ForegroundColor Yellow
git status

# Commit
Write-Host "`n💾 Committing changes..." -ForegroundColor Yellow
git commit -m "Add OAuth authentication with Firebase integration

- Real Google OAuth 2.0 sign-in
- Firebase Admin SDK with Firestore
- User profiles and session management
- Deployment ready (local + Streamlit Cloud)
- Complete setup and deployment documentation

Co-authored-by: factory-droid[bot] <138933559+factory-droid[bot]@users.noreply.github.com>"

# Push to GitHub
Write-Host "`n🌐 Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host "`n✅ Done! Code is now on GitHub" -ForegroundColor Green
Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to https://share.streamlit.io/"
Write-Host "2. Deploy your app from: ashmilgit15/clarityAI"
Write-Host "3. Follow DEPLOYMENT_GUIDE.md for complete instructions"
