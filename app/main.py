"""
Main Application Entry Point

This file initializes the FastAPI application for the AI-powered FAQ chatbot.
It handles startup and shutdown events, sets up the database, initializes the
NLP engine, seeds the FAQ database, and mounts necessary routes and templates.
"""

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

# Application imports
from app.config import (
    MODEL_NAME,
    APP_TITLE,
    APP_VERSION,
    CORS_ORIGINS,
)
from app.database import get_db, init_db, SessionLocal
from app.models import FAQEntry
from app.nlp.engine import NLPEngine
from app.nlp.preprocessor import download_nltk_data
from app.services.chat_service import ChatService
from app.services.faq_service import get_all_faqs
from app.routers import chat, faq, logs

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Base directory for the application
BASE_DIR = Path(__file__).resolve().parent.parent

# Set up Jinja2 templates
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


def seed_faq_database() -> None:
    """
    Seeds the FAQ database from the JSON seed file if the table is empty.
    """
    db = SessionLocal()
    try:
        # Check if FAQs already exist
        existing_faqs = db.query(FAQEntry).count()
        if existing_faqs == 0:
            logger.info("FAQ database is empty. Seeding data...")
            seed_file = BASE_DIR / "data" / "faq_seed.json"
            if seed_file.exists():
                with open(seed_file, "r", encoding="utf-8") as f:
                    seed_data = json.load(f)
                    
                for entry in seed_data:
                    new_faq = FAQEntry(
                        category=entry.get("category"),
                        question=entry.get("question"),
                        answer=entry.get("answer")
                    )
                    db.add(new_faq)
                db.commit()
                logger.info(f"Successfully seeded {len(seed_data)} FAQ entries.")
            else:
                logger.warning(f"Seed file not found at {seed_file}")
        else:
            logger.info(f"FAQ database already contains {existing_faqs} entries. Skipping seed.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    Executes startup logic before the application accepts requests,
    and cleanup logic when the application shuts down.
    """
    logger.info("Starting up the AI FAQ Chatbot Application...")
    
    # 1. Download necessary NLTK data
    logger.info("Downloading NLTK data...")
    download_nltk_data()
    
    # 2. Initialize the database (creates tables)
    logger.info("Initializing database...")
    init_db()
    
    # 3. Load the NLP Engine
    logger.info(f"Loading NLP Engine with model: {MODEL_NAME}...")
    nlp_engine = NLPEngine(MODEL_NAME)
    
    # 4. Seed the FAQ database if needed
    seed_faq_database()
    
    # 5. Build the NLP index from all FAQs
    logger.info("Building NLP search index...")
    db = SessionLocal()
    try:
        all_faqs = get_all_faqs(db)
        if all_faqs:
            # Convert ORM objects to dicts expected by NLPEngine
            faq_dicts = [{"id": f.id, "question": f.question} for f in all_faqs]
            nlp_engine.build_index(faq_dicts)
            logger.info("Index built successfully.")
        else:
            logger.warning("No FAQs found to build index.")
    finally:
        db.close()
        
    # 6. Initialize ChatService and configure routers
    logger.info("Configuring services and routers...")
    chat_service = ChatService(nlp_engine)
    chat.set_chat_service(chat_service)
    
    # 7. Set NLP engine for FAQ router
    faq.set_nlp_engine(nlp_engine)
    
    logger.info("Application startup complete.")
    
    # Yield control to the application
    yield
    
    # Shutdown logic
    logger.info("Shutting down the AI FAQ Chatbot Application...")


# Initialize FastAPI application
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="An AI-powered FAQ Chatbot API for smart customer support routing and query resolution. Internship Project.",
    lifespan=lifespan
)

# Add CORS middleware (configurable via CORS_ORIGINS env var)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False if "*" in CORS_ORIGINS else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include application routers
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(faq.router, prefix="/api/faq", tags=["FAQ"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])


@app.get("/", tags=["UI"])
async def read_root(request: Request):
    """
    Renders the main customer-facing chat interface.
    """
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/admin", tags=["UI"])
async def read_admin(request: Request):
    """
    Renders the admin dashboard for managing FAQs and viewing logs.
    """
    return templates.TemplateResponse(request=request, name="admin.html")


if __name__ == "__main__":
    # Run the application using uvicorn when executed directly
    # reload=True is only for development; in production use: uvicorn app.main:app
    import os
    is_dev = os.getenv("ENV", "development") == "development"
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=is_dev)
