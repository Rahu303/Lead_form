"""
Pydantic Models for Request/Response Validation
"""
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional, Any

class LeadForm(BaseModel):
    """Lead form submission schema"""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    budget: Optional[str] = None
    timeline: Optional[str] = None
    goals: Optional[str] = None
    message: Optional[str] = None

class ChatMessage(BaseModel):
    """Chat message from user"""
    user_email: str
    user_name: str
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response to user"""
    intent: str
    response: str
    hubspot_action: str
    follow_up: str
    llm_provider: str
    conversation_id: str

class ConversationHistory(BaseModel):
    """Conversation history for a user"""
    email: str
    history: List[Dict[str, str]]

class ContentRequest(BaseModel):
    """Content generation request"""
    content_type: Optional[str] = None
    type: Optional[str] = None
    prompt: str
    style: Optional[str] = None
    brand_name: Optional[str] = None
    personalization: Optional[Dict[str, Any]] = None

    @property
    def resolved_type(self) -> str:
        """Accept both content_type and type from different UI examples."""
        return (self.content_type or self.type or "image").lower()


class SimilarityItem(BaseModel):
    """Searchable asset/template item"""
    id: Any
    text: str
    item_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SimilaritySearchRequest(BaseModel):
    """Similarity search request for text/template matching"""
    query: str
    item_type: Optional[str] = "template"
    items: List[SimilarityItem]
    top_k: int = 3

class HubSpotContact(BaseModel):
    """HubSpot contact schema"""
    email: str
    name: str
    phone: Optional[str] = None
    properties: Dict[str, Any]

class WorkflowTrigger(BaseModel):
    """HubSpot workflow trigger schema"""
    contact_id: str
    intent: str
    action: str
    timestamp: str
