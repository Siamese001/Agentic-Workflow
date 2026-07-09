"""apps_rg ``doctor`` — fresh-checkout preflight diagnostics.

Plan: apps-rg-e2e-gap-remediation-7e2d9c (W1 — fail-loud / exit codes; gaps G1, G2-preflight, G5).

A clean checkout is missing the prerequisites a product run needs (`.env` credentials, a populated
``fact_vectors`` Chroma collection, a resolvable local BGE-m3 embedding model). Today those gaps only
surface deep inside C0.2 as an opaque ``REQUIRED_PROOF_ABSENT``. ``doctor`` checks each prerequisite
up front and reports a named status plus remediation. With ``--strict`` any *required* failure makes
the process exit non-zero (``EXIT_CONFIG_ERROR``) so the operator gets the exact missing-prerequisite
list instead of an empty resume later.

Invoked via ``python -m apps_rg doctor [--strict] [--json]`` (intercepted in ``apps_rg.__main__.main``).
"""

from __future__ import annotations

import argparse
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from agentic_core.config.model_catalog import BGE_M3_MODEL_ID
from apps_rg.runtime.cli_exit_codes import EXIT_CONFIG_ERROR, EXIT_SUCCESS

REQUIRED = "required"
RECOMMENDED = "recommended"

BOOTSTRAP_CMD = "python -m apps_rg bootstrap fact-vectors --strict"
FACT_VECTORS_COLLECTION = "fact_vectors"


@dataclass
class DoctorCheck:
    """One prerequisite verdict."""

    name: str
    ok: bool
    severity: str
    detail: str
    remediation: str = ""

    @property
    def is_blocking(self) -> bool:
        """A required check that failed — the reason ``--strict`` exits non-zero."""
        return (not self.ok) and self.severity == REQUIRED


def _repo_root() -> Path:
    # apps_rg/runtime/doctor.py -> parents[2] == repo root
    return Path(__file__).resolve().parents[2]


def _resolve_chroma_path() -> str:
    return (os.environ.get("CHROMA_PERSIST_DIR", "") or "").strip()


def _check_generation_provider_key() -> DoctorCheck:
    """Default apps_rg E2E generation needs Anthropic and OpenAI keys."""
    required_keys = {
        "ANTHROPIC_API_KEY": "Claude-backed bullets, headline, and executive_summary lanes",
        "OPENAI_API_KEY": "OpenAI-backed competencies and narrative lanes",
    }
    missing = [var for var in required_keys if not os.environ.get(var, "").strip()]
    if not missing:
        return DoctorCheck(
            "generation_provider_key",
            True,
            REQUIRED,
            "ANTHROPIC_API_KEY and OPENAI_API_KEY present for default lane matrix",
        )
    detail = "missing required generation key(s): " + ", ".join(
        f"{var} ({required_keys[var]})" for var in missing
    )
    return DoctorCheck(
        "generation_provider_key",
        False,
        REQUIRED,
        detail,
        "Set ANTHROPIC_API_KEY and OPENAI_API_KEY in .env for the default per-section lane matrix.",
    )


def _check_judge_keys() -> list[DoctorCheck]:
    out: list[DoctorCheck] = []
    for var, who in (
        ("GOOGLE_API_KEY", "Gemini X1D proof judges"),
        ("OPENAI_API_KEY", "OpenAI X1D proof judges"),
    ):
        present = bool(os.environ.get(var, "").strip())
        out.append(
            DoctorCheck(
                f"judge_key:{var}",
                present,
                RECOMMENDED,
                f"{var} {'present' if present else 'missing'} ({who})",
                "" if present else f"Set {var} in .env if you use {who}.",
            )
        )
    return out


def _check_chroma_path() -> DoctorCheck:
    path = _resolve_chroma_path()
    if path:
        return DoctorCheck(
            "chroma_persist_dir", True, REQUIRED, f"CHROMA_PERSIST_DIR={path}"
        )
    return DoctorCheck(
        "chroma_persist_dir",
        False,
        REQUIRED,
        "CHROMA_PERSIST_DIR unset (embedding env not bootstrapped, or EMBEDDING_ENABLED is false)",
        "Set EMBEDDING_ENABLED=true and CHROMA_PERSIST_DIR=./data/cache/chromadb in .env.",
    )


def _check_embedding_model() -> DoctorCheck:
    try:
        from apps_rg.runtime.embedding_settings import resolve_apps_rg_embedding_settings

        settings = resolve_apps_rg_embedding_settings(
            chroma_persist_dir=_resolve_chroma_path() or None
        )
    except Exception as exc:  # guardian: allow-broad-exception -- doctor reports resolver failure as a diagnostic; it must never crash the operator's preflight
        return DoctorCheck(
            "embedding_model",
            False,
            REQUIRED,
            f"embedding settings resolver failed: {exc}",
            "Check EMBEDDING_ENABLED / APPS_RG_EMBEDDING_MODEL_PATH in .env.",
        )
    if not getattr(settings, "embeddings_enabled", False):
        return DoctorCheck(
            "embedding_model",
            False,
            REQUIRED,
            f"embeddings disabled (route_result={getattr(settings, 'route_result', '')}; "
            f"{getattr(settings, 'decisive_reason', '')})",
            "Set EMBEDDING_ENABLED=true and provide the local BGE-m3 model path.",
        )
    if not getattr(settings, "embedding_model_resolved", False):
        return DoctorCheck(
            "embedding_model",
            False,
            REQUIRED,
            f"BGE model '{getattr(settings, 'embedding_model_name', '')}' not resolved "
            f"(source={getattr(settings, 'embedding_model_source', '')})",
            f"Set APPS_RG_EMBEDDING_MODEL_PATH to the local {BGE_M3_MODEL_ID} snapshot directory.",
        )
    return DoctorCheck(
        "embedding_model",
        True,
        REQUIRED,
        f"BGE model '{getattr(settings, 'embedding_model_name', '')}' resolved "
        f"(source={getattr(settings, 'embedding_model_source', '')})",
    )


def _check_fact_vectors() -> DoctorCheck:
    """Verify the fact_vectors Chroma collection exists AND is populated (G2)."""
    path = _resolve_chroma_path()
    if not path:
        return DoctorCheck(
            "fact_vectors_collection",
            False,
            REQUIRED,
            "cannot check fact_vectors: CHROMA_PERSIST_DIR is unset",
            f"Configure CHROMA_PERSIST_DIR, then build the collection: {BOOTSTRAP_CMD}.",
        )
    try:
        from apps_rg.runtime.chroma_precomputed_collection import (
            get_precomputed_embeddings_collection_for_query,
            persistent_chroma_client,
        )

        try:
            client = persistent_chroma_client(path)
        except Exception as exc:  # guardian: allow-broad-exception -- Chroma process cache may already hold the same path with default test settings
            if "different settings" not in str(exc):
                raise
            import chromadb

            client = chromadb.PersistentClient(path=path)
        collection = get_precomputed_embeddings_collection_for_query(
            client, FACT_VECTORS_COLLECTION
        )
        count = int(collection.count())
    except Exception as exc:  # guardian: allow-broad-exception -- Chroma collection-error taxonomy varies by version; doctor classifies any failure as a missing-prerequisite diagnostic
        return DoctorCheck(
            "fact_vectors_collection",
            False,
            REQUIRED,
            f"fact_vectors collection unavailable at {path!r}: {exc}",
            f"Build it from tracked graph/proof-pool sources: {BOOTSTRAP_CMD}.",
        )
    if count <= 0:
        return DoctorCheck(
            "fact_vectors_collection",
            False,
            REQUIRED,
            f"fact_vectors collection present but EMPTY (0 atoms) at {path!r}",
            f"Populate it: {BOOTSTRAP_CMD}.",
        )
    return DoctorCheck(
        "fact_vectors_collection",
        True,
        REQUIRED,
        f"fact_vectors present with {count} atoms at {path!r}",
    )


def run_doctor(
    *, strict: bool, bootstrap_env: bool = True, repo_root: Path | None = None
) -> tuple[list[DoctorCheck], int]:
    """Run all prerequisite checks; return (checks, process_exit_code).

    ``bootstrap_env`` loads ``.env`` + embedding env so checks reflect the *effective* runtime
    state (tests pass ``False`` to control the environment deterministically).
    """
    if bootstrap_env:
        root = repo_root or _repo_root()
        try:
            from apps_rg.runtime.env_bootstrap import bootstrap_apps_rg_env

            bootstrap_apps_rg_env(repo_root=root)
        except Exception:  # guardian: allow-broad-exception -- doctor fail-soft: env bootstrap is best-effort; checks still run and report the gap
            pass
        try:
            from apps_rg.runtime.embedding_settings import bootstrap_apps_rg_embedding_env

            bootstrap_apps_rg_embedding_env(repo_root=root)
        except Exception:  # guardian: allow-broad-exception -- doctor fail-soft: embedding-env bootstrap is best-effort; checks still run and report the gap
            pass

    checks: list[DoctorCheck] = [
        _check_generation_provider_key(),
        *_check_judge_keys(),
        _check_chroma_path(),
        _check_embedding_model(),
        _check_fact_vectors(),
    ]
    blocking = [c for c in checks if c.is_blocking]
    exit_code = EXIT_CONFIG_ERROR if (strict and blocking) else EXIT_SUCCESS
    return checks, exit_code


def _render(checks: list[DoctorCheck], *, strict: bool, exit_code: int) -> None:
    print("apps_rg doctor — fresh-checkout preflight", flush=True)
    print(f"mode={'strict' if strict else 'report'}  exit_code={exit_code}", flush=True)
    for check in checks:
        mark = "PASS" if check.ok else ("FAIL" if check.severity == REQUIRED else "WARN")
        print(f"  [{mark}] {check.name}: {check.detail}", flush=True)
        if not check.ok and check.remediation:
            print(f"         -> {check.remediation}", flush=True)
    blocking = [c for c in checks if c.is_blocking]
    if blocking:
        names = ", ".join(c.name for c in blocking)
        print(f"BLOCKED: missing required prerequisites: {names}", flush=True)
    else:
        print("OK: all required prerequisites satisfied", flush=True)


def run_doctor_cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m apps_rg doctor",
        description="apps_rg fresh-checkout preflight diagnostics (plan apps-rg-e2e-gap-remediation-7e2d9c).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any required prerequisite is missing.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON instead of a table."
    )
    namespace = parser.parse_args(argv)
    checks, exit_code = run_doctor(strict=namespace.strict)
    if namespace.json:
        import json

        print(
            json.dumps(
                {
                    "tool": "apps_rg.doctor",
                    "strict": namespace.strict,
                    "exit_code": exit_code,
                    "checks": [asdict(c) for c in checks],
                },
                indent=2,
            ),
            flush=True,
        )
    else:
        _render(checks, strict=namespace.strict, exit_code=exit_code)
    return exit_code


__all__ = [
    "BOOTSTRAP_CMD",
    "DoctorCheck",
    "run_doctor",
    "run_doctor_cli",
]
