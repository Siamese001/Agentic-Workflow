from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Runtime API: Backend service for real-time system monitoring and dashboard data.
Created: 2026-01-13 | Version: 2.0.0 (Phase 2 - Enhanced Telemetry)
"""


import json
import time
from pathlib import Path
from typing import Any

# Concurrent access retry configuration
MAX_READ_RETRIES = 3
RETRY_DELAY_MS = 10

from agentic_core.L2_execution.enforcement.redis import SovereignRedisClient

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
except ImportError as _err:
    raise ImportError(
        "fastapi is required for this module. Install with: pip install -e '.[infra]'",
    ) from _err
from pydantic import BaseModel

from agentic_core.L1_cognition.reasoning.MetaLearningAgent import MetaLearningAgent
from agentic_core.L0_routing.config import (
    RUNTIME_STATE_JSON,
)

# ARCHIVED: pinecone_telemetry import removed # PineconeTelemetryWrapper

app = FastAPI(title="Agentic AI Runtime API", version="2.0.0")

# Allow dashboard usage from file:// (origin "null") and localhost.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Runtime state file path
RUNTIME_STATE_FILE = Path(RUNTIME_STATE_JSON)

# Initialize telemetry-enabled clients
meta_agent = MetaLearningAgent()
redis_client = SovereignRedisClient()
pinecone_wrapper = PineconeTelemetryWrapper()

# Simple in-memory log buffer for the Live Runtime tab.
_LOG_BUFFER: list[str] = []
_MAX_LOG_LINES = 250


def _append_log(line: str) -> None:
    ts = time.strftime("%H:%M:%S")
    _LOG_BUFFER.append(f"[{ts}] {line}")
    if len(_LOG_BUFFER) > _MAX_LOG_LINES:
        del _LOG_BUFFER[: len(_LOG_BUFFER) - _MAX_LOG_LINES]


class ExperienceIn(BaseModel):
    state: dict[str, Any] = {}
    thought_type: str = "cot"
    outcome: dict[str, Any] = {}
    reward: float = 0.0


@app.get("/api/health")
async def health_check() -> dict[str, Any]:
    return {
        "status": "healthy",
        "version": "1.0.0",
        "state_file_found": RUNTIME_STATE_FILE.exists(),
    }


@app.get("/api/redis/logs")
async def get_redis_logs(limit: int = 50) -> dict[str, Any]:
    # For now this is an in-memory stream. Hooking it to Redis MCP is optional.
    lim = max(1, min(int(limit), 200))
    return {"logs": _LOG_BUFFER[-lim:]}


@app.get("/api/meta-learning/activity")
async def get_meta_learning() -> dict[str, Any]:
    try:
        return {
            "total_experiences": meta_agent.total_experiences,
            "patterns_extracted": meta_agent.patterns_extracted,
            "strategy_weights": meta_agent.strategy_weights,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/meta-learning/experience")
async def post_meta_learning_experience(payload: ExperienceIn) -> dict[str, Any]:
    """Records a new experience so dashboards can observe exp-count changes."""
    try:
        exp_id = meta_agent.store_experience(
            state=payload.state,
            thought_type=payload.thought_type,
            outcome=payload.outcome,
            reward=payload.reward,
        )
        _append_log(f"META store_experience {exp_id} reward={payload.reward}")
        return {
            "status": "ok",
            "experience_id": exp_id,
            "total_experiences": meta_agent.total_experiences,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/latency")
async def get_api_latency() -> dict[str, Any]:
    # Placeholder until real probes are wired.
    return {
        "pinecone": 42.5,
        "gemini_embeddings": 128.2,
        "redis_lookup": 1.4,
    }


# ============================================================================
# Phase 2 Endpoints - Enhanced Telemetry for Dashboard Live Runtime
# ============================================================================


def _safe_read_json(file_path: Path, retries: int = MAX_READ_RETRIES) -> dict[str, Any]:
    """Read JSON file with retry logic for concurrent access safety."""
    last_error = None
    for _attempt in range(retries):
        try:
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                if content.strip():  # Avoid empty file during write
                    return json.loads(content)
        except json.JSONDecodeError as e:
            last_error = e
            time.sleep(RETRY_DELAY_MS / 1000)  # Brief delay before retry
        except Exception as e:
            last_error = e
            break
    # Return safe default on failure
    return {"status": "error", "message": str(last_error) if last_error else "File not found"}


@app.get("/api/runtime/state")
async def get_runtime_state() -> dict[str, Any]:
    """Get current runtime state from runtime_state.json with retry logic."""
    return _safe_read_json(RUNTIME_STATE_FILE)


@app.get("/api/redis/stats")
async def get_redis_stats() -> dict[str, Any]:
    """Get Redis operation statistics."""
    try:
        return redis_client.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pinecone/stats")
async def get_pinecone_stats() -> dict[str, Any]:
    """Get Pinecone operation statistics."""
    try:
        return pinecone_wrapper.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/execution/timeline")
async def get_execution_timeline() -> list[dict[str, Any]]:
    """Get agent execution timeline from runtime_state.json."""
    try:
        if RUNTIME_STATE_FILE.exists():
            state = json.loads(RUNTIME_STATE_FILE.read_text(encoding="utf-8"))
            return state.get("execution_timeline", [])
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/meta-learning/statistics")
async def get_meta_learning_statistics() -> dict[str, Any]:
    """Get detailed meta-learning statistics including recent experiences."""
    try:
        return meta_agent.get_live_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
