"""
API Endpoints
FastAPI routes for chat, lead processing, and utilities
"""
import math
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, BackgroundTasks, HTTPException
from shared.config import CONTENT_PROVIDERS, LLM_PROVIDER
from shared.validation.schemas import ChatMessage, ChatResponse, ContentRequest, LeadForm, SimilaritySearchRequest
from app.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "KeaBuilder AI Agent",
        "version": "2.0.0"
    }


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat: ChatMessage, background_tasks: BackgroundTasks):
    """
    Main chat endpoint.
    - Detects user intent
    - Generates AI response
    - Syncs to HubSpot
    - Stores conversation history
    """
    try:
        response = orchestrator.process_chat(chat)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/{email}/history")
async def get_conversation_history(email: str):
    """Get conversation history for a user"""
    history = orchestrator.get_conversation_history(email)
    return {
        "email": email,
        "history": history,
        "total_messages": len(history)
    }


@router.delete("/chat/{email}/history")
async def clear_conversation_history(email: str):
    """Clear conversation history for a user"""
    cleared = orchestrator.clear_conversation_history(email)
    return {
        "email": email,
        "cleared": cleared
    }


@router.post("/leads/process")
async def process_lead(form: LeadForm, background_tasks: BackgroundTasks):
    """Process a traditional lead form submission"""
    try:
        lead_score, classification, reasons = classify_lead(form)
        reply = build_lead_reply(form, classification)

        chat_message = ChatMessage(
            user_email=form.email,
            user_name=form.name,
            message=form.message or form.goals or form.timeline or "Form submission"
        )
        response = orchestrator.process_chat(chat_message)

        return {
            "status": "success",
            "classification": classification,
            "score": lead_score,
            "reasons": reasons,
            "personalized_reply": reply,
            "intent": response.intent,
            "hubspot_status": response.hubspot_action,
            "conversation_id": response.conversation_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-lead")
async def classify_lead_endpoint(form: LeadForm):
    """Compatibility endpoint for the assessment README examples."""
    score, classification, reasons = classify_lead(form)
    return {
        "classification": classification,
        "score": score,
        "reasons": reasons
    }


@router.post("/generate-response")
async def generate_response_endpoint(form: LeadForm):
    """Generate a personalized reply for a lead form."""
    score, classification, reasons = classify_lead(form)
    return {
        "classification": classification,
        "score": score,
        "reasons": reasons,
        "personalized_reply": build_lead_reply(form, classification)
    }


@router.post("/content/generate")
async def generate_content(request: ContentRequest):
    """Route a content generation request to the correct AI provider."""
    try:
        content_type = request.resolved_type
        if content_type not in CONTENT_PROVIDERS:
            raise HTTPException(status_code=400, detail="content_type must be image, video, or voice")

        provider = CONTENT_PROVIDERS[content_type]
        asset_id = f"{content_type}_{int(datetime.now().timestamp())}"

        return {
            "status": "queued",
            "asset_id": asset_id,
            "content_type": content_type,
            "provider": provider,
            "prompt": request.prompt,
            "fallback_provider": fallback_provider_for(content_type),
            "storage": {
                "bucket": "keabuilder-user-assets",
                "path": f"generated/{content_type}/{asset_id}",
                "metadata_saved": True
            },
            "preview_url": f"https://cdn.keabuilder.example/generated/{content_type}/{asset_id}",
            "message": "Request accepted. The builder UI can poll this asset_id or subscribe to job updates."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/route-content")
async def route_content(request: ContentRequest):
    """Alias endpoint matching the assessment wording."""
    return await generate_content(request)


@router.post("/search-similarity")
async def search_similarity(request: SimilaritySearchRequest):
    """Prototype text/template similarity search using cosine similarity."""
    query_tokens = tokenize(request.query)
    scored_items = []

    for item in request.items:
        score = cosine_similarity(query_tokens, tokenize(item.text))
        scored_items.append({
            "item": item.model_dump(),
            "score": round(score, 3),
            "match_reason": build_match_reason(request.query, item.text)
        })

    scored_items.sort(key=lambda result: result["score"], reverse=True)
    return {
        "query": request.query,
        "item_type": request.item_type,
        "embedding_strategy": "prototype bag-of-words cosine similarity; production would use Gemini/OpenAI embeddings + pgvector/Pinecone",
        "top_matches": scored_items[: max(1, request.top_k)]
    }


def classify_lead(form: LeadForm):
    """Simple hot/warm/cold scoring for assessment lead forms."""
    combined = " ".join(
        value for value in [
            form.budget,
            form.timeline,
            form.goals,
            form.message,
            form.company
        ]
        if value
    ).lower()

    score = 0
    reasons = []
    if any(term in combined for term in ["premium", "enterprise", "million", "100000", "high budget", "$"]):
        score += 2
        reasons.append("strong budget signal")
    if any(term in combined for term in ["urgent", "next month", "4 weeks", "30 days", "soon", "launch"]):
        score += 2
        reasons.append("clear or urgent timeline")
    if any(term in combined for term in ["automation", "funnel", "lead", "conversion", "crm", "demo"]):
        score += 1
        reasons.append("clear KeaBuilder use case")
    if len(combined.split()) >= 12:
        score += 1
        reasons.append("detailed input")

    if score >= 4:
        return score, "hot", reasons
    if score >= 2:
        return score, "warm", reasons or ["some interest shown"]
    return score, "cold", reasons or ["not enough detail yet"]


def build_lead_reply(form: LeadForm, classification: str) -> str:
    first_name = form.name.split()[0] if form.name else "there"
    goal = form.goals or form.message or "your funnel"

    if classification == "hot":
        return (
            f"Hi {first_name}, this looks like a strong fit for KeaBuilder. "
            f"I noted your goal around {goal}. Can we schedule a quick call and confirm your timeline, budget, and success criteria?"
        )
    if classification == "warm":
        return (
            f"Hi {first_name}, thanks for sharing this. "
            "I can help map the right funnel and automation flow. What timeline and budget range should we plan around?"
        )
    return (
        f"Hi {first_name}, thanks for reaching out. "
        "Could you share your goal, timeline, and budget range so I can recommend the best next step?"
    )


def fallback_provider_for(content_type: str) -> str:
    fallback_map = {
        "image": "backup-image-provider.example.com",
        "video": "backup-video-provider.example.com",
        "voice": "backup-voice-provider.example.com",
    }
    return fallback_map[content_type]


def tokenize(text: str) -> Counter:
    return Counter(re.findall(r"[a-z0-9]+", text.lower()))


def cosine_similarity(left: Counter, right: Counter) -> float:
    if not left or not right:
        return 0.0

    common = set(left) & set(right)
    dot_product = sum(left[token] * right[token] for token in common)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return dot_product / (left_norm * right_norm) if left_norm and right_norm else 0.0


def build_match_reason(query: str, text: str) -> str:
    shared_terms = sorted(set(tokenize(query)) & set(tokenize(text)))
    if not shared_terms:
        return "No exact shared terms; low semantic overlap in prototype matcher."
    return f"Shared terms: {', '.join(shared_terms[:5])}"
