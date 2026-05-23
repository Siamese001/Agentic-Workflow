"""apps_rg SSOT embedding / BGE / Chroma vector-DB settings (fail-closed).

Terminology:
- embedding_model: BGE via explicit local SentenceTransformer path (never HF hub slug at runtime).
- embedding_function: explicit SentenceTransformer callable; never Chroma DefaultEmbeddingFunction.
- vector_db: Chroma persistence for pre-embedded collections or governed R1B projection only.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

_logger = logging.getLogger(__name__)

EMBEDDING_SETTINGS_RECEIPT_NAME = "apps_rg_embedding_settings.json"
CANONICAL_BGE_HF_ID = "BAAI/bge-m3"
DEFAULT_EMBEDDING_MODEL_ID_SLUG = "bge-m3-v1"

EmbeddingModelSource = Literal[
    "local",
    "pre_provisioned",
    "unavailable",
    "not_applicable",
]
FailureMode = Literal["fail_closed", "mark_ineligible", "not_applicable"]
RouteResult = Literal["CONTINUE_WITH_NON_EMBEDDING_PATH", "FAIL_CLOSED"]


class AppsRgEmbeddingFailClosedError(RuntimeError):
    """Dense retrieval or required embedding route cannot proceed without BGE."""


@dataclass(frozen=True)
class AppsRgEmbeddingSettings:
    embeddings_enabled: bool
    embedding_required: bool
    embedding_model_name: str | None
    embedding_model_path: str | None
    embedding_model_resolved: bool
    embedding_model_source: EmbeddingModelSource
    vector_db: Literal["chroma", "none"]
    semantic_cache_enabled: bool
    dense_retrieval_enabled: bool
    chroma_default_ef_allowed: bool
    chroma_default_ef_used: bool
    failure_mode: FailureMode
    semantic_cache_ineligible: bool
    dense_retrieval_ineligible: bool
    route_result: RouteResult
    decisive_reason: str
    chroma_persist_dir: str | None = None

    def to_receipt_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["embedding_function"] = "explicit_sentence_transformer_bge" if self.embedding_model_resolved else None
        d["forbidden_chroma_default_ef"] = True
        return d


def _env_truthy(name: str, *, default: str = "") -> bool:
    raw = os.environ.get(name, default).strip().lower()
    return raw in ("1", "true", "yes")


def _chroma_persist_dir(explicit: str | None = None) -> str | None:
    p = (explicit or os.environ.get("CHROMA_PERSIST_DIR") or "").strip()
    return p or None


def _embedding_explicitly_disabled() -> bool:
    for name in ("EMBEDDING_ENABLED", "APPS_RG_EMBEDDING_ENABLED"):
        raw = os.environ.get(name, "").strip().lower()
        if raw in ("0", "false", "no"):
            return True
    return False


def _embedding_env_unset() -> bool:
    for name in ("EMBEDDING_ENABLED", "APPS_RG_EMBEDDING_ENABLED"):
        if os.environ.get(name, "").strip():
            return False
    return True


def _hf_hub_bge_snapshot_dir(model_id: str) -> Path | None:
    """Resolve HuggingFace hub cache snapshot (local-files-only; no download)."""
    hf_home = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
    hub_root = hf_home / "hub"
    cache_name = f"models--{model_id.replace('/', '--')}"
    snaps = hub_root / cache_name / "snapshots"
    if not snaps.is_dir():
        return None
    candidates = sorted(snaps.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    for snap in candidates:
        if not snap.is_dir():
            continue
        if (snap / "config.json").is_file() or (snap / "modules.json").is_file():
            return snap
    return None


def _resolve_local_bge_path(model_id: str) -> tuple[str | None, bool, EmbeddingModelSource]:
    """Resolve BGE to an on-disk path only — no Hugging Face hub download."""
    explicit = os.environ.get("APPS_RG_EMBEDDING_MODEL_PATH", "").strip()
    if explicit:
        path = Path(explicit)
        if path.is_dir() and any(path.iterdir()):
            return str(path.resolve()), True, "local"
        return None, False, "unavailable"

    # Pre-provisioned repo-relative layouts (operator must materialize weights).
    repo = Path(os.environ.get("AGENTIC_REPO_ROOT", Path.cwd()))
    candidates: list[Path] = []
    if model_id and ("/" in model_id or model_id.startswith("BAAI")):
        candidates.append(repo / "artifacts" / "models" / model_id.replace("/", os.sep))
        candidates.append(repo / "models" / model_id.replace("/", os.sep))
    candidates.append(repo / "artifacts" / "models" / "BAAI" / "bge-m3")
    candidates.append(repo / "artifacts" / "models" / "bge-m3")

    for cand in candidates:
        if cand.is_dir() and any(cand.iterdir()):
            return str(cand.resolve()), True, "pre_provisioned"

    hf_snap = _hf_hub_bge_snapshot_dir(model_id or CANONICAL_BGE_HF_ID)
    if hf_snap is not None:
        return str(hf_snap.resolve()), True, "pre_provisioned"

    return None, False, "unavailable"


def _resolve_bootstrap_repo_root(repo_root: Path | str | None) -> Path:
    if repo_root is not None:
        return Path(repo_root).resolve()
    env_root = os.environ.get("AGENTIC_REPO_ROOT", "").strip()
    if env_root:
        return Path(env_root).resolve()
    from apps_rg.runtime.runtime_proof_layout import find_repo_root

    return find_repo_root()


def bootstrap_apps_rg_embedding_env(
    repo_root: Path | str | None = None,
) -> dict[str, str]:
    """Apply apps_rg SSOT defaults for Chroma + BGE on every CLI invocation.

    Defaults (no manual env required):
    - ``CHROMA_PERSIST_DIR`` → ``<repo>/data/cache/chromadb``
    - ``EMBEDDING_ENABLED`` / ``APPS_RG_EMBEDDING_ENABLED`` → ``true`` when not explicitly disabled
    - Local BGE path when HF cache or repo artifacts exist

    Opt-out: ``EMBEDDING_ENABLED=false`` (or ``0`` / ``no``). Override paths via env if needed.
    Does not download models; uses repo artifacts or HF hub cache snapshots only.
    """
    applied: dict[str, str] = {}
    repo = _resolve_bootstrap_repo_root(repo_root)
    os.environ.setdefault("AGENTIC_REPO_ROOT", str(repo))

    if not os.environ.get("CHROMA_PERSIST_DIR", "").strip():
        chroma = (repo / "data" / "cache" / "chromadb").resolve()
        os.environ["CHROMA_PERSIST_DIR"] = str(chroma)
        applied["CHROMA_PERSIST_DIR"] = os.environ["CHROMA_PERSIST_DIR"]

    if _embedding_explicitly_disabled():
        return applied

    if _embedding_env_unset():
        os.environ["EMBEDDING_ENABLED"] = "true"
        os.environ["APPS_RG_EMBEDDING_ENABLED"] = "true"
        applied["EMBEDDING_ENABLED"] = "true"
        applied["APPS_RG_EMBEDDING_ENABLED"] = "true"

    model_id = (
        os.environ.get("APPS_RG_EMBEDDING_MODEL_NAME", "").strip()
        or os.environ.get("EMBEDDING_MODEL_ID", "").strip()
        or CANONICAL_BGE_HF_ID
    )
    if model_id == DEFAULT_EMBEDDING_MODEL_ID_SLUG:
        model_id = CANONICAL_BGE_HF_ID

    path, resolved, _source = _resolve_local_bge_path(model_id)
    if not resolved or not path:
        return applied

    if not os.environ.get("APPS_RG_EMBEDDING_MODEL_PATH", "").strip():
        os.environ["APPS_RG_EMBEDDING_MODEL_PATH"] = path
        applied["APPS_RG_EMBEDDING_MODEL_PATH"] = path

    os.environ.setdefault("SEMANTIC_CACHE_D2_ENABLED", "1")
    os.environ.setdefault("APPS_RG_R1B_SEMANTIC_PROOF", "ELIGIBLE")
    os.environ.setdefault("EMBEDDING_MODEL_ID", DEFAULT_EMBEDDING_MODEL_ID_SLUG)
    os.environ.setdefault("APPS_RG_EMBEDDING_MODEL_NAME", CANONICAL_BGE_HF_ID)
    if os.environ.get("CHROMA_PERSIST_DIR"):
        applied["APPS_RG_R1B_CHROMA_COLLECTION"] = "apps_rg_r1b_semantic_cache_projection"
    os.environ.setdefault("APPS_RG_C0_DENSE_SPARSE_MANDATORY", "1")
    os.environ.setdefault("APPS_RG_C0_SPARSE_ENABLED", "1")
    os.environ.setdefault("APPS_RG_C03_GRAPH_MANDATORY", "1")
    applied["APPS_RG_C0_DENSE_SPARSE_MANDATORY"] = "1"
    applied["APPS_RG_C03_GRAPH_MANDATORY"] = "1"
    return applied


def resolve_apps_rg_embedding_settings(
    *,
    route_section: str = "",
    chroma_persist_dir: str | None = None,
    embedding_required_override: bool | None = None,
) -> AppsRgEmbeddingSettings:
    """Single resolver for all apps_rg embedding-backed paths."""
    del route_section  # reserved for route-specific contracts; SRFS lanes do not require embeddings
    embeddings_enabled = _env_truthy("EMBEDDING_ENABLED") or _env_truthy("APPS_RG_EMBEDDING_ENABLED")
    chroma_dir = _chroma_persist_dir(chroma_persist_dir)
    dense_requested = bool(chroma_dir)

    if embedding_required_override is not None:
        embedding_required = embedding_required_override
    else:
        embedding_required = dense_requested

    model_id = (
        os.environ.get("APPS_RG_EMBEDDING_MODEL_NAME", "").strip()
        or os.environ.get("EMBEDDING_MODEL_ID", "").strip()
        or CANONICAL_BGE_HF_ID
    )
    if model_id == DEFAULT_EMBEDDING_MODEL_ID_SLUG:
        model_id = CANONICAL_BGE_HF_ID

    model_path: str | None = None
    model_resolved = False
    model_source: EmbeddingModelSource = "not_applicable"

    if embeddings_enabled:
        model_path, model_resolved, model_source = _resolve_local_bge_path(model_id)
        if not model_resolved:
            model_source = "unavailable"
    else:
        model_source = "not_applicable"

    semantic_cache_ineligible = not embeddings_enabled
    dense_ineligible = not embeddings_enabled or not dense_requested

    if not embeddings_enabled:
        if dense_requested and embedding_required:
            return AppsRgEmbeddingSettings(
                embeddings_enabled=False,
                embedding_required=True,
                embedding_model_name=model_id,
                embedding_model_path=None,
                embedding_model_resolved=False,
                embedding_model_source="unavailable",
                vector_db="chroma" if chroma_dir else "none",
                semantic_cache_enabled=False,
                dense_retrieval_enabled=False,
                chroma_default_ef_allowed=False,
                chroma_default_ef_used=False,
                failure_mode="fail_closed",
                semantic_cache_ineligible=True,
                dense_retrieval_ineligible=True,
                route_result="FAIL_CLOSED",
                decisive_reason=(
                    "CHROMA_PERSIST_DIR configured but EMBEDDING_ENABLED is false; "
                    "dense retrieval and Chroma query embeddings are forbidden"
                ),
                chroma_persist_dir=chroma_dir,
            )
        return AppsRgEmbeddingSettings(
            embeddings_enabled=False,
            embedding_required=False,
            embedding_model_name=None,
            embedding_model_path=None,
            embedding_model_resolved=False,
            embedding_model_source="not_applicable",
            vector_db="none",
            semantic_cache_enabled=False,
            dense_retrieval_enabled=False,
            chroma_default_ef_allowed=False,
            chroma_default_ef_used=False,
            failure_mode="not_applicable",
            semantic_cache_ineligible=True,
            dense_retrieval_ineligible=True,
            route_result="CONTINUE_WITH_NON_EMBEDDING_PATH",
            decisive_reason="embeddings_enabled=false; no BGE/SentenceTransformer/Chroma default EF",
            chroma_persist_dir=chroma_dir,
        )

    # embeddings enabled
    d2_on = _env_truthy("SEMANTIC_CACHE_D2_ENABLED", default="1")
    semantic_cache_enabled = d2_on and model_resolved

    if embedding_required and not model_resolved:
        return AppsRgEmbeddingSettings(
            embeddings_enabled=True,
            embedding_required=True,
            embedding_model_name=model_id,
            embedding_model_path=None,
            embedding_model_resolved=False,
            embedding_model_source="unavailable",
            vector_db="chroma" if chroma_dir else "none",
            semantic_cache_enabled=False,
            dense_retrieval_enabled=dense_requested and model_resolved,
            chroma_default_ef_allowed=False,
            chroma_default_ef_used=False,
            failure_mode="fail_closed",
            semantic_cache_ineligible=not model_resolved,
            dense_retrieval_ineligible=True,
            route_result="FAIL_CLOSED",
            decisive_reason=(
                "embeddings_enabled=true but APPS_RG_EMBEDDING_MODEL_PATH (or pre-provisioned "
                f"artifacts/models/{CANONICAL_BGE_HF_ID}) is missing; no HF download permitted"
            ),
            chroma_persist_dir=chroma_dir,
        )

    return AppsRgEmbeddingSettings(
        embeddings_enabled=True,
        embedding_required=embedding_required,
        embedding_model_name=model_id,
        embedding_model_path=model_path,
        embedding_model_resolved=model_resolved,
        embedding_model_source=model_source,
        vector_db="chroma" if chroma_dir else "none",
        semantic_cache_enabled=semantic_cache_enabled,
        dense_retrieval_enabled=dense_requested and model_resolved,
        chroma_default_ef_allowed=False,
        chroma_default_ef_used=False,
        failure_mode="mark_ineligible" if not model_resolved else "not_applicable",
        semantic_cache_ineligible=not model_resolved,
        dense_retrieval_ineligible=not dense_requested,
        route_result="CONTINUE_WITH_NON_EMBEDDING_PATH",
        decisive_reason=(
            "explicit local BGE resolved"
            if model_resolved
            else "embeddings enabled but optional route — embedding-backed paths INELIGIBLE"
        ),
        chroma_persist_dir=chroma_dir,
    )


def apply_apps_rg_embedding_env_guards(
    settings: AppsRgEmbeddingSettings | None = None,
    *,
    route_section: str = "",
    chroma_persist_dir: str | None = None,
) -> AppsRgEmbeddingSettings:
    """Apply process env guards before any core L2 / apps_rg embedding init."""
    resolved = settings or resolve_apps_rg_embedding_settings(
        route_section=route_section,
        chroma_persist_dir=chroma_persist_dir,
    )
    if not resolved.embeddings_enabled:
        os.environ["SEMANTIC_CACHE_D2_ENABLED"] = "0"
        os.environ.setdefault("APPS_RG_R1B_SEMANTIC_PROOF", "INELIGIBLE")
    # Chroma is vector-store only; never allow Chroma/OpenAI default embedding functions.
    os.environ["APPS_RG_EMBEDDING_PROVIDER"] = "bge_local"
    os.environ["APPS_RG_FORBID_CHROMA_DEFAULT_EF"] = "1"
    os.environ.setdefault("CHROMA_DISABLE_DEFAULT_EMBEDDING", "1")
    if resolved.embedding_model_name:
        os.environ.setdefault("EMBEDDING_MODEL_ID", resolved.embedding_model_name)
    if resolved.embedding_model_path:
        os.environ.setdefault("APPS_RG_EMBEDDING_MODEL_PATH", resolved.embedding_model_path)
    os.environ.setdefault("APPS_RG_CHROMA_PRECOMPUTED_ONLY", "1")
    _logger.info(
        "apps_rg embedding settings: enabled=%s required=%s route=%s chroma_default_ef_used=%s",
        resolved.embeddings_enabled,
        resolved.embedding_required,
        resolved.route_result,
        resolved.chroma_default_ef_used,
    )
    return resolved


def assert_dense_retrieval_allowed(settings: AppsRgEmbeddingSettings) -> None:
    """Fail closed when dense C0 lane is configured but embeddings cannot run."""
    if settings.route_result == "FAIL_CLOSED":
        raise AppsRgEmbeddingFailClosedError(settings.decisive_reason)
    if settings.chroma_persist_dir and not settings.embeddings_enabled:
        raise AppsRgEmbeddingFailClosedError(settings.decisive_reason)
    if settings.dense_retrieval_enabled and settings.embedding_required:
        if not settings.embedding_model_resolved:
            raise AppsRgEmbeddingFailClosedError(settings.decisive_reason)


def load_bge_sentence_transformer(settings: AppsRgEmbeddingSettings) -> Any:
    """Load BGE from explicit local path only — no hub slug, no remote resolution."""
    if not settings.embeddings_enabled:
        raise AppsRgEmbeddingFailClosedError(
            "SentenceTransformer/BGE load forbidden when embeddings_enabled=false"
        )
    if not settings.embedding_model_resolved or not settings.embedding_model_path:
        raise AppsRgEmbeddingFailClosedError(settings.decisive_reason or "BGE path unresolved")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import]
    except ImportError as exc:
        detail = str(exc)
        if "Application Control policy" in detail or "torch._C" in detail:
            raise AppsRgEmbeddingFailClosedError(
                "PyTorch blocked by Windows Smart App Control (unsigned .pyd). "
                "Use WSL: tools/apps_rg/Invoke-AppsRgSectionWsl.ps1, or disable SAC: "
                "docs/guides/windows_smart_app_control_apps_rg.md"
            ) from exc
        raise AppsRgEmbeddingFailClosedError(
            "sentence-transformers required for BGE but not installed"
        ) from exc
    path = settings.embedding_model_path
    _logger.info("apps_rg BGE load: local path=%s (no HF hub)", path)
    return SentenceTransformer(path, local_files_only=True)


def write_embedding_settings_receipt(
    artifact_dir: Path | str | None,
    settings: AppsRgEmbeddingSettings,
) -> Path | None:
    if not artifact_dir or not str(artifact_dir).strip():
        return None
    root = Path(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    out = root / EMBEDDING_SETTINGS_RECEIPT_NAME
    from apps_rg.runtime.c02_chroma_lifecycle import resolve_proof_class
    from apps_rg.runtime.product_output_policy import product_fail_closed_runtime

    payload = settings.to_receipt_dict()
    payload["product_fail_closed"] = product_fail_closed_runtime()
    payload["proof_class"] = resolve_proof_class()
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def semantic_cache_r1b_eligible(settings: AppsRgEmbeddingSettings | None = None) -> bool:
    s = settings or resolve_apps_rg_embedding_settings()
    return bool(s.embeddings_enabled and s.semantic_cache_enabled and not s.semantic_cache_ineligible)


__all__ = [
    "AppsRgEmbeddingFailClosedError",
    "AppsRgEmbeddingSettings",
    "EMBEDDING_SETTINGS_RECEIPT_NAME",
    "bootstrap_apps_rg_embedding_env",
    "apply_apps_rg_embedding_env_guards",
    "assert_dense_retrieval_allowed",
    "load_bge_sentence_transformer",
    "resolve_apps_rg_embedding_settings",
    "semantic_cache_r1b_eligible",
    "write_embedding_settings_receipt",
]
