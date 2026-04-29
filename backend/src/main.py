"""
Command line runner for the Music Recommender Simulation.
Runs six user profiles: three standard and three adversarial edge cases.
"""

from recommender import load_songs, recommend_songs


WIDTH = 54


def print_recommendations(label: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a formatted recommendation block for a single user profile."""
    results = recommend_songs(user_prefs, songs, k=k)
    print(f"\n{'═' * WIDTH}")
    print(f"  {label}")
    print(f"  genre={user_prefs['genre']}  mood={user_prefs['mood']}  energy={user_prefs['energy']}")
    print(f"{'─' * WIDTH}")
    for rank, (song, score, explanation) in enumerate(results, start=1):
        print(f"  #{rank}  {song['title']}  —  {song['artist']}")
        print(f"       Score : {score:.2f} / 7.00")
        print(f"       Why   : {explanation}")
        print()
    print(f"{'═' * WIDTH}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    # ── Standard profiles ────────────────────────────────────────
    print_recommendations(
        "🎵  Profile 1: High-Energy Pop",
        {"genre": "pop", "mood": "happy", "energy": 0.85,
         "valence": 0.85, "danceability": 0.80, "acousticness": 0.15},
        songs,
    )

    print_recommendations(
        "☁️   Profile 2: Chill Lofi",
        {"genre": "lofi", "mood": "chill", "energy": 0.40,
         "valence": 0.60, "danceability": 0.60, "acousticness": 0.75},
        songs,
    )

    print_recommendations(
        "🤘  Profile 3: Deep Intense Rock",
        {"genre": "rock", "mood": "intense", "energy": 0.92,
         "valence": 0.35, "danceability": 0.55, "acousticness": 0.08},
        songs,
    )

    # ── Adversarial / edge-case profiles ─────────────────────────
    print_recommendations(
        "⚡  Edge Case 1: High Energy + Sad Mood (conflicting signals)",
        # energy 0.9 screams intensity but mood 'melancholic' pulls toward
        # quiet, dark songs — does genre or numeric energy win?
        {"genre": "classical", "mood": "melancholic", "energy": 0.90,
         "valence": 0.20, "danceability": 0.30, "acousticness": 0.95},
        songs,
    )

    print_recommendations(
        "👻  Edge Case 2: Genre ghost (no matching genre in catalog)",
        # 'ambient' has only one song; all other signals point to high energy
        # — does the lone ambient track still win on genre alone?
        {"genre": "ambient", "mood": "angry", "energy": 0.95,
         "valence": 0.10, "danceability": 0.90, "acousticness": 0.05},
        songs,
    )

    print_recommendations(
        "🎭  Edge Case 3: All-middle preferences (no strong signal)",
        # Every numeric feature is exactly 0.5 and genre/mood match nothing
        # — pure numeric proximity race with no categorical bonus
        {"genre": "reggae", "mood": "nostalgic", "energy": 0.50,
         "valence": 0.50, "danceability": 0.50, "acousticness": 0.50},
        songs,
    )


if __name__ == "__main__":
    main()
