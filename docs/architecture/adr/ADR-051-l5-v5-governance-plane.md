# ADR-051: L5 v5 Governance Plane

- Status: Accepted
- Date: 2026-04-25
- Deciders: Codex (under Author-Gate auto-recommendation), Amit
- Related ADRs: ADR-049 (v4), ADR-023 (runtime HITL), ADR-049 children
- Spec source: `docs/reference/00_L5_Policy_Plane/Governance & Safety v5.md`
- Implementation plan: `.codex/plans/l5-v5-governance-implementation-7d3a91.md`

## Context

v5 of the Governance & Safety document expands v4 with explicit primitives that v4 either implied or scattered across helpers:

1. **Entry contract (G0).** Seven packet kinds (`RequestEnvelope`, `L1PlanContract`, `L0RouteContract`, `L3StepContract`, `L2ExecutionRequest`, `HITLReentryPacket`, `ExitDispositionRequest`) and a fast-reject set.
2. **Triage (G1).** A 5-mode × 4-band × 4-depth lattice with explicit `triage_flags` and a `next_lane` selector.
3. **CRITICAL** risk tier (v4 only had LOW/MODERATE/HIGH).
4. **Origin-trust labeling (G2a)** with 9 origin labels and 5 boundary classifications.
5. **Decision Rail** explicitly named: `REJECT | REMEDIATE | ESCALATE | CERTIFY` with a 19-element reason-code taxonomy.
6. **GovernanceResult** wire shape carrying every report + capability_token + sandbox_envelope + replay_envelope + standards_fingerprint + audit_log + downstream_disposition.
7. **Out-of-band invariant.** No calibration / assurance / audit-forensic plane mutates the current run.

## Decision

Add a new package `agentic_core/L5_safety/v5/` that:

- Adds the v5-specific types (`RiskTierBandV5`, `GovernanceMode`, `ReviewDepth`, `OriginLabel`, `BoundaryClassification`, `DecisionVerdict`, `ReasonCode`, `SideEffectClass`, `NextLane`, `TriageFlag`, `PacketKind`, `StandardsTag`).
- Defines the v5 wire dataclasses (`GovernanceReviewRequest`, `TriageReport`, `OriginTrustManifest`, `CapabilityTokenV5`, `SandboxEnvelope`, `ReplayEnvelope`, `StandardsFingerprint`, `GovernanceResult`).
- Provides four small, deterministic functions that map each spec section to code:
  - `g0_entry.validate_entry_packet` (G0)
  - `g1_triage.triage_request` (G1)
  - `g2a_origin_trust.classify_origins` (G2a)
  - `decision_rail.emit_verdict` (Decision Rail)
- Provides a top-level `governance_plane.certify_packet` façade that composes the four steps and the existing v4 `evaluate_runtime_lane` (when a v4 token is supplied).
- Provides `replay_audit.seal_replay_envelope` for canonical JSON hash sealing.
- Provides `out_of_band_invariants.assert_no_current_run_mutation` as an API guard for any out-of-band component that touches a frozen `GovernanceResult`.

The v5 package is **additive** — v4 call sites continue to use `evaluate_runtime_lane`, and v5 callers wrap that result inside a `GovernanceResult`.

## Alternatives Considered

1. **Modify v4 in place.** Rejected — too many existing call sites depend on v4 shapes (`RuntimeLaneDecision`, `final_action` string).
2. **Extend `RiskTierBand` literal in `principal_chain_types`.** Rejected — would silently broaden the v4 contract; CRITICAL is a v5-only concept that maps to either `HIGH` + `LOCKDOWN` review_depth or directly to `REJECT`.
3. **Treat v5 as documentation only.** Rejected — the user requested gap implementation.

## Consequences

### Positive
- Every numbered section of the v5 spec maps to an importable artifact.
- Zero churn to existing v4 call sites.
- Decision rail and reason codes become enumerable and testable.

### Negative
- Two coexisting governance shapes (v4 `RuntimeLaneDecision`, v5 `GovernanceResult`) until call sites migrate.
- v5 façade re-evaluates some v4 reports (acceptable — they are pure functions).

### Migration path
- New code targeting v5 entry contract calls `governance_plane.certify_packet`.
- Existing v4 call sites unchanged.
- A future ADR may sunset v4 once all callers migrate.

## Implementation

See `.codex/plans/l5-v5-governance-implementation-7d3a91.md` for the wave structure and per-phase scope.
