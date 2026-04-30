# 🚀 KeaBuilder AI - Complete Guide

## ✅ Project Restructuring Complete!

Your project now has a **production-ready modular architecture** with:

✨ **LLM Integration** (GPT-4 / Gemini)  
💾 **Conversation History Tracking**  
🔄 **HubSpot Workflow Triggers**  
🎨 **Beautiful Frontend Chat Widget**  

---

## 📁 New Project Structure

```
lead_form_generation/
├── app/
│   ├── api/endpoints.py                    ← FastAPI Routes
│   ├── services/ai_service.py              ← LLM Integration
│   ├── orchestrator.py                     ← Flow Manager
│   └── __init__.py
├── connector/
│   ├── hubspot.py                          ← CRM Integration
│   └── __init__.py
├── shared/
│   ├── config.py                           ← Configuration
│   ├── validation/schemas.py               ← Data Models
│   └── __init__.py
├── static/
│   └── index.html                          ← Chat UI
├── main.py                                 ← Entry Point
├── requirements.txt                        ← Dependencies
├── ARCHITECTURE.md                         ← Detailed Design
├── CHAT_API_GUIDE.md                       ← API Reference
└── .env.example                            ← Config Template
```

---

## ⚡ Quick Start (3 Steps)

### 1. Activate Environment
```bash
cd /home/rahulranjan/test/lead_form_generation
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python main.py
```

### 4. Open Chat UI
```
http://127.0.0.1:8001/static/index.html
```

---

## 🎯 What's New

### LLM-Powered Intent Detection
- **GPT-4** (OpenAI) or **Gemini** (Google)
- Automatic keyword fallback if no API key
- Better accuracy and context understanding
- File: `app/services/ai_service.py`

### Conversation History
- Per-user message storage
- Full context for better responses
- Get history: `GET /chat/{email}/history`
- Clear history: `DELETE /chat/{email}/history`
- File: `app/orchestrator.py`

### HubSpot Workflows
- Automatic workflow triggers based on intent
- Real-time contact sync
- Intent-based automation:
  - lead_qualification → hot_lead_workflow
  - demo_request → demo_scheduler
  - pricing_inquiry → send_pricing
  - complaint → escalate_support
- File: `connector/hubspot.py`

### Beautiful Chat Widget
- Real-time messaging
- User info persistence
- Intent badges
- Mobile responsive
- File: `static/index.html`

---

## 🔧 Configuration (Optional)

### Use LLM APIs
Create `.env` file:
```bash
# For GPT-4
OPENAI_API_KEY=your-openai-api-key

# OR for Gemini
GEMINI_API_KEY=your-gemini-api-key

# HubSpot (already configured)
HUBSPOT_ACCESS_TOKEN=your-hubspot-private-app-token
```

Restart the server - it will auto-detect the API key!

---

## 📊 System Flow

```
User → Chat Input
       ↓
   Orchestrator
       ├→ AI Service (LLM or Keywords)
       │  - Detect intent
       │  - Generate response
       │
       └→ HubSpot Connector (Background)
          - Create/Update contact
          - Log note
          - Trigger workflow
       ↓
   Instant Response
```

---

## 🧪 Test the System

### Via Frontend
1. Open `http://127.0.0.1:8001/static/index.html`
2. Enter email & name
3. Send: "We need a demo"
4. Watch intent detection & HubSpot sync

### Via cURL
```bash
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "test@company.com",
    "user_name": "Test User",
    "message": "We need a demo"
  }'
```

### Via API Docs
```
http://127.0.0.1:8001/docs
```

---

## 🎯 Intent Types

Try these messages in the chat:

| Message | Intent | Response |
|---------|--------|----------|
| "We need to launch in 4 weeks" | lead_qualification | Ask about goals |
| "Can you show me a demo?" | demo_request | Schedule demo |
| "What are your prices?" | pricing_inquiry | Send pricing |
| "Does it support HubSpot?" | feature_question | Answer question |
| "I found a bug" | complaint | Escalate support |

---

## 📚 Documentation

- **ARCHITECTURE.md** - Complete system design
- **CHAT_API_GUIDE.md** - API reference with examples
- **.env.example** - Configuration template

---

## ✨ Key Features

✅ **Production-Ready** - Modular, scalable architecture  
✅ **LLM Integration** - GPT-4 & Gemini support  
✅ **Conversation History** - Full context tracking  
✅ **HubSpot Sync** - Real-time CRM integration  
✅ **Beautiful UI** - Modern chat widget  
✅ **No Setup** - Works immediately (with fallback keywords)  

---

## 🚀 You're Ready!

Everything is configured and running. Start chatting!

```bash
# Server
python main.py

# Chat UI
http://127.0.0.1:8001/static/index.html
```

For detailed information, see ARCHITECTURE.md
