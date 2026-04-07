"""Deterministic judges — ADG-powered evaluation without LLM calls.

Each judge consumes an EvidenceBundle and produces a JudgeVerdict.
All scoring is deterministic and reproducible.

Judges implemented:
- ARCH-001: Layer boundary compliance
- QUAL-001: Anti-pattern density
- QUAL-002: Cyclomatic complexity proxy (call fanout)
- DEP-001: Circular dependency detection
- COV-001: Governance edge coverage
- GOV-002: Write governance compliance (UWG)
- SEC-002: Import security
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from agentic_core.evaluation.judges.types import (
    EvidenceBundle,
    EvidenceItem,
    JudgeVerdict,
    VerdictOutcome,
)

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Layer ordering for ARCH-001
# ---------------------------------------------------------------------------
_LAYER_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}

# ---------------------------------------------------------------------------
# Governance dimensions for COV-001
# ---------------------------------------------------------------------------
_P0_GOVERNANCE_DIMS = frozenset(
    {
        "records_execution_trace",
        "applies_guardrail",
        "reads_policy_state",
        "signs_execution_trace",
        "snapshots_state",
        "emits_replay_key",
        "emits_determinism_digest",
    },
)

# ---------------------------------------------------------------------------
# Forbidden imports for SEC-002
# ---------------------------------------------------------------------------
_FORBIDDEN_IMPORTS = frozenset(
    {
        "subprocess",
        "os.system",
        "shutil.rmtree",
        "ctypes",
        "pickle",
    },
)

_IMPORT_ALLOWLIST_PATHS = frozenset(
    {
        "ops_scripts/",
        "tools/",
        "tests/",
    },
)


def _verdict_id() -> str:
    """Generate a short deterministic-friendly verdict ID."""
    return uuid.uuid4().hex[:12]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ===================================================================
# ARCH-001: Layer Boundary Compliance
# ===================================================================


def judge_arch_001(bundle: EvidenceBundle) -> JudgeVerdict:
    """Check that a module only imports from layers at or below its own level."""
    module_layer = bundle.module_metadata.get("layer", "")
    module_level = _LAYER_ORDER.get(module_layer, -1)

    import_edges = bundle.adg_edges.get("imports", [])
    if not import_edges:
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="architecture",
            rubric_id="ARCH-001",
            outcome=VerdictOutcome.SKIP.value,
            score=1.0,
            reasoning="No import edges found in ADG evidence",
            severity="CRITICAL",
            adg_digest=bundle.adg_digest,
            provider_id="deterministic",
            evidence_hash=bundle.evidence_hash,
            created_at=_now_iso(),
        )

    if module_level < 0:
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="architecture",
            rubric_id="ARCH-001",
            outcome=VerdictOutcome.SKIP.value,
            score=1.0,
            reasoning=f"Module layer '{module_layer}' not in layer hierarchy",
            severity="CRITICAL",
            adg_digest=bundle.adg_digest,
            provider_id="deterministic",
            evidence_hash=bundle.evidence_hash,
            created_at=_now_iso(),
        )

    violations: list[EvidenceItem] = []
    total = 0

    for edge in import_edges:
        target_layer = edge.get("target_layer", "")
        target_level = _LAYER_ORDER.get(target_layer, -1)
        if target_level < 0:
            continue
        total += 1
        if target_level > module_level:
            violations.append(
                EvidenceItem(
                    evidence_type="layer_violation",
                    key=f"{module_layer}->{target_layer}",
                    value=json.dumps(
                        {
                            "target": edge.get("target_name", ""),
                            "target_layer": target_layer,
                            "source_file": edge.get("source_file", ""),
                            "line_no": edge.get("line_no", 0),
                        },
                    ),
                    file_path=edge.get("source_file", ""),
                    line_no=edge.get("line_no", 0),
                ),
            )

    if total == 0:
        score = 1.0
    else:
        score = round((total - len(violations)) / total, 4)

    if score >= 1.0:
        outcome = VerdictOutcome.PASS.value
    elif score >= 0.95:
        outcome = VerdictOutcome.WARN.value
    else:
        outcome = VerdictOutcome.FAIL.value

    suggestions = []
    if violations:
        suggestions.append(
            f"Fix {len(violations)} layer boundary violation(s): "
            f"{module_layer} should not import from higher layers",
        )

    return JudgeVerdict(
        verdict_id=_verdict_id(),
        target=bundle.target,
        dimension="architecture",
        rubric_id="ARCH-001",
        outcome=outcome,
        score=score,
        reasoning=f"{total - len(violations)}/{total} imports comply with layer boundaries",
        evidence_items=tuple(violations),
        suggestions=tuple(suggestions),
        severity="CRITICAL",
        adg_digest=bundle.adg_digest,
        provider_id="deterministic",
        evidence_hash=bundle.evidence_hash,
        created_at=_now_iso(),
    )


# ===================================================================
# QUAL-001: Anti-Pattern Density
# ===================================================================


def judge_qual_001(bundle: EvidenceBundle) -> JudgeVerdict:
    """Measure anti-pattern violations per module."""
    antipattern_edges = bundle.adg_edges.get("antipattern", [])
    violates_edges = bundle.adg_edges.get("violates", [])
    violation_count = len(antipattern_edges) + len(violates_edges)

    threshold = 5.0
    score = round(max(0.0, 1.0 - violation_count / threshold), 4)

    if score >= 0.8:
        outcome = VerdictOutcome.PASS.value
    elif score >= 0.6:
        outcome = VerdictOutcome.WARN.value
    else:
        outcome = VerdictOutcome.FAIL.value

    evidence_items = []
    for edge in antipattern_edges[:10]:
        evidence_items.append(
            EvidenceItem(
                evidence_type="antipattern",
                key=edge.get("symbol", "unknown"),
                value=json.dumps(edge),
                file_path=edge.get("source_file", ""),
                line_no=edge.get("line_no", 0),
            ),
        )

    suggestions = []
    if violation_count > 0:
        suggestions.append(
            f"Reduce {violation_count} anti-pattern violation(s) to improve code quality",
        )

    return JudgeVerdict(
        verdict_id=_verdict_id(),
        target=bundle.target,
        dimension="code_quality",
        rubric_id="QUAL-001",
        outcome=outcome,
        score=score,
        reasoning=f"{violation_count} anti-pattern violation(s) found (threshold: {int(threshold)})",
        evidence_items=tuple(evidence_items),
        suggestions=tuple(suggestions),
        severity="HIGH",
        adg_digest=bundle.adg_digest,
        provider_id="deterministic",
        evidence_hash=bundle.evidence_hash,
        created_at=_now_iso(),
    )


# ===================================================================
# QUAL-002: Cyclomatic Complexity Proxy (Call Fanout)
# ===================================================================


def judge_qual_002(bundle: EvidenceBundle) -> JudgeVerdict:
    """Use ADG call-graph fanout as a complexity proxy."""
    call_edges = bundle.adg_edges.get("calls", [])
    fanout = len(call_edges)

    threshold = 50.0
    score = round(max(0.0, 1.0 - fanout / threshold), 4)

    if score >= 0.6:
        outcome = VerdictOutcome.PASS.value
    elif score >= 0.4:
        outcome = VerdictOutcome.WARN.value
    else:
        outcome = VerdictOutcome.FAIL.value

    suggestions = []
    if fanout > threshold:
        suggestions.append(
            f"Module has {fanout} outgoing calls — consider splitting into smaller modules",
        )

    return JudgeVerdict(
        verdict_id=_verdict_id(),
        target=bundle.target,
        dimension="code_quality",
        rubric_id="QUAL-002",
        outcome=outcome,
        score=score,
        reasoning=f"Call fanout: {fanout} (threshold: {int(threshold)})",
        severity="MEDIUM",
        adg_digest=bundle.adg_digest,
        provider_id="deterministic",
        evidence_hash=bundle.evidence_hash,
        created_at=_now_iso(),
        suggestions=tuple(suggestions),
    )


# ===================================================================
# DEP-001: Circular Dependency Detection
# ===================================================================


def judge_dep_001(bundle: EvidenceBundle) -> JudgeVerdict:
    """Detect if module participates in circular import chains.

    Uses a DFS from this module through its outgoing import edges
    to see if we can reach back to the original module.
    Note: This checks only immediate 2-hop cycles from the bundle's
    import edges. Full cycle detection requires the complete graph.
    """
    import_edges = bundle.adg_edges.get("imports", [])
    if not import_edges:
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="dependency_health",
            rubric_id="DEP-001",
            outcome=VerdictOutcome.PASS.value,
            score=1.0,
            reasoning="No import edges — no cycle possible",
            severity="HIGH",
            adg_digest=bundle.adg_digest,
            provider_id="deterministic",
            evidence_hash=bundle.evidence_hash,
            created_at=_now_iso(),
        )

    # Check if any import target also imports us back (2-hop cycle)
    # We'd need incoming edges for full detection
    incoming_imports = bundle.adg_edges.get("imports_incoming", [])
    our_targets = {e.get("target_name", "") for e in import_edges}
    their_targets = {e.get("source_name", "") for e in incoming_imports}

    cycles = our_targets & their_targets
    cycles.discard("")

    if not cycles:
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="dependency_health",
            rubric_id="DEP-001",
            outcome=VerdictOutcome.PASS.value,
            score=1.0,
            reasoning=f"No circular imports detected among {len(import_edges)} import edges",
            severity="HIGH",
            adg_digest=bundle.adg_digest,
            provider_id="deterministic",
            evidence_hash=bundle.evidence_hash,
            created_at=_now_iso(),
        )

    evidence_items = [
        EvidenceItem(
            evidence_type="circular_import",
            key=cycle_target,
            value=f"{bundle.target} <-> {cycle_target}",
        )
        for cycle_target in sorted(cycles)
    ]

    return JudgeVerdict(
        verdict_id=_verdict_id(),
        target=bundle.target,
        dimension="dependency_health",
        rubric_id="DEP-001",
        outcome=VerdictOutcome.FAIL.value,
        score=0.0,
        reasoning=f"Circular import detected with: {', '.join(sorted(cycles))}",
        evidence_items=tuple(evidence_items),
        suggestions=(f"Break circular dependency with {', '.join(sorted(cycles))}",),
        severity="HIGH",
        adg_digest=bundle.adg_digest,
        provider_id="deterministic",
        evidence_hash=bundle.evidence_hash,
        created_at=_now_iso(),
    )


# ===================================================================
# COV-001: Governance Edge Coverage
# ===================================================================


def judge_cov_001(bundle: EvidenceBundle) -> JudgeVerdict:
    """Measure what fraction of P0 governance dimensions are wired."""
    wired_dims = set()
    for dim in _P0_GOVERNANCE_DIMS:
        if bundle.adg_edges.get(dim):
            wired_dims.add(dim)

    total = len(_P0_GOVERNANCE_DIMS)
    covered = len(wired_dims)
    score = round(covered / total, 4) if total > 0 else 1.0

    if score >= 1.0:
        outcome = VerdictOutcome.PASS.value
    elif score >= 0.85:
        outcome = VerdictOutcome.WARN.value
    else:
        outcome = VerdictOutcome.FAIL.value

    missing = _P0_GOVERNANCE_DIMS - wired_dims
    suggestions = []
    if missing:
        suggestions.append(
            f"Wire missing governance dims: {', '.join(sorted(missing))}",
        )

    evidence_items = [
        EvidenceItem(
            evidence_type="governance_coverage",
            key=dim,
            value="wired" if dim in wired_dims else "missing",
        )
        for dim in sorted(_P0_GOVERNANCE_DIMS)
    ]

    return JudgeVerdict(
        verdict_id=_verdict_id(),
        target=bundle.target,
        dimension="governance_coverage",
        rubric_id="COV-001",
        outcome=outcome,
        score=score,
        reasoning=f"{covered}/{total} P0 governance dimensions wired",
        evidence_items=tuple(evidence_items),
        suggestions=tuple(suggestions),
        severity="HIGH",
        adg_digest=bundle.adg_digest,
        provider_id="deterministic",
        evidence_hash=bundle.evidence_hash,
        created_at=_now_iso(),
    )


# ===================================================================
# GOV-002: Write Governance Compliance (UWG)
# ===================================================================


def judge_gov_002(bundle: EvidenceBundle) -> JudgeVerdict:
    """Check that all writes go through the Universal Write Gateway."""
    uwg_writes = bundle.adg_edges.get("writes_via_uwg", [])
    all_writes = bundle.adg_edges.get("writes_to", [])
    blocks = bundle.adg_edges.get("blocks_direct_write", [])

    total_writes = len(all_writes)
    governed_writes = len(uwg_writes)

    if total_writes == 0:
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="governance_coverage",
            rubric_id="GOV-002",
            outcome=VerdictOutcome.SKIP.value,
            score=1.0,
            reasoning="No write operations detected",
            severity="CRITICAL",
            adg_digest=bundle.adg_digest,
            provider_id="deterministic",
            evidence_hash=bundle.evidence_hash,
            created_at=_now_iso(),
        )

    score = round(governed_writes / max(1, total_writes), 4)

    if score >= 1.0:
        outcome = VerdictOutcome.PASS.value
    elif score >= 0.9:
        outcome = VerdictOutcome.WARN.value
    else:
        outcome = VerdictOutcome.FAIL.value

    suggestions = []
    ungoverned = total_writes - governed_writes
    if ungoverned > 0:
        suggestions.append(
            f"Route {ungoverned} direct write(s) through UniversalWriteGateway",
        )

    return JudgeVerdict(
        verdict_id=_verdict_id(),
        target=bundle.target,
        dimension="governance_coverage",
        rubric_id="GOV-002",
        outcome=outcome,
        score=score,
        reasoning=f"{governed_writes}/{total_writes} writes governed via UWG",
        suggestions=tuple(suggestions),
        severity="CRITICAL",
        adg_digest=bundle.adg_digest,
        provider_id="deterministic",
        evidence_hash=bundle.evidence_hash,
        created_at=_now_iso(),
    )


# ===================================================================
# SEC-002: Import Security
# ===================================================================


def judge_sec_002(bundle: EvidenceBundle) -> JudgeVerdict:
    """Check for forbidden imports outside allowlisted paths."""
    import_edges = bundle.adg_edges.get("imports", [])
    target_path = bundle.target

    # Check if module is in an allowlisted path
    is_allowlisted = any(target_path.startswith(p) for p in _IMPORT_ALLOWLIST_PATHS)

    if is_allowlisted:
        return JudgeVerdict(
            verdict_id=_verdict_id(),
            target=bundle.target,
            dimension="security",
            rubric_id="SEC-002",
            outcome=VerdictOutcome.SKIP.value,
            score=1.0,
            reasoning="Module in allowlisted path — import restrictions relaxed",
            severity="HIGH",
            adg_digest=bundle.adg_digest,
            provider_id="deterministic",
            evidence_hash=bundle.evidence_hash,
            created_at=_now_iso(),
        )

    violations: list[EvidenceItem] = []
    for edge in import_edges:
        target_name = edge.get("target_name", "")
        for forbidden in _FORBIDDEN_IMPORTS:
            if forbidden in target_name:
                violations.append(
                    EvidenceItem(
                        evidence_type="forbidden_import",
                        key=forbidden,
                        value=target_name,
                        file_path=edge.get("source_file", ""),
                        line_no=edge.get("line_no", 0),
                    ),
                )

    score = 1.0 if not violations else 0.0
    outcome = VerdictOutcome.PASS.value if not violations else VerdictOutcome.FAIL.value

    suggestions = []
    if violations:
        forbidden_found = {v.key for v in violations}
        suggestions.append(
            f"Remove forbidden import(s): {', '.join(sorted(forbidden_found))}",
        )

    return JudgeVerdict(
        verdict_id=_verdict_id(),
        target=bundle.target,
        dimension="security",
        rubric_id="SEC-002",
        outcome=outcome,
        score=score,
        reasoning=f"{len(violations)} forbidden import(s) detected"
        if violations
        else "No forbidden imports found",
        evidence_items=tuple(violations),
        suggestions=tuple(suggestions),
        severity="HIGH",
        adg_digest=bundle.adg_digest,
        provider_id="deterministic",
        evidence_hash=bundle.evidence_hash,
        created_at=_now_iso(),
    )


# ===================================================================
# Registry — maps rubric_id to judge function
# ===================================================================

DETERMINISTIC_JUDGES: dict[str, Any] = {
    "ARCH-001": judge_arch_001,
    "QUAL-001": judge_qual_001,
    "QUAL-002": judge_qual_002,
    "DEP-001": judge_dep_001,
    "COV-001": judge_cov_001,
    "GOV-002": judge_gov_002,
    "SEC-002": judge_sec_002,
}


def run_deterministic_judge(rubric_id: str, bundle: EvidenceBundle) -> JudgeVerdict | None:
    """Run a deterministic judge by rubric ID.

    Returns None if rubric_id is not a deterministic judge.
    """
    judge_fn = DETERMINISTIC_JUDGES.get(rubric_id)
    if judge_fn is None:
        return None
    return judge_fn(bundle)


__all__ = [
    "DETERMINISTIC_JUDGES",
    "judge_arch_001",
    "judge_cov_001",
    "judge_dep_001",
    "judge_gov_002",
    "judge_qual_001",
    "judge_qual_002",
    "judge_sec_002",
    "run_deterministic_judge",
]
