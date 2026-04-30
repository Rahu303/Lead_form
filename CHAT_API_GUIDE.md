# AI Chat Agent with HubSpot Integration

## What's New

- **Conversational AI Chat** — Detect user intent from natural language
- **Intent Detection** — Classifies messages into: lead_qualification, demo_request, pricing_inquiry, feature_question, complaint, other
- **HubSpot CRM Integration** — Automatically syncs chats, notes, and contact info to HubSpot
- **Background Processing** — HubSpot sync happens in background for instant UI response
- **Health Check Endpoint** — `/` endpoint confirms service is running

---

## How to Run

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn main:app --reload --port 8000
```

Visit: `http://127.0.0.1:8001/docs` for interactive API docs.

---

## API Endpoints

### 1. Health Check
```bash
curl -X GET http://127.0.0.1:8001/
```

**Response:**
```json
{
  "status": "online",
  "service": "KeaBuilder AI Agent with HubSpot Integration"
}
```

---

### 2. Chat with AI (Main Endpoint)

```bash
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "priya@growthflow.com",
    "user_name": "Priya",
    "message": "We are looking to launch a conversion funnel in 4 weeks. What features do you recommend?"
  }'
```

**Response:**
```json
{
  "intent": "lead_qualification",
  "response": "Thanks Priya! I'd love to understand your needs better. Can you tell me more about your company size, current challenges, and what you're looking to achieve?",
  "hubspot_action": "Creating/Updating contact with intent: lead_qualification",
  "follow_up": "Your message has been logged. Our team will follow up on your lead_qualification."
}
```

---

### 3. Intent Detection Examples

#### a) Demo Request
```bash
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "amit@startup.com",
    "user_name": "Amit",
    "message": "Can you show me a demo of how the platform works?"
  }'
```

**Response:**
```json
{
  "intent": "demo_request",
  "response": "Perfect! I can schedule a personalized demo for you. When works best? I can do Tuesday-Thursday, 2-5 PM EST.",
  ...
}
```

#### b) Pricing Inquiry
```bash
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "sarah@company.com",
    "user_name": "Sarah",
    "message": "What is the pricing for your premium plan?"
  }'
```

**Response:**
```json
{
  "intent": "pricing_inquiry",
  "response": "We offer flexible plans starting at $99/month for startups up to enterprise custom pricing. Which features matter most to your use case?",
  ...
}
```

#### c) Feature Question
```bash
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "john@tech.com",
    "user_name": "John",
    "message": "Does your platform integrate with HubSpot CRM?"
  }'
```

**Response:**
```json
{
  "intent": "feature_question",
  "response": "Great question! Our platform supports [feature]. Would you like me to send over a detailed feature comparison or docs?",
  ...
}
```

#### d) Complaint / Issue
```bash
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "mike@company.com",
    "user_name": "Mike",
    "message": "I'm experiencing a bug when trying to export my leads."
  }'
```

**Response:**
```json
{
  "intent": "complaint",
  "response": "I'm sorry to hear you're experiencing an issue, Mike. Let me connect you with our support team right away.",
  ...
}
```

---

### 4. Traditional Lead Form Processing

```bash
curl -X POST http://127.0.0.1:8001/leads/process \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Priya Sharma",
    "email": "priya@growthflow.com",
    "phone": "+1-555-1234",
    "budget": "We are ready to invest in premium solutions.",
    "timeline": "Need to launch in 4 weeks.",
    "goals": "Create a conversion-focused funnel",
    "message": "We need automation and AI-powered lead qualification."
  }'
```

**Response:**
```json
{
  "status": "success",
  "classification": "hot",
  "personalized_reply": "Hi Priya! I noticed you're looking to Create a conversion-focused funnel. This is a high priority for us. Can we hop on a call tomorrow?",
  "hubspot_status": "Syncing in background..."
}
```

---

## HubSpot Integration Details

### What Gets Synced?
- **Contact Name** (first + last)
- **Email** (unique identifier)
- **Phone** (if provided)
- **AI Classification** (hot/warm/cold)
- **Intent** (from chat or form)
- **Goals & Timeline**
- **Chat Notes** (every message is logged)

### Automatic Actions
1. **New Contact** → Created in HubSpot
2. **Existing Contact** → Updated with new intent/goals
3. **Chat Message** → Logged as note/engagement
4. **Intent Detected** → Stored for follow-up automation

### HubSpot Fields Mapped
- `email` → Email address
- `firstname` → First name
- `lastname` → Last name
- `phone` → Phone number
- `hs_content_membership_notes` → AI notes & intent

---

## Next Steps

1. Test the endpoints in `http://127.0.0.1:8001/docs`
2. View synced leads in your HubSpot CRM
3. Set up workflows in HubSpot based on intent (e.g., auto-demo for "demo_request")
4. Enhance intent detection with LLM APIs (OpenAI/Gemini) for better accuracy

---

## Environment Variables (Secure)

Instead of hardcoding credentials, use environment variables:

```bash
export HUBSPOT_ACCESS_TOKEN="your-hubspot-private-app-token"
```

Then update app.py:
```python
HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN", "fallback-token")
```

---

## What the System Does

1. **User sends chat message** → `/chat` endpoint
2. **AI detects intent** (lead_qualification, demo_request, etc.)
3. **Generates personalized response** based on intent
4. **Syncs to HubSpot** (contact created/updated + note added)
5. **Returns response instantly** (HubSpot sync in background)
6. **HubSpot workflows trigger** automatically (e.g., send email, assign to sales, create task)

---
