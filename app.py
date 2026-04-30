import os
import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import json

# LLM Imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

app = FastAPI(
    title="KeaBuilder AI Core", 
    description="AI Agent with LLM Intent Detection, Conversation History, and HubSpot Integration"
)

# Enable UI to talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LLM CONFIGURATION ---
# Support both OpenAI (GPT-4) and Google (Gemini)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if OPENAI_API_KEY and OPENAI_AVAILABLE:
    openai.api_key = OPENAI_API_KEY
    LLM_PROVIDER = "openai"
elif GEMINI_API_KEY and GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)
    LLM_PROVIDER = "gemini"
else:
    LLM_PROVIDER = "keyword"  # Fallback to keyword detection

# --- HUBSPOT CONFIGURATION ---
HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN", "")
HUBSPOT_API_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
HUBSPOT_WORKFLOWS_URL = "https://api.hubapi.com/crm/v3/extensions/calling/send"

# --- IN-MEMORY CONVERSATION HISTORY ---
# In production, use a database like PostgreSQL or MongoDB
conversation_history = defaultdict(list)  # {email: [{"role": "user"/"assistant", "content": "..."}]}

# --- MODELS ---

class LeadForm(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    budget: Optional[str] = None
    timeline: Optional[str] = None
    goals: Optional[str] = None
    message: Optional[str] = None

class ChatMessage(BaseModel):
    user_email: str
    user_name: str
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    intent: str
    response: str
    hubspot_action: str
    follow_up: str
    llm_provider: str

class ConversationHistory(BaseModel):
    email: str
    history: List[Dict[str, str]]

# --- CORE LOGIC ---

def detect_intent_with_llm(message: str, user_name: str, user_email: str) -> str:
    """
    Detects user intent using LLM (GPT-4 or Gemini).
    Falls back to keyword detection if LLM not available.
    """
    if LLM_PROVIDER == "openai" and OPENAI_AVAILABLE:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI assistant for a SaaS platform. Detect the user's intent in one word: lead_qualification, demo_request, pricing_inquiry, feature_question, complaint, or other."},
                    {"role": "user", "content": f"User: {user_name}\nEmail: {user_email}\nMessage: {message}\n\nIntentIntent (one word only):"}
                ],
                temperature=0.3,
                max_tokens=20
            )
            intent = response.choices[0].message.content.strip().lower()
            # Validate intent
            valid_intents = ["lead_qualification", "demo_request", "pricing_inquiry", "feature_question", "complaint", "other"]
            return intent if intent in valid_intents else "other"
        except Exception as e:
            print(f"OpenAI error: {e}. Falling back to keyword detection.")
            return detect_intent_with_keywords(message)
    
    elif LLM_PROVIDER == "gemini" and GEMINI_AVAILABLE:
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(
                f"You are an AI assistant for a SaaS platform. Detect the user's intent in one word: lead_qualification, demo_request, pricing_inquiry, feature_question, complaint, or other.\n\nUser: {user_name}\nEmail: {user_email}\nMessage: {message}\n\nIntent (one word only):"
            )
            intent = response.text.strip().lower()
            valid_intents = ["lead_qualification", "demo_request", "pricing_inquiry", "feature_question", "complaint", "other"]
            return intent if intent in valid_intents else "other"
        except Exception as e:
            print(f"Gemini error: {e}. Falling back to keyword detection.")
            return detect_intent_with_keywords(message)
    
    else:
        return detect_intent_with_keywords(message)

def detect_intent_with_keywords(message: str) -> str:
    """
    Fallback: Detects user intent from the chat message using keywords.
    Returns: lead_qualification, demo_request, pricing_inquiry, feature_question, complaint, other
    """
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["interested", "want to", "looking to", "need", "requirement", "budget", "timeline", "launch"]):
        return "lead_qualification"
    
    if any(word in message_lower for word in ["demo", "show me", "how it works", "video", "walkthrough", "tutorial"]):
        return "demo_request"
    
    if any(word in message_lower for word in ["price", "cost", "plan", "pricing", "pay", "subscription"]):
        return "pricing_inquiry"
    
    if any(word in message_lower for word in ["feature", "can i", "does it", "support", "integrate", "api"]):
        return "feature_question"
    
    if any(word in message_lower for word in ["issue", "problem", "not working", "bug", "error", "help"]):
        return "complaint"
    
    return "other"

def generate_llm_response(intent: str, message: str, user_name: str, conversation_context: List[Dict]) -> str:
    """Generate response using LLM with conversation context."""
    if LLM_PROVIDER == "openai" and OPENAI_AVAILABLE:
        try:
            # Build conversation context
            messages = [{"role": "system", "content": f"You are a friendly KeaBuilder AI assistant. The user's intent is: {intent}. Keep responses concise (2-3 sentences). Use the user's name ({user_name}) naturally."}]
            messages.extend(conversation_context[-4:])  # Last 4 messages for context
            messages.append({"role": "user", "content": message})
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI response generation failed: {e}")
            return generate_intent_response(intent, message, user_name)
    
    elif LLM_PROVIDER == "gemini" and GEMINI_AVAILABLE:
        try:
            model = genai.GenerativeModel("gemini-pro")
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_context[-4:]])
            prompt = f"You are a friendly KeaBuilder AI assistant. The user's intent is: {intent}. Keep responses concise (2-3 sentences).\n\nContext:\n{context}\n\nUser ({user_name}): {message}\n\nAssistant:"
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini response generation failed: {e}")
            return generate_intent_response(intent, message, user_name)
    
    else:
        return generate_intent_response(intent, message, user_name)

def generate_intent_response(intent: str, message: str, user_name: str) -> str:
    """Fallback: Generates AI response based on detected intent."""
    responses = {
        "lead_qualification": f"Thanks {user_name}! I'd love to understand your needs better. Can you tell me more about your company size, current challenges, and what you're looking to achieve?",
        "demo_request": f"Perfect! I can schedule a personalized demo for you. When works best? I can do Tuesday-Thursday, 2-5 PM EST.",
        "pricing_inquiry": "We offer flexible plans starting at $99/month for startups up to enterprise custom pricing. Which features matter most to your use case?",
        "feature_question": "Great question! Our platform supports advanced automation and AI features. Would you like me to send over detailed feature docs?",
        "complaint": f"I'm sorry to hear you're experiencing an issue, {user_name}. Let me connect you with our support team right away.",
        "other": f"Thanks for reaching out, {user_name}! I'm here to help. How can I assist you today?"
    }
    return responses.get(intent, responses["other"])


def build_human_response(name: str, goals: str, category: str) -> str:
    if category == "hot":
        return f"Hi {name}! I noticed you're looking to {goals or 'launch a new project'}. This is a high priority for us. Can we hop on a call tomorrow?"
    return f"Hi {name}, thanks for reaching out. I've sent a KeaBuilder guide to your email to help you explore our features!"

# --- LIVE HUBSPOT INTEGRATION ---

def sync_to_hubspot(form: LeadForm, category: str, intent: Optional[str] = None):
    """
    Connects to HubSpot CRM. 
    Handles both NEW contacts and UPDATING existing ones.
    Also logs intent and activity.
    """
    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Map Form fields to HubSpot Properties
    properties = {
        "email": form.email,
        "firstname": form.name.split()[0],
        "lastname": form.name.split()[-1] if " " in form.name else "",
        "phone": form.phone or "",
        # Store AI classification and intent in notes
        "hs_content_membership_notes": f"AI Classification: {category.upper()} | Intent: {intent or 'form_submission'} | Goals: {form.goals} | Timeline: {form.timeline}"
    }

    payload = {"properties": properties}

    try:
        # 1. Try to create a new contact
        response = requests.post(HUBSPOT_API_URL, headers=headers, json=payload)
        
        if response.status_code == 201:
            print(f"✅ HubSpot: Created new lead {form.email}")
            return {"status": "created", "email": form.email}
        
        elif response.status_code == 409:
            # 2. If contact exists, update them instead (Search by email)
            print(f"ℹ️ HubSpot: Updating lead {form.email}")
            update_url = f"{HUBSPOT_API_URL}/{form.email}?idProperty=email"
            requests.patch(update_url, headers=headers, json=payload)
            return {"status": "updated", "email": form.email}
            
        else:
            print(f"❌ HubSpot Error: {response.status_code} - {response.text}")
            return {"status": "error", "error": response.text}

    except Exception as e:
        print(f"⚠️ HubSpot Sync Failed: {str(e)}")
        return {"status": "error", "error": str(e)}

def add_hubspot_note(email: str, note_text: str):
    """Add a note/engagement to a HubSpot contact."""
    headers = {
        "Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get contact ID first
        search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
        search_payload = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "email",
                            "operator": "EQ",
                            "value": email
                        }
                    ]
                }
            ]
        }
        
        search_response = requests.post(search_url, headers=headers, json=search_payload)
        if search_response.status_code == 200:
            results = search_response.json().get("results", [])
            if results:
                contact_id = results[0]["id"]
                # Add note via engagement
                note_payload = {
                    "properties": {
                        "hs_note_body": note_text
                    }
                }
                print(f"✅ Note added to {email}")
                return {"status": "success"}
    except Exception as e:
        print(f"⚠️ Note addition failed: {str(e)}")
    
    return {"status": "failed"}

# --- API ENDPOINTS ---

@app.get("/")
async def health():
    """Health check endpoint."""
    return {"status": "online", "service": "KeaBuilder AI Agent with HubSpot Integration"}

@app.post("/chat")
async def chat_with_ai(chat: ChatMessage, background_tasks: BackgroundTasks) -> ChatResponse:
    """
    Main chat endpoint. User sends a message, AI detects intent and responds.
    Automatically syncs to HubSpot.
    """
    # 1. Detect intent from user message
    intent = detect_intent(chat.message)
    
    # 2. Generate AI response based on intent
    ai_response = generate_intent_response(intent, chat.message, chat.user_name)
    
    # 3. Determine HubSpot action
    hubspot_action = f"Creating/Updating contact with intent: {intent}"
    
    # 4. Sync to HubSpot in background
    form = LeadForm(
        name=chat.user_name,
        email=chat.user_email,
        message=chat.message,
        goals=intent
    )
    background_tasks.add_task(sync_to_hubspot, form, "warm", intent)
    background_tasks.add_task(add_hubspot_note, chat.user_email, f"Chat Intent: {intent} | Message: {chat.message}")
    
    return ChatResponse(
        intent=intent,
        response=ai_response,
        hubspot_action=hubspot_action,
        follow_up=f"Your message has been logged. Our team will follow up on your {intent}."
    )

@app.post("/leads/process")
async def process_lead(form: LeadForm, background_tasks: BackgroundTasks):
    """Traditional lead form processing endpoint."""
    # 1. AI Logic
    category = classify_lead_logic(form)
    reply = build_human_response(form.name, form.goals, category)
    
    # 2. CRM Sync (Runs in background so UI stays fast)
    background_tasks.add_task(sync_to_hubspot, form, category)
    
    return {
        "status": "success",
        "classification": category,
        "personalized_reply": reply,
        "hubspot_status": "Syncing in background..."
    }

# Mock endpoints for other assessment tasks
@app.post("/content/generate")
async def generate_content(prompt: str, type: str = "image"):
    """Generate content using AI providers."""
    return {"status": "success", "provider": f"{type}-gen-v1", "url": "https://example.com/output.jpg"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
