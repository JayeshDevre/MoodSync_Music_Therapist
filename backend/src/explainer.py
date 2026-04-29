"""
Explainer — generates per-song explanations grounded in RAG research docs.
Each explanation cites the retrieved context, not hallucinated reasoning.
"""

import os
import json
import re
import logging
from typing import List, Dict, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
_MODEL = "liquid/lfm-2.5-1.2b-instruct:free"

EXPLAIN_PROMPT = """You are a music therapist. In exactly 2 sentences, explain why this song suits someone feeling {mood}.
Use the research context to ground your explanation. Mention specific audio features like tempo, energy, or acousticness.

Research context:
{rag_context}

Song: {title} by {artist} | genre={genre} | energy={energy} | tempo={tempo}bpm | acousticness={acousticness}

Return only the 2-sentence explanation, no JSON, no extra text."""


def explain_songs(
    mood_vector: Dict,
    picks: List[Tuple[Dict, float, str]],
    rag_context: List[Dict],
) -> List[Dict]:
    """
    Generate explanations for each picked song using RAG context.
    Returns list of {title, artist, genre, score, explanation} dicts.
    """
    rag_text = "\n".join(
        f"{c['text'][:200]}" for c in rag_context
    ) if rag_context else "No research context available."

    results = []
    for song, score, fallback_reason in picks:
        explanation = _explain_one(mood_vector, song, rag_text, fallback_reason)
        results.append({
            "title":        song["title"],
            "artist":       song["artist"],
            "genre":        song["genre"],
            "mood":         song["mood"],
            "energy":       song["energy"],
            "tempo_bpm":    song["tempo_bpm"],
            "valence":      song["valence"],
            "danceability": song["danceability"],
            "acousticness": song["acousticness"],
            "score":        round(score, 2),
            "explanation":  explanation,
        })

    return results


def _explain_one(mood_vector: Dict, song: Dict, rag_text: str, fallback: str) -> str:
    """Generate explanation for a single song. Falls back to score reason on failure."""
    prompt = EXPLAIN_PROMPT.format(
        mood=mood_vector.get("mood", "unknown"),
        rag_context=rag_text,
        title=song["title"],
        artist=song["artist"],
        genre=song["genre"],
        energy=song["energy"],
        tempo=song["tempo_bpm"],
        acousticness=song["acousticness"],
    )
    try:
        response = _client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Explainer failed for {song['title']}: {e}")
        return fallback
