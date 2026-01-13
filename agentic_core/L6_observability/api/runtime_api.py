"""
Runtime API: Backend service for real-time system monitoring and dashboard data.
Created: 2026-01-13 | Version: 1.0.0
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agentic_core.L1_cognition.learning.MetaLearningAgent import MetaLearningAgent

app = FastAPI(title="Agentic AI Runtime API")

# Allow dashboard usage from file:// (origin "null") and localhost.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

meta_agent = MetaLearningAgent()

# Simple in-memory log buffer for the Live Runtime tab.
_LOG_BUFFER: List[str] = []
_MAX_LOG_LINES = 250


def _append_log(line: str) -> None:
    ts = time.strftime("%H:%M:%S")
    _LOG_BUFFER.append(f"[{ts}] {line}")
    if len(_LOG_BUFFER) > _MAX_LOG_LINES:
        del _LOG_BUFFER[: len(_LOG_BUFFER) - _MAX_LOG_LINES]


class ExperienceIn(BaseModel):
    state: Dict[str, Any] = {}
    thought_type: str = "cot"
    outcome: Dict[str, Any] = {}
    reward: float = 0.0


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/redis/logs")
async def get_redis_logs(limit: int = 50) -> Dict[str, Any]:
    # For now this is an in-memory stream. Hooking it to Redis MCP is optional.
    lim = max(1, min(int(limit), 200))
    return {"logs": _LOG_BUFFER[-lim:]}


@app.get("/api/meta-learning/activity")
async def get_meta_learning() -> Dict[str, Any]:
    try:
        return {
            "total_experiences": meta_agent.total_experiences,
            "patterns_extracted": meta_agent.patterns_extracted,
            "strategy_weights": meta_agent.strategy_weights,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/meta-learning/experience")
async def post_meta_learning_experience(payload: ExperienceIn) -> Dict[str, Any]:
    """Records a new experience so dashboards can observe exp-count changes."""
    try:
        exp_id = meta_agent.store_experience(
            state=payload.state,
            thought_type=payload.thought_type,
            outcome=payload.outcome,
            reward=payload.reward,
        )
        _append_log(f"META store_experience {exp_id} reward={payload.reward}")
        return {"status": "ok", "experience_id": exp_id, "total_experiences": meta_agent.total_experiences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/latency")
async def get_api_latency() -> Dict[str, Any]:
    # Placeholder until real probes are wired.
    return {
        "pinecone": 42.5,
        "gemini_embeddings": 128.2,
        "redis_lookup": 1.4,
    }
