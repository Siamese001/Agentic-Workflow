"""Configuration and environment parsing for the vector retrieval service."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from agentic_core.config.model_catalog import BGE_M3_MODEL_ID

REPO_ROOT = Path(__file__).resolve().parents[2]

_raw_chroma_path = os.environ.get("VECTOR_DB_CHROMA_PATH", "")
CHROMA_PATH: Path = Path(_raw_chroma_path) if _raw_chroma_path else REPO_ROOT / "data" / "cache" / "chromadb"
DEFAULT_EMBEDDING_MODEL: str = os.environ.get("VECTOR_DB_EMBEDDING_MODEL", BGE_M3_MODEL_ID)
ALLOW_MODEL_DOWNLOAD: bool = os.environ.get("VECTOR_DB_ALLOW_MODEL_DOWNLOAD", "0").strip() == "1"


def _cuda_available() -> bool:
    try:
        import torch  # noqa: PLC0415

        return bool(torch.cuda.is_available())
    except (ImportError, RuntimeError):
        return False


def _resolve_vector_db_device() -> str:
    """Resolve vector embedding device: explicit override, shared embedding override, CUDA, CPU."""
    vector_override = os.environ.get("VECTOR_DB_DEVICE", "").strip().lower()
    if vector_override and vector_override != "auto":
        return vector_override
    embedding_override = os.environ.get("EMBEDDING_DEVICE", "").strip().lower()
    if embedding_override and embedding_override != "auto":
        return embedding_override
    return "cuda" if _cuda_available() else "cpu"


VECTOR_DB_DEVICE: str = _resolve_vector_db_device()
MODEL_LOAD_TIMEOUT: float = float(os.environ.get("VECTOR_DB_MODEL_LOAD_TIMEOUT", "120"))
CHROMA_INIT_TIMEOUT: float = float(os.environ.get("VECTOR_DB_CHROMA_INIT_TIMEOUT", "30"))
EMBEDDING_ENCODE_TIMEOUT: float = float(os.environ.get("VECTOR_DB_ENCODE_TIMEOUT", "20"))
EMBEDDING_QUEUE_WAIT_TIMEOUT: float = float(os.environ.get("VECTOR_DB_ENCODE_QUEUE_WAIT_TIMEOUT", "20"))
QUERY_COLLECTION_TIMEOUT: float = float(os.environ.get("VECTOR_DB_QUERY_COLLECTION_TIMEOUT", "40"))
SEARCH_PER_COLLECTION_TIMEOUT: float = float(os.environ.get("VECTOR_DB_SEARCH_PER_COLLECTION_TIMEOUT", "20"))
SEARCH_GLOBAL_TIMEOUT: float = float(os.environ.get("VECTOR_DB_SEARCH_GLOBAL_TIMEOUT", "60"))
COUNT_CACHE_TTL: float = float(os.environ.get("VECTOR_DB_COUNT_CACHE_TTL", "60"))
BACKGROUND_PREWARM_ENABLED: bool = os.environ.get("VECTOR_DB_ENABLE_STARTUP_PREWARM", "1").strip() == "1"

KNOWN_MODEL_DIMS: dict[str, int] = {
    BGE_M3_MODEL_ID: 1024,
    "all-MiniLM-L6-v2": 384,
    "all-mpnet-base-v2": 768,
    "text-embedding-ada-002": 1536,
}


def _parse_int_env(name: str, default: int, min_val: int = 1) -> int:
    raw = os.environ.get(name, "")
    if not raw:
        return default
    try:
        val = int(raw)
    except ValueError:
        logging.getLogger("vector_service").error(
            "Invalid value for %s=%r — must be an integer; using default %d",
            name,
            raw,
            default,
        )
        return default
    if val < min_val:
        logging.getLogger("vector_service").error(
            "Invalid value for %s=%d — must be >= %d; using default %d",
            name,
            val,
            min_val,
            default,
        )
        return default
    return val


MAX_RESULTS: int = _parse_int_env("VECTOR_DB_MAX_QUERY_RESULTS", 100)
MAX_EMBEDDING_BATCH_SIZE: int = _parse_int_env("VECTOR_DB_MAX_BATCH", 32)
MAX_SEARCH_RESULTS: int = _parse_int_env("VECTOR_DB_MAX_SEARCH_RESULTS", 20)


def validate_startup_config(logger: logging.Logger) -> None:
    """Emit a warning when startup config looks unusual but still runnable."""
    if DEFAULT_EMBEDDING_MODEL not in KNOWN_MODEL_DIMS:
        logger.warning(
            "STARTUP_WARN: VECTOR_DB_EMBEDDING_MODEL=%r is not in the known-dimension map; "
            "dimension-alignment checks will be best-effort only",
            DEFAULT_EMBEDDING_MODEL,
        )
