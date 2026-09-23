"""
Router for handling chat queries.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.models import ConversationLog

router = APIRouter()

_chat_service: ChatService | None = None

def set_chat_service(service: ChatService) -> None:
    """Set the global ChatService instance."""
    global _chat_service
    _chat_service = service

def get_chat_service() -> ChatService:
    """Retrieve the global ChatService instance."""
    if _chat_service is None:
        raise RuntimeError("ChatService not initialized")
    return _chat_service

@router.post("/", response_model=ChatResponse)
def handle_chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Process a chat message from the user and return a response.
    If session_id is not provided, a new UUID will be generated.
    """
    chat_service = get_chat_service()
    session_id = request.session_id or str(uuid.uuid4())
    
    result = chat_service.process_message(request.message, session_id, db)
    
    return ChatResponse(
        response=result["response"],
        confidence=result["confidence"],
        session_id=result["session_id"],
        matched_faq=result["matched_faq"],
        log_id=result["log_id"]
    )

@router.post("/{log_id}/feedback")
def submit_feedback(
    log_id: int, 
    feedback: str = Query(..., description="'positive' or 'negative'"),
    db: Session = Depends(get_db)
):
    """
    Submit feedback for a specific chat response.
    """
    if feedback not in ["positive", "negative"]:
        raise HTTPException(status_code=400, detail="Feedback must be 'positive' or 'negative'")
        
    log_entry = db.query(ConversationLog).filter(ConversationLog.id == log_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
        
    # Assuming ConversationLog has a feedback column.
    log_entry.feedback = feedback
    db.commit()
    
    return {"message": "Feedback recorded successfully"}
