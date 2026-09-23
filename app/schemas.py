"""
Pydantic schemas for data validation and serialization.

Defines the API request and response models.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """
    Request payload for interacting with the chatbot.
    """
    message: str = Field(..., description="The user's message to the chatbot")
    session_id: Optional[str] = Field(default=None, description="An optional session identifier")


class ChatResponse(BaseModel):
    """
    Response payload from the chatbot.
    """
    response: str = Field(..., description="The chatbot's answer")
    confidence: float = Field(..., description="Confidence score of the match")
    session_id: str = Field(..., description="The session identifier")
    matched_faq: Optional[str] = Field(default=None, description="The matched FAQ question, if any")
    log_id: int = Field(..., description="The ID of the conversation log entry")


class FAQCreate(BaseModel):
    """
    Payload for creating a new FAQ entry.
    """
    category: str = Field(..., description="The category of the FAQ")
    question: str = Field(..., description="The question")
    answer: str = Field(..., description="The answer")


class FAQUpdate(BaseModel):
    """
    Payload for updating an existing FAQ entry.
    """
    category: Optional[str] = Field(default=None, description="The category of the FAQ")
    question: Optional[str] = Field(default=None, description="The question")
    answer: Optional[str] = Field(default=None, description="The answer")


class FAQResponse(BaseModel):
    """
    Response model for an FAQ entry.
    """
    id: int
    category: str
    question: str
    answer: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LogResponse(BaseModel):
    """
    Response model for a conversation log entry.
    """
    id: int
    session_id: str
    user_message: str
    bot_response: str
    matched_faq_id: Optional[int]
    confidence_score: float
    timestamp: datetime
    feedback: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class LogStats(BaseModel):
    """
    Response model for chatbot statistics.
    """
    total_conversations: int = Field(..., description="Total number of logged conversations")
    avg_confidence: float = Field(..., description="Average confidence score across conversations")
    top_faqs: List[Dict[str, Any]] = Field(..., description="List of most frequently matched FAQs")
    unanswered_count: int = Field(..., description="Number of interactions with no matching FAQ")
