"""Synthetic / fixture / mock trace detector.

A small heuristic surface that the spine-proof bundle and verifiers
consult to decide whether the OTEL traces and per-run artifacts in a
run directory came from production code or from synthetic / fixture /
mock seeding.

Detection sources (best-effort; never raises):
    1. Environment variables explicitly set by callers:
         AGENTIC_CORE_SYNTHETIC_TRACE = 1|true|yes|on
         AGENTIC_CORE_FIXTURE_MODE    = 1|true|yes|on
         AGENTIC_CORE_MOCK_MODE       = 1|true|yes|on
    2. Repository-level seed scripts: presence of
       ``tools/otel/seed_synthetic_traces.py`` is informational only —
       the script can be present without being run.
    3. Inspection of the integrated_runtime manifest payload for
       known mock/fixture flags (``mock_safe_used``,
       ``deterministic_proof_stage_used``, ``veto_provider`` containing
       ``mock`` or ``fixture``).
    4. Optional artifact ``otel_synthetic_seed_marker.json`` placed by
       the synthetic-trace seeder. Absence is the default.

Doctrine:
    A run is **production** only when ALL three flags are False AND
    ``runtime_mode == 'production'``. Production runs MUST NOT carry any
    of the three flags True; the spine verifier fail-closes if they do.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

SYNTHETIC_SEED_MARKER_FILENAME = "otel_synthetic_seed_marker.json"


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _read_payload(path: Path) -> Mapping[str, Any] | None:
    if not path.exists():
        return None
    try:
        env = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):  # guardian: allow-return-none-swallow -- P1 ADG burndown
        return None
    if not isinstance(env, dict):
        return None
    payload = env.get("payload", env)
    return payload if isinstance(payload, dict) else None


@dataclass(frozen=True)
class TraceProvenanceFlags:
    """Three independent flags + a debug ``reasons`` list."""

    synthetic_trace_detected: bool
    fixture_mode_detected: bool
    mock_mode_detected: bool
    reasons: tuple[str, ...]


def detect_trace_provenance(
    artifact_dir: Path | None = None,
) -> TraceProvenanceFlags:
    """Return ``TraceProvenanceFlags`` for the given run directory.

    ``artifact_dir`` is optional — when omitted, only the env-var
    signals are consulted.
    """
    reasons: list[str] = []

    synthetic = _env_bool("AGENTIC_CORE_SYNTHETIC_TRACE", False)
    if synthetic:
        reasons.append("env_AGENTIC_CORE_SYNTHETIC_TRACE")
    fixture = _env_bool("AGENTIC_CORE_FIXTURE_MODE", False)
    if fixture:
        reasons.append("env_AGENTIC_CORE_FIXTURE_MODE")
    mock = _env_bool("AGENTIC_CORE_MOCK_MODE", False)
    if mock:
        reasons.append("env_AGENTIC_CORE_MOCK_MODE")

    if artifact_dir is not None:
        marker = Path(artifact_dir) / SYNTHETIC_SEED_MARKER_FILENAME
        if marker.exists():
            synthetic = True
            reasons.append("synthetic_seed_marker_present")

        manifest = _read_payload(
            Path(artifact_dir) / "integrated_runtime_artifact_manifest.json"
        )
        if manifest is not None:
            provider = str(manifest.get("veto_provider", "")).lower()
            if "mock" in provider:
                mock = True
                reasons.append(f"manifest_veto_provider_mock={provider}")
            if "fixture" in provider:
                fixture = True
                reasons.append(f"manifest_veto_provider_fixture={provider}")
            if bool(manifest.get("mock_safe_used")):
                mock = True
                reasons.append("manifest_mock_safe_used")
            if bool(manifest.get("deterministic_proof_stage_used")):
                # Deterministic proof stages are a proof-time-only fixture
                # — not synthetic traces, but they still flag a non-cert run.
                fixture = True
                reasons.append("manifest_deterministic_proof_stage_used")

    return TraceProvenanceFlags(
        synthetic_trace_detected=bool(synthetic),
        fixture_mode_detected=bool(fixture),
        mock_mode_detected=bool(mock),
        reasons=tuple(reasons),
    )


__all__ = [
    "SYNTHETIC_SEED_MARKER_FILENAME",
    "TraceProvenanceFlags",
    "detect_trace_provenance",
]
