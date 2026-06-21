# 🚀 EXECUTION GUIDE - Complete This Tonight!

## ⏱️ Timeline: 4-5 Hours Total

**Phase 1: Setup (30 min)**
**Phase 2: Configuration (45 min)**
**Phase 3: Local Testing (60 min)**
**Phase 4: Deployment (75 min)**
**Phase 5: Demo Video (45 min)**

---

## 📍 PHASE 1: QUICK SETUP (30 minutes)

### Step 1.1: Create GitHub Repository
```bash
# On GitHub.com:
1. Go to github.com/new
2. Repo name: "card-digitization" or similar
3. Make it PUBLIC (for sharing)
4. Add README (optional)
5. Create repository

# Get the clone URL
```

### Step 1.2: Initialize Your Project
```bash
# Clone or create local repo
mkdir card-digitization
cd card-digitization
git init
git remote add origin <your-github-url>

# Copy all the files I've created into this folder
# - main.py
# - requirements.txt
# - .env.example
# - Dockerfile
# - docker-compose.yml
# - README.md
# - ChatUI.jsx
# - ChatUI.css

# Create frontend directory
mkdir frontend
mkdir frontend/src
mkdir frontend/src/components
mkdir frontend/public

# Copy frontend files into frontend/src/components/
# Place package.json in frontend/

# Add all to git
git add .
git commit -m "Initial commit - Card Digitization System"
```

### Step 1.3: Python & Node Setup
```bash
# Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm init -y
# Or use the package.json I provided
npm install

cd ..
```

✅ **Phase 1 Complete!**

---

## 🔑 PHASE 2: CONFIGURATION (45 minutes)

### Step 2.1: Get Anthropic API Key (5 min) ⭐
**REQUIRED**

```bash
1. Go to: https://console.anthropic.com/
2. Sign in / Create account
3. Click "API Keys"
4. Create new API key
5. Copy the key (starts with sk_ant_)
6. Save somewhere safe

# This is CRITICAL - you NEED this to run
```

### Step 2.2: Google Cloud Setup (15 min) ⭐
**REQUIRED for Google Sheets integration**

```bash
# Part A: Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create new project: "Card Digitization"
3. Enable APIs:
   - Search "Vision API" → Enable
   - Search "Google Sheets API" → Enable
   - Search "Google Drive API" → Enable

# Part B: Create Service Account
1. APIs & Services → Service Accounts
2. Create Service Account
3. Name: "card-digitization-sa"
4. Grant roles: Basic Editor
5. Create key → JSON format
6. Download the JSON file
7. **COPY THE ENTIRE JSON CONTENT**

# Part C: Create Google Sheet
1. Go to https://sheets.google.com
2. Create new sheet
3. Name it: "Contact Cards"
4. Add headers: Name | Phone | Email | Company | Designation | Voice_Note_URL
5. Copy Sheet ID from URL:
   https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit
6. Share the sheet with service account email:
   (from JSON: "client_email": "xxx@yyy.iam.gserviceaccount.com")
   - Right-click → Share
   - Paste email
   - Give Editor permission
```

### Step 2.3: MongoDB Atlas Setup (10 min) ⭐
**REQUIRED for session storage**

```bash
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up (free tier)
3. Create M0 free cluster
4. Wait for cluster to be ready (~5 min)
5. Click "Connect"
6. Add IP Address: 0.0.0.0/0 (allows all IPs)
7. Create Database User: username/password
8. Choose "Drivers" connection
9. Copy connection string:
   mongodb+srv://username:password@cluster.mongodb.net/card_digitization?retryWrites=true&w=majority
```

### Step 2.4: WhatsApp Business API (Optional but recommended) (15 min)
**Optional - if you want WhatsApp notifications**

```bash
# If you have WhatsApp Business Account:
1. Go to https://developers.facebook.com/
2. Create/Select App
3. Add WhatsApp Business Platform
4. Get Phone Number ID
5. Get Temporary Access Token

# If you don't have it:
# Just skip this step - the system will still work
# (notifications will be logged but not sent)
```

### Step 2.5: Create .env File
```bash
# In your project root, create .env file:

ANTHROPIC_API_KEY=sk_ant_xxxxxxxxxxxx

GOOGLE_SHEETS_ID=1BxiMVs0XRA5nFMKUVfIrWK_eDp2vB5X8pz8nC_H89jQ

GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project-id","private_key_id":"xxx","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQE...-----END PRIVATE KEY-----\n","client_email":"xxx@iam.gserviceaccount.com","client_id":"123","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs"}

MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/card_digitization?retryWrites=true&w=majority

WHATSAPP_API_TOKEN=your_token_here_or_leave_blank
WHATSAPP_PHONE_ID=your_phone_id_or_leave_blank
MANAGER_PHONE=+1234567890

# Important: Keep this file SECRET! Add to .gitignore
```

### Step 2.6: Verify .env Setup
```bash
# Test if Python can load the env
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ .env loaded successfully')"

# You should see: ✓ .env loaded successfully
```

✅ **Phase 2 Complete!**

---

## 🧪 PHASE 3: LOCAL TESTING (60 minutes)

### Step 3.1: Start Backend

```bash
# Terminal 1: Backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py

# You should see:
# 🚀 Starting Card Digitization API...
# ✓ MongoDB connected
# ✓ Google Sheets API authenticated
# Uvicorn running on http://0.0.0.0:8000
```

### Step 3.2: Check Backend Health
```bash
# Terminal 2: Health check
curl http://localhost:8000/health

# Should return JSON with service statuses
```

### Step 3.3: Start Frontend

```bash
# Terminal 3: Frontend
cd frontend
npm start

# Should open http://localhost:3000 automatically
```

### Step 3.4: Full System Test

#### Test 1: Upload Card Image ✅
1. Open http://localhost:3000 in browser
2. Click "Upload Card" button
3. Select any business card image (or create a test image)
4. Verify:
   - Card details extracted
   - Data appears in chat
   - No errors in console

#### Test 2: Check Google Sheets ✅
1. Go to your Google Sheet
2. Should see new row with contact data
3. Verify: Name, Phone, Email, Company appear

#### Test 3: Check MongoDB ✅
1. Go to MongoDB Atlas → Collections
2. Look at `card_digitization.sessions`
3. Should see your session data

#### Test 4: WhatsApp (if configured) ✅
1. Check your WhatsApp for message from bot
2. Should show contact details

#### Test 5: Upload Voice Note ✅
1. In chat UI, click "Record" button
2. Record a few seconds of audio
3. Click "Stop"
4. Verify message appears in chat
5. Check Google Sheet - should have voice_note_url

#### Test 6: Duplicate Detection ✅
1. Upload the SAME card image again
2. Should show duplicate warning
3. Should NOT add to sheets again

### Step 3.5: Verify All Integrations
```bash
# Check backend logs for any errors
# Check browser console (F12) for frontend errors
# Check Google Sheets for data
# Check MongoDB for sessions
```

✅ **Phase 3 Complete!**

---

## 🌐 PHASE 4: CLOUD DEPLOYMENT (75 minutes)

### Option A: Deploy to Render.com (Recommended - Easiest) 
**Estimated time: 30 min**

#### Backend Deployment:

```bash
# Step 1: Push to GitHub
git add .
git commit -m "Ready for production"
git push origin main

# Step 2: Go to https://render.com/
# Step 3: Sign up / Sign in with GitHub
# Step 4: Create New → Web Service
# Step 5: Select your GitHub repo
# Step 6: Configuration:
Service Name:     card-digitization-api
Environment:      Python 3
Build Command:    pip install -r requirements.txt
Start Command:    uvicorn main:app --host 0.0.0.0 --port 8000
# Step 7: Add Environment Variables:
#   - ANTHROPIC_API_KEY
#   - GOOGLE_SHEETS_ID
#   - GOOGLE_CREDENTIALS_JSON
#   - MONGODB_URI
#   - WHATSAPP_API_TOKEN (optional)
#   - WHATSAPP_PHONE_ID (optional)
#   - MANAGER_PHONE (optional)
# Step 8: Click Deploy
# ⏳ Wait 3-5 minutes
# ✅ You'll get a URL like: https://card-digitization-api.onrender.com
```

#### Frontend Deployment:

```bash
# Step 1: Create render.yaml in project root:

services:
  - type: web
    name: card-digitization-frontend
    environment: static
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/build
    envVars:
      - key: REACT_APP_API_URL
        value: https://card-digitization-api.onrender.com

# Step 2: Go to Render → Create New → Static Site
# Step 3: Select your GitHub repo
# Step 4: Configuration:
Name:                 card-digitization-frontend
Build Command:        cd frontend && npm install && npm run build
Publish Directory:    frontend/build
# Step 5: Add Environment Variable:
REACT_APP_API_URL=https://card-digitization-api.onrender.com
# Step 6: Deploy
# ⏳ Wait 2-3 minutes
# ✅ You'll get a URL like: https://card-digitization-frontend.onrender.com
```

#### Update Frontend Code:
```bash
# In frontend/src/components/ChatUI.jsx, update:
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

# This reads from the environment variable automatically
```

### Option B: Docker Deployment (If using Docker)

```bash
# Build locally
docker build -t card-digitization:latest .

# Push to Docker Hub
docker tag card-digitization:latest YOUR_DOCKERHUB_USERNAME/card-digitization:latest
docker push YOUR_DOCKERHUB_USERNAME/card-digitization:latest

# Then deploy using docker-compose on a server
```

### Verify Deployment:

```bash
# Test backend
curl https://card-digitization-api.onrender.com/health

# Should return service status JSON

# Test frontend
Open https://card-digitization-frontend.onrender.com in browser
# Should load the chat UI
```

✅ **Phase 4 Complete!**

---

## 🎥 PHASE 5: DEMO VIDEO (45 minutes)

### Record with Loom (Free & Easy)

```bash
# Step 1: Go to https://www.loom.com/
# Step 2: Sign up (free)
# Step 3: Install browser extension
# Step 4: Start recording
# Step 5: Follow this script:

DEMO SCRIPT (3-5 minutes):
═══════════════════════════════════════════

Scene 1: Introduction (15 seconds)
────────────────────────────────
"Hi, this is the Card Digitization System. 
I'll demonstrate the complete workflow."

Scene 2: Upload Card Image (30 seconds)
──────────────────────────────────────
- Show the chat UI
- Click "Upload Card" button
- Select a business card image
- Watch it extract Name, Phone, Email, Company
- Narrate: "The AI Vision model extracts contact details"

Scene 3: Google Sheets Integration (30 seconds)
───────────────────────────────────────────────
- Open Google Sheet in new tab
- Show new row added with extracted data
- Narrate: "The contact is automatically logged with deduplication"

Scene 4: WhatsApp Notification (15 seconds)
──────────────────────────────────────────
- Show WhatsApp/chat notification (if configured)
- Narrate: "Manager receives instant WhatsApp notification"

Scene 5: Voice Note Upload (45 seconds)
─────────────────────────────────────
- Click "Record" button in UI
- Record 5-10 seconds audio: "Meeting notes for this contact"
- Click "Stop"
- Show message in chat: "Voice note recorded"
- Switch to Google Sheet
- Show voice_note_url column updated
- Narrate: "Voice notes are linked to the specific contact"

Scene 6: Duplicate Detection (30 seconds)
────────────────────────────────────────
- Upload the same card again
- Show duplicate detection message
- Narrate: "System prevents duplicate entries"

Scene 7: System Architecture (30 seconds)
────────────────────────────────────────
- Show the README or architecture diagram
- Narrate: "Powered by LangGraph for AI orchestration,
           FastAPI backend, React frontend, integrated with
           Google Sheets, MongoDB, and WhatsApp APIs"

Scene 8: Deployment (30 seconds)
───────────────────────────────
- Show deployed URLs
- Click both links
- Show them working online
- Narrate: "The complete system is deployed and working in production"

TOTAL: ~4 minutes
═══════════════════════════════════════════

# Step 6: Stop recording
# Step 7: Save/Share
# Step 8: Copy link
```

### Add Links to README
```markdown
## 🎥 Demo Video

Watch the complete system in action:
[View Demo Video](https://www.loom.com/share/xxxxx)

## 🌐 Live Deployment

- **Frontend:** https://card-digitization-frontend.onrender.com
- **Backend API:** https://card-digitization-api.onrender.com/docs

## 📊 GitHub Repository

https://github.com/yourusername/card-digitization
```

✅ **Phase 5 Complete!**

---

## 📤 FINAL SUBMISSION CHECKLIST

Before submitting, verify ALL of these:

### Code Repository
- [ ] GitHub repo is PUBLIC
- [ ] All code is committed and pushed
- [ ] .env.example file is present (with NO real keys)
- [ ] README.md is complete and clear
- [ ] Dockerfile works
- [ ] Requirements.txt has all dependencies

### Backend
- [ ] Backend deploys successfully
- [ ] `/health` endpoint returns service status
- [ ] `/api/chat` endpoint works
- [ ] Google Sheets integration functional
- [ ] MongoDB connection working
- [ ] WhatsApp notification (attempted/configured)

### Frontend
- [ ] Frontend deploys successfully
- [ ] Chat UI is responsive
- [ ] Image upload works
- [ ] Audio recording works
- [ ] Messages display properly
- [ ] Connected to deployed backend

### Integration
- [ ] Card image extracts data ✅
- [ ] Data logs to Google Sheets ✅
- [ ] Duplicates are detected ✅
- [ ] Voice notes are recorded ✅
- [ ] Sheet updates with voice URL ✅
- [ ] WhatsApp notification (if configured) ✅

### Documentation
- [ ] README has setup instructions
- [ ] README has architecture diagram
- [ ] Environment variables documented
- [ ] API endpoints documented
- [ ] Deployment guide included
- [ ] Troubleshooting section present

### Demo Video
- [ ] Video is 3-5 minutes
- [ ] Shows all key features
- [ ] Link added to README
- [ ] Video is publicly accessible

### Deployment
- [ ] Backend URL works
- [ ] Frontend URL works
- [ ] Health check passes
- [ ] Session state preserved
- [ ] Data persists in MongoDB

---

## 🎯 Success Criteria (for 30/30 points)

✅ **Agentic Logic (30%):** Single LangGraph agent manages all steps
✅ **System Integration (20%):** All APIs integrated and working
✅ **Deduplication (20%):** Duplicates detected, voice notes linked
✅ **Cloud Deployment (20%):** Both services deployed, secrets managed
✅ **Code Quality (10%):** Clean, documented, modular code

---

## ⏱️ TIMELINE SUMMARY

- **Now to 30 min:** Phase 1 - Setup
- **30 min to 75 min:** Phase 2 - Configuration  ⭐ Critical: Get credentials!
- **75 min to 135 min:** Phase 3 - Local Testing
- **135 min to 210 min:** Phase 4 - Cloud Deployment (Render.com)
- **210 min to 255 min:** Phase 5 - Demo Video & Final Checks

**Total: ~4.5 hours**

This leaves you time for troubleshooting and final polish!

---

## 🆘 IF YOU GET STUCK

### Issue: "ModuleNotFoundError: No module named..."
```bash
pip install -r requirements.txt
# Make sure venv is activated
```

### Issue: "Google Sheets not updating"
```bash
1. Check GOOGLE_SHEETS_ID is correct
2. Verify service account email has edit access
3. Check MongoDB is connected
```

### Issue: "CORS error in frontend"
```bash
# CORS is already enabled in main.py
# Just verify backend URL in frontend env
```

### Issue: "Deploy fails"
```bash
# Check Render build logs
# Verify all env vars are set
# Check requirements.txt for version conflicts
```

---

**YOU'VE GOT THIS! 🚀**

Estimated total time: **4-5 hours** ⏱️
Submission deadline: **Tonight** 🎯

All the code is ready. Just follow these steps and you'll submit on time!

---

**Questions?** Check the README troubleshooting section or look at your backend logs with: `docker logs backend`

**Good luck! 💪**
