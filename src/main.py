"""
Command line runner for the Music Recommender Simulation.
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Taste profile: upbeat pop listener who wants happy, high-energy tracks
    user_prefs = {
        "genre":        "pop",
        "mood":         "happy",
        "energy":       0.85,   # high energy
        "valence":      0.85,   # bright, positive tone
        "danceability": 0.80,   # danceable
        "acousticness": 0.15,   # produced, not acoustic
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    width = 52
    print(f"\n{'─' * width}")
    print(f"  🎵  Top {len(recommendations)} Recommendations")
    print(f"  Profile: {user_prefs['genre']} · {user_prefs['mood']} · energy {user_prefs['energy']}")
    print(f"{'─' * width}")

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']}  —  {song['artist']}")
        print(f"       Score : {score:.2f} / 7.00")
        print(f"       Why   : {explanation}")

    print(f"\n{'─' * width}\n")


if __name__ == "__main__":
    main()
