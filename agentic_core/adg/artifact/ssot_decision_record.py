"""SSOTDecisionRecord — cross-bucket reconciliation primitive.

When a claim requires reconciling evidence across the three ADG buckets
(static / runtime / registry), the answer is an ``SSOTDecisionRecord``.

The record answers the question:

    "For this exact run, under this exact policy and registry snapshot,
     did the thing exist, was it allowed, did it happen, and was the
     result sealed?"

The eight outcomes form a 3-axis (FOUND × ALLOWED × USED) decision matrix:

    found     | allowed   | used      | outcome             | severity
    ----------|-----------|-----------|---------------------|----------
    FOUND     | ALLOWED   | USED      | VALID_USE           | gold
    FOUND     | ALLOWED   | NOT_USED  | ALLOWED_NOT_USED    | benign
    FOUND     | BLOCKED   | USED      | POLICY_BYPASS       | INCIDENT
    FOUND     | BLOCKED   | NOT_USED  | BLOCKED_UNUSED      | benign
    NOT_FOUND | ALLOWED   | USED      | HIDDEN_PATH         | INTEGRITY
    NOT_FOUND | ALLOWED   | NOT_USED  | REGISTRY_DRIFT      | hygiene
    NOT_FOUND | BLOCKED   | USED      | SEVERE_BYPASS       | CRITICAL
    NOT_FOUND | BLOCKED   | NOT_USED  | CLEAN_ABSENCE       | benign

Where each axis is derived from one ADG bucket:

    FOUND     iff at least one static_ref exists      (static bucket)
    NOT_FOUND iff static_refs is empty
    ALLOWED   iff at least one registry_ref is        (registry bucket)
              AUTHORITATIVE_REGISTRY
    BLOCKED   iff registry_refs is empty OR every
              registry_ref is non-authoritative
    USED      iff at least one runtime_ref is         (runtime bucket)
              AUTHORITATIVE_RUNTIME
    NOT_USED  iff runtime_refs is empty OR no
              runtime_ref is authoritative

Only the three bucket-derived authority signals partition the outcome
space; bucket evidence presence alone does not — a registry_ref that is
``STALE_REGISTRY`` does not count as ``ALLOWED``.

Doctrinal source: 2026-04-29 user directive — "ADG must also emit an
SSOTDecisionRecord when a claim requires reconciliation across buckets."
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Final


# ---------------------------------------------------------------------------
# Closed enum: Outcome (8 cells of the FOUND × ALLOWED × USED matrix)
# ---------------------------------------------------------------------------


class Outcome(str, Enum):
    """The eight outcomes of a cross-bucket reconciliation.

    Inheriting from ``str`` lets us serialize as plain strings without
    enum handling everywhere.
    """

    VALID_USE = "VALID_USE"  # FOUND + ALLOWED + USED — gold
    ALLOWED_NOT_USED = "ALLOWED_NOT_USED"  # FOUND + ALLOWED + NOT_USED
    POLICY_BYPASS = "POLICY_BYPASS"  # FOUND + BLOCKED + USED — incident
    BLOCKED_UNUSED = "BLOCKED_UNUSED"  # FOUND + BLOCKED + NOT_USED
    HIDDEN_PATH = "HIDDEN_PATH"  # NOT_FOUND + ALLOWED + USED — integrity
    REGISTRY_DRIFT = "REGISTRY_DRIFT"  # NOT_FOUND + ALLOWED + NOT_USED
    SEVERE_BYPASS = "SEVERE_BYPASS"  # NOT_FOUND + BLOCKED + USED — critical
    CLEAN_ABSENCE = "CLEAN_ABSENCE"  # NOT_FOUND + BLOCKED + NOT_USED


ALL_OUTCOMES: Final[frozenset[str]] = frozenset(o.value for o in Outcome)

# Outcome → severity level for triage / alerting consumers.
OUTCOME_SEVERITY: Final[dict[str, str]] = {
    Outcome.VALID_USE.value: "gold",
    Outcome.ALLOWED_NOT_USED.value: "benign",
    Outcome.POLICY_BYPASS.value: "INCIDENT",
    Outcome.BLOCKED_UNUSED.value: "benign",
    Outcome.HIDDEN_PATH.value: "INTEGRITY",
    Outcome.REGISTRY_DRIFT.value: "hygiene",
    Outcome.SEVERE_BYPASS.value: "CRITICAL",
    Outcome.CLEAN_ABSENCE.value: "benign",
}


# ---------------------------------------------------------------------------
# Reconciler — pure function over the three bucket evidence lists
# ---------------------------------------------------------------------------


def reconcile_outcome(
    *,
    found: bool,
    allowed: bool,
    used: bool,
) -> Outcome:
    """Compute the matrix outcome from three boolean axes.

    This is the canonical decision function. All other reconciliation
    helpers must derive ``found`` / ``allowed`` / ``used`` from their
    inputs and delegate here.
    """
    if found and allowed and used:
        return Outcome.VALID_USE
    if found and allowed and not used:
        return Outcome.ALLOWED_NOT_USED
    if found and not allowed and used:
        return Outcome.POLICY_BYPASS
    if found and not allowed and not used:
        return Outcome.BLOCKED_UNUSED
    if not found and allowed and used:
        return Outcome.HIDDEN_PATH
    if not found and allowed and not used:
        return Outcome.REGISTRY_DRIFT
    if not found and not allowed and used:
        return Outcome.SEVERE_BYPASS
    return Outcome.CLEAN_ABSENCE


def reconcile_from_refs(
    *,
    static_refs: list[str] | tuple[str, ...],
    runtime_refs: list[str] | tuple[str, ...],
    registry_refs: list[str] | tuple[str, ...],
    registry_authoritative: bool = True,
    runtime_authoritative: bool = True,
) -> Outcome:
    """Derive the matrix outcome from the three reference lists.

    Args:
        static_refs:   edge_id / node_id list from ``proof_view`` filtered
                       to ``bucket = 'static'``
        runtime_refs:  edge_id list from ``proof_view`` filtered to
                       ``bucket = 'runtime'``
        registry_refs: edge_id list from ``proof_view`` filtered to
                       ``bucket = 'registry'``
        registry_authoritative: True iff every registry_ref has
                       ``authority_status = 'AUTHORITATIVE_REGISTRY'``.
                       False if any ref is stale/mismatched/unresolved.
                       (W3 work: callers infer this from the bucket.)
        runtime_authoritative: True iff at least one runtime_ref has
                       ``authority_status = 'AUTHORITATIVE_RUNTIME'``.
                       (Derived by the runtime bucket lift in W2.)

    Note: ``static_refs`` does not need an ``authoritative`` flag — by
    the time a static_ref reaches this function it is already in
    ``proof_view``, so it is AUTHORITATIVE by the authority law.
    """
    found = bool(static_refs)
    allowed = bool(registry_refs) and registry_authoritative
    used = bool(runtime_refs) and runtime_authoritative
    return reconcile_outcome(found=found, allowed=allowed, used=used)


# ---------------------------------------------------------------------------
# Determinism helpers — manifest_hash, replay_key, hmac_sig
# ---------------------------------------------------------------------------


def compute_manifest_hash(
    *,
    static_refs: list[str] | tuple[str, ...],
    runtime_refs: list[str] | tuple[str, ...],
    registry_refs: list[str] | tuple[str, ...],
    policy_hash: str,
    blueprint_hash: str,
    registry_digest_set: list[str] | tuple[str, ...],
) -> str:
    """Deterministic SHA-256 over the reconciliation inputs.

    The manifest_hash is the durable proof that the SSOT record's
    constituent evidence has not been tampered with. Same inputs (in any
    order) → same hash. Used by the W5 deterministic-digest test.
    """
    payload = {
        "static_refs": sorted(static_refs),
        "runtime_refs": sorted(runtime_refs),
        "registry_refs": sorted(registry_refs),
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "registry_digest_set": sorted(registry_digest_set),
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def compute_replay_key(
    *,
    request_id: str,
    run_id: str,
    route_contract_id: str,
    policy_hash: str,
) -> str:
    """Deterministic replay identifier.

    Two runs that share (request_id, run_id, route_contract_id,
    policy_hash) MUST produce the same replay_key. Replay = same key,
    same matrix outcome.
    """
    payload = f"{request_id}|{run_id}|{route_contract_id}|{policy_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_hmac_sig(*, manifest_hash: str, secret: str | None = None) -> str:
    """HMAC-SHA256 over manifest_hash for tamper-evident signing.

    Secret resolution order:
        1. Explicit ``secret`` argument
        2. ``ADG_SSOT_HMAC_KEY`` environment variable
        3. Built-in dev key (NOT for production — produces a deterministic
           signature that explicitly identifies itself as dev)
    """
    if secret is None:
        secret = os.environ.get("ADG_SSOT_HMAC_KEY", "ADG_DEV_HMAC_KEY_DO_NOT_USE_IN_PROD")
    return hmac.new(secret.encode("utf-8"), manifest_hash.encode("utf-8"), hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# Dataclass: SSOTDecisionRecord
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SSOTDecisionRecord:
    """Cross-bucket reconciliation record (durable evidence ledger entry).

    All required fields per spec Section 2 are mandatory at construction.
    Optional fields default to None.

    Use ``SSOTDecisionRecord.build(...)`` to construct one with computed
    manifest_hash, replay_key, hmac_sig, and outcome — this is the
    canonical path consumers should use rather than __init__ directly.
    """

    # Required scalar identifiers
    request_id: str
    run_id: str
    trace_id: str
    route_contract_id: str
    policy_hash: str
    blueprint_hash: str

    # Required bucket evidence (tuples — frozen for hashability)
    registry_digest_set: tuple[str, ...]
    static_refs: tuple[str, ...]
    runtime_refs: tuple[str, ...]
    registry_refs: tuple[str, ...]

    # Required determinism / signing
    replay_key: str
    manifest_hash: str
    hmac_sig: str

    # Required outcome
    outcome: str  # one of Outcome enum values

    # Optional context refs (per spec Section 2 — populated when applicable)
    evidence_contract_ref: str | None = None
    prompt_artifact_ref: str | None = None
    sealed_l2_artifact_ref: str | None = None
    exit_review_packet_ref: str | None = None
    x3_disposition: str | None = None
    uwg_commit_receipt_ref: str | None = None

    @classmethod
    def build(
        cls,
        *,
        request_id: str,
        run_id: str,
        trace_id: str,
        route_contract_id: str,
        policy_hash: str,
        blueprint_hash: str,
        registry_digest_set: list[str] | tuple[str, ...],
        static_refs: list[str] | tuple[str, ...],
        runtime_refs: list[str] | tuple[str, ...],
        registry_refs: list[str] | tuple[str, ...],
        registry_authoritative: bool = True,
        runtime_authoritative: bool = True,
        evidence_contract_ref: str | None = None,
        prompt_artifact_ref: str | None = None,
        sealed_l2_artifact_ref: str | None = None,
        exit_review_packet_ref: str | None = None,
        x3_disposition: str | None = None,
        uwg_commit_receipt_ref: str | None = None,
        hmac_secret: str | None = None,
    ) -> "SSOTDecisionRecord":
        """Construct a record with computed manifest_hash, replay_key,
        hmac_sig, and outcome. Canonical path for callers.
        """
        outcome = reconcile_from_refs(
            static_refs=static_refs,
            runtime_refs=runtime_refs,
            registry_refs=registry_refs,
            registry_authoritative=registry_authoritative,
            runtime_authoritative=runtime_authoritative,
        )
        manifest_hash = compute_manifest_hash(
            static_refs=static_refs,
            runtime_refs=runtime_refs,
            registry_refs=registry_refs,
            policy_hash=policy_hash,
            blueprint_hash=blueprint_hash,
            registry_digest_set=registry_digest_set,
        )
        replay_key = compute_replay_key(
            request_id=request_id,
            run_id=run_id,
            route_contract_id=route_contract_id,
            policy_hash=policy_hash,
        )
        hmac_sig = compute_hmac_sig(manifest_hash=manifest_hash, secret=hmac_secret)
        return cls(
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            route_contract_id=route_contract_id,
            policy_hash=policy_hash,
            blueprint_hash=blueprint_hash,
            registry_digest_set=tuple(registry_digest_set),
            static_refs=tuple(static_refs),
            runtime_refs=tuple(runtime_refs),
            registry_refs=tuple(registry_refs),
            replay_key=replay_key,
            manifest_hash=manifest_hash,
            hmac_sig=hmac_sig,
            outcome=outcome.value,
            evidence_contract_ref=evidence_contract_ref,
            prompt_artifact_ref=prompt_artifact_ref,
            sealed_l2_artifact_ref=sealed_l2_artifact_ref,
            exit_review_packet_ref=exit_review_packet_ref,
            x3_disposition=x3_disposition,
            uwg_commit_receipt_ref=uwg_commit_receipt_ref,
        )

    def to_db_row(self) -> dict[str, str | None]:
        """Serialize to a dict suitable for INSERT into ssot_decision_records.

        Tuples are JSON-encoded; optional fields keep None (NULL in SQL).
        """
        return {
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_id": self.trace_id,
            "route_contract_id": self.route_contract_id,
            "policy_hash": self.policy_hash,
            "blueprint_hash": self.blueprint_hash,
            "registry_digest_set": json.dumps(list(self.registry_digest_set)),
            "static_refs": json.dumps(list(self.static_refs)),
            "runtime_refs": json.dumps(list(self.runtime_refs)),
            "registry_refs": json.dumps(list(self.registry_refs)),
            "evidence_contract_ref": self.evidence_contract_ref,
            "prompt_artifact_ref": self.prompt_artifact_ref,
            "sealed_l2_artifact_ref": self.sealed_l2_artifact_ref,
            "exit_review_packet_ref": self.exit_review_packet_ref,
            "x3_disposition": self.x3_disposition,
            "uwg_commit_receipt_ref": self.uwg_commit_receipt_ref,
            "replay_key": self.replay_key,
            "manifest_hash": self.manifest_hash,
            "hmac_sig": self.hmac_sig,
            "outcome": self.outcome,
        }


# ---------------------------------------------------------------------------
# SQL: durable storage for SSOTDecisionRecord
# ---------------------------------------------------------------------------

SQL_CREATE_SSOT_DECISION_RECORDS: Final[str] = """\
CREATE TABLE IF NOT EXISTS ssot_decision_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Required scalar identifiers
    request_id          TEXT NOT NULL,
    run_id              TEXT NOT NULL,
    trace_id            TEXT NOT NULL,
    route_contract_id   TEXT NOT NULL,
    policy_hash         TEXT NOT NULL,
    blueprint_hash      TEXT NOT NULL,

    -- Bucket evidence (JSON arrays — sorted at write time for determinism)
    registry_digest_set TEXT NOT NULL,
    static_refs         TEXT NOT NULL,
    runtime_refs        TEXT NOT NULL,
    registry_refs       TEXT NOT NULL,

    -- Optional context refs (NULL when not applicable)
    evidence_contract_ref   TEXT,
    prompt_artifact_ref     TEXT,
    sealed_l2_artifact_ref  TEXT,
    exit_review_packet_ref  TEXT,
    x3_disposition          TEXT,
    uwg_commit_receipt_ref  TEXT,

    -- Determinism + signing
    replay_key      TEXT NOT NULL,
    manifest_hash   TEXT NOT NULL,
    hmac_sig        TEXT NOT NULL,

    -- Reconciled outcome (one of the 8 matrix cells)
    outcome         TEXT NOT NULL,

    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ssot_run         ON ssot_decision_records(run_id);
CREATE INDEX IF NOT EXISTS idx_ssot_trace       ON ssot_decision_records(trace_id);
CREATE INDEX IF NOT EXISTS idx_ssot_request     ON ssot_decision_records(request_id);
CREATE INDEX IF NOT EXISTS idx_ssot_outcome     ON ssot_decision_records(outcome);
CREATE INDEX IF NOT EXISTS idx_ssot_replay_key  ON ssot_decision_records(replay_key);
CREATE INDEX IF NOT EXISTS idx_ssot_manifest    ON ssot_decision_records(manifest_hash);
"""

SQL_INSERT_SSOT_DECISION_RECORD: Final[str] = """\
INSERT INTO ssot_decision_records (
    request_id, run_id, trace_id, route_contract_id, policy_hash, blueprint_hash,
    registry_digest_set, static_refs, runtime_refs, registry_refs,
    evidence_contract_ref, prompt_artifact_ref, sealed_l2_artifact_ref,
    exit_review_packet_ref, x3_disposition, uwg_commit_receipt_ref,
    replay_key, manifest_hash, hmac_sig, outcome
) VALUES (
    :request_id, :run_id, :trace_id, :route_contract_id, :policy_hash, :blueprint_hash,
    :registry_digest_set, :static_refs, :runtime_refs, :registry_refs,
    :evidence_contract_ref, :prompt_artifact_ref, :sealed_l2_artifact_ref,
    :exit_review_packet_ref, :x3_disposition, :uwg_commit_receipt_ref,
    :replay_key, :manifest_hash, :hmac_sig, :outcome
)
"""

# Outcome distribution histogram — quick health signal for SSOT records.
SQL_OUTCOME_HISTOGRAM: Final[str] = (
    "SELECT outcome, COUNT(*) AS n FROM ssot_decision_records GROUP BY outcome ORDER BY n DESC"
)
