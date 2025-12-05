import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

_model_cache = None

class EmbeddingService:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        global _model_cache
        if _model_cache is None:
            logger.info(f"Loading embedding model: {model_name}")
            _model_cache = SentenceTransformer(model_name)
        self.model = _model_cache

    def _clean_text(self, text):
        if not text:
            return ""
        # Basic cleaning: strip, collapse whitespace
        return " ".join(text.strip().split())

    def _normalize_vector(self, vec: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return vec / norm

    def generate_embedding(self, text_or_texts):
        """
        Accepts a string (or list of strings). Returns a normalized list[float] or None on error.
        """
        try:
            if not text_or_texts:
                return None

            if isinstance(text_or_texts, list):
                inputs = [self._clean_text(t) for t in text_or_texts if t and t.strip()]
                if not inputs:
                    return None
                emb = self.model.encode(inputs, convert_to_numpy=True)
                # If multiple inputs, average them and normalize
                if emb.ndim == 2:
                    emb_mean = np.mean(emb, axis=0)
                    emb_norm = self._normalize_vector(emb_mean)
                    return emb_norm.astype(float).tolist()
                else:
                    emb_norm = self._normalize_vector(emb)
                    return emb_norm.astype(float).tolist()
            else:
                text = self._clean_text(text_or_texts)
                if not text:
                    return None
                emb = self.model.encode(text, convert_to_numpy=True)
                emb_norm = self._normalize_vector(emb)
                return emb_norm.astype(float).tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def calculate_similarity(self, embedding1, embedding2):
        """Cosine similarity (expects normalized vectors)"""
        try:
            if not embedding1 or not embedding2:
                return 0.0
            a = np.array(embedding1, dtype=float)
            b = np.array(embedding2, dtype=float)
            # Assume embeddings are normalized — still guard against zero norm
            if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
                return 0.0
            return float(np.dot(a / np.linalg.norm(a), b / np.linalg.norm(b)))
        except Exception as e:
            logger.error(f"Similarity error: {e}")
            return 0.0

    def summarize_text(self, text, max_length=200):
        # Lightweight summarizer fallback — keep the start; it's cheap
        if not text:
            return ""
        s = self._clean_text(text)
        return s[:max_length] + ("..." if len(s) > max_length else "")

    def extract_keywords(self, text, num_keywords=5):
        """Simple freq-based keywords; tune/replace with RAKE/spacy if needed."""
        try:
            if not text:
                return []
            tokens = [w.strip('.,;:!?()[]') for w in text.lower().split()]
            freq = {}
            for t in tokens:
                if len(t) > 3:
                    freq[t] = freq.get(t, 0) + 1
            keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:num_keywords]
            return [k for k, _ in keywords]
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return []
