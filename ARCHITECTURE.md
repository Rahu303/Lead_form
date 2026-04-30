# KeaBuilder AI - Complete Modular Architecture

## 📁 Project Structure

```
lead_form_generation/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py              # FastAPI Routes (/chat, /leads/process, etc.)
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py             # LLM Intent Detection & Response Generation
│   ├── models/
│   │   └── __init__.py
│   └── orchestrator.py               # Core Flow Manager (Chat -> AI -> HubSpot)
├── connector/
│   ├── __init__.py
│   └── hubspot.py                    # HubSpot API Integration
├── shared/
│   ├── __init__.py
│   ├── config.py                     # API Keys, Constants, Environment Variables
│   └── validation/
│       ├── __init__.py
│       └── schemas.py                # Pydantic Models (LeadForm, ChatMessage, etc.)
├── static/
│   └── index.html                    # Interactive Frontend Chat Widget
├── main.py                           # FastAPI App Entry Point
├── requirements.txt                  # Python Dependencies
└── .env                              # Environment Variables (not in repo)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/rahulranjan/test/lead_form_generation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Environment Variables (Optional)

Create `.env` file:
```bash
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
HUBSPOT_ACCESS_TOKEN=your-hubspot-private-app-token
```

### 3. Run the Server

```bash
python main.py
```

Server runs at: `http://127.0.0.1:8000`

### 4. Open the Chat UI

Visit: `http://127.0.0.1:8000/static/index.html`

---

## 🎯 Core Features

### 1. **LLM-Powered Intent Detection**
- **GPT-4** (OpenAI) or **Gemini** (Google) support
- Falls back to keyword detection if no LLM available
- 6 intent types: lead_qualification, demo_request, pricing_inquiry, feature_question, complaint, other

### 2. **Conversation History Tracking**
- In-memory storage (upgrade to database in production)
- Full message context for better responses
- Per-user conversation isolation

### 3. **HubSpot CRM Integration**
- Real-time contact creation/updates
- Automatic note logging
- Workflow triggers based on intent

### 4. **Beautiful Frontend Chat Widget**
- Real-time messaging
- User info persistence (localStorage)
- Intent badges on responses
- Mobile-responsive design

---

## 📝 API Endpoints

### Health Check
```bash
GET /health
```
Response:
```json
{
  "status": "online",
  "service": "KeaBuilder AI Agent",
  "version": "2.0.0"
}
```

### Main Chat Endpoint
```bash
POST /chat
Content-Type: application/json

{
  "user_email": "priya@company.com",
  "user_name": "Priya",
  "message": "We need to launch a conversion funnel in 4 weeks"
}
```

Response:
```json
{
  "intent": "lead_qualification",
  "response": "Thanks Priya! I'd love to understand your needs...",
  "hubspot_action": "created + success",
  "follow_up": "Your message has been logged...",
  "llm_provider": "openai",
  "conversation_id": "conv_0_1234567890.123"
}
```

### Get Conversation History
```bash
GET /chat/{email}/history
```

### Clear Conversation History
```bash
DELETE /chat/{email}/history
```

### Traditional Lead Form Processing
```bash
POST /leads/process
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@company.com",
  "phone": "+1-555-1234",
  "budget": "50k",
  "timeline": "This month",
  "goals": "Lead capture",
  "message": "Urgent implementation needed"
}
```

---

## 🏗️ Architecture Explanation

### Flow Diagram
```
User Chat Input
     ↓
┌─────────────────────┐
│  Orchestrator       │
│  - Manages flow     │
│  - Coordinates all  │
└─────────────────────┘
     ↓
┌─────────────────────────────┐
│  AI Service                 │
│  - Detect Intent (LLM)      │
│  - Generate Response (LLM)  │
│  - Conversation Context     │
└─────────────────────────────┘
     ↓
┌─────────────────────────────┐
│  HubSpot Connector          │
│  - Create/Update Contact    │
│  - Add Notes                │
│  - Trigger Workflows        │
└─────────────────────────────┘
     ↓
Return Response to Frontend
```

### Component Breakdown

#### `main.py` - Entry Point
- Initializes FastAPI application
- Mounts static files (frontend)
- Includes API routes

#### `app/orchestrator.py` - Core Orchestrator
- Manages the entire conversation flow
- Coordinates AI service and HubSpot connector
- Maintains conversation history
- Triggers workflows

#### `app/services/ai_service.py` - AI Service
- LLM-based intent detection
- Response generation with context
- Fallback to keyword detection
- Supports OpenAI (GPT-4) and Google Gemini

#### `connector/hubspot.py` - HubSpot Connector
- Create or update contacts
- Add notes/engagements
- Trigger workflows
- Get contact details

#### `app/api/endpoints.py` - API Routes
- `/health` - Health check
- `/chat` - Main chat endpoint
- `/chat/{email}/history` - Get conversation history
- `/chat/{email}/history` - Clear history
- `/leads/process` - Form processing

#### `shared/config.py` - Configuration
- Environment variables
- API keys
- Constants and thresholds
- Provider settings

#### `shared/validation/schemas.py` - Pydantic Models
- LeadForm
- ChatMessage
- ChatResponse
- ConversationHistory
- ContentRequest
- HubSpotContact
- WorkflowTrigger

#### `static/index.html` - Frontend UI
- Beautiful chat widget
- Real-time messaging
- User info persistence
- Intent display badges
- Mobile responsive

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# LLM Provider
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key

# HubSpot
HUBSPOT_ACCESS_TOKEN=your-hubspot-private-app-token

# App Settings
DEBUG=false
```

### Using LLM Providers

#### OpenAI (GPT-4)
```bash
export OPENAI_API_KEY="your_key_here"
```

#### Google Gemini
```bash
export GEMINI_API_KEY="your_key_here"
```

#### Fallback (Keyword Detection)
If no LLM API keys provided, the system automatically falls back to keyword-based intent detection.

---

## 💾 Data Flow

### Chat Message Processing

1. **User sends message** via frontend
2. **API receives** ChatMessage at `/chat`
3. **Orchestrator processes**:
   - Stores message in history
   - Detects intent (LLM or keyword)
   - Gets conversation context
   - Generates response
   - Stores response in history
4. **HubSpot sync** (in background):
   - Creates/updates contact
   - Adds note with message
   - Triggers workflow
5. **Response returned** to user instantly

### Conversation History Storage

Currently uses **in-memory dictionary** (suitable for development):
```python
conversation_history = {
    "email@example.com": [
        {"role": "user", "content": "...", "timestamp": "..."},
        {"role": "assistant", "content": "...", "timestamp": "..."}
    ]
}
```

**Production upgrade**: Use PostgreSQL/MongoDB for persistence.

---

## 🔌 HubSpot Integration Details

### What Gets Synced

1. **Contact Properties**
   - name (first + last)
   - email (unique identifier)
   - phone (optional)
   - custom field: AI intent and notes

2. **Activities/Engagements**
   - Chat message stored as note
   - Intent type recorded
   - Timestamp captured

3. **Workflow Triggers**
   - lead_qualification → hot_lead_workflow
   - demo_request → demo_scheduler_workflow
   - pricing_inquiry → send_pricing_workflow
   - complaint → escalate_support_workflow

### HubSpot Workflow Automation Examples

**Auto-schedule demo for demo requests:**
```
Trigger: Lead intent = "demo_request"
Action: Create calendar event + Send confirmation email
```

**Prioritize hot leads:**
```
Trigger: Lead intent = "lead_qualification" + High engagement
Action: Assign to top sales rep + Create task
```

**Send pricing info:**
```
Trigger: Lead intent = "pricing_inquiry"
Action: Send pricing sheet + Schedule follow-up call
```

---

## 📊 Intent Types & Examples

| Intent | Keywords | Example | AI Response |
|--------|----------|---------|-------------|
| `lead_qualification` | want, need, launch, budget, timeline | "We need a funnel in 4 weeks" | Ask clarifying questions |
| `demo_request` | demo, show, video, walkthrough | "Can you show me how it works?" | Schedule demo appointment |
| `pricing_inquiry` | price, cost, plan, subscription | "What are your plans?" | Provide pricing info |
| `feature_question` | feature, support, integrate, API | "Do you support HubSpot?" | Answer & send docs |
| `complaint` | issue, problem, bug, error | "I found a bug" | Escalate to support |
| `other` | general message | "Hello!" | Generic response |

---

## 🧪 Testing

### Test via Frontend UI
1. Open `http://127.0.0.1:8000/static/index.html`
2. Enter email and name
3. Send messages
4. Watch intent detection in real-time

### Test via cURL

```bash
# Health check
curl -X GET http://127.0.0.1:8000/health

# Send chat message
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "priya@company.com",
    "user_name": "Priya",
    "message": "We need a demo"
  }'

# Get conversation history
curl -X GET http://127.0.0.1:8000/chat/priya@company.com/history
```

---

## 🚀 Production Deployment

### Recommendations

1. **Database for Conversation History**
   - PostgreSQL or MongoDB
   - Persistent across restarts

2. **Queue for HubSpot Sync**
   - Redis + Celery
   - Reliable background task processing

3. **Logging & Monitoring**
   - Sentry for error tracking
   - CloudWatch for logs

4. **API Rate Limiting**
   - Slow down abuse
   - Protect LLM API costs

5. **Authentication**
   - OAuth2 for user login
   - API key management

6. **Docker Deployment**
   ```dockerfile
   FROM python:3.10
   COPY . /app
   WORKDIR /app
   RUN pip install -r requirements.txt
   CMD ["python", "main.py"]
   ```

---

## 📚 Next Enhancements

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Custom LLM prompt engineering
- [ ] Integration with more CRM systems
- [ ] Conversation export (PDF/CSV)
- [ ] Real-time agent collaboration
- [ ] A/B testing different AI responses
- [ ] Sentiment analysis on messages

---

## ❓ Troubleshooting

### LLM API not working
- Check API keys in `.env`
- Verify internet connection
- Check API quota/limits
- Fallback to keyword detection

### HubSpot sync failed
- Verify access token
- Check token permissions
- Confirm contact doesn't have conflicts
- Review HubSpot API logs

### Frontend not loading
- Ensure static folder exists
- Check CORS settings
- Verify server is running

---

## 📖 API Documentation

Interactive docs available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---
