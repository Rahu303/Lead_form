"""
AI/LLM Service
Handles intent detection and response generation using LLM APIs
"""
import re
from typing import List, Dict
from shared.config import LLM_PROVIDER, OPENAI_API_KEY, GEMINI_API_KEY, VALID_INTENTS

try:
    import openai
    OPENAI_AVAILABLE = True
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
except ImportError:
    GEMINI_AVAILABLE = False


class AIService:
    """Service for LLM-based intent detection and response generation"""

    @staticmethod
    def detect_intent(message: str, user_name: str, user_email: str) -> str:
        """
        Detects user intent using LLM (GPT-4 or Gemini).
        Falls back to keyword detection if LLM not available.
        """
        if LLM_PROVIDER == "openai" and OPENAI_AVAILABLE:
            return AIService._detect_intent_openai(message, user_name, user_email)
        elif LLM_PROVIDER == "gemini" and GEMINI_AVAILABLE:
            return AIService._detect_intent_gemini(message, user_name, user_email)
        else:
            return AIService._detect_intent_keywords(message)

    @staticmethod
    def _detect_intent_openai(message: str, user_name: str, user_email: str) -> str:
        """Detect intent using OpenAI GPT-4"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant. Detect the user's intent in ONE word only. Choose from: lead_qualification, demo_request, pricing_inquiry, feature_question, complaint, or other."
                    },
                    {
                        "role": "user",
                        "content": f"User: {user_name}\nEmail: {user_email}\nMessage: {message}\n\nIntent:"
                    }
                ],
                temperature=0.3,
                max_tokens=20
            )
            intent = response.choices[0].message.content.strip().lower().strip(" .:-")
            if intent == "other":
                return AIService._detect_intent_keywords(message)
            return intent if intent in VALID_INTENTS else AIService._detect_intent_keywords(message)
        except Exception as e:
            print(f"OpenAI error: {e}. Falling back to keyword detection.")
            return AIService._detect_intent_keywords(message)

    @staticmethod
    def _detect_intent_gemini(message: str, user_name: str, user_email: str) -> str:
        """Detect intent using Google Gemini"""
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(
                f"You are an AI assistant. Detect the user's intent in ONE word only. Choose from: lead_qualification, demo_request, pricing_inquiry, feature_question, complaint, or other.\n\nUser: {user_name}\nEmail: {user_email}\nMessage: {message}\n\nIntent:"
            )
            intent = response.text.strip().lower().strip(" .:-")
            if intent == "other":
                return AIService._detect_intent_keywords(message)
            return intent if intent in VALID_INTENTS else AIService._detect_intent_keywords(message)
        except Exception as e:
            print(f"Gemini error: {e}. Falling back to keyword detection.")
            return AIService._detect_intent_keywords(message)

    @staticmethod
    def _detect_intent_keywords(message: str) -> str:
        """Fallback: Keyword-based intent detection"""
        message_lower = message.lower()

        lead_phrases = [
            "interested",
            "want to",
            "looking to",
            "need",
            "requirement",
            "budget",
            "timeline",
            "launch",
            "project",
            "create a contact",
            "add a contact",
            "create contact",
            "add contact",
            "new contact",
            "new lead",
            "create a lead",
            "add a lead",
            "million dollar",
        ]
        lead_patterns = [
            r"\$\s?\d+",
            r"\b\d+\s?(k|m|million|lakh|crore)\b",
            r"\b(high|large|enterprise)\s+(budget|value|project)\b",
        ]

        if any(phrase in message_lower for phrase in lead_phrases):
            return "lead_qualification"
        if any(re.search(pattern, message_lower) for pattern in lead_patterns):
            return "lead_qualification"
        if any(word in message_lower for word in ["demo", "show me", "how it works", "video", "walkthrough"]):
            return "demo_request"
        if any(word in message_lower for word in ["price", "cost", "plan", "pricing"]):
            return "pricing_inquiry"
        if any(word in message_lower for word in ["feature", "support", "integrate", "api"]):
            return "feature_question"
        if any(word in message_lower for word in ["issue", "problem", "bug", "error", "help"]):
            return "complaint"

        return "other"

    @staticmethod
    def generate_response(intent: str, message: str, user_name: str, conversation_context: List[Dict] = None) -> str:
        """Generate response using LLM with conversation context"""
        conversation_context = conversation_context or []

        if LLM_PROVIDER == "openai" and OPENAI_AVAILABLE:
            return AIService._generate_response_openai(intent, message, user_name, conversation_context)
        elif LLM_PROVIDER == "gemini" and GEMINI_AVAILABLE:
            return AIService._generate_response_gemini(intent, message, user_name, conversation_context)
        else:
            return AIService._generate_response_template(intent, user_name, message)

    @staticmethod
    def _generate_response_openai(intent: str, message: str, user_name: str, conversation_context: List[Dict]) -> str:
        """Generate response using OpenAI GPT-4"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"You are a friendly KeaBuilder AI assistant. The user's intent is: {intent}. Keep responses concise (2-3 sentences). Use the user's name ({user_name}) naturally."
                }
            ]
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
            return AIService._generate_response_template(intent, user_name, message)

    @staticmethod
    def _generate_response_gemini(intent: str, message: str, user_name: str, conversation_context: List[Dict]) -> str:
        """Generate response using Google Gemini"""
        try:
            model = genai.GenerativeModel("gemini-pro")
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_context[-4:]])
            prompt = f"You are a friendly KeaBuilder AI assistant. The user's intent is: {intent}. Keep responses concise (2-3 sentences).\n\nContext:\n{context}\n\nUser ({user_name}): {message}\n\nAssistant:"
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini response generation failed: {e}")
            return AIService._generate_response_template(intent, user_name, message)

    @staticmethod
    def _generate_response_template(intent: str, user_name: str, message: str = "") -> str:
        """Fallback: Template-based response"""
        normalized_message = message.strip().lower()
        affirmative_replies = {"yes", "yeah", "yep", "ok", "okay", "sure", "please", "go ahead", "do it"}
        has_contact_details = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", message))
        if has_contact_details:
            lead_response = "Got it. I have created/updated the contact and logged the project details for follow-up."
        elif normalized_message in affirmative_replies:
            lead_response = "Great, please share the contact details: full name, email id, company name, phone number, budget, and timeline."
        else:
            lead_response = (
                f"Thanks {user_name}! This sounds like a strong opportunity. "
                "Please share the contact details: full name, email id, company name, phone number, budget, and timeline."
            )
        responses = {
            "lead_qualification": lead_response,
            "demo_request": f"Perfect! When would you like to see a demo? I have slots Tuesday-Thursday, 2-5 PM EST.",
            "pricing_inquiry": "We offer flexible plans from $99/month for startups to enterprise custom pricing. What features matter most?",
            "feature_question": "Great question! Would you like detailed feature docs or a quick comparison?",
            "complaint": f"I'm sorry to hear about the issue, {user_name}. Our support team will help right away.",
            "other": f"Thanks for reaching out, {user_name}! How can I help you today?"
        }
        return responses.get(intent, responses["other"])
