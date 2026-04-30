"""
Centralized Configuration
API Keys, Constants, and Environment Variables
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM CONFIGURATION ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Determine which LLM provider to use
LLM_PROVIDER = "keyword"  # Default fallback
if OPENAI_API_KEY:
    LLM_PROVIDER = "openai"
elif GEMINI_API_KEY:
    LLM_PROVIDER = "gemini"

# --- HUBSPOT CONFIGURATION ---
HUBSPOT_ACCESS_TOKEN = os.getenv(
    "HUBSPOT_ACCESS_TOKEN",
    ""
)
HUBSPOT_API_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
HUBSPOT_WORKFLOWS_URL = "https://api.hubapi.com/crm/v3/extensions/calling/send"

# --- APPLICATION SETTINGS ---
APP_NAME = "KeaBuilder AI Agent"
APP_DESCRIPTION = "AI-powered lead qualification with HubSpot CRM integration"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# --- CONTENT PROVIDERS ---
CONTENT_PROVIDERS = {
    "image": "stability-or-gemini-image-provider",
    "video": "runway-or-pika-video-provider",
    "voice": "elevenlabs-voice-provider",
}

# --- VALID INTENTS ---
VALID_INTENTS = [
    "lead_qualification",
    "demo_request",
    "pricing_inquiry",
    "feature_question",
    "complaint",
    "other"
]

# --- LEAD CLASSIFICATION THRESHOLDS ---
HOT_SCORE = 4
WARM_SCORE = 2
COLD_SCORE = 0
