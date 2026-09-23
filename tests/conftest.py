"""
Test configuration and shared fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import FAQEntry


# Use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_database():
    """Create the database tables once for the entire test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """Provide a clean database session for each test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # Clean up all data after each test
        db.rollback()
        db.close()


@pytest.fixture
def client(db_session):
    """
    Provide a TestClient with the database dependency overridden.
    The lifespan will fire and load the NLP model on first use.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seed_faqs(db_session):
    """
    Seed the test database with FAQ entries and rebuild the NLP index
    so the chat endpoint can find matches.
    """
    faqs = [
        FAQEntry(
            question="What are your business hours?",
            answer="We are open Monday to Friday, 9 AM to 5 PM.",
            category="General"
        ),
        FAQEntry(
            question="How long does shipping take?",
            answer="Standard shipping takes 3-5 business days.",
            category="Shipping"
        ),
        FAQEntry(
            question="What is your return policy?",
            answer="You can return any item within 30 days of purchase.",
            category="Returns"
        ),
    ]
    db_session.add_all(faqs)
    db_session.commit()
    for faq in faqs:
        db_session.refresh(faq)

    # Rebuild the NLP engine index with these test FAQs
    from app.routers.chat import get_chat_service
    try:
        chat_service = get_chat_service()
        faq_dicts = [{"id": f.id, "question": f.question} for f in faqs]
        chat_service.nlp_engine.build_index(faq_dicts)
    except RuntimeError:
        pass  # Service not initialized yet (unit tests)

    return faqs


# Lazy import to avoid loading the model at module level
from app.main import app  # noqa: E402
