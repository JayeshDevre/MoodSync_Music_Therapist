# Model Card: MoodSync — AI Music Therapist

## 1. Model Name
MoodSync v1.0

---

## 2. Intended Use

MoodSync is an AI music recommendation system that takes natural language emotional input and returns science-backed song recommendations with grounded explanations. It is designed as a portfolio project demonstrating RAG, agentic workflows, and reliability testing in a full-stack AI system.

Intended users: anyone who wants music matched to their current emotional state without manually selecting genre or mood filters.

Non-intended uses: clinical music therapy, mental health diagnosis, or any context requiring medically validated recommendations.

---

## 3. How the System Works

MoodSync uses a multi-step pipeline:

1. **Mood Parser** — sends user's natural language input to an LLM (via OpenRouter) with a music therapist persona. Returns a structured JSON mood vector: `{ mood, energy, valence, danceability, acousticness, genre_hint }`.

2. **RAG Retriever** — embeds the user query using `sentence-transformers/all-MiniLM-L6-v2` (local), searches a FAISS index over 6 music psychology knowledge base documents, and returns the top 3 most relevant research chunks.

3. **Song Scorer** — the original rule-based scoring engine from the prototype. Scores 18 songs against the mood vector using weighted feature similarity. Energy is weighted 3x, genre/mood matches add categorical bonuses.

4. **Agentic Self-Critique Loop** — sends top 5 candidates + RAG context to the LLM for critique. Checks genre diversity, energy flow, and mood alignment. Re-ranks with genre penalty if critique fails. Max 2 retries.

5. **Explainer** — generates a 2-sentence explanation per song, grounded in the retrieved research docs. The LLM must cite the context — it cannot hallucinate freely.

6. **Confidence Scorer** — `score = 0.6 × match_score + 0.4 × rag_relevance`. Assigns HIGH / MEDIUM / LOW and flags low confidence picks.

7. **Logger** — writes full decision trace to `logs/session.jsonl` for every session.

---

## 4. Data

**Song catalog:** 18 songs across 15 genres. Each song has title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. All numeric features are 0–1 except tempo (BPM, not used in scoring).

**Knowledge base:** 6 markdown documents covering music psychology research — tempo and mood, acousticness and anxiety, energy and focus, valence and emotion, genre-mood mapping, danceability and wellbeing. Written specifically for this project based on established music therapy principles.

**Limitations:** 18 songs is very small. Most genres appear only once, meaning genre matching is often a single-song race. A production system would need thousands of songs.

---

## 5. Strengths

- Natural language input removes friction — users don't need to know music terminology
- RAG grounds every explanation in research rather than hallucination
- Agentic loop catches homogeneous picks and enforces diversity
- Full audit trail via session logging — every decision is traceable
- Graceful degradation — every component has fallbacks, system never crashes on API failure
- Confidence scoring makes uncertainty visible to the user

---

## 6. Limitations and Bias

**Small catalog bias:** With 18 songs, 13 of 15 genres appear only once. A genre match is almost always a single-song win regardless of numeric fit. This is inherited from the original prototype and would require a larger dataset to fix.

**Energy dominance:** Energy is weighted 3x in the scorer. Songs that are far off on energy get heavily penalized even if they match well on every other dimension. This makes the system better at matching intensity than nuance.

**Genre hint mismatch:** The mood parser suggests a genre hint but the catalog may not have songs in that genre. When the hint doesn't match any catalog song, the system falls back to pure numeric scoring which can produce unexpected results.

**LLM rate limits:** The free-tier LLM (OpenRouter) has a 50 requests/day limit. When exhausted, the mood parser falls back to neutral defaults, making all recommendations identical. This is a deployment constraint, not a logic flaw, but it affects reliability in demo settings.

**Western music bias:** The catalog covers Western popular genres only. No classical Indian, Latin, African, or other global music traditions are represented.

---

## 7. Evaluation and Testing

**Automated eval (tests/eval.py):** 10 fixed mood inputs, 5 checks each.
- Result: 40/41 checks passed (98%)
- Failed check: genre coverage — caused by LLM rate limit exhaustion during testing, not a logic error
- All confidence, mood alignment, RAG retrieval, and agent stability checks passed 10/10

**Confidence scoring:** Average confidence score 0.55 (MEDIUM range) across normal sessions. No all-LOW picks in standard mood inputs. HIGH confidence triggered on strong genre + energy matches.

**Human evaluation:** 5 manual checks — stressed→lofi, happy→pop, workout→pop, nostalgic→folk, angry→rock. All 5 passed when LLM was available.

**What worked:** RAG retrieval was accurate from first test. Agentic loop passed on first attempt for most inputs. Fallback handling worked correctly throughout.

**What didn't work:** Free-tier rate limits caused neutral fallback during heavy testing. Small LLM couldn't produce valid JSON arrays for multi-song prompts — had to switch to per-song calls.

---

## 8. AI Collaboration Reflection

**One instance where AI was helpful:**
When designing the RAG retriever, the AI suggested using cosine similarity via FAISS `IndexFlatIP` with L2 normalization rather than Euclidean distance. This was the right call — cosine similarity is more appropriate for semantic text embeddings because it measures directional similarity rather than magnitude. Without that suggestion I would have used the default Euclidean index and gotten worse retrieval results.

**One instance where AI was flawed:**
The AI initially suggested calling the LLM once with all 5 songs in a single prompt for the explainer, returning a JSON array. This failed repeatedly — the small free-tier model couldn't reliably produce valid JSON arrays for 5 songs at once. The AI kept suggesting minor prompt tweaks rather than recognizing the fundamental issue: the model was too small for that output format. The fix required stepping back and switching to per-song calls with plain text output, which the AI didn't suggest until explicitly pushed.

---

## 9. Ethics and Responsible Design

**Could this be misused?**
The system recommends music based on emotional state. A bad actor could theoretically use it to keep users in negative emotional states (e.g., always recommending sad music to someone who says they're sad) rather than helping them regulate. The current design partially addresses this through the valence-based scoring — it doesn't just match current mood, it considers what music would be therapeutically appropriate.

**What surprised me in testing:**
The most surprising finding was how well the system worked even when the LLM was rate-limited and fell back to neutral defaults. The RAG retrieval and rule-based scorer still returned reasonable results — lofi and ambient tracks for neutral inputs. This showed that the deterministic components carry more weight than expected, and the LLM is primarily responsible for personalization rather than basic correctness.

**Transparency:**
Every recommendation shows the RAG sources used, the confidence score, and the agent's reasoning. Users can see exactly why each song was picked. This is a deliberate design choice — the system should be explainable, not a black box.

---

## 10. Future Work

- Expand catalog to 500+ songs via Spotify API integration
- Add soft genre similarity (genre families instead of exact match)
- Implement session memory so the agent remembers previous preferences
- Add diversity enforcement to prevent all-same-genre results
- Replace free-tier LLM with a locally hosted model (Ollama) to eliminate rate limit issues
