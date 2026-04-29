"""
Mood Parser — converts raw user text into a structured mood vector
using Llama 3 via OpenRouter (free). Output feeds into the song scorer.
"""

import os
import json
import re
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
_MODEL = "openai/gpt-oss-20b:free"

SYSTEM_PROMPT = "You are a music therapist assistant. You analyze emotional states and return structured JSON only. No markdown, no explanation, just raw JSON."

USER_PROMPT = """Analyze this emotional state and return ONLY a JSON object, no extra text:

User says: "{user_input}"

Return exactly this structure:
{{
  "mood": "<one word: happy|sad|anxious|angry|focused|tired|excited|melancholic|stressed|calm|nostalgic|romantic|energetic|peaceful>",
  "energy": <float 0.0-1.0>,
  "valence": <float 0.0-1.0, 0=very negative 1=very positive>,
  "danceability": <float 0.0-1.0>,
  "acousticness": <float 0.0-1.0>,
  "genre_hint": "<one of: pop|lofi|rock|classical|ambient|jazz|electronic|folk|r&b|hip-hop|synthwave|metal|country|funk>",
  "reasoning": "<one sentence explaining your interpretation>"
}}"""

_FALLBACK_MOOD = {
    "mood": "calm",
    "energy": 0.5,
    "valence": 0.5,
    "danceability": 0.5,
    "acousticness": 0.5,
    "genre_hint": "lofi",
    "reasoning": "Could not parse mood, using neutral defaults."
}


def parse_mood(user_input: str) -> dict:
    """Send user text to Llama 3 via OpenRouter and return a structured mood vector."""
    if not user_input or not user_input.strip():
        logger.warning("Empty user input, using fallback mood")
        return _FALLBACK_MOOD.copy()

    try:
        response = _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT.format(user_input=user_input.strip())}
            ],
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown code blocks if model wraps in them
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        mood_data = json.loads(raw)
        mood_data = _validate_mood(mood_data)

        logger.info(f"Mood parsed: {mood_data['mood']} | energy={mood_data['energy']} | genre={mood_data['genre_hint']}")
        return mood_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e} | raw: {raw[:200]}")
        return _FALLBACK_MOOD.copy()
    except Exception as e:
        logger.error(f"Mood parser error: {e}")
        return _FALLBACK_MOOD.copy()


def _validate_mood(data: dict) -> dict:
    """Clamp numeric fields to [0,1] and fill missing keys with fallback values."""
    for key in ["energy", "valence", "danceability", "acousticness"]:
        if key not in data:
            data[key] = _FALLBACK_MOOD[key]
        else:
            data[key] = max(0.0, min(1.0, float(data[key])))
    for key in ["mood", "genre_hint", "reasoning"]:
        if key not in data:
            data[key] = _FALLBACK_MOOD[key]
    return data
