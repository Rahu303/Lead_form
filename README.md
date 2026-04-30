# KeaBuilder AI Feature Prototype

A lightweight AI workflow prototype built for the Dream Reflection Media assessment.

## ✨ What's New

- **Conversational AI Chat** — Chat with an AI agent that detects user intent
- **Intent Detection** — Automatically classifies messages into: lead_qualification, demo_request, pricing_inquiry, feature_question, complaint, other
- **HubSpot CRM Integration** — All chats and form submissions are synced to HubSpot in real-time
- **Personalized Responses** — AI generates contextual responses based on detected intent
- **Background Processing** — HubSpot sync happens asynchronously for instant UI response

## What is included

- `app.py` — FastAPI backend with chat, lead classification, response generation, and HubSpot integration
- `CHAT_API_GUIDE.md` — Complete API documentation with curl examples
- `test_chat_api.sh` — Bash script to test all endpoints
- `design_and_implementation.md` — answers to all assessment questions with system design and prompt examples
- `sample_outputs.json` — sample input/output JSON for lead processing and routing
- `requirements.txt` — minimal dependencies

## How to run

1. Activate Python environment:
   - `source .venv/bin/activate`

2. Install dependencies:
   - `pip install -r requirements.txt`

3. Start the API:
   - `uvicorn main:app --reload --port 8000`

4. Access the interactive docs:
   - `http://127.0.0.1:8001/docs`

## Quick Start Examples

### 1. Health Check
```bash
curl -X GET http://127.0.0.1:8001/
```

### 2. Chat with AI (Main Feature)
```bash
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "priya@growthflow.com",
    "user_name": "Priya",
    "message": "We need to launch a conversion funnel in 4 weeks"
  }'
```

The AI will:
- Detect intent: `lead_qualification`
- Generate personalized response
- Automatically sync to HubSpot
- Log all conversation data

### 3. Run All Tests
```bash
chmod +x test_chat_api.sh
./test_chat_api.sh
```

## Intent Types Detected

| Intent | Example | AI Response |
|--------|---------|-----------|
| `lead_qualification` | "We need to launch urgently" | Asks clarifying questions about goals |
| `demo_request` | "Can you show me a demo?" | Schedules a personalized demo |
| `pricing_inquiry` | "What are your plans?" | Provides pricing info |
| `feature_question` | "Do you support HubSpot?" | Answers feature questions |
| `complaint` | "I found a bug" | Escalates to support |
| `other` | General message | Generic helpful response |

## HubSpot Integration

- All chats automatically sync to HubSpot CRM
- Contacts are created or updated based on email
- Chat messages stored as notes/engagements
- AI classification (hot/warm/cold) stored for follow-up automation
- Background processing ensures no UI delay

## Example curl requests

### Classify a lead

```bash
curl -X POST http://127.0.0.1:8001/classify-lead \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Priya",
    "email": "priya@example.com",
    "company": "GrowthFlow Labs",
    "budget": "We are ready to invest in a premium funnel this quarter.",
    "timeline": "Need to launch within 4 weeks.",
    "goals": "Create a lead capture funnel that converts high-value B2B prospects.",
    "message": "We need a strong offer and automated follow-up sequences."
  }'
```

### Generate a personalized response

```bash
curl -X POST http://127.0.0.1:8001/generate-response \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Priya",
    "email": "priya@example.com",
    "company": "GrowthFlow Labs",
    "budget": "We are ready to invest in a premium funnel this quarter.",
    "timeline": "Need to launch within 4 weeks.",
    "goals": "Create a lead capture funnel that converts high-value B2B prospects.",
    "message": "We need a strong offer and automated follow-up sequences."
  }'
```

### Route a content request

```bash
curl -X POST http://127.0.0.1:8001/route-content \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "image",
    "prompt": "A modern landing page hero showcasing a SaaS product for small business owners.",
    "style": "clean",
    "brand_name": "KeaBuilder"
  }'
```

### Search for similar assets

```bash
curl -X POST http://127.0.0.1:8001/search-similarity \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SaaS onboarding flow with a friendly brand tone.",
    "item_type": "template",
    "items": [
      {"id": 1, "text": "Friendly SaaS onboarding email series."},
      {"id": 2, "text": "Modern funnel landing page for SaaS startups."},
      {"id": 3, "text": "Conversational chatbot flow for product demos."}
    ]
  }'
```

## Notes

- No real API keys are stored in this repository.
- HubSpot credentials are stored in environment variables in production.
- The demo uses real HubSpot API calls with your provided PAT token.
- For a full SaaS integration, enhance intent detection with LLM APIs (OpenAI/Gemini) for better accuracy.

## Architecture

```
User Chat Input
     ↓
FastAPI Endpoint (/chat)
     ↓
Intent Detection (keyword-based)
     ↓
Generate AI Response
     ↓
Background HubSpot Sync
     ├─ Create/Update Contact
     ├─ Add Chat Note
     └─ Log Intent & Goals
     ↓
Return Instant Response
```

## Next Improvements

1. Replace keyword-based intent detection with LLM API (GPT-4 / Gemini)
2. Add conversation history tracking
3. Implement HubSpot workflow automation triggers
4. Add multi-language support
5. Create a frontend UI for the chat interface
6. Implement analytics dashboard for intent tracking
