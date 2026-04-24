"""Tier 1 span coverage contract for Runtime ADG snapshots.

Plan: `.windsurf/plans/runtime-adg-tier1-trace-binding-c9b84d.md`
Doctrine: `docs/reference/Runtime ADG and OTEL Spans.md`

What this module does
---------------------
Given a `RuntimeADGSnapshot`, report whether it contains each of the 5
Tier 1 span categories that constitute the "correlation spine." Does NOT
emit spans and does NOT mutate anything. Pure read-only validation.

Tier 1 categories (minimum viable runtime ADG)
----------------------------------------------
    1. runtime.trace_root       — "Which execution is this?"
    2. L0.route.select          — "Why did L0 choose this path?"
    3. L2.step.seal             — "What did execution finish with?"
    4. L2.(model|tool).invoke   — "What actually ran?"
    5. Exit.disposition         — "Was it allowed / denied / escalated?"

Why this is a contract, not a test
----------------------------------
Because it runs against EVERY persisted snapshot at production time (when
`strict_tier1=True` is enabled on the store). A snapshot that fails the
contract either (a) reveals an emit-site gap, or (b) reveals a run that
took an unusual path. Either way the operator needs to know.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from system_learning.runtime_adg.snapshot import RuntimeADGNode, RuntimeADGSnapshot

# Signal-based Tier 1 contracts — Tier 1.5 upgrade.
#
# Moving from pure name-substring matching to multi-signal scoring. A node
# matches a category if the sum of satisfied signals >= SIGNAL_THRESHOLD.
# This recognizes production-like spans (e.g. `heal_router.v1.route` is the
# canonical L0.route.select in this codebase — router kind, L0 layer,
# routing.* attrs — even though its name never contains "route.select").


@dataclass(frozen=True, slots=True)
class _CategoryContract:
    """Multi-signal contract for one Tier 1 category."""

    name_patterns: tuple[str, ...]  # substring matched case-insensitive against node.name
    kinds: tuple[str, ...]  # acceptable node.kind values (case-insensitive)
    layers: tuple[str, ...]  # acceptable node.layer prefixes (case-insensitive)
    required_any_attr: tuple[str, ...]  # at least one of these keys must be in attributes_json


# SIGNAL_THRESHOLD=2 means a node must score on at least 2 of 4 signals
# (name / kind / layer / attrs). Tuned empirically: gives `heal_router.v1.route`
# a 4/4 match for L0.route.select, but keeps `test.op` from matching
# anything (name non-matching, kind=tool matches invoke only by itself).
SIGNAL_THRESHOLD: int = 2

_TIER1_CONTRACTS: dict[str, _CategoryContract] = {
    "runtime.trace_root": _CategoryContract(
        name_patterns=(
            "trace_root",
            "runtime.trace",
            "runtime.root",
            "orchestrator.execute",
            "intake.stamp_trace",
        ),
        kinds=("orchestrator", "intake", "trace_root"),
        layers=("u0", "l0"),
        required_any_attr=("trace_id", "run_id", "input_envelope_hash"),
    ),
    "L0.route.select": _CategoryContract(
        name_patterns=(
            "l0.route",
            "route.select",
            "route.contract",
            "router.",
            "heal_router",
            ".v1.route",
        ),
        kinds=("router", "route"),
        layers=("l0",),
        required_any_attr=(
            "selected_route",
            "routing.target_model",
            "route.reason_codes",
            "routing.confidence_score",
            "routing.tier",
            "cache_decision",
        ),
    ),
    "L2.step.seal": _CategoryContract(
        name_patterns=(
            "l2.step.seal",
            "step.seal",
            "execution.seal",
            ".seal",
        ),
        kinds=("seal", "execution"),
        layers=("l2",),
        required_any_attr=(
            "output_hash",
            "output_artifact_ids",
            "lineage_hash",
            "replay_key",
            "evidence_ids",
        ),
    ),
    "L2.invoke": _CategoryContract(
        name_patterns=(
            "l2.model.invoke",
            "l2.tool.invoke",
            "model.invoke",
            "tool.invoke",
            "tool.",
            "model.",
            ".judge",
            "consensus.v1.judge",
        ),
        kinds=("tool", "model", "cognitive", "invoke"),
        layers=("l1", "l2"),
        required_any_attr=(
            "tool_name",
            "model_id",
            "args_hash",
            "prompt_hash",
            "return_code",
            "consensus.verdict",
            "consensus.juror_count",
        ),
    ),
    "Exit.disposition": _CategoryContract(
        name_patterns=(
            "exit.disposition",
            "exit.eval",
            "disposition",
            "exit.allow",
            "exit.deny",
        ),
        kinds=("exit", "disposition", "eval"),
        layers=("l3", "l5"),
        required_any_attr=(
            "exit_disposition",
            "policy_hash",
            "guardrail_result",
            "compliance_hash",
        ),
    ),
}


@dataclass(frozen=True, slots=True)
class _MatchBreakdown:
    """Debug-friendly per-category breakdown of which signals hit."""

    matched_by_name: bool
    matched_by_kind: bool
    matched_by_layer: bool
    matched_by_attrs: bool

    def signal_count(self) -> int:
        return sum(
            [
                int(self.matched_by_name),
                int(self.matched_by_kind),
                int(self.matched_by_layer),
                int(self.matched_by_attrs),
            ]
        )


@dataclass(frozen=True, slots=True)
class Tier1Coverage:
    """Coverage report for one snapshot.

    Attributes
    ----------
    category_present : dict[str, bool]
        Whether each Tier 1 category has at least one matching node.
    category_with_attrs : dict[str, bool]
        Whether at least one matching node for each category also carries
        the required attributes.
    coverage_pct : float
        Fraction of the 5 Tier 1 categories satisfied (with attrs). In [0, 1].
    missing_categories : tuple[str, ...]
        Category names missing at the attrs level.
    """

    category_present: dict[str, bool]
    category_with_attrs: dict[str, bool]
    coverage_pct: float
    missing_categories: tuple[str, ...]

    def is_complete(self) -> bool:
        return self.coverage_pct >= 1.0

    def to_dict(self) -> dict[str, object]:
        return {
            "category_present": dict(self.category_present),
            "category_with_attrs": dict(self.category_with_attrs),
            "coverage_pct": round(self.coverage_pct, 4),
            "missing_categories": list(self.missing_categories),
            "is_complete": self.is_complete(),
        }


def _match_name(node: RuntimeADGNode, patterns: tuple[str, ...]) -> bool:
    name = node.name.lower()
    return any(pat.lower() in name for pat in patterns)


def _match_kind(node: RuntimeADGNode, kinds: tuple[str, ...]) -> bool:
    if not kinds:
        return False
    nk = node.kind.lower()
    return any(nk == k.lower() or nk.startswith(k.lower()) for k in kinds)


def _match_layer(node: RuntimeADGNode, layers: tuple[str, ...]) -> bool:
    if not layers:
        return False
    nl = node.layer.lower()
    return any(nl.startswith(layer.lower()) for layer in layers)


def _match_attrs(node: RuntimeADGNode, required_any: tuple[str, ...]) -> bool:
    if not required_any:
        return False
    if not node.attributes_json:
        return False
    try:
        attrs = json.loads(node.attributes_json)
    except (ValueError, TypeError):
        return False
    if not isinstance(attrs, dict):
        return False
    return any(k in attrs and attrs[k] not in (None, "") for k in required_any)


def _score_node(node: RuntimeADGNode, contract: _CategoryContract) -> _MatchBreakdown:
    return _MatchBreakdown(
        matched_by_name=_match_name(node, contract.name_patterns),
        matched_by_kind=_match_kind(node, contract.kinds),
        matched_by_layer=_match_layer(node, contract.layers),
        matched_by_attrs=_match_attrs(node, contract.required_any_attr),
    )


def validate_tier1_coverage(snapshot: RuntimeADGSnapshot) -> Tier1Coverage:
    """Report Tier 1 span coverage for a snapshot.

    Uses multi-signal matching (name / kind / layer / attrs). A node matches
    a category if `signal_count >= SIGNAL_THRESHOLD`.

    `category_present`  : any node scored >= threshold on name alone (partial)
    `category_with_attrs`: any node scored >= threshold AND had a signature attr
    """
    category_present: dict[str, bool] = {}
    category_with_attrs: dict[str, bool] = {}

    for category, contract in _TIER1_CONTRACTS.items():
        name_hit = False
        full_hit = False
        for node in snapshot.nodes:
            br = _score_node(node, contract)
            if br.signal_count() < SIGNAL_THRESHOLD:
                continue
            name_hit = True
            # A "with_attrs" hit requires attrs to be one of the satisfied
            # signals OR the name to explicitly match (keeping backward-
            # compatibility for cases like L2.invoke where attrs are optional).
            # Full hit if attrs match OR signal count >= 3 (strong multi-signal
            # match even without the signature attribute). Three-of-four
            # signals is an unambiguous production match.
            if br.matched_by_attrs or br.signal_count() >= 3:
                full_hit = True
                break
        category_present[category] = name_hit
        category_with_attrs[category] = full_hit

    total = len(_TIER1_CONTRACTS)
    satisfied = sum(1 for v in category_with_attrs.values() if v)
    pct = satisfied / total if total else 0.0
    missing = tuple(c for c, ok in category_with_attrs.items() if not ok)
    return Tier1Coverage(
        category_present=category_present,
        category_with_attrs=category_with_attrs,
        coverage_pct=pct,
        missing_categories=missing,
    )


# ---------------------------------------------------------------------------
# Corpus-level analysis — distinguishes emit-site gaps from name-mismatches.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CorpusTier1Report:
    """Aggregate Tier 1 report across an entire snapshot corpus.

    Each category is classified as exactly one of:
      - "satisfied"       : at least one snapshot had a full match (name + attrs)
      - "name_mismatch"   : some node matches by signals but no signature attrs
                            are present anywhere — likely a naming/attr-key
                            drift problem, not an emit-site gap
      - "emit_site_gap"   : zero nodes in the entire corpus scored above
                            threshold — this category has no emit site at all,
                            which is a real architectural hole
    """

    snapshots_scanned: int
    nodes_scanned: int
    category_status: dict[str, str]
    category_example_hits: dict[str, tuple[str, ...]]  # up to 3 example span names per satisfied cat
    satisfied_pct: float

    def satisfied_count(self) -> int:
        return sum(1 for s in self.category_status.values() if s == "satisfied")

    def name_mismatch_count(self) -> int:
        return sum(1 for s in self.category_status.values() if s == "name_mismatch")

    def emit_site_gap_count(self) -> int:
        return sum(1 for s in self.category_status.values() if s == "emit_site_gap")

    def to_dict(self) -> dict[str, object]:
        return {
            "snapshots_scanned": self.snapshots_scanned,
            "nodes_scanned": self.nodes_scanned,
            "category_status": dict(self.category_status),
            "category_example_hits": {k: list(v) for k, v in self.category_example_hits.items()},
            "satisfied_pct": round(self.satisfied_pct, 4),
            "satisfied_count": self.satisfied_count(),
            "name_mismatch_count": self.name_mismatch_count(),
            "emit_site_gap_count": self.emit_site_gap_count(),
        }


def validate_tier1_corpus_coverage(
    snapshots: list[RuntimeADGSnapshot],
) -> CorpusTier1Report:
    """Aggregate Tier 1 analysis across a corpus of snapshots.

    A category is:
      - `satisfied` if any node anywhere in the corpus hit `signal_count >= threshold`
        AND had a signature attr (or name-matched a category with no attr requirement)
      - `name_mismatch` if some node scored `>= threshold` but no signature attr
        ever appeared — the signal is there but the data drifted
      - `emit_site_gap` if zero nodes anywhere hit `>= threshold` for this category
    """
    # Per-category counters across the whole corpus.
    any_signal_hit: dict[str, bool] = {c: False for c in _TIER1_CONTRACTS}
    any_full_hit: dict[str, bool] = {c: False for c in _TIER1_CONTRACTS}
    example_hits: dict[str, list[str]] = {c: [] for c in _TIER1_CONTRACTS}

    nodes_scanned = 0
    for snap in snapshots:
        for node in snap.nodes:
            nodes_scanned += 1
            for category, contract in _TIER1_CONTRACTS.items():
                br = _score_node(node, contract)
                if br.signal_count() < SIGNAL_THRESHOLD:
                    continue
                any_signal_hit[category] = True
                full_hit = br.matched_by_attrs or br.signal_count() >= 3
                if full_hit:
                    any_full_hit[category] = True
                    if node.name not in example_hits[category] and len(example_hits[category]) < 3:
                        example_hits[category].append(node.name)

    status: dict[str, str] = {}
    for category in _TIER1_CONTRACTS:
        if any_full_hit[category]:
            status[category] = "satisfied"
        elif any_signal_hit[category]:
            status[category] = "name_mismatch"
        else:
            status[category] = "emit_site_gap"

    satisfied_pct = sum(1 for s in status.values() if s == "satisfied") / max(1, len(status))
    return CorpusTier1Report(
        snapshots_scanned=len(snapshots),
        nodes_scanned=nodes_scanned,
        category_status=status,
        category_example_hits={k: tuple(v) for k, v in example_hits.items()},
        satisfied_pct=satisfied_pct,
    )


__all__ = [
    "Tier1Coverage",
    "CorpusTier1Report",
    "validate_tier1_coverage",
    "validate_tier1_corpus_coverage",
    "SIGNAL_THRESHOLD",
]
