"""W1 phase 2 evidence probes for R1B semantic-cache certification.

Probes are read-only introspection + deterministic fixture harnesses.
They never write the sidecar or overrides — only raw evidence JSON.
The sidecar composer (scripts/compose_semantic_cache_subclaims.py) reads
these artifacts and writes the canonical sidecar.

Anti-cheat contract:
  - No probe may emit ``final_acceptance_status`` on any cache row.
  - No probe may silently lower thresholds.
  - No probe may claim BGE-M3 PASS when MiniLM/default EF was used.
  - No probe may claim production-durable mutation without UWG receipt.
  - No probe may claim integrated-runtime / OTEL / replay evidence.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_evidence(filename: str, payload: dict) -> Path:
    """Write an evidence JSON artifact to the canonical location."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS_DIR / filename
    payload = dict(payload)
    payload.setdefault("evidence_schema_version", 1)
    payload.setdefault("emitted_at_utc", now_utc())
    payload.setdefault("emitter", "w1_phase_2_probe")
    # Anti-cheat: strip any field an evidence harness must not set
    for forbidden in ("final_acceptance_status", "actual_proof_depth",
                      "acceptance_caveat", "blocking_gap"):
        payload.pop(forbidden, None)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    return path


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)
