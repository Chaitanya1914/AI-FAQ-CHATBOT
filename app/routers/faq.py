"""
Router for FAQ management operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import FAQCreate, FAQUpdate, FAQResponse
from app.services import faq_service
from app.nlp.engine import NLPEngine

router = APIRouter()

_nlp_engine: NLPEngine | None = None

def set_nlp_engine(engine: NLPEngine) -> None:
    """Set the global NLPEngine instance."""
    global _nlp_engine
    _nlp_engine = engine

def get_nlp_engine() -> NLPEngine:
    """Retrieve the global NLPEngine instance."""
    if _nlp_engine is None:
        raise RuntimeError("NLPEngine not initialized")
    return _nlp_engine


def _refresh_nlp_index(db: Session) -> None:
    """Helper to refresh the NLP engine index after FAQ mutations."""
    try:
        engine = get_nlp_engine()
        all_faqs = faq_service.get_all_faqs(db)
        faq_dicts = [{"id": f.id, "question": f.question} for f in all_faqs]
        engine.refresh_index(faq_dicts)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to refresh NLP index: {e}")


@router.get("/", response_model=List[FAQResponse])
def list_faqs(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Retrieve all FAQs. Can be filtered by category."""
    return faq_service.get_all_faqs(db, category)

@router.get("/{faq_id}", response_model=FAQResponse)
def get_faq(faq_id: int, db: Session = Depends(get_db)):
    """Retrieve a single FAQ by its ID."""
    faq = faq_service.get_faq_by_id(db, faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq

@router.post("/", response_model=FAQResponse)
def create_faq(faq_data: FAQCreate, db: Session = Depends(get_db)):
    """Create a new FAQ and trigger an NLP engine index refresh."""
    new_faq = faq_service.create_faq(db, faq_data)
    _refresh_nlp_index(db)
    return new_faq

@router.put("/{faq_id}", response_model=FAQResponse)
def update_faq(faq_id: int, faq_data: FAQUpdate, db: Session = Depends(get_db)):
    """Update an existing FAQ and trigger an NLP engine index refresh."""
    updated_faq = faq_service.update_faq(db, faq_id, faq_data)
    if not updated_faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    _refresh_nlp_index(db)
    return updated_faq

@router.delete("/{faq_id}")
def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    """Delete an FAQ and trigger an NLP engine index refresh."""
    success = faq_service.delete_faq(db, faq_id)
    if not success:
        raise HTTPException(status_code=404, detail="FAQ not found")
    _refresh_nlp_index(db)
    return {"message": "FAQ deleted successfully"}
