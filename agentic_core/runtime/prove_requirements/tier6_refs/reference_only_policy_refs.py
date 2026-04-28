"""Tier 6 -- 15 NON_BLOCKING_REFERENCE rows static reference module.

Static metadata only. Does not call runtime services, execute tools,
emit OTEL spans, import an OTEL exporter, or mutate runtime state.

Implements the **reference-only policy** for the 15 final-tier
NON_BLOCKING_REFERENCE rows. These rows are documentation / parent /
traceability surfaces, not runtime invariants. The policy refuses to
fabricate runtime fixtures (no fake traces, no fake replay, no fake
OTEL, no fake negative controls). Instead each row is judged by a
documentation-integrity contract:

  * release_gate_rule MUST be NON_BLOCKING_REFERENCE
  * requirement_strength MUST be REFERENCE
  * source_matrix_file MUST exist on disk
  * a reference_only_reason MUST be declared

If those checks pass, the row qualifies as LINKED_LITERAL through the
reference-only contract -- not through fake runtime evidence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Mapping, Tuple

CLUSTER_ID: str = "R"  # R = REFERENCE-only

STEP1_REQ_IDS: Tuple[str, ...] = (
    "REQ-C0-OVERVIEW-REFERENCE-001",
    "REQ-C0-TRACEABILITY-MATRIX-REF-001",
    "REQ-E2E-OVERVIEW-REFERENCE-001",
    "REQ-E2E-REQ-TO-EVIDENCE-COMPILER-001",
    "REQ-EXIT-OVERVIEW-REFERENCE-001",
    "REQ-L0-OVERVIEW-REFERENCE-001",
    "REQ-L1-OVERVIEW-REFERENCE-001",
    "REQ-L2-COVERAGE-MATRIX-REF-001",
    "REQ-L4-OVERVIEW-REFERENCE-001",
    "REQ-L5-V5-COVERAGE-MATRIX-REF-001",
    "REQ-L6-OVERVIEW-REFERENCE-001",
    "REQ-L6-V6-COVERAGE-MATRIX-REF-001",
    "REQ-PA-OVERVIEW-REFERENCE-001",
    "REQ-PA-TRACEABILITY-MATRIX-REF-001",
    "REQ-U0-OVERVIEW-REFERENCE-001",
)

REFERENCE_ONLY_EFR: str = "REFERENCE_ONLY_ROW_NOT_RELEASE_BLOCKING"

REFERENCE_ONLY_REASON_BY_REQ_ID: dict[str, str] = {
    "REQ-C0-OVERVIEW-REFERENCE-001": "C0 parent overview file is a reference parent/child traceability surface; no runtime invariant attached.",
    "REQ-C0-TRACEABILITY-MATRIX-REF-001": "C0 traceability matrix is the parent/child reference surface; no runtime invariant attached.",
    "REQ-E2E-OVERVIEW-REFERENCE-001": "E2E parent overview file is a reference parent/child traceability surface; no runtime invariant attached.",
    "REQ-E2E-REQ-TO-EVIDENCE-COMPILER-001": "Requirements-to-runtime-evidence compiler is the canonical traceability reference for E2E; no runtime invariant attached.",
    "REQ-EXIT-OVERVIEW-REFERENCE-001": "Exit parent overview file is a reference parent/child traceability surface; no runtime invariant attached.",
    "REQ-L0-OVERVIEW-REFERENCE-001": "L0/L3 parent overview file is a reference parent/child traceability surface; no runtime invariant attached.",
    "REQ-L1-OVERVIEW-REFERENCE-001": "L1 reasoning/plan parent overview file is a reference parent/child traceability surface; no runtime invariant attached.",
    "REQ-L2-COVERAGE-MATRIX-REF-001": "L2 coverage matrix is the reference parent/child surface; no claims carried into Step 1.",
    "REQ-L4-OVERVIEW-REFERENCE-001": "L4 state archive parent overview file is a reference parent/child traceability surface; no runtime invariant attached.",
    "REQ-L5-V5-COVERAGE-MATRIX-REF-001": "v5 coverage matrix is referenced as the L5 traceability surface; no claims carried into Step 1.",
    "REQ-L6-OVERVIEW-REFERENCE-001": "L6 parent overview file is a reference parent/child traceability surface; no runtime invariant attached.",
    "REQ-L6-V6-COVERAGE-MATRIX-REF-001": "v6 coverage matrix is the reference parent/child surface; no claims carried into Step 1.",
    "REQ-PA-OVERVIEW-REFERENCE-001": "PA parent overview file is a reference parent/child traceability surface; no runtime invariant attached.",
    "REQ-PA-TRACEABILITY-MATRIX-REF-001": "PA traceability matrix is the parent/child reference surface; no runtime invariant attached.",
    "REQ-U0-OVERVIEW-REFERENCE-001": "U0 request intake parent overview file is a reference parent/child traceability surface; no runtime invariant attached.",
}

REQUIRED_REFERENCE_FIELDS_BY_REQ_ID: dict[str, Tuple[str, ...]] = {
    rid: ("step1_req_id", "source_matrix_file", "release_gate_rule", "requirement_strength")
    for rid in STEP1_REQ_IDS
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def validate_reference_only_contract(req_id: str, row: Mapping[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a Tier 6 NON_BLOCKING_REFERENCE row against the reference-only contract.

    Pure function; no I/O beyond a single Path.is_file() check on the
    source matrix file. No runtime, no OTEL. Returns ``(ok, errors)``.
    """
    errors: List[str] = []
    if req_id not in STEP1_REQ_IDS:
        errors.append(f"req_id {req_id!r} not in REFERENCE-only STEP1_REQ_IDS")
        return (False, errors)
    if row.get("step1_req_id") != req_id:
        errors.append(f"step1_req_id mismatch: got {row.get('step1_req_id')!r} expected {req_id!r}")
    if row.get("release_gate_rule") != "NON_BLOCKING_REFERENCE":
        errors.append(
            f"release_gate_rule must be NON_BLOCKING_REFERENCE, got {row.get('release_gate_rule')!r}"
        )
    if row.get("requirement_strength") != "REFERENCE":
        errors.append(f"requirement_strength must be REFERENCE, got {row.get('requirement_strength')!r}")
    matrix_rel = row.get("source_matrix_file") or ""
    if not matrix_rel:
        errors.append("source_matrix_file missing")
    else:
        matrix_path = _repo_root() / "docs" / "reference" / "contracts" / "step1" / matrix_rel
        if not matrix_path.is_file():
            errors.append(f"source_matrix_file does not exist on disk: {matrix_rel}")
    if not REFERENCE_ONLY_REASON_BY_REQ_ID.get(req_id, "").strip():
        errors.append(f"reference_only_reason missing for {req_id}")
    return (not errors, errors)
