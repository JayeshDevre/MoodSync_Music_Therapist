# 🎧 Model Card: VibeFinder 1.0

## 1. Model Name

VibeFinder 1.0

---

## 2. Intended Use

VibeFinder is a content-based music recommender built for classroom exploration. It is not a real product. It is designed to show how a simple scoring algorithm can turn a listener's stated preferences into a ranked list of song suggestions.

It assumes the user can describe what they want in advance — a preferred genre, a mood, and rough numeric targets for energy, tone, groove, and texture. It works best as a learning tool for understanding how features, weights, and ranking interact. It should not be used to make real music recommendations for real users.

Non-intended uses: production music apps, personalized streaming, any context where fairness or diversity of results actually matters to a listener's experience.

---

## 3. How the Model Works

Every song in the catalog gets a score. The score is made up of two parts.

The first part is label matching. If a song's genre matches what the user asked for, it gets 1 point (originally 2 points before the weight experiment). If the mood matches, it gets another point. These are all-or-nothing — either the label matches exactly or it scores zero.

The second part is numeric closeness. For four features — energy, emotional tone (valence), danceability, and acousticness — the system measures how far the song's value is from what the user wants. A perfect match scores the full weight for that feature. The further away the song is, the fewer points it earns. Energy is weighted the most because it has the biggest effect on how a song feels.

Once every song has a score, they are sorted from highest to lowest and the top five are returned. The system also generates a short explanation for each result, listing which features were close matches.

---

## 4. Data

The catalog has 18 songs. Each song has a title, artist, genre, mood, and five numeric features: energy, tempo, valence, danceability, and acousticness. All numeric features are on a 0 to 1 scale except tempo, which is in BPM and is not used in scoring.

The catalog covers 15 genres and 14 moods, but most appear only once. Lofi is the most represented genre with 3 songs. Chill is the most common mood with 3 songs. The catalog skews toward Western popular music styles and does not include classical Indian, Latin, African, or other global genres. No songs were added or removed from the starter dataset.

The biggest data limitation is size. With only 18 songs, the system cannot provide meaningful variety for most genre preferences. A real recommender would need thousands of songs to avoid the single-song genre trap described in the limitations section.

---

## 5. Strengths

The system works well when the user's preferences are specific and the catalog has good coverage for that preference. The lofi/chill profile is the clearest example — three songs match the genre, all three score well, and the results feel genuinely appropriate for someone who wants background study music.

The explanation feature is a real strength. Every recommendation comes with a plain-language reason (genre match, mood match, close energy, etc.), which makes the system transparent. A user can immediately see why a song was recommended and whether they agree with the reasoning.

The system is also fast and simple to modify. Changing a weight takes one line of code, and the effect on rankings is immediately visible. This makes it a good tool for understanding how weight choices shape outcomes.

---

## 6. Limitations and Bias

The most significant weakness is the single-song genre trap. Thirteen of the fifteen genres in the catalog appear exactly once. This means a user who prefers rock, jazz, metal, or folk will always get the same song at #1 regardless of how well its numeric features actually match. The genre bonus is unbeatable when there is only one competitor. The system does not discover variety; it just locks onto the one catalog entry that shares a label.

A related problem is the energy asymmetry bias. Energy carries the highest numeric weight (×1.5 in the final version). A song that is 0.30 off on energy loses up to 0.45 points, which can push genuinely good matches out of the top 5 entirely. Because energy is so heavily weighted, the system is really a high-energy song finder with genre and mood as tiebreakers.

The binary mood penalty is another hard edge. Mood is treated as an exact string match with no partial credit for moods that are semantically close — relaxed, chill, and peaceful are all treated as completely different. Users with less common mood preferences are quietly penalized without any explanation in the output.

Finally, the system has no diversity enforcement. The top results are always the closest matches, so a lofi listener gets all three lofi songs before any cross-genre discovery happens. In a real product this would feel repetitive fast.

---

## 7. Evaluation

I tested six user profiles in total — three standard and three adversarial edge cases designed to stress-test the scoring logic.

The three standard profiles were: a high-energy pop listener (genre=pop, mood=happy, energy=0.85), a chill lofi listener (genre=lofi, mood=chill, energy=0.40), and a deep intense rock listener (genre=rock, mood=intense, energy=0.92). For all three, the top result was exactly what you would expect — Sunrise City, Midnight Coding, and Storm Runner respectively. Each of those songs matched both the genre and mood label, and their numeric features were close to the target. This confirmed the basic logic was working.

What surprised me was how quickly the scores dropped after #1. For the rock profile, Storm Runner scored 6.76 but #2 Gym Hero only scored 4.29 — a gap of 2.47 points. That gap exists entirely because there is only one rock song in the catalog. In a real app with thousands of songs this would not be a problem, but in an 18-song catalog it means the system makes one confident recommendation and then guesses for the rest.

The most surprising edge case result: when I asked for classical/melancholic music but set energy to 0.90, the system still recommended Moonlit Sonata — a very quiet piano piece with energy of 0.22. It won because the genre and mood labels matched, and those categorical bonuses outweighed the energy mismatch entirely. This showed the system can be tricked by its own label-matching logic into recommending something that feels completely wrong.

I also ran a weight-shift experiment: halving the genre bonus (2.0 → 1.0) and doubling the energy weight (1.5 → 3.0). The genre ghost edge case improved — the quiet ambient song stopped appearing for a high-energy angry profile. But the classical/melancholic edge case still misbehaved, just with a smaller margin. Categorical bonuses still dominated when both genre and mood matched.

---

## 8. Future Work

Add soft genre similarity. Instead of a binary genre match, group genres into families (lofi/ambient/jazz = low-energy organic; metal/rock/electronic = high-energy produced) and award partial points for adjacent genres. This would reduce the single-song genre trap and produce more interesting cross-genre recommendations.

Add a diversity penalty. After scoring, check if the top results are all from the same genre or artist and swap in a lower-ranked but different song. This would make the list feel less like a retrieval query and more like an actual recommendation.

Replace binary mood matching with a mood distance table. Define a small matrix where "relaxed" is close to "chill" and "euphoric" is close to "happy," and award partial points based on that distance. This would stop silently penalizing users whose preferred mood appears rarely in the catalog.

---

## 9. Personal Reflection

The biggest learning moment was the weight-shift experiment. I expected halving the genre weight to make the recommendations more diverse and more accurate. It did improve one edge case (the genre ghost), but it barely changed the others. That told me the problem was not just the weights — it was the binary nature of the categorical matching itself. No matter how much you reduce the genre bonus, a song that matches the genre label will always beat a song that does not, even if the non-matching song is a better fit in every other way. Fixing that requires a different approach entirely, not just a number change.

Using AI tools helped most during the implementation phase. The scoring loop, the CSV parser, and the sorted comprehension all came together quickly. Where I needed to double-check was in the bias analysis — the AI suggested several potential issues, but I had to run the actual catalog distribution numbers myself to confirm which ones were real. The single-song genre trap only became obvious when I counted that 13 of 15 genres appear exactly once. That is not something you can see from reading the code.

What surprised me most was how much the results felt like real recommendations even though the algorithm is just arithmetic. Sunrise City ranking first for a happy pop listener, Midnight Coding for a chill lofi listener — those feel right. The system is not intelligent; it is just measuring distance. But distance in the right feature space produces outputs that match human intuition surprisingly often. The cases where it fails (Moonlit Sonata for a high-energy user) are the ones where the feature space does not capture what the user actually means.

If I extended this project, I would want to try collaborative filtering alongside the content-based approach — not to replace it, but to use it as a tiebreaker when the content scores are close. The all-middle edge case (where scores clustered between 3.34 and 4.39 with no clear winner) is exactly the situation where knowing what similar users listened to next would make a real difference.
