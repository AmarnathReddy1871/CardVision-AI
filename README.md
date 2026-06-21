# 📇 Card Digitization & Voice Notes Orchestrator

> An AI-powered system that digitizes visiting cards, logs them to Google Sheets, sends WhatsApp notifications, and handles voice notes using LangGraph orchestration.

## 🎯 Quick Start (15 minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- Git

### 1️⃣ Clone & Setup

```bash
git clone <your-repo-url>
cd card-digitization
cp .env.example .env
```

### 2️⃣ Get Your Credentials (5 minutes)

#### A. Anthropic API Key
1. Visit https://console.anthropic.com/
2. Create API key and copy it
3. Add to `.env`: `ANTHROPIC_API_KEY=sk_...`

#### B. Google Cloud Setup
1. Go to https://console.cloud.google.com/
2. Create new project (e.g., "Card Digitization")
3. Enable APIs:
   - Vision API
   - Google Sheets API
   - Google Drive API
4. Create Service Account:
   - APIs & Services → Service Accounts
   - Create Service Account
   - Create JSON key
   - Download the JSON file
5. Create Google Sheet:
   - Go to https://sheets.google.com/
   - Create new sheet
   - Copy the Sheet ID from URL: `docs.google.com/spreadsheets/d/SHEET_ID/edit`
   - Share sheet with service account email
6. Update `.env`:
   ```
   GOOGLE_SHEETS_ID=<your_sheet_id>
   GOOGLE_CREDENTIALS_JSON=<entire_json_content_from_key_file>
   ```

#### C. MongoDB Atlas
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free M0 cluster
3. Get connection string from "Connect" button
4. Update `.env`: `MONGODB_URI=mongodb+srv://...`

#### D. WhatsApp Business API (Optional - for notifications)
1. Go to https://developers.facebook.com/
2. Create App → WhatsApp Business Platform
3. Get Phone Number ID and Temporary Access Token
4. Update `.env`:
   ```
   WHATSAPP_API_TOKEN=<token>
   WHATSAPP_PHONE_ID=<phone_id>
   MANAGER_PHONE=+1234567890
   ```

### 3️⃣ Local Development

#### Option A: Docker Compose (Easiest)
```bash
docker-compose up
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Docs: http://localhost:8000/docs

#### Option B: Manual Setup

**Backend:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Backend runs at http://localhost:8000

**Frontend:**
```bash
cd frontend
npm install
npm start
```
Frontend runs at http://localhost:3000

### 4️⃣ Test the System

1. Open http://localhost:3000
2. Upload a visiting card image
3. Verify extraction in the UI
4. Check Google Sheets for new entry
5. Verify WhatsApp notification
6. Upload a voice note
7. Verify sheet update

---

## 🏗️ Architecture

### System Flow

```
┌─────────────┐
│  React UI   │  (Chat Interface)
└──────┬──────┘
       │ (Image/Audio uploads)
       ▼
┌─────────────────────────────┐
│  FastAPI + LangGraph Agent  │  (Orchestration)
├─────────────────────────────┤
│ 1. Extract card (Claude Vision)
│ 2. Check duplicates (MongoDB)
│ 3. Log to Google Sheets
│ 4. Send WhatsApp notification
│ 5. Handle voice notes
└─────────────────────────────┘
       │
       ├──► Google Sheets (Data Storage)
       ├──► MongoDB (Session State)
       ├──► WhatsApp API (Notifications)
       └──► Claude API (AI Processing)
```

### LangGraph Agent State Machine

```
START
  │
  ▼
┌─────────────────┐
│  AWAITING_CARD  │ (Waiting for card image)
└────────┬────────┘
         │ (Image uploaded)
         ▼
┌──────────────────────┐
│  PROCESSING_CARD     │ (Extracting data)
└────────┬─────────────┘
         │
         ▼
┌──────────────────────────┐
│  CHECK_DUPLICATE         │ (Query MongoDB/Sheets)
└────────┬─────────────────┘
         │
    ┌────┴────┐
    │          │
 (NEW)      (DUP)
    │          │
    ▼          ▼
┌────────┐  ┌──────────┐
│ ADD    │  │ SKIP     │
│SHEETS  │  │ ADD      │
└───┬────┘  └──────────┘
    │
    ▼
┌──────────────────┐
│SEND_WHATSAPP     │
└───────┬──────────┘
        │
        ▼
┌──────────────────┐
│AWAITING_VOICE    │ (Waiting for voice note)
└───────┬──────────┘
        │ (Voice uploaded or skip)
        ▼
┌──────────────────┐
│COMPLETE/RESET    │ (Ready for next card)
└──────────────────┘
```

---

## 📚 API Endpoints

### Health Check
```
GET /health
```
Returns service status (MongoDB, Google Sheets, Anthropic)

### Chat Endpoint (Main)
```
POST /api/chat
Content-Type: application/json

{
  "session_id": "session_123",
  "user_id": "user_456",
  "message": "Optional text",
  "image_base64": "base64_encoded_image",
  "audio_base64": "base64_encoded_audio"
}
```

**Response:**
```json
{
  "session_id": "session_123",
  "messages": [
    {
      "type": "status|success|error|confirmation|prompt",
      "content": "Message text",
      "contact": {...}
    }
  ],
  "session_state": {
    "step": "awaiting_card|processing_card|awaiting_voice|complete",
    "current_contact": {...}
  }
}
```

### Get Session State
```
GET /api/session/{session_id}?user_id=user_456
```

### List Contacts
```
GET /api/contacts?user_id=user_456&skip=0&limit=50
```

### API Docs
```
GET /docs  (Swagger UI)
GET /redoc (ReDoc)
```

---

## 🚀 Deployment (Production)

### Option 1: Render.com (Easiest - Free tier available)

1. **Prepare:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy Backend:**
   - Go to https://render.com/
   - Connect GitHub repo
   - Create New → Web Service
   - Select your repo
   - Settings:
     ```
     Name: card-digitization-api
     Environment: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn main:app --host 0.0.0.0 --port 8000
     ```
   - Add Environment Variables from `.env`
   - Deploy

3. **Deploy Frontend:**
   - Create New → Static Site
   - Select repo
   - Settings:
     ```
     Name: card-digitization-ui
     Build Command: cd frontend && npm install && npm run build
     Publish Directory: frontend/build
     ```
   - Add env: `REACT_APP_API_URL=<backend_url>`
   - Deploy

4. **Update Frontend API URL:**
   ```bash
   # In frontend/.env
   REACT_APP_API_URL=https://card-digitization-api.onrender.com
   ```

### Option 2: GCP Cloud Run

```bash
# Build and push Docker image
docker build -t gcr.io/YOUR_PROJECT/card-digitization .
docker push gcr.io/YOUR_PROJECT/card-digitization

# Deploy to Cloud Run
gcloud run deploy card-digitization \
  --image gcr.io/YOUR_PROJECT/card-digitization \
  --platform managed \
  --region us-central1 \
  --set-env-vars MONGODB_URI=$MONGODB_URI,ANTHROPIC_API_KEY=$KEY...
```

### Option 3: AWS Lambda + API Gateway

```bash
# Create SAM template (serverless.yaml)
# Deploy with: sam deploy --guided
```

### Secrets Management

**For Render:**
- Use "Secrets" feature in project settings
- Auto-loads from environment variables

**For GCP Cloud Run:**
```bash
gcloud secrets create anthropic-key --data-file=- <<< $ANTHROPIC_API_KEY
gcloud run services update card-digitization \
  --set-env-vars=ANTHROPIC_API_KEY=anthropic-key
```

**For AWS:**
- Use AWS Secrets Manager
- Reference in Lambda environment

---

## 🎥 Creating Demo Video (3-5 minutes)

### Record with Loom (Free):
1. Go to https://www.loom.com/
2. Install extension
3. Start recording
4. Demo flow:
   - ✅ Open app
   - ✅ Upload card image
   - ✅ Show extraction
   - ✅ Show Google Sheet update
   - ✅ Show WhatsApp notification
   - ✅ Upload voice note
   - ✅ Show sheet update with voice URL
5. Save and share link

### Recording Checklist:
- [ ] Clear, audible narration
- [ ] Show all key steps
- [ ] Highlight data flow
- [ ] Show final results
- [ ] Include error handling (if any)

---

## 📊 Monitoring & Logging

### Health Checks
```bash
# Check backend health
curl http://localhost:8000/health

# Logs
docker logs <container_id>
```

### Database Inspection
```bash
# MongoDB Atlas
# Visit https://cloud.mongodb.com/ → Collections tab

# Local MongoDB
mongosh
use card_digitization
db.sessions.find()
db.contacts.find()
```

### Google Sheets Verification
1. Go to your Google Sheet
2. Verify new rows added with correct data
3. Check for duplicate detection working

---

## 🐛 Troubleshooting

### Issue: "Google Sheets API error"
**Solution:**
- Verify `GOOGLE_SHEETS_ID` is correct
- Check service account has Sheet edit permissions
- Validate `GOOGLE_CREDENTIALS_JSON` is properly escaped

### Issue: "MongoDB connection failed"
**Solution:**
- Verify `MONGODB_URI` is correct
- Check IP whitelist in Atlas (add 0.0.0.0/0 for development)
- Ensure network connectivity

### Issue: "WhatsApp not sending"
**Solution:**
- Verify token is valid and not expired
- Check `MANAGER_PHONE` format: +<country_code><number>
- Ensure phone number is registered in WhatsApp Business

### Issue: "CORS error in frontend"
**Solution:**
- Backend CORS is enabled for all origins
- Verify `REACT_APP_API_URL` matches backend URL
- Check browser console for actual error

### Issue: "Claude API error"
**Solution:**
- Verify `ANTHROPIC_API_KEY` is correct
- Check API rate limits
- Ensure Vision API calls include valid base64 image

---

## 📋 Evaluation Checklist

- [ ] **Agentic Logic (30%)**
  - [ ] Single LangGraph agent orchestrates all tasks
  - [ ] State machine properly transitions between steps
  - [ ] Conversation history maintained across interactions

- [ ] **System Integration (20%)**
  - [ ] Chat UI communicates with FastAPI
  - [ ] Vision extraction works
  - [ ] Google Sheets API integration functional
  - [ ] WhatsApp notifications send successfully

- [ ] **Deduplication Logic (20%)**
  - [ ] Duplicate detection works (by email/phone)
  - [ ] Graceful handling of duplicates in UI
  - [ ] Voice notes linked to correct contact

- [ ] **Cloud Deployment (20%)**
  - [ ] Backend deployed and accessible
  - [ ] Frontend deployed and functional
  - [ ] Secrets properly managed
  - [ ] Containerization works

- [ ] **Code Quality (10%)**
  - [ ] Clean, modular code structure
  - [ ] FastAPI endpoints well-documented
  - [ ] Agent state machine clearly defined
  - [ ] Error handling implemented

---

## 📁 Project Structure

```
card-digitization/
├── main.py                  # FastAPI + LangGraph orchestration
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Local dev stack
├── .env.example            # Environment template
├── README.md               # This file
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatUI.jsx
│   │   ├── ChatUI.css
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── .env
├── .github/
│   └── workflows/
│       └── deploy.yml      # CI/CD pipeline
└── docs/
    ├── ARCHITECTURE.md
    ├── API_REFERENCE.md
    └── DEPLOYMENT_GUIDE.md
```

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Create Pull Request

---

## 📄 License

MIT License - feel free to use for your assignment!

---

## 🆘 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review API logs: `docker logs backend`
3. Check MongoDB collections for data
4. Verify all credentials in `.env`

---

## ✅ Submission Checklist

Before submitting:

- [ ] GitHub repo public/shared
- [ ] README complete with setup instructions
- [ ] All credentials working in `.env`
- [ ] Local testing passed (all 7 tasks working)
- [ ] Backend deployed and functional
- [ ] Frontend deployed and functional
- [ ] Demo video recorded (3-5 min)
- [ ] Video links added to README
- [ ] Code is clean and documented

---

**Good luck with your submission! 🚀**

**Last Updated:** 2024
**Version:** 1.0.0
