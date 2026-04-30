# Dream Reflection Media AI Engineer Assessment

## Project

This prototype shows how KeaBuilder can use AI for lead capture, CRM automation, content generation, personalization, similarity search, and fallback handling.

Run locally:

```bash
source .venv/bin/activate
uvicorn main:app --reload --port 8001
```

UI:

```text
http://127.0.0.1:8001/static/index.html
```

API docs:

```text
http://127.0.0.1:8001/docs
```

## 1. AI Lead Processing

When a user fills a form or chats with the AI assistant, the backend:

1. Detects user intent.
2. Classifies the lead as `hot`, `warm`, or `cold`.
3. Generates a human follow-up response.
4. Creates or updates the contact in HubSpot.
5. Stores conversation context in memory for follow-up messages.

Classification signals:

- `hot`: strong budget, urgent timeline, clear project need.
- `warm`: interested but missing budget/timeline or not urgent.
- `cold`: vague message or incomplete information.

Classification prompt:

```text
Classify this lead as hot, warm, or cold.

Rules:
- Hot: high intent, clear need, budget, urgent timeline.
- Warm: interested but not urgent or missing some details.
- Cold: vague, unclear, or low intent.

Return JSON:
{
  "lead_type": "",
  "confidence": "",
  "reason": ""
}

Input:
Name: {{name}}
Budget: {{budget}}
Timeline: {{timeline}}
Message: {{message}}
```

Response prompt:

```text
You are a friendly KeaBuilder sales assistant.

Write a short personalized response.

Rules:
- Use the user's name.
- Reference their project or goal.
- Ask for missing details if needed.
- Keep it human and simple.
```

Sample input:

```json
{
  "name": "Rahul Ranjan",
  "email": "rahulranjan0327@gmail.com",
  "company": "Iffort",
  "budget": "100000",
  "timeline": "next month",
  "goals": "Create a million dollar lead funnel"
}
```

Sample output:

```json
{
  "status": "success",
  "classification": "hot",
  "score": 5,
  "personalized_reply": "Hi Rahul, this looks like a strong fit for KeaBuilder. I noted your goal around Create a million dollar lead funnel. Can we schedule a quick call and confirm your timeline, budget, and success criteria?"
}
```

## 2. Multi-Provider Content Generation

KeaBuilder can route generation by content type:

- Images -> image provider.
- Videos -> video provider.
- Voice -> voice provider.

Backend endpoints:

- `POST /content/generate`
- `POST /route-content`

Routing logic:

```python
if content_type == "image":
    provider = image_provider
elif content_type == "video":
    provider = video_provider
elif content_type == "voice":
    provider = voice_provider
```

Frontend flow:

1. User enters a prompt inside the builder UI.
2. UI sends `content_type` and `prompt` to backend.
3. Backend selects provider.
4. Backend creates an asset job.
5. UI shows preview when generation is complete.

Output management:

- Store file in cloud storage.
- Store metadata in DB: `asset_id`, `user_id`, `type`, `provider`, `status`, `url`.
- Let users insert the generated asset into funnel pages.

## 3. Personalized Images With LoRA

LoRA is a small adapter that teaches a base image model a specific face, brand, or visual style.

KeaBuilder flow:

1. User uploads reference images or brand assets.
2. System trains or loads a LoRA adapter.
3. Backend stores `lora_model_id`.
4. During image generation, backend sends prompt + LoRA ID to the image provider.
5. Output keeps the user's face or brand style consistent.

Example:

```json
{
  "prompt": "Create a founder profile image for a SaaS landing page",
  "lora_model_id": "rahul_brand_v1",
  "style": "professional startup"
}
```

## 4. Similarity Search

KeaBuilder stores user assets like images, copy, templates, and generated content.

Production design:

- Convert text/images into embeddings.
- Store embeddings in pgvector, Pinecone, FAISS, or Weaviate.
- Search using cosine similarity.

Prototype endpoint:

- `POST /search-similarity`

Use cases:

- Find similar landing page templates.
- Match similar lead form messages.
- Find visually similar brand images.
- Suggest reusable assets.

## 5. Fallback Handling

If one AI provider fails:

1. Retry once with timeout.
2. Switch to fallback provider.
3. Save job status.
4. Show a friendly UI message instead of raw error.

Example UI message:

```text
The primary AI provider is taking longer than expected. We are trying an alternate provider.
```

## 6. High-Volume AI Requests

For many users, KeaBuilder should avoid processing heavy AI jobs directly inside the web request.

Recommended design:

- FastAPI for request handling.
- Redis/Celery or Kafka for background jobs.
- Workers for image/video/voice generation.
- Object storage for generated files.
- Database for job status.
- Rate limiting and caching for cost control.

Flow:

```text
Frontend -> API -> Queue -> Worker -> AI Provider -> Storage -> UI Preview
```

## 7. Tools and Frameworks

Tools used or suitable for this project:

- Python
- FastAPI
- Gemini API
- OpenAI API
- HubSpot CRM API
- FAISS / pgvector / Pinecone
- Redis / Celery
- PostgreSQL
- Docker
- GitHub

## Gemini API Key

Create a free Gemini API key from Google AI Studio:

```text
https://aistudio.google.com/app/apikey
```

Store it in `.env`:

```bash
GEMINI_API_KEY=your_key_here
```

Keep the key server-side only. Do not put it in frontend code or public GitHub files.

## Loom Script

Use this 3 to 5 minute structure:

1. "I built a KeaBuilder AI prototype for lead capture, chat automation, content routing, and similarity search."
2. "The chat endpoint detects intent, keeps conversation memory, asks for missing contact details, and syncs contacts to HubSpot."
3. "The lead form endpoint scores leads as hot, warm, or cold using budget, timeline, and goal signals."
4. "The content endpoint routes image, video, and voice requests to different providers and returns asset metadata."
5. "The similarity endpoint demonstrates how KeaBuilder could match templates or assets using vector search."
6. "For production, I would use queues, workers, fallback providers, cloud storage, and a vector database."
