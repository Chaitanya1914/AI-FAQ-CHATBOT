"""
Service layer for chat processing.
"""
from sqlalchemy.orm import Session
from app.config import SIMILARITY_THRESHOLD
from app.models import FAQEntry, ConversationLog
from app.nlp.engine import NLPEngine
from typing import Dict, Any, Optional

class ChatService:
    """Service to process incoming chat messages and generate responses."""
    
    def __init__(self, nlp_engine: NLPEngine):
        """
        Initialize the ChatService.

        Args:
            nlp_engine (NLPEngine): The NLP engine used to find best matches.
        """
        self.nlp_engine = nlp_engine

    def process_message(self, message: str, session_id: str, db: Session) -> Dict[str, Any]:
        """
        Process a chat message, find the best FAQ match, and log the conversation.

        Args:
            message (str): The user's input message.
            session_id (str): The conversation session ID.
            db (Session): Database session.

        Returns:
            dict: The response payload containing answer, confidence, and metadata.
        """
        # Find best match using NLP engine
        matches = self.nlp_engine.find_best_match(message)
        
        response_text = ""
        matched_faq = None
        matched_faq_id = None
        
        # Get the top match from the results list
        best_match = matches[0] if matches else {"score": 0.0, "faq_id": None}
        score = best_match.get("score", 0.0)
        
        if score >= SIMILARITY_THRESHOLD:
            faq_id = best_match.get("faq_id")
            faq_entry = db.query(FAQEntry).filter(FAQEntry.id == faq_id).first()
            if faq_entry:
                response_text = faq_entry.answer
                matched_faq = faq_entry.question
                matched_faq_id = faq_entry.id
            else:
                response_text = "I'm sorry, I couldn't find the exact answer."
        else:
            response_text = (
                "I'm not sure I understand your question. Could you try rephrasing it? "
                "You can ask me about shipping, returns, payments, or account management."
            )
            
        # Create a ConversationLog entry
        log_entry = ConversationLog(
            session_id=session_id,
            user_message=message,
            bot_response=response_text,
            confidence_score=score,
            matched_faq_id=matched_faq_id
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        return {
            "response": response_text,
            "confidence": score,
            "session_id": session_id,
            "matched_faq": matched_faq,
            "log_id": log_entry.id
        }
