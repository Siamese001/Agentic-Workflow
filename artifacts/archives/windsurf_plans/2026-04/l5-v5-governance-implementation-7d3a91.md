# L5 v5 Governance Plane — Gap Implementation Plan

Status: In-progress
Source spec: `docs/reference/00_L5_Policy_Plane/Governance & Safety v5.md`
Predecessor: ADR-049 (v4) — `docs/architecture/adr/ADR-049-l5-v4-governance-plane.md`
ADR (this plan): `docs/architecture/adr/ADR-051-l5-v5-governance-plane.md`

## Background

v5 spec extends v4 with explicit:
- **G0** GovernanceReviewRequest entry contract with packet types and fast-reject conditions.
- **G1** triage layer: governance_mode × risk_tier_band × review_depth × triage_flags × next_lane.
- **G2a** Origin-Trust labeling and content boundary classification (9 origin labels).
- **CRITICAL** risk tier (v4 only had LOW/MODERATE/HIGH).
- Explicit **Decision Rail** verdicts: REJECT | REMEDIATE | ESCALATE | CERTIFY with full reason-code taxonomy.
- **GovernanceResult** wire shape combining all reports + capability_token + sandbox_envelope + replay_envelope + standards_fingerprint.
- **Out-of-band invariants** asserted at API boundary (no current-run mutation from learning planes).

The existing v4 implementation under `agentic_core/L5_safety/identity/` (`runtime_rails.py`, `runtime_entry.py`, `out_of_band_planes.py`, `principal_verifier.py`, `guardrail_bank.py`) covers R1–R8 partially. This plan adds a v5 façade package that:

1. Adds the v5-specific primitives missing from v4.
2. Wraps the existing v4 runtime-lane composer rather than replacing it.
3. Emits the v5 GovernanceResult wire shape required by the spec.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1   | W1.1, W1.2 | Foundation types + contracts | ~3000 | v4 PrincipalChain + CapabilityTokenV4Artifact stable | Done | Importable enums and frozen dataclasses with `to_dict` |
| W2   | W2.1, W2.2, W2.3 | G0 entry / G1 triage / G2a origin-trust | ~3500 | Inputs are dict-like packets | Done | Functions return immutable reports |
| W3   | W3.1, W3.2, W3.3 | Decision rail / replay sealing / OOB invariants | ~3000 | Reports composable | Done | Verdict deterministic; replay envelope hashable |
| W4   | W4.1 | Top-level governance_plane.certify_packet façade + __init__ | ~1500 | Composes W1–W3 | Done | Single entrypoint returns GovernanceResult |
| W5   | W5.1 | Unit tests covering invariants + happy/reject/escalate paths | ~3000 | pytest available | Done | All tests pass |
| W6   | W6.1 | Reharden — py_compile + targeted pytest | ~500 | tests/unit collection healthy | Done | rc=0 on compile + pytest |
| W7   | W7.1 | Commit + push (scoped to plan files) | ~300 | git clean for unrelated work | Done | origin/main contains v5 artifacts |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Enum types | `agentic_core/L5_safety/v5/types.py` | CRITICAL band; broader enum surface than v4 | ~1500 | Done |
| W1.2 | Dataclass contracts | `agentic_core/L5_safety/v5/contracts.py` | Replay envelope hash binding; standards_fingerprint shape | ~1500 | Done |
| W2.1 | G0 entry | `agentic_core/L5_safety/v5/g0_entry.py` | Fast-reject conditions exhaustive | ~1500 | Done |
| W2.2 | G1 triage | `agentic_core/L5_safety/v5/g1_triage.py` | Mode × band × depth deterministic table | ~1000 | Done |
| W2.3 | G2a origin-trust | `agentic_core/L5_safety/v5/g2a_origin_trust.py` | Quarantine pattern set | ~1000 | Done |
| W3.1 | Decision rail | `agentic_core/L5_safety/v5/decision_rail.py` | Hard-stop precedence; remediate-forbidden when hard_constraint | ~1500 | Done |
| W3.2 | Replay sealing | `agentic_core/L5_safety/v5/replay_audit.py` | Canonical JSON hash | ~1000 | Done |
| W3.3 | Out-of-band invariants | `agentic_core/L5_safety/v5/out_of_band_invariants.py` | Promotion gate guard | ~500 | Done |
| W4.1 | Governance plane façade | `agentic_core/L5_safety/v5/governance_plane.py` + `__init__.py` | Compose W1–W3 cleanly | ~1500 | Done |
| W5.1 | Tests | `tests/unit/agentic_core/L5_safety/v5/test_*.py` | Cover all reason_codes + invariants | ~3000 | Done |

## Gap Register (vs v5 spec)

| Spec section | Gap | Resolution |
|--------------|-----|------------|
| G0 packet types | No formal entry validator | `g0_entry.validate_entry_packet` |
| G1 governance_mode | Implicit only | `g1_triage.triage_request` |
| G1 review_depth | Not surfaced | `ReviewDepth` enum + table |
| G1 risk band CRITICAL | Missing in v4 literal | `RiskTierBandV5` |
| G2a origin labels | Partial | 9-label `OriginLabel` enum + classifier |
| G2a quarantine | Not surfaced | `BoundaryClassification` + pattern detector |
| Decision rail | Composed implicitly via `final_action` string | Explicit `DecisionVerdict` + reason codes |
| GovernanceResult | No wire shape | `GovernanceResult` dataclass with `to_dict` |
| Replay envelope | Partial via audit_binding | `ReplayEnvelope` w/ canonical hash |
| Standards fingerprint | Missing | `StandardsFingerprint` struct |
| OOB no-mutation invariant | Implicit | `assert_no_current_run_mutation` API guard |

## Non-goals
- Not replacing existing v4 runtime_entry.evaluate_runtime_lane.
- Not changing existing call sites; v5 is additive façade.
- Not modifying capability_token_v4_types schema.
