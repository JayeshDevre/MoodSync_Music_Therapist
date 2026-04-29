"""
Agentic Self-Critique Loop — reviews song candidates and checks:
  1. Genre diversity (not all same genre)
  2. Energy flow (gradual, not jarring jumps)
  3. Mood alignment (songs match the user's emotional state)

If critique fails, it adjusts weights and rescores. Max 2 retry loops.
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

MAX_RETRIES = 2

CRITIQUE_PROMPT = """You are a music curation expert. Review these song recommendations for a user feeling: "{mood}".

Recommended songs:
{songs_list}

Retrieved research context:
{rag_context}

Evaluate these 3 criteria and return ONLY a JSON object, no extra text:
{{
  "passed": <true if all criteria pass, false if any fail>,
  "genre_diversity": <true if at least 2 different genres present>,
  "energy_flow": <true if energy levels are reasonably smooth, no jarring jumps>,
  "mood_alignment": <true if songs generally match the user mood>,
  "issues": "<comma-separated list of failed criteria, or empty string if passed>",
  "adjustment": "<one sentence on what to change if failed, or empty string if passed>"
}}"""


def run_agent(
    mood_vector: Dict,
    candidates: List[Tuple[Dict, float, str]],
    rag_context: List[Dict],
    songs_pool: List[Dict],
    k: int = 5,
) -> Tuple[List[Tuple[Dict, float, str]], Dict]:
    """
    Agentic loop: critique candidates, adjust if needed, return final picks + agent log.

    Returns:
        final_picks: top-k (song, score, reason) tuples
        agent_log: dict with critique results and retry info
    """
    from recommender import recommend_songs, score_song

    agent_log = {"retries": 0, "critiques": [], "final_passed": False}
    current_candidates = candidates[:k]
    weight_boost = 0.0  # incremental adjustment on retry

    for attempt in range(MAX_RETRIES + 1):
        critique = _critique(mood_vector, current_candidates, rag_context)
        agent_log["critiques"].append(critique)

        if critique.get("passed", True):
            agent_log["final_passed"] = True
            logger.info(f"Agent passed on attempt {attempt + 1}")
            break

        # Failed — log and adjust
        logger.warning(f"Agent critique failed (attempt {attempt + 1}): {critique.get('issues')}")
        agent_log["retries"] += 1

        if attempt < MAX_RETRIES:
            # Boost acousticness weight to increase variety on retry
            weight_boost += 0.5
            current_candidates = _rerank(
                mood_vector, songs_pool, k, weight_boost, current_candidates
            )

    return current_candidates, agent_log


def _critique(
    mood_vector: Dict,
    candidates: List[Tuple[Dict, float, str]],
    rag_context: List[Dict],
) -> Dict:
    """Send candidates to LLM for critique. Returns critique dict."""
    songs_list = "\n".join(
        f"- {s['title']} by {s['artist']} | genre={s['genre']} | mood={s['mood']} | energy={s['energy']}"
        for s, _, _ in candidates
    )
    rag_text = "\n".join(c["text"][:200] for c in rag_context) if rag_context else "No context retrieved."

    prompt = CRITIQUE_PROMPT.format(
        mood=mood_vector.get("mood", "unknown"),
        songs_list=songs_list,
        rag_context=rag_text,
    )

    # Fallback if LLM call fails — assume passed to avoid blocking
    fallback = {
        "passed": True,
        "genre_diversity": True,
        "energy_flow": True,
        "mood_alignment": True,
        "issues": "",
        "adjustment": "",
    }

    try:
        response = _client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Critique LLM call failed: {e}")
        return fallback


def _rerank(
    mood_vector: Dict,
    songs_pool: List[Dict],
    k: int,
    weight_boost: float,
    previous: List[Tuple[Dict, float, str]],
) -> List[Tuple[Dict, float, str]]:
    """
    Rerank by penalizing genres already dominant in previous picks,
    encouraging diversity on retry.
    """
    from recommender import score_song

    # Count genres in previous picks
    genre_counts: Dict[str, int] = {}
    for song, _, _ in previous:
        g = song.get("genre", "")
        genre_counts[g] = genre_counts.get(g, 0) + 1

    user_prefs = {
        "genre":        mood_vector.get("genre_hint", ""),
        "mood":         mood_vector.get("mood", ""),
        "energy":       mood_vector.get("energy", 0.5),
        "valence":      mood_vector.get("valence", 0.5),
        "danceability": mood_vector.get("danceability", 0.5),
        "acousticness": mood_vector.get("acousticness", 0.5),
    }

    rescored = []
    for song in songs_pool:
        base_score, reasons = score_song(user_prefs, song)
        # Penalize over-represented genres
        penalty = genre_counts.get(song.get("genre", ""), 0) * weight_boost
        adjusted_score = base_score - penalty
        rescored.append((song, adjusted_score, ", ".join(reasons) if reasons else "general match"))

    rescored.sort(key=lambda x: x[1], reverse=True)
    return rescored[:k]
