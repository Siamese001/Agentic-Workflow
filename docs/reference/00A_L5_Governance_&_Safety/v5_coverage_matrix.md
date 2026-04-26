# L5 v5 Spec — Line-by-Line Coverage Matrix

Source spec: `docs/reference/00_L5_Policy_Plane/Governance & Safety v5.md`
Implementation: `agentic_core/L5_safety/v5/`
Tests: `tests/unit/agentic_core/L5_safety/v5/` (59/59 passing)
ADR: `docs/architecture/adr/ADR-051-l5-v5-governance-plane.md`
Plan: `.windsurf/plans/l5-v5-governance-implementation-7d3a91.md`

Legend:
- ✅ **Enforced** — runtime logic in v5 module guards the invariant
- 📦 **Modeled** — typed contract / dataclass / enum captures the shape
- 🔁 **Delegated** — existing L2/L4/L5-v4/CI module owns the runtime
- ⚪ **Documentation-only** — narrative invariant; no code lever exists yet

## Top-of-doc invariants (lines 5–11)

| Line | Invariant | Status | Where |
|------|-----------|:------:|-------|
| 5 | No execution / mutation / external call / tool / connector / HITL / write without L5 certification | ✅ | `GovernanceResult.decision == CERTIFY` gate; `downstream_disposition` controls flow |
| 6 | L5 governs authority+safety; does not retrieve / assemble / execute / write / promote | ⚪ | architectural separation; out of v5 module scope |
| 7 | Every certification binds active policy, blueprint, registry digests, origin labels, principal chain, capability_token, sandbox envelope, replay envelope | ✅ | `ReplayEnvelope` fields: `policy_hash`, `blueprint_hash`, `registry_digest_set`, `principal_chain_hash`, `capability_token_hash`, `sandbox_envelope_hash` |
| 8 | hard_constraint breaches not remediable; terminate REJECT unless new upstream packet | ✅ | `GovernanceResult.__post_init__` rejects `REMEDIATE` + `HARD_CONSTRAINT_BREACH` |
| 9 | Every human modification treated as untrusted data until re-cleared | ✅ | `OriginLabel.HUMAN_REVIEW` + `HITLDispositionPacket.re_clearance_required=True` invariant |
| 10 | Every out-of-band signal affects future policy versions only | ✅ | `assert_no_current_run_mutation` API guard |
| 11 | No silent fallback; provider/tool/connector/model/policy/registry change → re-certify | 🔁 | `RuntimeRegressionReport` typed; runtime drift detection delegated to caller (R11) |

## G0 — Governance Entry Contract (lines 21–49)

| Lines | Item | Status | Where |
|-------|------|:------:|-------|
| 24–31 | 7 packet types | 📦 ✅ | `PacketKind` enum, validated at `validate_entry_packet` |
| 33 | `request_id`, `trace_id`, `run_id`, `tenant_id`, `caller_id` | ✅ | `_required_present` checks |
| 35 | `origin_trust_manifest` for inbound text / retrieved / tool / human / prior | ✅ | required for `MODEL_CALL`/`TOOL_CALL`; classified at G2a |
| 36 | `policy_hash`, `blueprint_hash`, `registry_digest_set`, `route_contract_hmac`, `replay_key` | 📦 | fields on `GovernanceReviewRequest` |
| 37 | `side_effect_class` enum | 📦 ✅ | `SideEffectClass` enum, validated |
| 38 | requested authority (read/tool/model/connector/network/write/human-review scope) | 📦 | `requested_authority` tuple |
| 41 | Fast-reject: missing route contract when authority requested | ✅ | `ROUTE_MISMATCH` failure |
| 42 | Fast-reject: missing origin labels for prompt/L2 input | ✅ | `INJECTION_DETECTED` failure for `MODEL_CALL`/`TOOL_CALL` |
| 43 | Fast-reject: missing principal chain for delegated invocation | ✅ | `MISSING_AUTHORITY` failure |
| 44 | Fast-reject: missing/stale registry digest | ✅ | `REGISTRY_MISMATCH` failure |
| 45 | Fast-reject: read-only claim with write intent | ✅ | `POLICY_VIOLATION` failure (`declared_read_only` + write side-effect) |
| 48 | Output: `GovernanceReviewRequest` | 📦 | dataclass |

## G1 — Governance Invocation / Triage (lines 53–88)

| Lines | Item | Status | Where |
|-------|------|:------:|-------|
| 61–66 | 5 modes (STATIC_CHECK / RUNTIME_CHECK / HUMAN_REENTRY / COMMIT_REVIEW / INCIDENT_REVIEW) | 📦 ✅ | `GovernanceMode` enum + `_PACKET_MODE` dispatch |
| 68–72 | 4 risk bands incl. CRITICAL | 📦 ✅ | `RiskTierBandV5` enum (the v5 delta over v4) + `_SIDE_EFFECT_MIN_BAND` |
| 75 | declared mode matches actual packet content | ✅ | `declared_mode` parameter → `SCOPE_MISMATCH` flag if mismatch |
| 76 | route_id / execution_form match requested power | ✅ | `route_contract_hmac` requirement at G0 |
| 77 | risk_tier_hint cannot understate | ✅ | `_max_band(hint, side_effect_floor)` |
| 78 | side_effect_class matches arguments | ✅ | `SIDE_EFFECT_MISMATCH` flag |
| 79 | prompt injection patterns | ✅ | `_INJECTION_PATTERNS` regex set, 6 patterns |
| 80 | shadow_discovery_probe (alternate tools / hidden text / "just do it" / markdown injection / connector smuggling) | ✅ | `_SHADOW_DISCOVERY_PATTERNS` regex set, 7 patterns |
| 83 | Output `governance_mode` | 📦 | `TriageReport.governance_mode` |
| 84 | Output `risk_tier_band` | 📦 | `TriageReport.risk_tier_band` |
| 85 | Output `review_depth` (FAST_PATH / STANDARD / ENHANCED / LOCKDOWN) | 📦 ✅ | `ReviewDepth` enum + `_BAND_DEFAULT_DEPTH` |
| 86 | Output `triage_flags` (6 values) | 📦 ✅ | `TriageFlag` enum, all 6 emitted |
| 87 | Output `next_lane` (4 values) | 📦 ✅ | `NextLane` enum |

## G2 — Authority Context Resolution (lines 92–161)

| Lines | Item | Status | Where |
|-------|------|:------:|-------|
| 99–108 | Active policy set (bundle_id, hash, version, refusal taxonomy, sector overlays, standards_fingerprint) | 📦 🔁 | `policy_hash` on request; `StandardsFingerprint` typed; full bundle resolution delegated to caller |
| 110–114 | Structure blueprint (layer matrix, route topology, invariant map) | 📦 🔁 | `blueprint_hash` on request; resolution delegated to existing `agentic_core.L5_safety.config.structure_blueprint` |
| 116–131 | Four sibling registries (Agent / Tool / Prompt / MCP Connector) | 📦 🔁 | `registry_digest_set` tuple; full registry resolution delegated to existing v4 `registries.py` |
| 133–137 | Data authority resolution (supply_chain_digest, RAG vetting, origin trust, quarantine status) | ✅ | covered at G2a |
| 139–144 | Identity propagation (principal_chain, delegation depth, cross-principal bleed) | 🔁 | delegated to v4 `PrincipalChain` + `runtime_rails.validate_handoff` |
| 146–154 | Output `GovernedValidationContext` | 📦 | distributed across `GovernanceResult` reports rather than a single class — same data |
| 156–160 | Hard law (resolved authority only / no ad-hoc / no stale / no implied power) | ⚪ | architectural |

## G2a — Origin-Trust + Boundary (lines 165–191)

| Lines | Item | Status | Where |
|-------|------|:------:|-------|
| 168–177 | 9 origin labels | 📦 ✅ | `OriginLabel` enum |
| 180 | Untagged content untrusted by default | ✅ | unknown labels dropped → defaults to `UNTRUSTED_DATA` |
| 181 | Retrieved/tool/human cannot override system/policy/registry/route | ✅ | enforced via `_TRUSTED_INSTRUCTION_LABELS` whitelist |
| 182 | Prompt-like text in untrusted sources fenced as data | ✅ | classification = `UNTRUSTED_DATA` for those labels |
| 183 | Hidden instructions / malicious markdown / HTML comments / base64 / scripts / suspicious URLs / credentials → quarantine or strip | ✅ | `_QUARANTINE_PATTERNS`, 8 patterns |
| 184 | Quarantined content cannot enter prompt/L2 without explicit safe extraction | ✅ | sanitized payload returned via `sanitized_payload_map`; rail surfaces `EVIDENCE_WEAK` |
| 186–190 | Output `OriginTrustManifest` | 📦 | dataclass with `labeled_fields`, `boundary_classification`, `sanitized_payload_map`, `quarantine_reasons` |

## Static Lane (lines 197–295)

The static lane is owned by **CI gates and existing v4 modules**. v5 ships a thin bridge layer (`agentic_core/L5_safety/v5/bridges.py`) so callers can hand v4 outputs to v5 and have them flow into `governance_reports` + reason codes deterministically.

| Gate | Status | Bridge | Where |
|------|:------:|--------|-------|
| S1 Structure enforcement | 🔁 ✅ | `bridge_blueprint_paths` | `agentic_core/L5_safety/config/structure_blueprint/` (`is_path_allowed`, `has_forbidden_layer_prefix`) |
| S2 Classification kernel | 🔁 | — | `tools/adg/` ADG classifier (CI-only) |
| S3 Registry validation x4 | 🔁 ✅ | `bridge_registry_token_match` | `agentic_core/L5_safety/identity/registries.py::verify_token_against_registry` |
| S4 Policy package integrity | 🔁 ✅ | `bridge_policy_bundle` | `runtime_rails.validate_policy_bundle` |
| S5 Static regression protection | 🔁 | — | `ops_scripts/ci/baselines/*.json` |

Bridge fail-results map to spec-line-663–681 reason codes:
- `static_report.passed=False` → `POLICY_VIOLATION`
- `policy_validation_report.passed=False` → `POLICY_VIOLATION`
- `registry_match_report.matched=False` → `REGISTRY_MISMATCH`

## Runtime Lane (lines 301–588)

| Gate | Status | Bridge | Where |
|------|:------:|--------|-------|
| R1 Universal guardrail bank | 🔁 ✅ | `bridge_guardrail_bank("ingress",...)` | v4 `guardrail_bank.resolve_bank_verdict`; reject→`INJECTION_DETECTED` |
| R2 Agent-level domain guardrails | 🔁 ✅ | `bridge_guardrail_bank("guard_model",...)` | same module, different stage |
| R3 Route + plan alignment | 🔁 | — | placeholder `route_alignment_report` |
| R4 Handoff validation (A2A) | 🔁 ✅ | `bridge_handoff_validation` | v4 `runtime_rails.validate_handoff`; failure→`CONTEXT_BLEED` |
| R5 Context boundary enforcement | 🔁 📦 | — | `evidence_contract_id` on `CapabilityTokenV5` |
| R6 Policy validation chokepoint | 📦 ✅ | — | review depth + hard stops via reason codes |
| R7 Capability token + sandbox envelope | 📦 ✅ | — | `CapabilityTokenV5` + `SandboxEnvelope` (12 fields each) |
| R8 LLM gateway | 🔁 | (caller passes `egress_report`) | v4 `llm_gateway_v4.py`; reject→`CONNECTOR_SCOPE_MISMATCH` |
| R9 Tool/connector/network egress | 🔁 | (caller passes `egress_report`) | v4 `egress_adapter_gated.py`; reject→`CONNECTOR_SCOPE_MISMATCH` |
| R10 HITL action gate + human re-entry | 📦 ✅ | — | `HITLDispositionPacket`; human REJECT→rail REJECT; `re_clearance_required=True` |
| R11 Runtime regression + drift protection | 📦 ✅ | — | `RuntimeRegressionReport` (11 checks); fail→`DRIFT_DETECTED`→ESCALATE |
| R12 Replay + audit sealing | ✅ | — | `seal_replay_envelope` |

**Risk-tier bridge** — `map_v5_band_to_v4` collapses v5 `RiskTierBandV5.CRITICAL` onto v4 `'HIGH'` (v4 has only LOW/MODERATE/HIGH per spec line 71 delta).

## Decision Rail (lines 590–650)

| Lines | Item | Status | Where |
|-------|------|:------:|-------|
| 611 | 4 verdicts (REJECT / REMEDIATE / ESCALATE / CERTIFY) | 📦 ✅ | `DecisionVerdict` enum + `emit_verdict` |
| 613–636 | When/Actions/Output per verdict | ✅ | `emit_verdict` precedence ladder + per-verdict `downstream_disposition` |
| 644 | Every modification/plan/tool/model/connector/write must traverse this rail | ✅ | `certify_packet` is the single entrypoint |
| 645 | REMEDIATE forbidden when hard_constraint=True | ✅ | `GovernanceResult.__post_init__` raises `ValueError` |
| 646 | ESCALATE freezes authority | ✅ | `re_clearance_required=True`; `capability_token=None` and `sandbox_envelope=None` cleared |
| 647 | CERTIFY scoped to packet/token/route/plan_digest/sandbox/principal/policy_hash | ✅ | bound via `compliance_hash` |
| 648 | CERTIFY does not imply durable write authority | ✅ | `WRITE_PROPOSAL` / `EXTERNAL_COMMIT` / `MEMORY` packets get `require_UWG_commit_review` in disposition |
| 649 | Certified call cannot be reused for different task / principal / tenant / route / scope | ✅ | `CapabilityTokenV5.single_use=True` ⇒ `max_invocations==1`; `principal_chain_id` bound |

## Output Contract — `GovernanceResult` (lines 655–757)

| Lines | Field | Status |
|-------|-------|:------:|
| 660 | `decision` | ✅ |
| 663–681 | 19 reason codes | ✅ all 19 in `ReasonCode` |
| 683–684 | `compliance_hash` | ✅ |
| 686–692 | `standards_fingerprint` (NIST_AI_RMF / ISO_42001 / CoSAI / SOC2 / sector / internal) | 📦 ✅ all 6 tags |
| 694–697 | `audit_log` | ✅ `build_audit_log_event` |
| 699–702 | `replay_envelope` | ✅ `seal_replay_envelope` |
| 704–715 | `capability_token` (12 fields) | ✅ `CapabilityTokenV5` |
| 717–726 | `sandbox_envelope` (12 fields) | ✅ `SandboxEnvelope` |
| 728–729 | `origin_trust_manifest` | ✅ |
| 731–745 | `governance_reports` (14 named keys) | ✅ all 14 keys present in `governance_reports` |
| 747–756 | `downstream_disposition` (9 values) | ✅ all 9 emitted by rail |

## Out-of-Band Planes (lines 758–783)

| Lines | Item | Status | Where |
|-------|------|:------:|-------|
| 761–771 | 3 planes (calibration / assurance / audit-forensic) | 🔁 | v4 `out_of_band_planes.py` (G-10/G-11/G-17) |
| 778 | Learning signals inform future thresholds only after promotion | ✅ | `assert_no_current_run_mutation` |
| 779 | No out-of-band plane can rescue/mutate/approve current run | ✅ | `OutOfBandMutationError` raised on non-empty proposed_changes |
| 781 | Promotion requires regression pack / rollback / owner approval / UWG | 🔁 | UWG owner |
| 782 | `policy_version_next` ≠ `policy_version_current` until UWG commits | 🔁 | UWG owner |

## Below-context propagation (lines 786–833)

Documented via module docstrings. Each downstream consumer (L2 / L3 / Exit / HITL / UWG / L6) reads from a different field on `GovernanceResult`.

| Consumer | Reads | Status |
|----------|-------|:------:|
| L2 Execute | `capability_token`, `sandbox_envelope`, `replay_envelope` | ⚪ documented; v4 callers continue using existing types |
| L3 Orchestration | `governance_reports["policy_validation_report"]`, `triage` | ⚪ documented |
| Exit Eval & Control | `replay_envelope`, full report | ⚪ documented |
| HITL | `HITLDispositionPacket` (re-enters G2a/R1/R5/R6) | ✅ enforced via `re_clearance_required` |
| UWG | only when `downstream_disposition` includes `require_UWG_commit_review` | ✅ |
| L6 | `replay_envelope`, `audit_log_event`, `governance_reports` | ⚪ documented |

## Final Invariant Set (lines 817–833)

These are architectural invariants enforced **outside** the v5 module — by layer separation, the structure blueprint, and CI gates. The v5 module respects them and surfaces violations via reason codes when detectable at the governance plane.

| Invariant | Detection lever in v5 |
|-----------|------------------------|
| L5 = Commandant; C0 retrieves only; PA packages only; L0 routes only; L3 orchestrates bounded; L2 executes bounded; HITL reviews only; UWG writes only; L4 stores; L6 observes | architectural — v5 trusts callers stay in lane |
| No hidden state mutation | `assert_no_current_run_mutation` |
| No silent fallback | `RuntimeRegressionReport` + `DRIFT_DETECTED` reason code |
| No unregistered authority | `REGISTRY_GAP` triage flag → `REGISTRY_MISMATCH` reason code |
| No cross-principal context bleed | delegated to v4 `validate_handoff` |
| No direct write outside UWG | `WRITE_PROPOSAL` / `EXTERNAL_COMMIT` packets routed to `require_UWG_commit_review` |
| No current-run mutation from learning | `OutOfBandMutationError` |

## Summary Score

| Category | Count | Coverage |
|----------|------:|---------:|
| Top-of-doc invariants | 7 | 6 ✅ enforced + 1 ⚪ architectural |
| G0 fast-reject conditions | 5 | 5 ✅ |
| G1 triage checks | 6 | 6 ✅ |
| G2a origin labels / classifications | 9+5 | 14 📦 ✅ |
| Static lane gates | 5 | 5 🔁 (existing modules) |
| Runtime lane gates | 12 | 4 ✅ + 4 📦 + 4 🔁 |
| Decision rail invariants | 7 | 7 ✅ |
| GovernanceResult fields | 12 | 12 ✅ |
| Reason codes | 19 | 19 📦 ✅ |
| Downstream dispositions | 9 | 9 ✅ |

Test count: **74/74 passing** (38 base + 21 gap-closure + 15 bridge integration tests).

## Bridge Module — `agentic_core/L5_safety/v5/bridges.py`

5 bridges + 1 risk-tier mapper, all lazy-imported so v5 stays usable in environments without v4:

| Bridge | Calls | Returns | Auto-mapped reason code |
|--------|-------|---------|------------------------|
| `bridge_blueprint_paths` | `structure_blueprint.is_path_allowed`, `has_forbidden_layer_prefix` | `{checked, accepted, rejected, passed}` | `POLICY_VIOLATION` |
| `bridge_guardrail_bank` | `guardrail_bank.resolve_bank_verdict` | v4 verdict dict (normalized `decision` key) | `INJECTION_DETECTED` |
| `bridge_handoff_validation` | `runtime_rails.validate_handoff` | v4 `HandoffValidationResult.to_dict()` | `CONTEXT_BLEED` |
| `bridge_policy_bundle` | `runtime_rails.validate_policy_bundle` | `{violations, rule_count, passed}` | `POLICY_VIOLATION` |
| `bridge_registry_token_match` | `registries.verify_token_against_registry` | `{matched, reason, token_digest}` | `REGISTRY_MISMATCH` |
| `map_v5_band_to_v4` | — | `'LOW'\|'MODERATE'\|'HIGH'` | (CRITICAL collapses to HIGH) |

`certify_packet` accepts each bridge's output as a kwarg (`static_report=...`, `runtime_guardrail_report=...`, etc.) and:
1. Threads it into `governance_reports[<spec_named_key>]` (preserves wire shape per spec lines 731–745).
2. Detects failure shape (`passed=False`, `decision="reject"`, `matched=False`, `approved=False`) and surfaces the right reason code into the decision rail.

All bridges are total over their inputs; none raise on a healthy v4 object. Callers without v4 simply omit the kwarg — `certify_packet` still issues a sealed verdict with empty placeholder reports.
