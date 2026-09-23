"""
Configuration settings for the AI-Powered FAQ Chatbot.

This module defines global constants and settings used throughout the application.
Settings can be overridden via environment variables for deployment flexibility.
"""

import os

# The name of the sentence-transformers model to use for embeddings
MODEL_NAME: str = os.getenv('MODEL_NAME', 'all-MiniLM-L6-v2')

# Minimum cosine similarity score required for a confident FAQ match
SIMILARITY_THRESHOLD: float = float(os.getenv('SIMILARITY_THRESHOLD', '0.65'))

# Database connection URL (override via DATABASE_URL env var for production)
DB_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./chatbot.db')

# Number of candidate matches to retrieve and evaluate
TOP_K: int = int(os.getenv('TOP_K', '3'))

# Application metadata
APP_TITLE: str = 'AI-Powered FAQ Chatbot'
APP_VERSION: str = '1.0.0'

# CORS allowed origins (comma-separated in env var, default allows all for development)
CORS_ORIGINS: list[str] = os.getenv('CORS_ORIGINS', '*').split(',')
