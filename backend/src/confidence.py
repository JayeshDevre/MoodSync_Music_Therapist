"""
Confidence Scorer — assigns a confidence score to each recommendation.

Score is a weighted combination of:
  - Numeric match score (from recommender) normalized to [0, 1]
  - RAG relevance (average score of retrieved docs)
  - Mood/genre alignment bonus

Confidence levels:
  HIGH   >= 0.70
  MEDIUM >= 0.45
  LOW    <  0.45  → flagged for clarification
"""

from typing import List, Dict, Tuple

MAX_RECOMMENDER_SCORE = 7.5   # theoretical max from score_song weights

# Weights for final confidence
W_MATCH = 0.60   # how well song matched numerically
W_RAG   = 0.40   # how relevant the retrieved research was


def score_confidence(
    explained_songs: List[Dict],
    rag_context: List[Dict],
) -> List[Dict]:
    """
    Add confidence score and level to each explained song dict.
    Returns the same list with 'confidence_score' and 'confidence_level' added.
    """
    rag_relevance = _avg_rag_score(rag_context)

    for song in explained_songs:
        match_norm = min(song["score"] / MAX_RECOMMENDER_SCORE, 1.0)
        confidence = round(W_MATCH * match_norm + W_RAG * rag_relevance, 3)
        song["confidence_score"] = confidence
        song["confidence_level"] = _level(confidence)
        song["low_confidence_flag"] = confidence < 0.45

    return explained_songs


def needs_clarification(songs: List[Dict]) -> bool:
    """Return True if majority of picks are low confidence — prompt user to clarify."""
    low = sum(1 for s in songs if s.get("low_confidence_flag", False))
    return low >= len(songs) // 2


def _avg_rag_score(rag_context: List[Dict]) -> float:
    """Average cosine similarity score of retrieved RAG docs, normalized to [0, 1]."""
    if not rag_context:
        return 0.3   # neutral penalty if no docs retrieved
    scores = [c.get("score", 0.0) for c in rag_context]
    # RAG scores are cosine similarities typically in [0, 1]
    return round(sum(scores) / len(scores), 3)


def _level(score: float) -> str:
    if score >= 0.70:
        return "HIGH"
    elif score >= 0.45:
        return "MEDIUM"
    return "LOW"
