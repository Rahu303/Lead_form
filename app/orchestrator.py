"""
Application Orchestrator
Manages the flow: Chat Input -> AI Intent Detection -> Response Generation -> HubSpot Sync
"""
import re
from typing import Dict, List, Optional, Any
from collections import defaultdict
from datetime import datetime
from shared.validation.schemas import ChatMessage, ChatResponse
from app.services.ai_service import AIService
from connector.hubspot import HubSpotConnector
from shared.config import LLM_PROVIDER


AFFIRMATIVE_REPLIES = {"yes", "yeah", "yep", "ok", "okay", "sure", "please", "go ahead", "do it"}


class Orchestrator:
    """Orchestrates the entire flow from user input to HubSpot"""

    def __init__(self):
        self.ai_service = AIService()
        self.hubspot = HubSpotConnector()
        # In-memory conversation history (use database in production)
        self.conversation_history = defaultdict(list)
        self.conversation_counter = 0

    def process_chat(self, chat_message: ChatMessage) -> ChatResponse:
        """
        Process a chat message end-to-end:
        1. Detect intent
        2. Generate response
        3. Store conversation history
        4. Sync to HubSpot
        5. Trigger workflows
        """
        # Generate conversation ID if not provided
        conversation_id = chat_message.conversation_id or f"conv_{self.conversation_counter}_{datetime.now().timestamp()}"
        self.conversation_counter += 1

        context = self.conversation_history[chat_message.user_email]

        # Step 1: Detect intent
        intent = self._resolve_intent(chat_message, context)
        contact_details = self._extract_contact_details(chat_message.message)

        # Store user message in history with the resolved intent
        context.append({
            "role": "user",
            "content": chat_message.message,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        })

        # Step 3: Generate response
        response_text = self.ai_service.generate_response(
            intent,
            chat_message.message,
            chat_message.user_name,
            context
        )

        # Store assistant response in history
        self.conversation_history[chat_message.user_email].append({
            "role": "assistant",
            "content": response_text,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        })

        # Step 4: HubSpot sync (background task)
        sync_email = contact_details.get("email") or chat_message.user_email
        sync_name = contact_details.get("name") or chat_message.user_name
        hubspot_action = self._sync_to_hubspot(
            sync_email,
            sync_name,
            intent,
            chat_message.message,
            contact_details
        )

        # Step 5: Trigger workflow
        workflow_action = self.hubspot.trigger_workflow(
            sync_email,
            intent,
            "auto_triggered"
        )

        return ChatResponse(
            intent=intent,
            response=response_text,
            hubspot_action=hubspot_action,
            follow_up=f"Your message has been logged. Our team will follow up on your {intent}.",
            llm_provider=LLM_PROVIDER,
            conversation_id=conversation_id
        )

    def _resolve_intent(self, chat_message: ChatMessage, context: List[Dict]) -> str:
        """Use recent conversation state for lead follow-up replies."""
        normalized_message = chat_message.message.strip().lower()
        active_intent = self._get_active_intent(context)

        if normalized_message in AFFIRMATIVE_REPLIES:
            if active_intent:
                return active_intent

        detected_intent = self.ai_service.detect_intent(
            chat_message.message,
            chat_message.user_name,
            chat_message.user_email
        )

        if detected_intent == "other" and active_intent == "lead_qualification":
            return active_intent

        return detected_intent

    def _get_active_intent(self, context: List[Dict]) -> Optional[str]:
        """Find the most recent actionable intent in this conversation."""
        for message in reversed(context[-6:]):
            intent = message.get("intent")
            if intent and intent != "other":
                return intent
            content = message.get("content", "").lower()
            if "contact details" in content or "company name" in content:
                return "lead_qualification"
        return None

    def _extract_contact_details(self, message: str) -> Dict[str, str]:
        """Extract common contact fields from a lead follow-up message."""
        details = {}
        parts = [part.strip() for part in message.split(",") if part.strip()]

        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", message)
        if email_match:
            details["email"] = email_match.group(0)

        phone_match = re.search(r"(?:\+?\d[\d\s-]{7,}\d)", message)
        if phone_match:
            details["phone"] = re.sub(r"[^\d+]", "", phone_match.group(0))

        if parts:
            email_index = next((index for index, part in enumerate(parts) if "@" in part), None)
            if email_index and email_index > 0:
                details["name"] = parts[email_index - 1]
            elif "@" not in parts[0]:
                details["name"] = parts[0]

            if email_index is not None and len(parts) > email_index + 1:
                details["company"] = parts[email_index + 1]
            if len(parts) >= 5:
                details["budget"] = parts[-2]
                details["timeline"] = parts[-1]

        return details

    def _sync_to_hubspot(self, email: str, name: str, intent: str, message: str, contact_details: Optional[Dict[str, str]] = None) -> str:
        """Sync chat data to HubSpot"""
        contact_details = contact_details or {}
        try:
            note_parts = [f"AI Intent: {intent.upper()}", f"Message: {message[:100]}..."]
            if contact_details.get("company"):
                note_parts.append(f"Company: {contact_details['company']}")
            if contact_details.get("budget"):
                note_parts.append(f"Budget: {contact_details['budget']}")
            if contact_details.get("timeline"):
                note_parts.append(f"Timeline: {contact_details['timeline']}")

            properties = {
                "hs_content_membership_notes": " | ".join(note_parts)
            }
            if contact_details.get("company"):
                properties["company"] = contact_details["company"]

            # Create or update contact
            contact_result = self.hubspot.create_or_update_contact(
                email=email,
                name=name,
                phone=contact_details.get("phone"),
                properties=properties
            )

            # Add note
            note_result = self.hubspot.add_note(
                email,
                f"[AI Chat] Intent: {intent} | User: {name}\nMessage: {message}"
            )

            return f"{contact_result['status']} + {note_result['status']}"

        except Exception as e:
            print(f"HubSpot sync failed: {e}")
            return "sync_failed"

    def get_conversation_history(self, email: str) -> List[Dict]:
        """Get conversation history for a user"""
        return self.conversation_history.get(email, [])

    def clear_conversation_history(self, email: str) -> bool:
        """Clear conversation history for a user"""
        if email in self.conversation_history:
            self.conversation_history[email] = []
            return True
        return False
