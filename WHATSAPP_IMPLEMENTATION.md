# 📱 WhatsApp Implementation Guide (For Later)

## Where I Added Comments in main_python313.py

### 1. Line ~184: WhatsApp Configuration (Commented Out)

```python
# WhatsApp Configuration (Optional - implement later)
# WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")
# WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
# MANAGER_PHONE = os.getenv("MANAGER_PHONE", "+1234567890")
```

**To Enable:** Uncomment these 3 lines when you have WhatsApp credentials

---

### 2. Line ~326: send_whatsapp_notification() Function

The function is fully documented with a TODO block:

```python
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
```

**Current Implementation:** Just logs that a notification would be sent

---

## How to Enable WhatsApp Later

### Step 1: Uncomment Configuration (Line 184-186)
```python
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
MANAGER_PHONE = os.getenv("MANAGER_PHONE", "+1234567890")
```

### Step 2: Add to .env
```bash
WHATSAPP_API_TOKEN=your_token_from_meta
WHATSAPP_PHONE_ID=your_phone_id
MANAGER_PHONE=+1234567890
```

### Step 3: Replace send_whatsapp_notification() Function

Replace the function body with:

```python
async def send_whatsapp_notification(contact: ContactData) -> dict:
    """Send WhatsApp message to manager about new card"""
    
    if not WHATSAPP_API_TOKEN or not WHATSAPP_PHONE_ID:
        print("⚠️ WhatsApp credentials not configured")
        return {"success": False, "message": "WhatsApp not configured"}
    
    try:
        message_text = f"""
📇 New Contact Digitized!

Name: {contact.name}
Phone: {contact.phone or 'N/A'}
Email: {contact.email or 'N/A'}
Company: {contact.company or 'N/A'}
Designation: {contact.designation or 'N/A'}

Logged at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        url = f"https://graph.instagram.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": MANAGER_PHONE.replace("+", ""),
            "type": "text",
            "text": {"body": message_text}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return {"success": True, "message": "WhatsApp notification sent"}
        else:
            return {
                "success": False,
                "error": f"WhatsApp API error: {response.text}"
            }
    except Exception as e:
        print(f"WhatsApp error: {e}")
        return {"success": False, "error": str(e)}
```

---

## For Now (Current Status)

✅ **What Works:**
- Card extraction (Google Vision)
- Google Sheets integration
- Duplicate detection
- Voice note handling
- MongoDB session storage

⏸️ **What's Pending:**
- WhatsApp notifications (all comments in place, ready to implement)

---

## Testing the Current System

### Run without WhatsApp:
```bash
python main_python313.py
# All features work, WhatsApp just logs success
```

### Test the app:
```bash
# In browser: http://localhost:3000
# Upload a card → Should extract and log to Sheets
# Record voice → Should link to contact
# WhatsApp → Logs success (no actual message sent)
```

---

## When You're Ready for WhatsApp

Just:
1. Get WhatsApp Business API credentials
2. Uncomment 3 lines at line 184-186
3. Replace the function body (copy code above)
4. Add credentials to .env
5. Restart backend
6. WhatsApp notifications now send!

---

## Files Updated for Python 3.13.14

✅ **main_python313.py** - Use this file!
✅ **requirements.txt** - Updated for Python 3.13.14

---

## How to Use main_python313.py

```bash
# Rename the file:
mv main_python313.py main.py

# Or keep both:
# Use main_python313.py as your main backend file

# Install requirements:
pip install -r requirements.txt

# Run:
python main.py
```

---

## Comments in main_python313.py

All WhatsApp-related code has:
- ✅ Clear TODO comments
- ✅ Implementation steps documented
- ✅ Reference links to API docs
- ✅ Example code provided above

**No need to do anything now** - just focus on testing the core features!

---

**Status: Ready for Local Testing** ✅
