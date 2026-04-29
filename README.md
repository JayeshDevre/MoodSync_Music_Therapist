# MoodSync — AI Music Therapist

A full-stack AI music recommendation system that takes how you're feeling in plain English and returns science-backed song picks with grounded explanations.

**Live demo flow:** type "I'm stressed and can't focus" → system parses your mood → retrieves music psychology research → scores songs → agent self-critiques picks → returns explanations citing the research.

---

## AI Features

| Feature | Implementation |
|---|---|
| RAG | sentence-transformers + FAISS over 6 music psychology docs |
| Agentic Workflow | self-critique loop that re-ranks if picks lack diversity |
| Specialized Model | Llama via OpenRouter with music therapist persona + structured JSON output |
| Reliability & Testing | confidence scoring, decision logging, eval script with 10 fixed test cases |

---

## Project Structure

```
applied-ai-system-project/
├── backend/
│   ├── src/
│   │   ├── mood_parser.py      # LLM mood extraction
│   │   ├── retriever.py        # RAG — FAISS vector search
│   │   ├── recommender.py      # song scoring engine
│   │   ├── agent.py            # agentic self-critique loop
│   │   ├── explainer.py        # RAG-grounded explanations
│   │   ├── confidence.py       # confidence scoring
│   │   └── logger.py           # decision audit trail
│   ├── knowledge_base/         # 6 music psychology markdown docs
│   ├── data/songs.csv          # 18-song catalog
│   ├── logs/                   # auto-generated session logs
│   ├── main.py                 # FastAPI app
│   └── requirements.txt
├── frontend/
│   └── moodsync/               # React + Vite app
├── tests/
│   └── eval.py                 # evaluation script
└── README.md
```

---

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenRouter API key (free) — sign up at [openrouter.ai](https://openrouter.ai)

### 1. Clone and install backend dependencies

```bash
cd applied-ai-system-project/backend
pip install -r requirements.txt
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and add your key:
```
OPENROUTER_API_KEY=sk-or-...
```

### 3. Run the backend

```bash
cd applied-ai-system-project/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### 4. Install and run the frontend

```bash
cd applied-ai-system-project/frontend/moodsync
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## How It Works

```
User types: "I'm stressed and can't focus"
        ↓
Mood Parser (LLM)
  → extracts: mood=stressed, energy=0.3, genre=lofi
        ↓
RAG Retriever (FAISS)
  → finds: acousticness_and_anxiety.md, energy_and_focus.md
        ↓
Song Scorer (recommender.py)
  → ranks 18 songs against mood vector
        ↓
Agentic Self-Critique (LLM)
  → checks diversity, energy flow, mood alignment
  → re-ranks if needed (max 2 retries)
        ↓
Explainer (LLM + RAG context)
  → generates per-song explanation grounded in research
        ↓
Confidence Scorer
  → assigns HIGH / MEDIUM / LOW to each pick
        ↓
Logger
  → saves full decision trace to logs/session.jsonl
        ↓
React UI
  → chat panel + song cards + RAG sources panel
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | server status + songs loaded |
| POST | `/recommend` | full pipeline — body: `{"user_input": "..."}` |
| GET | `/logs?n=5` | last n session logs |

---

## Running the Eval Script

```bash
cd applied-ai-system-project/tests
python eval.py
```

Runs 10 fixed mood inputs and checks:
- confidence — no all-LOW picks
- mood alignment — high energy input returns high energy songs
- RAG retrieval — at least 2 docs retrieved per request
- agent stability — never exceeds 2 retries
- genre coverage — at least 4 distinct genres across all results

---

## Knowledge Base

The RAG system retrieves from 6 music psychology documents in `backend/knowledge_base/`:

- `tempo_and_mood.md` — how BPM affects emotional state
- `acousticness_and_anxiety.md` — why acoustic music calms the nervous system
- `energy_and_focus.md` — energy levels and cognitive performance
- `valence_and_emotion.md` — musical positiveness and mood regulation
- `genre_mood_mapping.md` — genre to emotional state mappings
- `danceability_and_wellbeing.md` — rhythm and mental wellbeing

---

## Tech Stack

- **LLM** — Llama / Nemotron via OpenRouter (free tier)
- **Embeddings** — `sentence-transformers/all-MiniLM-L6-v2` (local, no API cost)
- **Vector search** — FAISS (local)
- **Backend** — FastAPI + Uvicorn
- **Frontend** — React + Vite
- **Logging** — JSONL audit trail
