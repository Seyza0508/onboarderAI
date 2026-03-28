from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer


def create_vectorizer() -> TfidfVectorizer:
    # TF-IDF is lightweight for V1 and easy to replace with dense embeddings later.
    return TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
