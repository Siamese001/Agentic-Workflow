"""PA Invariants Checker (spec lines 1896-1929).

Encodes the 30 PA invariants from the spec as deterministic predicates.
Each invariant returns an :class:`InvariantResult` and the aggregate
:func:`check_invariants` returns an :class:`InvariantReport` listing every
violation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class InvariantResult:
    invariant_id: str
    description: str
    held: bool
    detail: str = ""


@dataclass(frozen=True)
class InvariantReport:
    results: tuple[InvariantResult, ...]
    violations: tuple[InvariantResult, ...]

    @property
    def all_held(self) -> bool:
        return not self.violations


# ---------------------------------------------------------------------------
# Individual invariants — labelled INV-01 .. INV-30
# ---------------------------------------------------------------------------


def _inv(id_: str, desc: str, held: bool, detail: str = "") -> InvariantResult:
    return InvariantResult(id_, desc, held, detail if not held else "")


def check_invariants(ctx: Mapping[str, Any]) -> InvariantReport:
    """Run all 30 invariants against a flat context dict.

    Expected keys (all optional; missing keys are treated as benign):

        boundary_status                   str
        bom_valid                         bool
        bom_slots_missing                 tuple[str, ...]
        s0_present                        bool
        s0_user_supplied                  bool
        d0_present                        bool
        d0_includes_rc_controls           bool
        c0_present                        bool
        u0_origin_trust                   str
        u0_disposition                    str
        h0_present                        bool
        h0_accepted                       bool
        h0_overrides_d0                   bool
        c0_overrides_s0                   bool
        u0_overrides_s0                   bool
        contradictions_present            bool
        contradictions_preserved          bool
        grounding_required                bool
        evidence_present                  bool
        evidence_status                   str
        support_score                     float
        support_threshold                 float
        r0_parseable                      bool
        r0_can_abstain                    bool
        r0_can_cite                       bool
        citation_required                 bool
        tools_present                     bool
        tools_in_registry                 bool
        tools_allowed_by_token            bool
        capability_token_present          bool
        policy_hashes                     tuple[str, ...]
        blueprint_hashes                  tuple[str, ...]
        replay_key_present                bool
        manifest_hash_present             bool
        signature_present                 bool
        budget_overflow                   bool
        token_budget_respected            bool
        dispatch_allowed                  bool
        events_emitted                    tuple[str, ...]
        spans_emitted                     tuple[str, ...]
        executable_requested              bool
        hitl_required                     bool
        provider_lane                     str
        provider_lanes_supported          tuple[str, ...]
    """
    g = ctx.get
    results: list[InvariantResult] = []

    # Identity / authority --------------------------------------------------
    results.append(
        _inv(
            "INV-01",
            "S0 must be present",
            bool(g("s0_present", True)),
        )
    )
    results.append(
        _inv(
            "INV-02",
            "S0 must never be user-supplied",
            not bool(g("s0_user_supplied", False)),
        )
    )
    results.append(
        _inv(
            "INV-03",
            "D0 must be present",
            bool(g("d0_present", True)),
        )
    )
    results.append(
        _inv(
            "INV-04",
            "D0 must include retrieved-content controls when C0 is present",
            not bool(g("c0_present", False)) or bool(g("d0_includes_rc_controls", True)),
        )
    )
    results.append(
        _inv(
            "INV-05",
            "C0 must never override S0",
            not bool(g("c0_overrides_s0", False)),
        )
    )
    results.append(
        _inv(
            "INV-06",
            "U0 must never override S0",
            not bool(g("u0_overrides_s0", False)),
        )
    )
    results.append(
        _inv(
            "INV-07",
            "H0 must never override D0 fences",
            not bool(g("h0_overrides_d0", False)),
        )
    )
    results.append(
        _inv(
            "INV-08",
            "U0 origin_trust must equal user_turn",
            g("u0_origin_trust", "user_turn") == "user_turn",
        )
    )

    # Evidence --------------------------------------------------------------
    results.append(
        _inv(
            "INV-09",
            "Grounding required implies evidence present",
            not bool(g("grounding_required", False)) or bool(g("evidence_present", True)),
        )
    )
    results.append(
        _inv(
            "INV-10",
            "Grounding required implies evidence_status not in {BLOCKED, EMPTY}",
            not bool(g("grounding_required", False))
            or g("evidence_status", "PASS") not in {"BLOCKED", "EMPTY"},
        )
    )
    results.append(
        _inv(
            "INV-11",
            "Contradictions present implies preservation",
            not bool(g("contradictions_present", False)) or bool(g("contradictions_preserved", True)),
        )
    )
    results.append(
        _inv(
            "INV-12",
            "Support score >= threshold when grounding required",
            not bool(g("grounding_required", False))
            or float(g("support_score", 1.0)) >= float(g("support_threshold", 0.0)),
        )
    )

    # Schema / tools --------------------------------------------------------
    results.append(
        _inv(
            "INV-13",
            "R0 must be parseable",
            bool(g("r0_parseable", True)),
        )
    )
    results.append(
        _inv(
            "INV-14",
            "R0 must support abstain when grounding required",
            not bool(g("grounding_required", False)) or bool(g("r0_can_abstain", True)),
        )
    )
    results.append(
        _inv(
            "INV-15",
            "R0 must support citations when citations required",
            not bool(g("citation_required", False)) or bool(g("r0_can_cite", True)),
        )
    )
    results.append(
        _inv(
            "INV-16",
            "Bound tools must all be in registry",
            not bool(g("tools_present", False)) or bool(g("tools_in_registry", True)),
        )
    )
    results.append(
        _inv(
            "INV-17",
            "Bound tools must all be allowed by capability token",
            not bool(g("tools_present", False)) or bool(g("tools_allowed_by_token", True)),
        )
    )
    results.append(
        _inv(
            "INV-18",
            "Capability token present when tools bound",
            not bool(g("tools_present", False)) or bool(g("capability_token_present", True)),
        )
    )

    # Replay / signature ----------------------------------------------------
    policy_hashes = tuple(g("policy_hashes", ()) or ())
    distinct_p = {h for h in policy_hashes if h}
    results.append(
        _inv(
            "INV-19",
            "Policy hash consistent across all inputs",
            len(distinct_p) <= 1,
            detail=("distinct: " + ",".join(sorted(distinct_p))),
        )
    )
    blueprint_hashes = tuple(g("blueprint_hashes", ()) or ())
    distinct_b = {h for h in blueprint_hashes if h}
    results.append(
        _inv(
            "INV-20",
            "Blueprint hash consistent",
            len(distinct_b) <= 1,
            detail=("distinct: " + ",".join(sorted(distinct_b))),
        )
    )
    results.append(
        _inv(
            "INV-21",
            "Replay key present",
            bool(g("replay_key_present", True)),
        )
    )
    results.append(
        _inv(
            "INV-22",
            "Manifest hash present",
            bool(g("manifest_hash_present", True)),
        )
    )
    results.append(
        _inv(
            "INV-23",
            "Signature present",
            bool(g("signature_present", True)),
        )
    )

    # Budget ----------------------------------------------------------------
    results.append(
        _inv(
            "INV-24",
            "Budget overflow implies dispatch not allowed",
            not bool(g("budget_overflow", False)) or not bool(g("dispatch_allowed", False)),
        )
    )
    results.append(
        _inv(
            "INV-25",
            "Token budget respected when dispatched",
            not bool(g("dispatch_allowed", False)) or bool(g("token_budget_respected", True)),
        )
    )

    # Observability ---------------------------------------------------------
    events = tuple(g("events_emitted", ()) or ())
    results.append(
        _inv(
            "INV-26",
            "PromptAssemblyStarted is the first event",
            not events or events[0] == "PromptAssemblyStarted",
        )
    )
    final_event_ok = not events or events[-1] in {"PromptAssemblyDispatched", "PromptAssemblyBlocked"}
    results.append(
        _inv(
            "INV-27",
            "Final event is Dispatched or Blocked",
            final_event_ok,
        )
    )
    spans = tuple(g("spans_emitted", ()) or ())
    results.append(
        _inv(
            "INV-28",
            "All emitted spans are PA-prefixed",
            all(s.startswith("prompt_assembly.") for s in spans),
        )
    )

    # Governance / HITL -----------------------------------------------------
    results.append(
        _inv(
            "INV-29",
            "HITL required implies executable_requested False",
            not bool(g("hitl_required", False)) or not bool(g("executable_requested", False)),
        )
    )

    # Provider lane ---------------------------------------------------------
    lanes = tuple(g("provider_lanes_supported", ()) or ())
    lane = g("provider_lane", "")
    results.append(
        _inv(
            "INV-30",
            "Provider lane is in supported set when set",
            not lane or not lanes or lane in lanes,
        )
    )

    violations = tuple(r for r in results if not r.held)
    return InvariantReport(results=tuple(results), violations=violations)


__all__ = [
    "InvariantReport",
    "InvariantResult",
    "check_invariants",
]
