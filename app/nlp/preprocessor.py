"""
Text preprocessor module for the AI-powered FAQ chatbot.
Handles tokenization, stopword removal, and lemmatization using NLTK.
"""

import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def download_nltk_data() -> None:
    """
    Downloads required NLTK datasets if they are not already present.
    Required datasets: 'punkt_tab', 'stopwords', 'wordnet'.
    """
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)


# Cache stopwords and lemmatizer at module level for performance.
# These are loaded once when the module is first imported, instead of
# being recreated on every call to preprocess().
_stop_words: set | None = None
_lemmatizer: WordNetLemmatizer | None = None


def _get_stop_words() -> set:
    """Lazily load and cache the English stopwords set."""
    global _stop_words
    if _stop_words is None:
        _stop_words = set(stopwords.words('english'))
    return _stop_words


def _get_lemmatizer() -> WordNetLemmatizer:
    """Lazily load and cache the WordNet lemmatizer."""
    global _lemmatizer
    if _lemmatizer is None:
        _lemmatizer = WordNetLemmatizer()
    return _lemmatizer


def preprocess(text: str) -> str:
    """
    Preprocesses the input text by applying lowercase conversion, punctuation removal,
    tokenization, stopword removal, and lemmatization.

    Args:
        text (str): The raw input text to preprocess.

    Returns:
        str: The cleaned and preprocessed text as a single string.
    """
    if not text or not text.strip():
        return ""

    # 1. Convert to lowercase
    text = text.lower()

    # 2. Remove punctuation (keep alphanumeric and spaces)
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)

    # 3. Tokenize with nltk.word_tokenize
    tokens = word_tokenize(text)

    # 4. Remove English stopwords (using cached set)
    stop_words = _get_stop_words()
    filtered_tokens = [word for word in tokens if word not in stop_words]

    # 5. Lemmatize with WordNetLemmatizer (using cached instance)
    lemmatizer = _get_lemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]

    # 6. Return joined cleaned tokens
    return " ".join(lemmatized_tokens)
