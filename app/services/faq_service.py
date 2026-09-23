"""
Service layer for FAQ management.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import FAQEntry
from app.schemas import FAQCreate, FAQUpdate

def get_all_faqs(db: Session, category: Optional[str] = None) -> List[FAQEntry]:
    """Retrieve all FAQs, optionally filtered by category."""
    query = db.query(FAQEntry)
    if category:
        query = query.filter(FAQEntry.category == category)
    return query.all()

def get_faq_by_id(db: Session, faq_id: int) -> Optional[FAQEntry]:
    """Retrieve a single FAQ by its ID."""
    return db.query(FAQEntry).filter(FAQEntry.id == faq_id).first()

def create_faq(db: Session, faq_data: FAQCreate) -> FAQEntry:
    """Create a new FAQ entry."""
    new_faq = FAQEntry(
        question=faq_data.question,
        answer=faq_data.answer,
        category=faq_data.category
    )
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    return new_faq

def update_faq(db: Session, faq_id: int, faq_data: FAQUpdate) -> Optional[FAQEntry]:
    """Update an existing FAQ entry."""
    faq_entry = get_faq_by_id(db, faq_id)
    if faq_entry:
        if faq_data.question is not None:
            faq_entry.question = faq_data.question
        if faq_data.answer is not None:
            faq_entry.answer = faq_data.answer
        if faq_data.category is not None:
            faq_entry.category = faq_data.category
        db.commit()
        db.refresh(faq_entry)
    return faq_entry

def delete_faq(db: Session, faq_id: int) -> bool:
    """Delete an FAQ entry by its ID."""
    faq_entry = get_faq_by_id(db, faq_id)
    if faq_entry:
        db.delete(faq_entry)
        db.commit()
        return True
    return False
