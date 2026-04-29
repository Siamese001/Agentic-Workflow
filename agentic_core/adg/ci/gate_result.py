"""Normalized result contract for ADG three-graph CI gates.

All ADG CI gates — when invoked via the manifest-driven runner — emit one of
these structured records. The shape is the SSOT consumed by:

  * ops_scripts/ci/run_adg_three_graph_tests.py (rollup + acceptance)
  * tests/integration/adg/test_legacy_parity.py (legacy vs manifest)
  * tests/integration/adg/test_negative_controls.py (expected_fail_reason match)

Status semantics
----------------
PASS   — gate ran, all assertions held
FAIL   — gate ran, at least one assertion violated; populates ``sample_failures``
WARN   — assertion not met but the gate is in advisory/audit mode (or the
         underlying schema field is aspirational); gate did NOT fail-close
SKIP   — pre-conditions not met (no snapshot, view absent, etc.); gate
         emitted no verdict
ERROR  — gate crashed or returned malformed output; runner should treat as
         hard failure regardless of strict mode

Buckets
-------
static       — operates on AST-extracted nodes/edges/mv_*/v_p*
registry     — operates on edges WHERE bucket='registry' + registry_node nodes
runtime      — operates on v_runtime_proof + runtime store evidence
cross_bucket — operates on the gap classifier or multi-bucket joins
provenance   — operates on snapshot signature / digest / lineage
schema       — operates on PRAGMA / column-level closed-enum integrity
preflight    — environmental sanity (snapshot exists, schema_version, etc.)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Final

# This module ships data contracts only; it does not query ADG views itself.
__adg_consumer_mode__ = "inventory"


VALID_STATUSES: Final[frozenset[str]] = frozenset(
    {"PASS", "FAIL", "WARN", "SKIP", "ERROR"}
)
VALID_BUCKETS: Final[frozenset[str]] = frozenset(
    {
        "static",
        "registry",
        "runtime",
        "cross_bucket",
        "provenance",
        "schema",
        "preflight",
    }
)
VALID_EVIDENCE_MODES: Final[frozenset[str]] = frozenset(
    {"proof", "risk", "inventory"}
)
VALID_ENFORCEMENT_MODES: Final[frozenset[str]] = frozenset(
    {"strict", "advisory", "ratchet", "audit"}
)


@dataclass
class GateResult:
    """Normalized result emitted by every ADG three-graph CI gate.

    Field semantics
    ---------------
    gate_id              — manifest gate_id (e.g. ``static.snapshot_has_mvs``)
    bucket               — one of VALID_BUCKETS
    status               — one of VALID_STATUSES
    evidence_mode        — proof | risk | inventory (matches manifest)
    enforcement_mode     — strict | advisory | ratchet | audit (matches manifest)
    snapshot_id          — short SHA of the snapshot under test (or empty)
    input_refs           — files/views the gate read; for traceability
    counts               — gate-specific count rollup (rows, violations, ...)
    thresholds           — thresholds applied (max_count, max_pct, ...)
    sample_failures      — up to 10 representative failure rows
    bypass_env_detected  — list of bypass env vars active when gate ran
    expected_fail_reason — non-empty for negative-control fixtures
    actual_fail_reason   — short stable string identifying WHY the gate failed
                           (matched against expected_fail_reason in negative
                           controls); empty when status=PASS
    artifact_hash        — SHA-256 of the gate's full structured output
                           (computed by ``finalize()``); used by runner to
                           detect mid-run report corruption
    duration_ms          — wall-clock duration of the gate run
    started_at           — ISO-8601 UTC timestamp
    """

    gate_id: str
    bucket: str
    status: str
    evidence_mode: str = "inventory"
    enforcement_mode: str = "advisory"
    snapshot_id: str = ""
    input_refs: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    thresholds: dict[str, Any] = field(default_factory=dict)
    sample_failures: list[dict[str, Any]] = field(default_factory=list)
    bypass_env_detected: list[str] = field(default_factory=list)
    expected_fail_reason: str = ""
    actual_fail_reason: str = ""
    artifact_hash: str = ""
    duration_ms: int = 0
    started_at: str = ""

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(
                f"GateResult.status={self.status!r} not in {sorted(VALID_STATUSES)}"
            )
        if self.bucket not in VALID_BUCKETS:
            raise ValueError(
                f"GateResult.bucket={self.bucket!r} not in {sorted(VALID_BUCKETS)}"
            )
        if self.evidence_mode not in VALID_EVIDENCE_MODES:
            raise ValueError(
                f"GateResult.evidence_mode={self.evidence_mode!r} "
                f"not in {sorted(VALID_EVIDENCE_MODES)}"
            )
        if self.enforcement_mode not in VALID_ENFORCEMENT_MODES:
            raise ValueError(
                f"GateResult.enforcement_mode={self.enforcement_mode!r} "
                f"not in {sorted(VALID_ENFORCEMENT_MODES)}"
            )
        if self.status == "PASS" and self.actual_fail_reason:
            raise ValueError(
                "actual_fail_reason must be empty when status=PASS"
            )
        if self.status == "FAIL" and not self.actual_fail_reason:
            raise ValueError(
                "actual_fail_reason must be non-empty when status=FAIL"
            )
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()
        if len(self.sample_failures) > 10:
            self.sample_failures = self.sample_failures[:10]

    def to_json(self) -> dict[str, Any]:
        """Return a deterministic dict ready for ``json.dumps(sort_keys=True)``."""
        out = asdict(self)
        # asdict preserves insertion order, but the artifact_hash must
        # reflect the post-sort canonical form so callers can verify.
        return out

    def finalize(self) -> "GateResult":
        """Compute artifact_hash over the canonical JSON form.

        Hash excludes ``artifact_hash`` itself (otherwise it would be
        self-referential).
        """
        payload = self.to_json()
        payload["artifact_hash"] = ""
        canon = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        self.artifact_hash = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]
        return self


def gate_result_from_dict(payload: dict[str, Any]) -> GateResult:
    """Reconstruct a GateResult from a dict (e.g. when loading a rollup JSON).

    Tolerates extra keys (forward-compat) and missing optional fields.
    Raises ValueError on missing-required or invalid-enum fields via
    GateResult.__post_init__.
    """
    required = {"gate_id", "bucket", "status"}
    missing = required - set(payload)
    if missing:
        raise ValueError(f"gate_result_from_dict: missing required fields {missing}")

    return GateResult(
        gate_id=str(payload["gate_id"]),
        bucket=str(payload["bucket"]),
        status=str(payload["status"]),
        evidence_mode=str(payload.get("evidence_mode", "inventory")),
        enforcement_mode=str(payload.get("enforcement_mode", "advisory")),
        snapshot_id=str(payload.get("snapshot_id", "")),
        input_refs=list(payload.get("input_refs") or []),
        counts=dict(payload.get("counts") or {}),
        thresholds=dict(payload.get("thresholds") or {}),
        sample_failures=list(payload.get("sample_failures") or []),
        bypass_env_detected=list(payload.get("bypass_env_detected") or []),
        expected_fail_reason=str(payload.get("expected_fail_reason", "")),
        actual_fail_reason=str(payload.get("actual_fail_reason", "")),
        artifact_hash=str(payload.get("artifact_hash", "")),
        duration_ms=int(payload.get("duration_ms", 0)),
        started_at=str(payload.get("started_at", "")),
    )


# ---------------------------------------------------------------------------
# Rollup
# ---------------------------------------------------------------------------


@dataclass
class RollupResult:
    """Output of one full run of the manifest-driven runner."""

    suite: str
    snapshot_id: str
    started_at: str
    finished_at: str = ""
    strict_mode: bool = False
    gates: list[dict[str, Any]] = field(default_factory=list)
    summary_by_bucket: dict[str, dict[str, int]] = field(default_factory=dict)
    summary_by_status: dict[str, int] = field(default_factory=dict)
    overall_status: str = "PENDING"  # PASS | FAIL | ERROR | PENDING
    overall_fail_reasons: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


__all__ = [
    "GateResult",
    "RollupResult",
    "gate_result_from_dict",
    "VALID_STATUSES",
    "VALID_BUCKETS",
    "VALID_EVIDENCE_MODES",
    "VALID_ENFORCEMENT_MODES",
]
