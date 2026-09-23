"""
Unit tests for the NLP engine and preprocessor.
Tests the text preprocessing pipeline and semantic search functionality.
"""
import pytest
from app.nlp.preprocessor import preprocess, download_nltk_data
from app.nlp.engine import NLPEngine
from app.config import MODEL_NAME


# Ensure NLTK data is available for all tests
@pytest.fixture(scope="module", autouse=True)
def nltk_data():
    """Download NLTK data once for this module."""
    download_nltk_data()


# ── Preprocessor Tests ───────────────────────────────────────────────


def test_preprocess_removes_stopwords():
    """Verify that common English stopwords are removed."""
    text = "this is a test of the chatbot"
    result = preprocess(text)
    assert "test" in result
    assert "chatbot" in result
    # Common stopwords should be removed
    assert " is " not in f" {result} " or "is" not in result.split()


def test_preprocess_lemmatizes():
    """Verify lemmatization (e.g., 'cats' -> 'cat')."""
    text = "the cats are running quickly"
    result = preprocess(text)
    assert "cat" in result
    # 'running' may lemmatize to 'running' (verb lemmatization needs POS tag)
    # but 'cats' should become 'cat'
    assert "cat" in result.split()


def test_preprocess_handles_empty_string():
    """Edge case: empty string should return empty string."""
    assert preprocess("") == ""


def test_preprocess_removes_punctuation():
    """Punctuation should be stripped from input text."""
    text = "Hello! How are you doing?"
    result = preprocess(text)
    assert "!" not in result
    assert "?" not in result


# ── NLP Engine Tests ─────────────────────────────────────────────────


@pytest.fixture(scope="module")
def nlp_engine():
    """Provide an NLPEngine instance for tests (loads model once)."""
    return NLPEngine(MODEL_NAME)


@pytest.fixture
def sample_faqs():
    """Sample FAQ data matching the dict format expected by NLPEngine."""
    return [
        {"id": 1, "question": "What is the price of this product?"},
        {"id": 2, "question": "How do I return an item?"},
        {"id": 3, "question": "What are your business hours?"},
    ]


def test_engine_build_index(nlp_engine, sample_faqs):
    """Verify index is built with correct shape."""
    nlp_engine.build_index(sample_faqs)
    assert nlp_engine.is_indexed is True
    assert len(nlp_engine.faq_ids) == 3
    assert nlp_engine.embeddings.shape[0] == 3


def test_engine_find_exact_match(nlp_engine, sample_faqs):
    """Query with exact FAQ question should return high confidence."""
    nlp_engine.build_index(sample_faqs)
    results = nlp_engine.find_best_match("What is the price of this product?")
    assert len(results) > 0
    assert results[0]["faq_id"] == 1
    assert results[0]["score"] > 0.85


def test_engine_find_semantic_match(nlp_engine, sample_faqs):
    """Query with semantically similar question should match."""
    nlp_engine.build_index(sample_faqs)
    results = nlp_engine.find_best_match("How much does it cost?")
    assert len(results) > 0
    # Should match "What is the price of this product?"
    assert results[0]["faq_id"] == 1
    assert results[0]["score"] > 0.4


def test_engine_low_confidence_for_irrelevant(nlp_engine, sample_faqs):
    """Completely irrelevant query should have low score."""
    nlp_engine.build_index(sample_faqs)
    results = nlp_engine.find_best_match("quantum physics dark matter")
    assert len(results) > 0
    assert results[0]["score"] < 0.4


def test_engine_empty_index(nlp_engine):
    """Querying empty index should return empty results."""
    nlp_engine.build_index([])  # Build with empty list
    results = nlp_engine.find_best_match("Hello?")
    assert results == []


def test_engine_empty_query(nlp_engine, sample_faqs):
    """Empty query string should return empty results."""
    nlp_engine.build_index(sample_faqs)
    results = nlp_engine.find_best_match("")
    assert results == []
