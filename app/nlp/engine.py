"""
Core NLP Engine module for the AI-powered FAQ chatbot.
Utilizes sentence-transformers for semantic search and numpy for cosine similarity.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

from app.nlp.preprocessor import preprocess

class NLPEngine:
    """
    The core engine that powers semantic search for the FAQ chatbot.
    It uses sentence-transformers to capture the semantic meaning of questions
    rather than just relying on simple keyword matching.
    """
    
    def __init__(self, model_name: str) -> None:
        """
        Initializes the NLP engine.

        Args:
            model_name (str): The name of the SentenceTransformer model to load.
        """
        # Load the sentence transformer model
        self.model = SentenceTransformer(model_name)
        
        # Initialize empty index
        self.faq_ids: List[Any] = []
        self.embeddings: np.ndarray = np.array([])
        self.is_indexed: bool = False

    def build_index(self, faqs: List[Dict[str, Any]]) -> None:
        """
        Builds the search index from a list of FAQs.
        Preprocesses each question, encodes them using the model, and stores the
        embeddings as a numpy array alongside the FAQ IDs.

        Args:
            faqs (List[Dict[str, Any]]): A list of dictionaries containing 'id' and 'question'.
        """
        if not faqs:
            self.faq_ids = []
            self.embeddings = np.array([])
            self.is_indexed = False
            return

        self.faq_ids = [faq['id'] for faq in faqs]
        questions = [faq['question'] for faq in faqs]
        
        # Preprocess questions
        preprocessed_questions = [preprocess(q) for q in questions]
        
        # Encode all questions to capture semantic meaning
        self.embeddings = self.model.encode(preprocessed_questions)
        self.is_indexed = True

    def _cosine_similarity(self, query_embedding: np.ndarray, corpus_embeddings: np.ndarray) -> np.ndarray:
        """
        Computes cosine similarity between a query embedding and corpus embeddings.
        Formula: similarity = (A · B) / (||A|| * ||B||)

        Args:
            query_embedding (np.ndarray): The embedding of the search query.
            corpus_embeddings (np.ndarray): The embeddings of the indexed FAQs.

        Returns:
            np.ndarray: An array of similarity scores.
        """
        # Calculate dot product (A · B)
        dot_product = np.dot(corpus_embeddings, query_embedding)
        
        # Calculate norms (||A|| and ||B||)
        query_norm = np.linalg.norm(query_embedding)
        corpus_norms = np.linalg.norm(corpus_embeddings, axis=1)
        
        # Avoid division by zero
        if query_norm == 0 or np.any(corpus_norms == 0):
            # Handle zeroes gracefully
            norms_product = corpus_norms * query_norm
            norms_product[norms_product == 0] = 1e-9
        else:
            norms_product = corpus_norms * query_norm

        return dot_product / norms_product

    def find_best_match(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Finds the most relevant FAQs for a given user query using semantic search.
        
        Args:
            query (str): The user's input question.
            top_k (int, optional): The number of top matches to return. Defaults to 3.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing 'faq_id' and 'score',
                                  sorted by score in descending order.
        """
        if not query or not self.is_indexed or len(self.faq_ids) == 0:
            return []

        # Preprocess query
        preprocessed_query = preprocess(query)
        if not preprocessed_query:
            # If query becomes empty after preprocessing, use original query for encoding
            preprocessed_query = query
            
        # Encode query
        query_embedding = self.model.encode(preprocessed_query)
        
        # Compute cosine similarities
        similarities = self._cosine_similarity(query_embedding, self.embeddings)
        
        # Get top-k indices sorted in descending order
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Construct results
        results = []
        for idx in top_indices:
            results.append({
                'faq_id': self.faq_ids[idx],
                'score': float(similarities[idx])
            })
            
        return results

    def refresh_index(self, faqs: List[Dict[str, Any]]) -> None:
        """
        Rebuilds the index with a new set of FAQs.

        Args:
            faqs (List[Dict[str, Any]]): The updated list of FAQs.
        """
        self.build_index(faqs)
