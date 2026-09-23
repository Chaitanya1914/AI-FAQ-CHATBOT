"""
Router for querying conversation logs and statistics.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import ConversationLog, FAQEntry
from app.schemas import LogResponse, LogStats
from app.config import SIMILARITY_THRESHOLD

router = APIRouter()

@router.get("/", response_model=List[LogResponse])
def get_logs(
    session_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    low_confidence: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """
    Retrieve conversation logs with optional filters.
    """
    query = db.query(ConversationLog)
    
    if session_id:
        query = query.filter(ConversationLog.session_id == session_id)
    if date_from:
        query = query.filter(ConversationLog.timestamp >= date_from)
    if date_to:
        query = query.filter(ConversationLog.timestamp <= date_to)
    if low_confidence:
        query = query.filter(ConversationLog.confidence_score < SIMILARITY_THRESHOLD)
        
    return query.order_by(desc(ConversationLog.timestamp)).all()

@router.get("/stats", response_model=LogStats)
def get_log_stats(db: Session = Depends(get_db)):
    """
    Get statistics for conversation logs.
    Returns total count, average confidence, top matched FAQs, and count of unanswered queries.
    """
    total_conversations = db.query(func.count(ConversationLog.id)).scalar() or 0
    
    avg_confidence = db.query(func.avg(ConversationLog.confidence_score)).scalar() or 0.0
    
    unanswered_count = db.query(func.count(ConversationLog.id)).filter(
        ConversationLog.confidence_score < SIMILARITY_THRESHOLD
    ).scalar() or 0
    
    top_faqs = (
        db.query(FAQEntry.question, func.count(ConversationLog.id).label("count"))
        .join(ConversationLog, FAQEntry.id == ConversationLog.matched_faq_id)
        .group_by(FAQEntry.id)
        .order_by(desc("count"))
        .limit(5)
        .all()
    )
    
    top_matched = [{"question": q, "count": c} for q, c in top_faqs]
    
    return LogStats(
        total_conversations=total_conversations,
        avg_confidence=float(avg_confidence),
        top_faqs=top_matched,
        unanswered_count=unanswered_count
    )
