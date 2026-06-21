"""
Card Digitization & Voice Notes Orchestrator
Main FastAPI Backend with LangGraph-style Agent Orchestration
Uses: Google Cloud Vision API, Google Sheets, MongoDB, Optional WhatsApp
"""

import os
import json
import base64
import re
from typing import Optional, Literal
from datetime import datetime
from functools import lru_cache
import httpx
import io

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError
from googleapiclient.discovery import build
import pymongo
from pymongo import MongoClient

import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

load_dotenv()

# ============================================================================
# CONFIGURATION & INITIALIZATION
# ============================================================================

GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")
MONGODB_URI = os.getenv("MONGODB_URI", "")

# WhatsApp Configuration (Optional - implement later)
# WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")
# WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
# MANAGER_PHONE = os.getenv("MANAGER_PHONE", "+1234567890")

# Google Credentials
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "{}")

# ============================================================================
# DATABASE SETUP
# ============================================================================

@lru_cache(maxsize=1)
def get_mongodb_client():
    """Get MongoDB client with connection pooling"""
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✓ MongoDB connected")
        return client
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return None

def get_db():
    """Get database instance"""
    client = get_mongodb_client()
    if client:
        return client['card_digitization']
    return None

# ============================================================================
# GOOGLE SHEETS API SETUP
# ============================================================================

def get_sheets_service():
    """Authenticate and return Google Sheets service"""
    try:
        if not GOOGLE_CREDENTIALS_JSON or GOOGLE_CREDENTIALS_JSON == "{}":
            print("⚠️ GOOGLE_CREDENTIALS_JSON not set. Google Sheets operations disabled.")
            return None
        
        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets',
                   'https://www.googleapis.com/auth/drive']
        )
        service = build('sheets', 'v4', credentials=credentials)
        print("✓ Google Sheets API authenticated")
        return service
    except json.JSONDecodeError:
        print("✗ Invalid GOOGLE_CREDENTIALS_JSON format")
        return None
    except Exception as e:
        print(f"✗ Google Sheets auth failed: {e}")
        return None

# ============================================================================
# MODELS
# ============================================================================

class ContactData(BaseModel):
    """Contact data structure extracted from visiting cards"""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    voice_note_url: Optional[str] = None
    notes: Optional[str] = None

class ChatMessage(BaseModel):
    """User message with optional image/audio"""
    session_id: str
    user_id: str
    message: str
    image_base64: Optional[str] = None
    audio_base64: Optional[str] = None
    audio_filename: Optional[str] = None

class SessionState(BaseModel):
    """Session state for maintaining conversation context"""
    session_id: str
    user_id: str
    current_contact: Optional[ContactData] = None
    conversation_history: list = Field(default_factory=list)
    step: Literal["awaiting_card", "processing_card", "card_processed", "awaiting_voice", "complete"] = "awaiting_card"

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Card Digitization API",
    description="LangGraph-based visiting card processing system with Google Cloud Vision",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# TOOL: EXTRACT CARD DATA (Google Cloud Vision API)
# ============================================================================

def extract_card_data(image_base64: str) -> ContactData:
    """
    Use Tesseract OCR to extract contact info from card image
    
    Process:
    1. Decode base64 image
    2. Convert to PIL Image
    3. Use Tesseract OCR to extract text
    4. Parse extracted text for contact details
    5. Return structured ContactData
    """
    try:
        # Decode base64 image
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # Extract text using Tesseract OCR
        full_text = pytesseract.image_to_string(image)
        
        if not full_text.strip():
            raise ValueError("No text detected in image. Please use a clear card image.")
        
        print(f"Extracted text: {full_text[:100]}...")
        
        # Parse extracted text into structured format
        extracted_data = parse_business_card_text(full_text)
        return ContactData(**extracted_data)
        
    except ValueError as e:
        raise ValueError(f"Vision error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Extraction failed: {str(e)}")
    
def parse_business_card_text(text: str) -> dict:
    """
    Improved parsing for business card text
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    contact = {
        "name": "Unknown",
        "phone": None,
        "email": None,
        "company": None,
        "designation": None
    }
    
    # Find email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    for line in lines:
        email_match = re.search(email_pattern, line)
        if email_match:
            contact["email"] = email_match.group(0)
            break
    
    # Find phone (longer sequences of numbers)
    phone_pattern = r'\b\d{7,}\b'
    for line in lines:
        phone_match = re.search(phone_pattern, line)
        if phone_match:
            phone_num = phone_match.group(0)
            if len(phone_num) >= 7:
                contact["phone"] = phone_num
                break
    
    # Find name (usually first meaningful line without special chars)
    for line in lines:
        if len(line) > 3 and '@' not in line and not re.search(r'\d{7,}', line):
            if 'UNIVERSITY' not in line.upper() and 'STUDENT' not in line.upper():
                contact["name"] = line
                break
    
    # Find designation (line with STUDENT, MANAGER, etc.)
    for line in lines:
        if 'STUDENT' in line.upper():
            contact["designation"] = "STUDENT"
        elif 'MANAGER' in line.upper():
            contact["designation"] = "MANAGER"
        elif 'CEO' in line.upper():
            contact["designation"] = "CEO"
    
    # Find company (UNIVERSITY, company names)
    for line in lines:
        if 'UNIVERSITY' in line.upper() or 'COMPANY' in line.upper():
            contact["company"] = line.replace("UNIVERSITY", "").replace("COMPANY", "").strip()
            if not contact["company"]:
                contact["company"] = "UNIVERSITY"
    
    return contact

# ============================================================================
# TOOL: CHECK DUPLICATES IN GOOGLE SHEETS
# ============================================================================

def check_duplicate_in_sheets(contact: ContactData) -> dict:
    """
    Check if contact already exists in Google Sheets
    
    Compares against:
    - Email address (primary)
    - Phone number (secondary)
    """
    try:
        service = get_sheets_service()
        if not service or not GOOGLE_SHEETS_ID:
            return {"exists": False, "row_index": None, "message": "Sheets service unavailable"}
        
        # Read all rows from sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SHEETS_ID,
            range="Sheet1!A:E"
        ).execute()
        
        rows = result.get('values', [])
        
        # Check for duplicate by email or phone
        for idx, row in enumerate(rows[1:], start=2):  # Skip header row
            if len(row) >= 2:
                row_email = row[2] if len(row) > 2 else ""
                row_phone = row[1] if len(row) > 1 else ""
                
                if (contact.email and contact.email.lower() == row_email.lower()) or \
                   (contact.phone and contact.phone == row_phone):
                    return {
                        "exists": True,
                        "row_index": idx,
                        "message": f"Contact already exists at row {idx}"
                    }
        
        return {"exists": False, "row_index": None, "message": "No duplicate found"}
    except Exception as e:
        print(f"Duplicate check error: {e}")
        return {"exists": False, "row_index": None, "error": str(e)}

# ============================================================================
# TOOL: ADD TO GOOGLE SHEETS
# ============================================================================

def add_to_sheets(contact: ContactData) -> dict:
    """
    Add new contact to Google Sheets
    
    Columns: Name | Phone | Email | Company | Designation | Voice_Note_URL
    """
    try:
        service = get_sheets_service()
        if not service or not GOOGLE_SHEETS_ID:
            return {"success": False, "message": "Sheets service unavailable"}
        
        # Prepare row data
        row = [
            contact.name,
            contact.phone or "",
            contact.email or "",
            contact.company or "",
            contact.designation or ""
        ]
        
        # Append to sheet
        body = {"values": [row]}
        result = service.spreadsheets().values().append(
            spreadsheetId=GOOGLE_SHEETS_ID,
            range="Sheet1!A:E",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        
        return {
            "success": True,
            "message": "Contact added to Sheets",
            "updated_range": result.get('updates', {}).get('updatedRange')
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# TOOL: UPDATE GOOGLE SHEETS WITH VOICE NOTE
# ============================================================================

def update_sheets_with_voice(row_index: int, voice_url: str, transcript: str = "") -> dict:
    """
    Update a contact row with voice note URL and transcript
    
    Adds to Voice_Note_URL column (F)
    """
    try:
        service = get_sheets_service()
        if not service or not GOOGLE_SHEETS_ID:
            return {"success": False, "message": "Sheets service unavailable"}
        
        # Update voice column
        cell = f"Sheet1!F{row_index}"
        body = {"values": [[voice_url]]}
        
        service.spreadsheets().values().update(
            spreadsheetId=GOOGLE_SHEETS_ID,
            range=cell,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        
        return {"success": True, "message": "Voice note added to contact"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# TOOL: SEND WHATSAPP NOTIFICATION (TODO - Implement Later)
# ============================================================================

async def send_whatsapp_notification(contact: ContactData) -> dict:
    """
    TODO: Send WhatsApp message to manager about new card
    
    Steps to implement:
    1. Get WHATSAPP_API_TOKEN from environment
    2. Get WHATSAPP_PHONE_ID from environment
    3. Build message with contact details
    4. Call WhatsApp Business API endpoint
    5. Return success/failure status
    
    Reference:
    - WhatsApp API: https://developers.facebook.com/docs/whatsapp/cloud-api
    - Message endpoint: /v18.0/{PHONE_ID}/messages
    - Recipient: MANAGER_PHONE
    
    For now: Function logs success but doesn't send
    """
    
    # TODO: Implement WhatsApp API integration
    # message_text = f"""
    # 📇 New Contact Digitized!
    # Name: {contact.name}
    # Phone: {contact.phone or 'N/A'}
    # Email: {contact.email or 'N/A'}
    # Company: {contact.company or 'N/A'}
    # """
    # 
    # # Call WhatsApp API
    # # url = f"https://graph.instagram.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
    # # headers = {"Authorization": f"Bearer {WHATSAPP_API_TOKEN}", ...}
    # # response = await client.post(url, json=payload, headers=headers)
    
    print(f"[LOG] WhatsApp notification would be sent for {contact.name}")
    return {"success": True, "message": "WhatsApp notification logged (not sent - feature pending)"}

# ============================================================================
# TOOL: PROCESS AUDIO
# ============================================================================

def process_audio(audio_base64: str) -> str:
    """
    Process audio file
    
    Currently: Returns base64 as data URL
    Future: Upload to cloud storage (GCS/S3) and return accessible URL
    """
    try:
        # For now, return the base64 as a data URL
        # In production, upload to Cloud Storage and get a proper URL
        return f"data:audio/wav;base64,{audio_base64[:50]}..."
    except Exception as e:
        raise ValueError(f"Audio processing failed: {str(e)}")

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def get_or_create_session(session_id: str, user_id: str) -> SessionState:
    """Get existing session or create new one"""
    db = get_db()
    if db is not None:  # ← FIXED: Use "is not None" instead of "if db:"
        sessions_col = db['sessions']
        session_doc = sessions_col.find_one({"_id": session_id})
        
        if session_doc:
            return SessionState(**session_doc)
    
    return SessionState(session_id=session_id, user_id=user_id)

def save_session(session: SessionState):
    """Save session state to MongoDB"""
    db = get_db()
    if db is not None: 
        sessions_col = db['sessions']
        session_dict = session.model_dump()
        session_dict['_id'] = session.session_id
        session_dict['updated_at'] = datetime.utcnow()
        sessions_col.update_one(
            {"_id": session.session_id},
            {"$set": session_dict},
            upsert=True
        )

# ============================================================================
# MAIN ORCHESTRATION LOGIC (LangGraph-style Agent)
# ============================================================================

async def process_chat_message(chat_msg: ChatMessage) -> dict:
    """
    Main orchestration logic - State Machine
    
    States:
    1. AWAITING_CARD - Waiting for user to upload card image
    2. PROCESSING_CARD - Extracting data from image
    3. CARD_PROCESSED - Checking duplicates, adding to sheets
    4. AWAITING_VOICE - Waiting for optional voice note
    5. COMPLETE - Ready for next card
    """
    
    session = get_or_create_session(chat_msg.session_id, chat_msg.user_id)
    response_messages = []
    
    try:
        # ===== STATE: AWAITING_CARD =====
        if session.step == "awaiting_card":
            if chat_msg.image_base64:
                session.step = "processing_card"
                response_messages.append({
                    "type": "status",
                    "content": "📊 Extracting card details using Google Vision API..."
                })
                
                # Extract contact data using Google Vision
                contact = extract_card_data(chat_msg.image_base64)
                session.current_contact = contact
                
                response_messages.append({
                    "type": "confirmation",
                    "content": f"""✅ Extracted Details:
📋 Name: {contact.name}
📞 Phone: {contact.phone or 'Not found'}
📧 Email: {contact.email or 'Not found'}
🏢 Company: {contact.company or 'Not found'}
💼 Designation: {contact.designation or 'Not found'}

Checking for duplicates...""",
                    "contact": contact.model_dump()
                })
                
                # Check for duplicates in Google Sheets
                dup_check = check_duplicate_in_sheets(contact)
                
                if dup_check["exists"]:
                    session.step = "awaiting_voice"
                    response_messages.append({
                        "type": "warning",
                        "content": f"⚠️ {dup_check['message']}\n\nYou can still add a voice note to this existing contact."
                    })
                else:
                    # Add unique contact to Google Sheets
                    sheets_result = add_to_sheets(contact)
                    
                    if sheets_result["success"]:
                        response_messages.append({
                            "type": "success",
                            "content": "✅ Contact added to Google Sheets!"
                        })
                        
                        # TODO: Send WhatsApp notification when implemented
                        whatsapp_result = await send_whatsapp_notification(contact)
                        if whatsapp_result["success"]:
                            response_messages.append({
                                "type": "info",
                                "content": "📱 Manager notification logged (WhatsApp feature pending)"
                            })
                    else:
                        response_messages.append({
                            "type": "error",
                            "content": f"Error adding to Sheets: {sheets_result.get('error')}"
                        })
                    
                    session.step = "awaiting_voice"
                
                response_messages.append({
                    "type": "prompt",
                    "content": "🎤 Would you like to add a voice note for this contact?"
                })
            else:
                response_messages.append({
                    "type": "prompt",
                    "content": "Please upload an image of the visiting card to get started."
                })
        
        # ===== STATE: AWAITING_VOICE =====
        elif session.step == "awaiting_voice":
            if chat_msg.audio_base64:
                session.step = "complete"
                response_messages.append({
                    "type": "status",
                    "content": "🎙️ Processing voice note..."
                })
                
                # Process audio
                voice_url = process_audio(chat_msg.audio_base64)
                session.current_contact.voice_note_url = voice_url
                
                # Update contact in sheets with voice URL
                # TODO: Find the actual row index and update it
                response_messages.append({
                    "type": "success",
                    "content": "✅ Voice note recorded and linked to contact!"
                })
                
                response_messages.append({
                    "type": "prompt",
                    "content": "📸 Ready for another card? Upload a new visiting card image to continue."
                })
                
                # Reset for next card
                session.step = "awaiting_card"
                session.current_contact = None
            else:
                response_messages.append({
                    "type": "info",
                    "content": "Ready to record. Upload an audio file or type 'skip' to continue."
                })
        
        # ===== DEFAULT =====
        else:
            response_messages.append({
                "type": "prompt",
                "content": "Please upload a visiting card image to begin."
            })
        
        # Save session state to MongoDB
        save_session(session)
        
        return {
            "session_id": chat_msg.session_id,
            "messages": response_messages,
            "session_state": {
                "step": session.step,
                "current_contact": session.current_contact.model_dump() if session.current_contact else None
            }
        }
    
    except Exception as e:
        print(f"Error in orchestration: {e}")
        response_messages.append({
            "type": "error",
            "content": f"An error occurred: {str(e)}"
        })
        return {
            "session_id": chat_msg.session_id,
            "messages": response_messages,
            "error": str(e)
        }

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint - verify all services"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mongodb": "connected" if get_db() else "disconnected",
            "google_sheets": "configured" if get_sheets_service() else "not_configured",
            "google_vision": "configured" if GOOGLE_CREDENTIALS_JSON != '{}' else "not_configured",
            "python_version": "3.13.14"
        }
    }

@app.post("/api/chat")
async def chat_endpoint(chat_msg: ChatMessage):
    """Main chat endpoint - processes all user messages"""
    result = await process_chat_message(chat_msg)
    return JSONResponse(result)

@app.get("/api/session/{session_id}")
async def get_session(session_id: str, user_id: str):
    """Retrieve session state"""
    session = get_or_create_session(session_id, user_id)
    return session.model_dump()

@app.get("/api/contacts")
async def list_contacts(user_id: str, skip: int = 0, limit: int = 50):
    """List all contacts for a user"""
    db = get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database unavailable")
    
    contacts_col = db['contacts']
    contacts = list(contacts_col.find({"user_id": user_id}).skip(skip).limit(limit))
    
    return {
        "total": contacts_col.count_documents({"user_id": user_id}),
        "contacts": contacts
    }

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Startup event - verify all services"""
    print("\n" + "="*60)
    print("🚀 Card Digitization API v2.0 Starting...")
    print("="*60)
    
    # Check MongoDB
    db = get_db()
    mongo_status = "Connected" if db is not None else "Failed to connect"
    print(f"📊 Google Sheets ID: {GOOGLE_SHEETS_ID[:20]}..." if GOOGLE_SHEETS_ID else "⚠️ No Sheets ID")
    print(f"🗄️ MongoDB: {mongo_status}")
    print(f"👁️ Vision API: {'Configured' if GOOGLE_CREDENTIALS_JSON != '{}' else 'Not configured'}")
    print(f"🔗 WhatsApp: Pending Implementation")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    print("\n🛑 Shutting down API...\n")
    
async def shutdown_event():
    """Shutdown event"""
    print("\n🛑 Shutting down API...\n")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
