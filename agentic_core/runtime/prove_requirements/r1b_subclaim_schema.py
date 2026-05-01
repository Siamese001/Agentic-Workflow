"""R1B Subclaim Schema — sidecar contract for the semantic-cache certification.

Plan: ``.windsurf/plans/runtime-cert-hardened-w0-7e3c9a.md``  (W1 phase 1)
Author-Gate decision (2026-04-30, architecture_choice):
``map_to_RTC_REQ_055_plus_conditional_056_057_058``.

Boundary
--------

W1 phase 1 is **contract wiring only**. This module defines the sidecar
schema for declaring R1B semantic-cache subclaim verdicts. It does NOT
emit evidence, run cache fixtures, or modify ``SemanticCacheManager``.
Evidence emission is W1 phase 2's job.

Sidecar contract
----------------

Input file: ``artifacts/certification/semantic_cache_subclaims.json``

Schema::

    {
      "schema_version": 1,
      "evaluated_at_utc": "...",
      "evidence_evaluator": "...",
      "scope": {
        "runtime_certification_claimed":       false,
        "observability_certification_claimed": false,
        "replay_certification_claimed":        false
      },
      "subclaims": {
        "R1B_DENSE_SIMILARITY_COMPOSITION_PROOF":  {"status": "...", "evidence_path": null, "notes": "..."},
        "R1B_APPROVED_MODEL_PROOF":                {"status": "...", "evidence_path": null, "notes": "..."},
        "R1B_PRODUCTION_THRESHOLD_PROOF":          {"status": "...", "evidence_path": null, "notes": "..."},
        "R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF": {"status": "...", "evidence_path": null, "notes": "..."},
        "R1B_NEGATIVE_CONTROL_PROOF":              {"status": "...", "evidence_path": null, "notes": "..."},
        "R1B_TERMINAL_EXIT_PROOF":                 {"status": "...", "evidence_path": null, "notes": "..."},
        "R1B_INTEGRATED_RUNTIME_PROOF":            {"status": "...", "evidence_path": null, "notes": "..."},
        "R1B_REAL_OTEL_PROOF":                    {"status": "...", "evidence_path": null, "notes": "..."},
        "R1B_REPLAY_PROOF":                       {"status": "...", "evidence_path": null, "notes": "..."}
      }
    }

Anti-cheat
----------

  - The sidecar carries NO ``final_acceptance_status`` field. Only the
    verifier writes overrides; the sidecar can only declare per-subclaim
    verdicts.
  - ``NOT_APPLICABLE`` is permitted ONLY on the 3 conditional subclaims
    (integrated/otel/replay) AND ONLY when their scope flag is False.
  - All 6 core subclaims MUST be present and MUST NOT be NOT_APPLICABLE.
  - Sidecar fields ``actual_proof_depth``, ``final_acceptance_status``,
    or anything else not declared above are silently dropped during
    validation; they cannot promote a row.

Row mapping (per Author-Gate 2026-04-30)
----------------------------------------

  - RTC-REQ-055 (E5_COMPOSITION_PROOF, R1B parent): gated by 6 core
    subclaims always.
  - RTC-REQ-056 (E6_INTEGRATED_RUNTIME_PROOF): gated when
    ``scope.runtime_certification_claimed`` AND R1B_INTEGRATED_RUNTIME_PROOF.
  - RTC-REQ-057 (E7_REAL_OTEL_EXPORT): gated when
    ``scope.observability_certification_claimed`` AND R1B_REAL_OTEL_PROOF.
  - RTC-REQ-058 (E8_REPLAY_DETERMINISM): gated when
    ``scope.replay_certification_claimed`` AND R1B_REPLAY_PROOF.

Public API
----------

- ``CORE_SUBCLAIMS`` — the 6 always-required subclaim ids
- ``CONDITIONAL_SUBCLAIMS`` — 3 conditional ids
- ``ALL_SUBCLAIMS`` — union, in canonical order
- ``ALLOWED_STATUSES`` — frozenset of permitted status strings
- ``GATED_ROWS`` — mapping of ``row_id -> required_proof_depth``
- ``SUBCLAIM_TO_GATE`` — mapping of subclaim id -> the row it gates
- ``SidecarLoadResult``, ``SubclaimVerdict``, ``RowOutcome`` — dataclasses
- ``load_sidecar(path)`` — fail-closed reader
- ``compute_row_outcomes(load_result)`` — verdict computer
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, Mapping


# ──────────────────────────────────────────────────────────────────────
# Canonical subclaim catalog
# ──────────────────────────────────────────────────────────────────────

# Legacy RTC-REQ-055 gating set — DENSE-ONLY semantic cache reuse proof.
# Keeps R1B_PRODUCTION_THRESHOLD_PROOF in the gating, so RTC-REQ-055
# remains PARTIAL/CALIBRATION_GAP until SEMCACHE-THRESH-001 is approved.
# This preserves the W1p4 finding — see W1p6 migration report.
LEGACY_RTC_REQ_055_SUBCLAIMS: Final[tuple[str, ...]] = (
    "R1B_DENSE_SIMILARITY_COMPOSITION_PROOF",
    "R1B_APPROVED_MODEL_PROOF",
    "R1B_PRODUCTION_THRESHOLD_PROOF",
    "R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF",
    "R1B_NEGATIVE_CONTROL_PROOF",
    "R1B_TERMINAL_EXIT_PROOF",
    # W1p5: layered safety veto proof added to the legacy R1B parent.
    "R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF",
)

# All core subclaims that MUST appear in the sidecar. The composer emits
# all of these on every run.
CORE_SUBCLAIMS: Final[tuple[str, ...]] = LEGACY_RTC_REQ_055_SUBCLAIMS + (
    # W1p6: dense + veto composite "safe reuse" proof. Gates RTC-REQ-059
    # (new requirement reflecting the approved dense+veto architecture).
    # Explicitly NOT part of LEGACY_RTC_REQ_055_SUBCLAIMS so dense-only
    # RTC-REQ-055 remains pinned to its W1p4 CALIBRATION_GAP finding.
    "R1B_SAFE_REUSE_COMPOSITE_PROOF",
)

CONDITIONAL_SUBCLAIMS: Final[tuple[str, ...]] = (
    "R1B_INTEGRATED_RUNTIME_PROOF",
    "R1B_REAL_OTEL_PROOF",
    "R1B_REPLAY_PROOF",
)

ALL_SUBCLAIMS: Final[tuple[str, ...]] = CORE_SUBCLAIMS + CONDITIONAL_SUBCLAIMS

ALLOWED_STATUSES: Final[frozenset[str]] = frozenset({
    "PASS",
    "PARTIAL",
    "BLOCKED",
    "NOT_PROVEN",
    "CALIBRATION_GAP",
    "INFRASTRUCTURE_GAP",
    "NOT_APPLICABLE",
})

# Statuses that block ACCEPTED. Order intentionally distinguishes hard
# blockers (BLOCKED/NOT_PROVEN/INFRASTRUCTURE_GAP) from soft blockers
# (PARTIAL/CALIBRATION_GAP); the verifier maps hard -> BLOCKED row status,
# soft -> PARTIAL row status.
HARD_BLOCKER_STATUSES: Final[frozenset[str]] = frozenset({
    "BLOCKED",
    "NOT_PROVEN",
    "INFRASTRUCTURE_GAP",
})
SOFT_BLOCKER_STATUSES: Final[frozenset[str]] = frozenset({
    "PARTIAL",
    "CALIBRATION_GAP",
})

# Conditional scope flags. Each maps to (a) a scope-key and
# (b) the conditional subclaim that must be present when scope is True.
SCOPE_FLAG_TO_CONDITIONAL_SUBCLAIM: Final[Mapping[str, str]] = {
    "runtime_certification_claimed":       "R1B_INTEGRATED_RUNTIME_PROOF",
    "observability_certification_claimed": "R1B_REAL_OTEL_PROOF",
    "replay_certification_claimed":        "R1B_REPLAY_PROOF",
}

# Row id -> (required_proof_depth, scope_flag, gating_subclaims).
#   - RTC-REQ-055: legacy dense-only R1B parent. Pinned to
#     LEGACY_RTC_REQ_055_SUBCLAIMS so the W1p4 CALIBRATION_GAP finding
#     on R1B_PRODUCTION_THRESHOLD_PROOF is preserved regardless of W1p6
#     additions.
#   - RTC-REQ-056/057/058: conditional runtime/OTEL/replay. Also pinned to
#     the legacy set so W1p6 doesn't retroactively change their gating.
#   - RTC-REQ-059: NEW. Certifies the approved dense+veto "safe reuse"
#     architecture. Gated by R1B_SAFE_REUSE_COMPOSITE_PROOF plus the
#     subclaims that materially feed the composite (model, veto, negatives,
#     policy/freshness, terminal exit). Does NOT gate on the legacy
#     R1B_PRODUCTION_THRESHOLD_PROOF because that subclaim is now scoped
#     to dense-only semantic-equivalence claims, not safe-reuse claims.
GATED_ROWS: Final[Mapping[str, dict[str, Any]]] = {
    "RTC-REQ-055": {
        "required_proof_depth": "E5_COMPOSITION_PROOF",
        "scope_flag":           None,
        "gating_subclaims":     LEGACY_RTC_REQ_055_SUBCLAIMS,
    },
    # W2 (2026-05-01): RTC-REQ-056 is the integrated-runtime companion row
    # for the dense+veto SAFE-REUSE composite (the approved architecture).
    # It mirrors RTC-REQ-059's gating set + the W2 R1B_INTEGRATED_RUNTIME_PROOF.
    # It does NOT gate on R1B_PRODUCTION_THRESHOLD_PROOF — the W1p4
    # CALIBRATION_GAP finding remains pinned to RTC-REQ-055 only. RTC-REQ-056
    # certifies "the safe-reuse architecture (dense+veto) was driven through
    # a single production integrated-runtime entry point, with the full
    # artifact chain and all 5 W2 verifiers passing", not "dense-only
    # semantic equivalence is calibrated".
    "RTC-REQ-056": {
        "required_proof_depth": "E6_INTEGRATED_RUNTIME_PROOF",
        "scope_flag":           "runtime_certification_claimed",
        "gating_subclaims":     (
            "R1B_INTEGRATED_RUNTIME_PROOF",
            "R1B_SAFE_REUSE_COMPOSITE_PROOF",
            "R1B_APPROVED_MODEL_PROOF",
            "R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF",
            "R1B_NEGATIVE_CONTROL_PROOF",
            "R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF",
            "R1B_TERMINAL_EXIT_PROOF",
        ),
    },
    "RTC-REQ-057": {
        "required_proof_depth": "E7_REAL_OTEL_EXPORT",
        "scope_flag":           "observability_certification_claimed",
        "gating_subclaims":     LEGACY_RTC_REQ_055_SUBCLAIMS + ("R1B_REAL_OTEL_PROOF",),
    },
    "RTC-REQ-058": {
        "required_proof_depth": "E8_REPLAY_DETERMINISM",
        "scope_flag":           "replay_certification_claimed",
        "gating_subclaims":     LEGACY_RTC_REQ_055_SUBCLAIMS + ("R1B_REPLAY_PROOF",),
    },
    # W1p6: new row certifying the approved dense+veto safe-reuse
    # architecture. PASS requires the composite subclaim PLUS each of its
    # material inputs. Legacy R1B_PRODUCTION_THRESHOLD_PROOF is
    # intentionally absent — its role here is candidate generation, which
    # the composite subclaim evaluates via the threshold_sweep_results_with_veto
    # confusion matrix (unsafe_fp_count=0 at configured threshold).
    "RTC-REQ-059": {
        "required_proof_depth": "E5_COMPOSITION_PROOF",
        "scope_flag":           None,
        "gating_subclaims":     (
            "R1B_SAFE_REUSE_COMPOSITE_PROOF",
            "R1B_APPROVED_MODEL_PROOF",
            "R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF",
            "R1B_NEGATIVE_CONTROL_PROOF",
            "R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF",
            "R1B_TERMINAL_EXIT_PROOF",
        ),
    },
}


# ──────────────────────────────────────────────────────────────────────
# Dataclasses
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SubclaimVerdict:
    """One subclaim's declared verdict from the sidecar."""

    subclaim_id: str
    status: str
    evidence_path: str | None = None
    notes: str = ""


@dataclass(frozen=True)
class SidecarLoadResult:
    """Result of loading + validating the sidecar."""

    sidecar_path: Path
    sidecar_present: bool
    """True iff the file exists. False is a valid (advisory) state."""

    schema_version: int
    evaluated_at_utc: str
    evidence_evaluator: str
    scope: dict[str, bool]
    subclaims: dict[str, SubclaimVerdict] = field(default_factory=dict)
    schema_errors: tuple[str, ...] = field(default_factory=tuple)
    """Non-empty when the sidecar exists but is malformed."""

    @property
    def is_valid(self) -> bool:
        """True only when sidecar present AND no schema errors."""
        return self.sidecar_present and not self.schema_errors


@dataclass(frozen=True)
class RowOutcome:
    """Per-row verdict produced by ``compute_row_outcomes``."""

    row_id: str
    required_proof_depth: str
    scope_flag: str | None
    in_scope: bool
    """True iff scope_flag is None or scope[scope_flag] == True."""

    actual_proof_depth: str
    """Set to required_proof_depth on PASS, else E0_REQUIREMENT_TEXT."""

    final_acceptance_status: str
    """One of: PENDING, PARTIAL, BLOCKED, ACCEPTED."""

    acceptance_caveat: str
    blocking_gap: str
    blocking_subclaims: tuple[str, ...] = field(default_factory=tuple)
    soft_blocker_subclaims: tuple[str, ...] = field(default_factory=tuple)
    expected_fail_reason: str = ""


# ──────────────────────────────────────────────────────────────────────
# Sidecar loading + validation
# ──────────────────────────────────────────────────────────────────────


def load_sidecar(path: Path | str) -> SidecarLoadResult:
    """Read + structurally validate the sidecar at ``path``.

    Returns a ``SidecarLoadResult`` with:
      - ``sidecar_present=False`` if file missing (advisory baseline)
      - ``schema_errors`` populated if file present but malformed
      - ``is_valid=True`` only when present + structurally clean

    The verdict computer (``compute_row_outcomes``) then translates
    valid sidecars into per-row outcomes.
    """
    p = Path(path)
    if not p.exists():
        return SidecarLoadResult(
            sidecar_path=p,
            sidecar_present=False,
            schema_version=0,
            evaluated_at_utc="",
            evidence_evaluator="",
            scope={},
            subclaims={},
            schema_errors=(),
        )

    errors: list[str] = []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return SidecarLoadResult(
            sidecar_path=p,
            sidecar_present=True,
            schema_version=0,
            evaluated_at_utc="",
            evidence_evaluator="",
            scope={},
            subclaims={},
            schema_errors=(f"MALFORMED_JSON: {exc.msg} at line {exc.lineno}",),
        )
    if not isinstance(raw, dict):
        return SidecarLoadResult(
            sidecar_path=p,
            sidecar_present=True,
            schema_version=0,
            evaluated_at_utc="",
            evidence_evaluator="",
            scope={},
            subclaims={},
            schema_errors=("MALFORMED_SIDECAR: top-level must be a JSON object",),
        )

    schema_version = raw.get("schema_version")
    if schema_version != 1:
        errors.append(
            f"UNSUPPORTED_SCHEMA_VERSION: expected schema_version=1, got {schema_version!r}"
        )

    evaluated_at = str(raw.get("evaluated_at_utc") or "")
    evaluator = str(raw.get("evidence_evaluator") or "")

    # ── scope object
    scope_raw = raw.get("scope") or {}
    if not isinstance(scope_raw, dict):
        errors.append("MALFORMED_SCOPE: 'scope' must be a JSON object")
        scope_raw = {}
    scope: dict[str, bool] = {}
    for flag in SCOPE_FLAG_TO_CONDITIONAL_SUBCLAIM:
        v = scope_raw.get(flag, False)
        if not isinstance(v, bool):
            errors.append(f"MALFORMED_SCOPE_FLAG: scope.{flag} must be bool, got {v!r}")
            v = False
        scope[flag] = v

    # ── subclaims block
    sub_raw = raw.get("subclaims") or {}
    if not isinstance(sub_raw, dict):
        errors.append("MALFORMED_SUBCLAIMS: 'subclaims' must be a JSON object")
        sub_raw = {}

    verdicts: dict[str, SubclaimVerdict] = {}

    # Validate every declared subclaim
    for sid, entry in sub_raw.items():
        if sid not in ALL_SUBCLAIMS:
            errors.append(f"UNKNOWN_SUBCLAIM: '{sid}' is not in canonical subclaim catalog")
            continue
        if not isinstance(entry, dict):
            errors.append(f"MALFORMED_SUBCLAIM_ENTRY: subclaim '{sid}' must be an object")
            continue
        status = str(entry.get("status") or "").strip()
        if status not in ALLOWED_STATUSES:
            errors.append(
                f"INVALID_SUBCLAIM_STATUS: '{sid}' has status='{status}', "
                f"must be one of {sorted(ALLOWED_STATUSES)}"
            )
            continue
        # Anti-cheat: NOT_APPLICABLE only on conditional subclaims.
        if status == "NOT_APPLICABLE" and sid in CORE_SUBCLAIMS:
            errors.append(
                f"INVALID_NOT_APPLICABLE: core subclaim '{sid}' cannot be NOT_APPLICABLE"
            )
            continue
        # Anti-cheat: NOT_APPLICABLE only when its scope flag is False.
        for flag, conditional_sid in SCOPE_FLAG_TO_CONDITIONAL_SUBCLAIM.items():
            if sid == conditional_sid and status == "NOT_APPLICABLE" and scope.get(flag, False):
                errors.append(
                    f"INVALID_NOT_APPLICABLE_WHEN_SCOPE_CLAIMED: "
                    f"subclaim '{sid}' is NOT_APPLICABLE but scope.{flag}=true"
                )
                continue
        evidence = entry.get("evidence_path")
        evidence_str: str | None = str(evidence) if evidence is not None else None
        notes = str(entry.get("notes") or "")
        verdicts[sid] = SubclaimVerdict(
            subclaim_id=sid,
            status=status,
            evidence_path=evidence_str,
            notes=notes,
        )

    # Anti-cheat: every core subclaim must be present.
    for core in CORE_SUBCLAIMS:
        if core not in verdicts:
            errors.append(f"MISSING_CORE_SUBCLAIM: '{core}' is required but absent")

    # Anti-cheat: when a scope flag is True, its conditional subclaim must be present.
    for flag, conditional_sid in SCOPE_FLAG_TO_CONDITIONAL_SUBCLAIM.items():
        if scope.get(flag, False) and conditional_sid not in verdicts:
            errors.append(
                f"MISSING_CONDITIONAL_SUBCLAIM: '{conditional_sid}' is required because "
                f"scope.{flag}=true but subclaim is absent"
            )

    return SidecarLoadResult(
        sidecar_path=p,
        sidecar_present=True,
        schema_version=int(schema_version) if isinstance(schema_version, int) else 0,
        evaluated_at_utc=evaluated_at,
        evidence_evaluator=evaluator,
        scope=scope,
        subclaims=verdicts,
        schema_errors=tuple(errors),
    )


# ──────────────────────────────────────────────────────────────────────
# Verdict computation
# ──────────────────────────────────────────────────────────────────────


def _gating_status_for(
    gating_ids: tuple[str, ...],
    verdicts: Mapping[str, SubclaimVerdict],
) -> tuple[str, list[str], list[str]]:
    """Return (row_status, hard_blockers, soft_blockers) for a row's gating set.

    Row status mapping:
      - all gating subclaims PASS                       -> ACCEPTED
      - any subclaim missing                             -> BLOCKED
      - any subclaim in HARD_BLOCKER_STATUSES            -> BLOCKED
      - any subclaim in SOFT_BLOCKER_STATUSES            -> PARTIAL
      - any subclaim NOT_APPLICABLE on a gating slot     -> BLOCKED (cannot opt out of a gating subclaim)
      - any subclaim with unrecognized status            -> BLOCKED (defensive)
    """
    hard: list[str] = []
    soft: list[str] = []
    for sid in gating_ids:
        v = verdicts.get(sid)
        if v is None:
            hard.append(f"{sid}:MISSING")
            continue
        s = v.status
        if s == "PASS":
            continue
        if s in HARD_BLOCKER_STATUSES:
            hard.append(f"{sid}:{s}")
        elif s in SOFT_BLOCKER_STATUSES:
            soft.append(f"{sid}:{s}")
        elif s == "NOT_APPLICABLE":
            # NOT_APPLICABLE on a gating-required slot is a hard blocker —
            # gating subclaims cannot be opted out of.
            hard.append(f"{sid}:NOT_APPLICABLE_ON_GATING_SLOT")
        else:
            hard.append(f"{sid}:{s}")
    if hard:
        return "BLOCKED", hard, soft
    if soft:
        return "PARTIAL", hard, soft
    return "ACCEPTED", hard, soft


def compute_row_outcomes(
    load_result: SidecarLoadResult,
) -> dict[str, RowOutcome]:
    """Compute per-row outcomes for the 4 R1B-gated rows.

    When the sidecar is absent or invalid, every row's outcome is BLOCKED
    with a clear ``expected_fail_reason``. When the sidecar is valid,
    outcomes follow the gating rule above.

    Out-of-scope rows (RTC-REQ-056/057/058 when their scope flag is False)
    return an outcome with ``in_scope=False`` and ``final_acceptance_status``
    left as ``"PENDING"`` (the W0 baseline). They do NOT get promoted.
    """
    outcomes: dict[str, RowOutcome] = {}

    # ── Sidecar absent: advisory baseline. Every row stays PENDING.
    # The verifier records this as "no sidecar evidence yet".
    if not load_result.sidecar_present:
        for rid, meta in GATED_ROWS.items():
            outcomes[rid] = RowOutcome(
                row_id=rid,
                required_proof_depth=meta["required_proof_depth"],
                scope_flag=meta["scope_flag"],
                in_scope=meta["scope_flag"] is None,
                actual_proof_depth="E0_REQUIREMENT_TEXT",
                final_acceptance_status="PENDING",
                acceptance_caveat="",
                blocking_gap="",
                expected_fail_reason="SIDECAR_ABSENT",
            )
        return outcomes

    # ── Sidecar malformed: every in-scope row is BLOCKED.
    if load_result.schema_errors:
        gap_text = "; ".join(load_result.schema_errors[:3]) + (
            f" (+{len(load_result.schema_errors) - 3} more)"
            if len(load_result.schema_errors) > 3 else ""
        )
        for rid, meta in GATED_ROWS.items():
            in_scope = meta["scope_flag"] is None or load_result.scope.get(meta["scope_flag"], False)
            outcomes[rid] = RowOutcome(
                row_id=rid,
                required_proof_depth=meta["required_proof_depth"],
                scope_flag=meta["scope_flag"],
                in_scope=in_scope,
                actual_proof_depth="E0_REQUIREMENT_TEXT",
                final_acceptance_status="BLOCKED" if in_scope else "PENDING",
                acceptance_caveat="",
                blocking_gap=f"sidecar malformed: {gap_text}" if in_scope else "",
                expected_fail_reason="SIDECAR_MALFORMED" if in_scope else "OUT_OF_SCOPE",
            )
        return outcomes

    # ── Valid sidecar: per-row gating
    for rid, meta in GATED_ROWS.items():
        scope_flag = meta["scope_flag"]
        in_scope = scope_flag is None or load_result.scope.get(scope_flag, False)

        if not in_scope:
            outcomes[rid] = RowOutcome(
                row_id=rid,
                required_proof_depth=meta["required_proof_depth"],
                scope_flag=scope_flag,
                in_scope=False,
                actual_proof_depth="E0_REQUIREMENT_TEXT",
                final_acceptance_status="PENDING",
                acceptance_caveat="",
                blocking_gap="",
                expected_fail_reason=f"SCOPE_FLAG_{scope_flag}_FALSE",
            )
            continue

        gating: tuple[str, ...] = meta["gating_subclaims"]
        row_status, hard, soft = _gating_status_for(gating, load_result.subclaims)

        if row_status == "ACCEPTED":
            outcomes[rid] = RowOutcome(
                row_id=rid,
                required_proof_depth=meta["required_proof_depth"],
                scope_flag=scope_flag,
                in_scope=True,
                actual_proof_depth=meta["required_proof_depth"],
                final_acceptance_status="ACCEPTED",
                acceptance_caveat="",
                blocking_gap="",
                blocking_subclaims=tuple(hard),
                soft_blocker_subclaims=tuple(soft),
                expected_fail_reason="",
            )
        elif row_status == "PARTIAL":
            caveat = (
                "R1B subclaims with soft blockers prevent ACCEPTED: "
                + ", ".join(soft)
            )
            outcomes[rid] = RowOutcome(
                row_id=rid,
                required_proof_depth=meta["required_proof_depth"],
                scope_flag=scope_flag,
                in_scope=True,
                actual_proof_depth="E0_REQUIREMENT_TEXT",
                final_acceptance_status="PARTIAL",
                acceptance_caveat=caveat,
                blocking_gap="",
                blocking_subclaims=tuple(hard),
                soft_blocker_subclaims=tuple(soft),
                expected_fail_reason="SOFT_BLOCKER_SUBCLAIMS_PRESENT",
            )
        else:  # BLOCKED
            gap = (
                "R1B subclaims with hard blockers prevent acceptance: "
                + ", ".join(hard)
            )
            outcomes[rid] = RowOutcome(
                row_id=rid,
                required_proof_depth=meta["required_proof_depth"],
                scope_flag=scope_flag,
                in_scope=True,
                actual_proof_depth="E0_REQUIREMENT_TEXT",
                final_acceptance_status="BLOCKED",
                acceptance_caveat="",
                blocking_gap=gap,
                blocking_subclaims=tuple(hard),
                soft_blocker_subclaims=tuple(soft),
                expected_fail_reason="HARD_BLOCKER_SUBCLAIMS_PRESENT",
            )

    return outcomes


__all__ = [
    "ALL_SUBCLAIMS",
    "CORE_SUBCLAIMS",
    "LEGACY_RTC_REQ_055_SUBCLAIMS",
    "CONDITIONAL_SUBCLAIMS",
    "ALLOWED_STATUSES",
    "HARD_BLOCKER_STATUSES",
    "SOFT_BLOCKER_STATUSES",
    "SCOPE_FLAG_TO_CONDITIONAL_SUBCLAIM",
    "GATED_ROWS",
    "SubclaimVerdict",
    "SidecarLoadResult",
    "RowOutcome",
    "load_sidecar",
    "compute_row_outcomes",
]
