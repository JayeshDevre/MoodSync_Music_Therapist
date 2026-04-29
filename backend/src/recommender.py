from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """Dataclass representing a song and its audio feature attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """Dataclass representing a listener's taste preferences used for scoring."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_valence: float
    target_danceability: float
    target_acousticness: float

class Recommender:
    """OOP wrapper around score_song that ranks catalog songs for a given UserProfile."""

    def __init__(self, songs: List[Song]):
        """Store the song catalog for repeated recommendation calls."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score_song against the given UserProfile."""
        user_prefs = {
            "genre":        user.favorite_genre,
            "mood":         user.favorite_mood,
            "energy":       user.target_energy,
            "valence":      user.target_valence,
            "danceability": user.target_danceability,
            "acousticness": user.target_acousticness,
        }
        scored = sorted(
            self.songs,
            key=lambda s: score_song(user_prefs, vars(s))[0],
            reverse=True,
        )
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string of reasons why a song was recommended."""
        user_prefs = {
            "genre":        user.favorite_genre,
            "mood":         user.favorite_mood,
            "energy":       user.target_energy,
            "valence":      user.target_valence,
            "danceability": user.target_danceability,
            "acousticness": user.target_acousticness,
        }
        _, reasons = score_song(user_prefs, vars(song))
        return ", ".join(reasons) if reasons else "general match"

def load_songs(csv_path: str) -> List[Dict]:
    """Parse songs.csv into a list of dicts with numeric fields cast to float."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["energy"]       = float(row["energy"])
            row["tempo_bpm"]    = float(row["tempo_bpm"])
            row["valence"]      = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user preferences: +1.0 genre, +1.0 mood, weighted numeric proximity.

    Experiment — Weight Shift:
      genre  halved : 2.0 → 1.0  (less categorical dominance)
      energy doubled: 1.5 → 3.0  (numeric feel matters more)
    New max possible score: 1.0 + 1.0 + 3.0 + 1.0 + 0.75 + 0.75 = 7.5
    Math check: all weights positive, similarity in [0,1] → score always in [0, 7.5] ✓
    """
    score = 0.0
    reasons: List[str] = []

    # --- categorical (genre halved to reduce dominance) ---
    if song.get("genre", "").lower() == user_prefs.get("genre", "").lower():
        score += 1.0          # was 2.0
        reasons.append("genre match")

    if song.get("mood", "").lower() == user_prefs.get("mood", "").lower():
        score += 1.0
        reasons.append("mood match")

    # --- continuous similarity (energy doubled to amplify feel signal) ---
    numeric_weights = [
        ("energy",       "energy",       3.00),   # was 1.50
        ("valence",      "valence",      1.00),
        ("danceability", "danceability", 0.75),
        ("acousticness", "acousticness", 0.75),
    ]
    for song_key, pref_key, weight in numeric_weights:
        similarity = 1.0 - abs(song[song_key] - user_prefs[pref_key])
        score += weight * similarity
        if similarity >= 0.85:
            reasons.append(f"close {song_key}")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song in the catalog, sort descending, and return the top-k as (song, score, explanation)."""
    scored = sorted(
        (
            (song, score, ", ".join(reasons) if reasons else "general match")
            for song in songs
            for score, reasons in (score_song(user_prefs, song),)
        ),
        key=lambda x: x[1],
        reverse=True,
    )
    return scored[:k]


def mood_vector_to_prefs(mood_vector: Dict) -> Dict:
    """Convert mood parser output into the user_prefs dict expected by score_song/recommend_songs.

    mood_parser returns:
      { mood, energy, valence, danceability, acousticness, genre_hint, reasoning }
    score_song expects:
      { genre, mood, energy, valence, danceability, acousticness }
    """
    return {
        "genre":        mood_vector.get("genre_hint", ""),
        "mood":         mood_vector.get("mood", ""),
        "energy":       mood_vector.get("energy", 0.5),
        "valence":      mood_vector.get("valence", 0.5),
        "danceability": mood_vector.get("danceability", 0.5),
        "acousticness": mood_vector.get("acousticness", 0.5),
    }

