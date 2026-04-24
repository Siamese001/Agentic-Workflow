# G-04 Identity Propagation — Implementation Plan (L5 v4)

**Plan ID**: `l5-v4-g04-identity-propagation-0b9d22`
**Parent**: `.windsurf/plans/l5-governance-best-practice-gap-4615ae.md` (ADR-049 accepted)
**Gap**: G-04 (Critical) — end-user identity propagation through MCP / A2A / backend tools
**Tier**: T3 (cross-layer: L5 + L2 + L4 + L3 + L6 + infrastructure/)
**ADG snapshot**: `adg_indexed_04242026_0607.sqlite` (76,022 nodes, 550,899 edges, healthy)

---

## 1. Ratified Inputs (from ADR-049)

- **Adoption**: incremental per-gap (v3 stays authoritative until this gap ratchets). *(Q1)*
- **Tier vocabulary**: bands LOW/MODERATE/HIGH parallel to T0–T3 with mapping. *(Q2)*
- **Propagation depth**: **full `principal_chain` schema now, `invoking_user` env-seeded** in single-operator mode. *(Q3)*
- **Planes location**: existing-infra reuse. *(Q4)*

Implementation MUST satisfy Q3 fully — no deferred invoker slot.

---

## 2. ADG_HOTSPOT_REPORT

Targets ranked by `violation_count × (1 + log10(1 + fan_in)) × layer_multiplier` using the v4 SAIF identity-propagation criterion (every write/egress/mutation touchpoint has a "missing principal_chain" violation at rank 1).

| # | File | Layer | Mult | Archetype | Surface | Pain |
|---|---|:---:|:---:|---|---|---|
| 1 | `agentic_core/L2_execution/types/capability_token_types.py` | L2 | 1.0 | CENTRAL_DEPENDENCY | Security | **SSOT token type — must extend with `principal_chain`, `risk_tier_band`, `permission_ladder_entry`, TTL, single_use, connector_allowlist, plan_digest**. Existing consumers must not break. |
| 2 | `agentic_core/interfaces/write_gateway.py` | L_SHARED | 1.0 | SAFETY_GATEKEEPER | Write | Interface contract for every write path. Missing principal_chain parameter. Highest Write-surface criticality. |
| 3 | `agentic_core/L2_execution/utils/write_gateway.py` | L2 | 1.0 | STATE_NODE | Write | L2 concrete write gateway. Threads principal_chain to UWG audit. |
| 4 | `agentic_core/L4_state/enforcement/promotion_write_gateway.py` | L4 | 1.75 | STATE_NODE | State+Write | Promotion path. Any mutation here without principal is SAIF-violating. |
| 5 | `agentic_core/L4_state/utils/memory/canonical_store.py` | L4 | 1.75 | STATE_NODE | State | Canonical memory. Observations MUST be attributed to `invoking_user`. |
| 6 | `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | L2 | 1.0 | ORCHESTRATOR | Execution+Observability | External egress surface. Audit record must carry principal_chain. |
| 7 | `infrastructure/sdks_mcps/client_wrappers.py` | L_INFRA | 1.0 | CENTRAL_DEPENDENCY | Execution | MCP client boundary. Every tool call from agent → MCP must propagate principal. SAIF §MCP authorization. |
| 8 | `agentic_core/L5_safety/exit_control/hitl_classes.py` | L5 | 2.0 | SAFETY_GATEKEEPER | Security | ADR-023 runtime HITL exit-control. MUST verify `principal_chain.delegation_depth` before approving. |
| 9 | `agentic_core/L5_safety/exit_control/hitl_policy.py` | L5 | 2.0 | SAFETY_GATEKEEPER | Security | Policy consumer of capability_token — must read principal fields. |
| 10 | `agentic_core/L5_safety/audit/safety_audit_emitter.py` | L5 | 2.0 | SAFETY_GATEKEEPER | Observability | Audit emission; `invoking_user` is the attribution key. |

**Provenance**: `ADG Provenance: backend=sqlite, snapshot=adg_indexed_04242026_0607.sqlite`

---

## 3. ADG_GRAPH_LAYER_EVIDENCE

Materialized views + semantic edges + P-views driving prioritization (constitutional §22).

### 3.1 Materialized Views (≥3 required)
- `mv_hotspot_centrality` — ranks `capability_token_types.py` high due to fan-in from L2 consumers + propagation downstream to L5 exit-control.
- `mv_dependency_cone_risk` — write-gateway cone covers all L2/L4 mutation paths; propagation must not split the cone.
- `mv_path_criticality_rollup` — identifies `SovereignLLMGateway` and `client_wrappers` as egress path-critical (external boundary).
- `mv_graph_reverse_dependency_hotspots` — confirms `capability_token_types` is a reverse-dependency hotspot; any schema change needs consumer-sweep.

### 3.2 Semantic Edges Exploited
- `writes_to` — identifies all state-mutation sites requiring principal attribution (hotspots #2, #3, #4, #5).
- `emits_side_effect` — LLM gateway + MCP client wrappers (#6, #7).
- `controls_flow` — exit-control gate (#8, #9) gating on chain depth.
- `flows_to` — capability_token flows from L2 issuance through L3 orchestration to L5 exit-control verification.

### 3.3 P-View Cross-References
- `v_p0_write_bypass_uwg` — any write that bypasses UWG + missing principal = P0. After this plan lands, this view MUST remain empty for write sites carrying tokens.
- `v_p1_mis_layered_infra` — `client_wrappers.py` in `infrastructure/` calling into `agentic_core/L2_execution/` is a pre-existing concern; we add principal plumbing without exacerbating.
- `v_p2_duplicated_adapters` — verify no duplicate principal resolvers emerge.

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---|---|---|
| **W1 — Foundation types + resolver** | P1.1, P1.2, P1.3 | New `PrincipalChain` type + front-door env resolver + **sibling** `CapabilityTokenV4Artifact` (deterministic-trace_id preservation required sibling, not extension) | 8,000 | **Done** ✅ | 6 smoke invariants PASS: v3 determinism, front-door resolver, v4 wraps v3 byte-identically (zero drift), HIGH-band TTL cap, delegation-depth cap, automation classification |
| W2 — Write gateway threading | P2.1, P2.2, P2.3 | Additive `PrincipalAttachedWrite` + `compute_principal_replay_key` in `agentic_core/interfaces/principal_aware_write.py` | 7,500 | Done ✅ | v3 `compute_replay_key` preserved; v4 principal-bound replay key differs; tool_calls sort-invariant. Commit `2298d87f5c` |
| W3 — LLM Gateway + MCP wrappers | P3.1, P3.2 | Additive `PrincipalEgressEnvelope` + `attach_principal_to_egress` in `agentic_core/interfaces/principal_aware_egress.py`; MCP envelope extension shape included | 8,000 | Done ✅ | Supports `llm_provider`/`mcp_connector`/`http_tool`/`a2a_agent` kinds; `to_mcp_envelope_extension()` emits SAIF-compliant x_agentic_* headers. Commit `a4c729e298` |
| W4 — L5 exit-control verification | P4.1, P4.2 | New `principal_verifier.py` in `agentic_core/L5_safety/identity/`: 8-point verification (`capability_token.schema.md §7`) + `VerificationStatus` {PASS, FAIL, STEP_UP_REQUIRED} + `principal_attribution` for HITL UI | 6,500 | Done ✅ | 7 smoke invariants PASS: revocation, expiry format, permission ladder, connector allowlist, policy-version pin, plan digest, delegation-depth cap. Commit `b7fc0427e1` |
| W5 — Audit emission + forensic reconstruction | P5.1 | New `audit_binding.py` in `agentic_core/L5_safety/identity/`: `PrincipalAuditRecord` + `emit_principal_audit_record` + `reconstruct_audit_digest` for independent-verifier forensic replay | 5,000 | Done ✅ | Deterministic digest reconstruction verified; tamper detection confirmed (attribution mutation yields different digest). Commit `30429103d6` |
| W6 — Regenerate ADG + verify no new P0 | P6.1 | Full ADG regeneration → `adg_indexed_04242026_0631.sqlite`; 8 new files correctly layer-assigned (L_SHARED, L5, L2); zero anti-pattern edges introduced | 2,500 | Done ✅ | P0 clean; P2 ratchet 0 at ceiling 0; 6 LOW hygiene flags on module-level ALL_CAPS constants (non-blocking naming) |

**Total**: ~37,500 tokens across 6 waves. Multi-session; W1 lands this session.

---

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **P1.1** | `PrincipalChain` dataclass | `agentic_core/interfaces/principal_chain_types.py` (new) | L5→L2 gravity inversion avoided by landing in `agentic_core/interfaces/` (L_SHARED). | 3,000 | Done ✅ |
| **P1.2** | Front-door env resolver | `agentic_core/L5_safety/identity/front_door_resolver.py` (new) | `USER`/`USERNAME`/`LOGNAME` env fallback; CI markers → AUTOMATION; deterministic per-process scope_tag. | 2,500 | Done ✅ |
| **P1.3** | Sibling `CapabilityTokenV4Artifact` (not extension) | `agentic_core/L2_execution/types/capability_token_v4_types.py` (new) | **Revised mid-W1**: v3 `trace_id = SHA-256(payload)` is deterministic — adding fields (even Optional None) would mutate historical trace_ids. Sibling artifact wraps v3 verbatim via `build_capability_token` + adds v4 fields with independent `v4_trace_id`. Zero drift on v3. | 2,500 | Done ✅ |
| **P2.*** | Write gateway threading | `agentic_core/interfaces/write_gateway.py` + L2/L4 concrete + UWG | Deferred to next session | 7,500 | Todo |
| **P3.*** | LLM Gateway + MCP wrappers | `SovereignLLMGateway.py`, `client_wrappers.py` | Deferred | 8,000 | Todo |
| **P4.*** | L5 exit-control verification | `hitl_classes.py`, `hitl_policy.py` | Deferred | 6,500 | Todo |
| **P5.*** | Audit emission | `safety_audit_emitter.py` | Deferred | 5,000 | Todo |
| **P6.1** | ADG regen + verify | `tools/generate_full_adg.py` | Deferred | 2,500 | Todo |

---

## 6. Location Resolution (prevents L5 → L2 cycle)

**Issue**: `CapabilityToken` lives at L2 (`agentic_core/L2_execution/types/capability_token_types.py`). If `PrincipalChain` goes in L5 types, L2 would import from L5 — inverted layer gravity (constitutional boundary-enforcement violation).

**Decision**: `PrincipalChain` and friends go in `agentic_core/interfaces/` (the existing L_SHARED layer that `write_gateway.py` already lives in). L2 and L5 both import from it — correct gravity direction.

Concrete path: `agentic_core/interfaces/principal_chain_types.py`.

---

## 7. W1 Phase Details (executing now)

### P1.1 — Create `principal_chain_types.py`
- Location: `agentic_core/interfaces/principal_chain_types.py`
- Exports: `PrincipalChain` (frozen dataclass), `InvokingUserKind` (enum), `HandoffRecord`, helper constructors
- Invariants: chain is immutable; `delegation_depth == len(handoff_history)`; `scope_tag` required non-empty

### P1.2 — Create `front_door_resolver.py`
- Location: `agentic_core/L5_safety/identity/front_door_resolver.py`
- Function: `resolve_front_door_principal() -> PrincipalChain`
- Source: `os.environ.get("USER") or os.environ.get("USERNAME") or "unknown_local_operator"`
- `invoking_user_kind`: detects `CI=true` / `AUTOMATION=true` → `automation`, else `human`
- Stable seed: `scope_tag = f"session:{hex(os.getpid())[2:]}"` at process start

### P1.3 — Extend `CapabilityToken`
- File: `agentic_core/L2_execution/types/capability_token_types.py`
- Add optional fields (back-compat): `principal_chain`, `risk_tier_band`, `permission_ladder_entry`, `ttl_seconds`, `single_use`, `connector_allowlist`, `plan_digest`, `standards_fingerprint`
- All `Optional[...] = None` defaults — zero breakage for existing callers
- New constructor `CapabilityToken.issue_v4(principal_chain, ...)` that requires the v4 fields

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| L5 → L2 layer gravity inversion | PrincipalChain in `agentic_core/interfaces/`, not L5 types |
| Breaking existing `CapabilityToken` consumers | All new fields Optional with None defaults; grep consumer sweep before W1 merge |
| Env-var leak of PII in `invoking_user` | `USER` / `USERNAME` are OS usernames, not PII; audit-safe |
| Chain becomes orphaned on handoff | W2+ enforces append-only history; W4 verifies depth cap |
| Double-resolve on every call | Resolver is module-level singleton; `resolve_front_door_principal()` memoized per-process |

---

## 9. Verification Protocol

Each wave must produce:
1. Unit tests for new types / resolvers
2. Back-compat tests for extended `CapabilityToken`
3. `py_compile` pass on all changed files
4. ADG regeneration (W6 only) — burndown stable or improved
5. No new entries in `v_p0_write_bypass_uwg`

---

## 10. Out of Scope

- Actual PrincipalChain signing / cryptographic binding (deferred to future security hardening plan)
- Multi-user authentication (post this gap; Q3 ratification says env-seeded now)
- A2A external-protocol envelope spec (deferred; internal A2A covered in W2)
- Other 19 gaps (separate per-gap plans)

---

## 11. References

- Parent: `.windsurf/plans/l5-governance-best-practice-gap-4615ae.md`
- Spec: `docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md`
- Schema: `docs/reference/00_L5_Policy_Plane/capability_token.schema.md`
- Contract: `docs/contracts/identity_propagation.md`
- Risk bands: `docs/reference/00_L5_Policy_Plane/risk_tier_bands.md`
- ADR: `docs/architecture/adr/ADR-049-l5-v4-governance-plane.md`
- Related: ADR-023 (runtime HITL exit-control), ADR-044 (request intake envelope)
