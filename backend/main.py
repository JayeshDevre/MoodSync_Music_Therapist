"""
MoodSync API — FastAPI backend that wires all AI components together.
POST /recommend  → full pipeline: mood parse → RAG → score → agent → explain → confidence
GET  /health     → sanity check
GET  /logs       → recent sessions
"""

import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mood_parser import parse_mood
from retriever import get_retriever
from recommender import load_songs, recommend_songs, mood_vector_to_prefs
from agent import run_agent
from explainer import explain_songs
from confidence import score_confidence, needs_clarification
from logger import log_session, get_recent_sessions

# ── Logging setup ────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

# ── Data path ────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "songs.csv")

# ── App state (loaded once at startup) ───────────────────────────
app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading songs catalog...")
    app_state["songs"] = load_songs(DATA_PATH)
    logger.info(f"Loaded {len(app_state['songs'])} songs")

    logger.info("Building RAG index...")
    app_state["retriever"] = get_retriever()
    logger.info("RAG index ready")
    yield
    app_state.clear()


app = FastAPI(title="MoodSync API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────
class RecommendRequest(BaseModel):
    user_input: str


class SongResult(BaseModel):
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    score: float
    explanation: str
    confidence_score: float
    confidence_level: str
    low_confidence_flag: bool


class RecommendResponse(BaseModel):
    session_id: str
    user_input: str
    mood: dict
    rag_sources: list
    agent_retries: int
    agent_passed: bool
    needs_clarification: bool
    recommendations: list


# ── Routes ────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "songs_loaded": len(app_state.get("songs", [])),
        "rag_ready": "retriever" in app_state,
    }


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    if not req.user_input.strip():
        raise HTTPException(status_code=400, detail="user_input cannot be empty")

    songs = app_state["songs"]

    # Step 1 — Parse mood
    mood_vector = parse_mood(req.user_input)

    # Step 2 — RAG retrieval
    rag_docs = app_state["retriever"].retrieve(req.user_input, top_k=3)

    # Step 3 — Score songs
    prefs = mood_vector_to_prefs(mood_vector)
    candidates = recommend_songs(prefs, songs, k=10)

    # Step 4 — Agentic self-critique
    final_picks, agent_log = run_agent(mood_vector, candidates, rag_docs, songs, k=5)

    # Step 5 — Generate explanations
    explained = explain_songs(mood_vector, final_picks, rag_docs)

    # Step 6 — Confidence scoring
    scored = score_confidence(explained, rag_docs)

    # Step 7 — Log session
    session_id = log_session(req.user_input, mood_vector, rag_docs, agent_log, scored)

    return RecommendResponse(
        session_id=session_id,
        user_input=req.user_input,
        mood=mood_vector,
        rag_sources=[{"source": c["source"], "score": round(c["score"], 3)} for c in rag_docs],
        agent_retries=agent_log.get("retries", 0),
        agent_passed=agent_log.get("final_passed", True),
        needs_clarification=needs_clarification(scored),
        recommendations=scored,
    )


@app.get("/logs")
def logs(n: int = 5):
    return {"sessions": get_recent_sessions(n)}
