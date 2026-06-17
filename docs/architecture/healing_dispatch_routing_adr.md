# Architecture Decision Record — Confidence-Scored Tiered Healing Dispatch Routing

**ADR ID**: ADR-F25-int  
**Status**: Accepted  
**Date**: 2026-04-16  
**Scope marker**: F25-int (project-internal)  
**Wave context**: Wave C2.2 — closes WC-G02 per `docs/reports/wave_c_gap_map.md`  
**Authority tier**: T4_repo_canonical  
**Normative use**: `invalid_for_normative_use = True` — describes the current repo-internal architecture only; not an external normative source

---

## 0. Scope Boundary (Read This First)

This ADR is the authoritative **repo-internal** architecture decision for **F25-int only** — confidence-scored tiered healing dispatch routing inside this repository.

It is **not**:

- The F25-ext external baseline (tiered escalation / HITL / durable execution as a general industry pattern)
- An ext_authority source — this ADR lives in `repo_evidence` Lane C only
- An attempt to redefine the Wave B external-only target-state baseline
- A reopening of the F25 adjudication (which is final per `docs/reports/wave_b_b7_final_audit.md` §3)

F25-ext is grounded by external sources (e.g. OpenAI `running_agents.md` HITL section) already indexed in `ext_authority` and is ADEQUATE advisory at B7. F25-int is the project-specific *implementation shape* of that general concept inside this codebase, and has no external analogue.

---

## 1. Status

**Accepted** — this ADR codifies existing architectural intent that was previously described only inside the process map and the healer retry hardening spec. No module rewrite is mandated by this decision; the ADR is a current-state authority document whose implementation state is tracked separately in `docs/reports/wave_c_gap_map.md` as WC-G02 IMPL_GAP.

---

## 2. Context

### 2.1 What exists today

The project has two concept-documented artifacts describing healing dispatch behavior, neither of which is an ADR:

- `docs/reference/_notes/agentic_process_mapping_v34.md` describes a `dispatch_healing()` entry point and names three healing tiers: **LOCAL_AGENT**, **COORDINATED**, **ESCALATED**. It also names two components: `healing_tier_router.py` (tier-based routing via `route_by_confidence()`) and `healing_tier_dispatcher.py` (healing dispatch via `dispatch_healing()`). Neither module exists yet under `agentic_core/base_agents/`.
- `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md` defines `RetryConfig.strictness_escalation = [0.7, 0.85, 0.95]` with `max_attempts = 3` and `timeout_escalation = [30, 20, 10]` seconds per attempt, managed by a `HealerRetryManager` class that is already referenced in existing healing call-sites.

### 2.2 Why an ADR is needed

The Wave C handoff contract classifies F25-int as `IMPL_GAP` because the routing module is absent and the concept is not captured in any authoritative architectural decision document. Without an ADR:

- The tier semantics live only in a process map entry whose semantic density is diluted by surrounding routing content (measured `dist@1 = 0.3881` on the F25-int gap query — relevant but not authoritative)
- The link between strictness thresholds `[0.7, 0.85, 0.95]` and tier boundaries is undocumented
- Wave D implementers have no single source of truth for the fallback chain (local rule → model retry → human escalation)
- The decision to treat F25-int as a repo-internal concern, distinct from F25-ext, is implicit

This ADR closes that documentation gap without mandating implementation changes.

### 2.3 Constraints carried forward

- **No modification to `query_router.py`**: architecture-domain queries already route to `repo_evidence`. This ADR must be reachable from the `architecture` domain prefilter without route changes.
- **No modification to `evidence_shaper.py`**: `invalid_for_normative_use = True` on all chunks of this ADR ensures it is filtered out of normative (target-state) shaping paths.
- **No ext_authority addition**: F25-int has no external analogue. Adding this ADR to `ext_authority` would violate the anti-drift rule in `docs/requirements/wave_c_handoff_contract.md` §1.

---

## 3. Decision

### 3.1 Tier Contract

The repo-internal healing dispatch tiers are defined exactly as follows. These names MUST be used verbatim in implementation modules, tests, and telemetry.

| Tier | Mechanism | Responsible component | Confidence / strictness band |
|------|-----------|-----------------------|------------------------------|
| `LOCAL_AGENT` | In-agent retry with local rule fallback | `l2_evaluate_and_heal()` inside the owning agent | Attempt 1, strictness `0.70` — lowest bar, local-rule-only corrections |
| `COORDINATED` | Multi-agent healing with model retry | `healing_tier_router.route_by_confidence()` dispatching to `healing_tier_dispatcher.dispatch_healing()` | Attempt 2, strictness `0.85` — tighter scope, cross-agent coordination |
| `ESCALATED` | Human-in-the-loop or deterministic abort | HITL gate (`hitl-enforcement.md`) or planner-level abort | Attempt 3, strictness `0.95` — last retry before human escalation; if attempt 3 fails, route to HITL or abort |

### 3.2 Confidence-Scored Dispatch Semantics

Dispatch is **confidence-scored** in two senses:

1. **Per-tier strictness**: each tier raises the acceptance bar for a healing attempt. A corrected artifact passing at strictness `0.70` in LOCAL_AGENT would not necessarily pass at `0.85` in COORDINATED. Strictness is the minimum validator score required to accept the healed artifact.
2. **Between-tier routing**: `route_by_confidence()` selects the starting tier based on the confidence score carried with the violation. Low-confidence violations (weak signal, likely transient) start at LOCAL_AGENT. High-confidence violations (strong signal, systematic) may start at COORDINATED to skip a doomed local retry.

### 3.3 Fallback Chain

The authoritative fallback order is **local rule → model retry → human escalation**:

1. **Local rule fallback** (LOCAL_AGENT): apply deterministic correction rules inside the owning agent. No model call. Fast, cheap, scope-locked. If the corrected artifact fails strictness `0.70`, escalate.
2. **Model retry escalation** (COORDINATED): re-run the healing prompt via the healer model with tighter strictness `0.85` and reduced timeout (20s). `healing_tier_router` selects the appropriate healer based on the violation type. If the corrected artifact fails strictness `0.85`, escalate.
3. **Human escalation / HITL threshold** (ESCALATED): at strictness `0.95` with attempts exhausted, route to the HITL gate per `hitl-enforcement.md`. If HITL approval is not configured or not available, abort the healing pipeline and surface a `RoutingContractError`-equivalent.

### 3.4 Scope Lock Invariant

During all three tiers, `RetryConfig.scope_lock = True`. A healing attempt MUST NOT widen the scope of the violation being healed. If a proposed correction touches content outside the original violation scope, the attempt is rejected at the tier boundary and escalated to the next tier.

### 3.5 Abort Conditions

Deterministic abort (no further escalation) is required when:

- `max_attempts = 3` is exhausted and no HITL gate is configured
- Scope-lock is violated at any tier (correction attempts to widen scope)
- Strictness configuration is invalid (non-monotonic thresholds or out-of-range values)
- The violation itself is classified as non-healable (e.g. governance hard-fail)

---

## 4. Consequences

### 4.1 Positive

- **Single source of truth**: tier names, thresholds, and fallback order now have one authoritative definition. Wave D implementers can build `healing_tier_router.py` and `healing_tier_dispatcher.py` against this ADR without re-deriving semantics from the process map.
- **Retrieval alignment**: repo_evidence Lane C queries on the F25-int gap query now resolve to an ADR-authority document (dist target < 0.50), replacing the process-map-chunk best result (`dist@1 = 0.3881`).
- **Telemetry uniformity**: tier names `LOCAL_AGENT`, `COORDINATED`, `ESCALATED` are reserved for telemetry keys, ADG node classes, and healing-outcome logs. No synonyms (e.g. `local`, `multi_agent`, `human`) are permitted in new code.
- **Anti-drift**: codifying F25-int as repo-internal prevents accidental cross-contamination with the F25-ext external baseline in ext_authority.

### 4.2 Negative / tradeoffs

- **Implementation debt**: the ADR documents intent; the routing modules `healing_tier_router.py` and `healing_tier_dispatcher.py` remain absent. WC-G02 stays IMPL_GAP until Wave D.
- **Threshold rigidity**: the strictness triple `[0.70, 0.85, 0.95]` is inherited from `HEALER_RETRY_HARDENING_SPEC.md`. Changing these values requires a new ADR revision and re-ingestion of `repo_evidence`.
- **HITL coupling**: the ESCALATED tier depends on `hitl-enforcement.md` being operationally available. In environments without HITL (CI, batch jobs), ESCALATED collapses to deterministic abort.

### 4.3 Non-consequences (explicitly not covered)

- This ADR does NOT define healer model selection, prompt design, or correction validator internals. Those remain in `HEALER_RETRY_HARDENING_SPEC.md` and downstream specs.
- This ADR does NOT define how `route_by_confidence()` computes the initial confidence score. Confidence inputs (signal strength, violation type, prior-attempt history) are left to the router implementation.
- This ADR does NOT change routing for any other domain (policy, best_practice, tool_contracts, architecture, code). The `query_router.py` `_domain_to_collection` mapping is frozen per handoff contract §4.

---

## 5. Alignment with Existing Repo Evidence

| Prior artifact | Relationship to this ADR |
|----------------|--------------------------|
| `docs/reference/_notes/agentic_process_mapping_v34.md` | Describes `dispatch_healing()` entry point and names the three tiers; this ADR promotes those names to a canonical contract |
| `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md` | Defines `RetryConfig.strictness_escalation = [0.7, 0.85, 0.95]`, `max_attempts = 3`, `timeout_escalation = [30, 20, 10]`, `scope_lock = True`; this ADR binds these values to tier boundaries |
| `docs/reference/_archive/Healing & Escalation Loop.md` | Archived predecessor; superseded by this ADR |
| `docs/requirements/wave_b_target_state_registry.md` §F25 split | Records the F25-int / F25-ext classification and the F25-int OUT OF SCOPE disposition for ext_authority |
| `docs/requirements/wave_c_handoff_contract.md` §2, §9 | Binds F25-int to repo_evidence Lane C; forbids ext_authority additions for this topic |
| `docs/reports/wave_c_gap_map.md` §4 WC-G02 | Records the IMPL_GAP status; this ADR is the deliverable that closes the documentation portion of WC-G02 |
| `.claude/rules/hitl-enforcement.md` | Defines the HITL gate invoked at ESCALATED tier |

No external URLs are referenced. All alignment is with in-repo artifacts.

---

## 6. Validation Criteria

This ADR is accepted into `repo_evidence` Lane C when:

1. The new chunks carry `source_collection = repo_evidence`, `source_band = repo_canonical`, `authority_tier = T4_repo_canonical`, `invalid_for_normative_use = True`, `normative_scope = repo_internal`, `source_url = docs/architecture/healing_dispatch_routing_adr.md` (repo-relative, no `https://`).
2. The F25-int acceptance query — `"confidence-scored tiered healing dispatch routing tiers local rules model retry human escalation"` — returns this ADR at rank 1 with `dist@1 < 0.50`.
3. All 14 required metadata fields per `docs/requirements/wave_b_metadata_contract.md` are present on every chunk.
4. Wave B freeze gates G4, G5, G6 continue to pass for `repo_evidence` after rebuild.

---

## 7. Change History

| Version | Date | Note |
|---------|------|------|
| 1.0 | 2026-04-16 | Initial ADR — closes WC-G02 documentation gap |

---

## 8. References

- `docs/reference/_notes/agentic_process_mapping_v34.md` (tier names `LOCAL_AGENT`, `COORDINATED`, `ESCALATED`; `dispatch_healing()`; `healing_tier_router`)
- `docs/specs/hardening/HEALER_RETRY_HARDENING_SPEC.md` (`RetryConfig`, `strictness_escalation`, `HealerRetryManager`, `scope_lock`)
- `docs/requirements/wave_b_target_state_registry.md` (F25 split; F25-int OUT OF SCOPE for ext_authority)
- `docs/requirements/wave_c_handoff_contract.md` (repo_evidence Lane C constraint; ext_authority prohibition for F25-int)
- `docs/reports/wave_c_gap_map.md` (WC-G02 IMPL_GAP record)
- `docs/requirements/wave_b_metadata_contract.md` (14-field metadata contract enforced by freeze gates G4, G5, G6)
- `.claude/rules/hitl-enforcement.md` (HITL gate invoked at ESCALATED tier)
- `docs/requirements/normative_requirements_spec.md` (AGEN-0100 abstain/refine/fallback requirement, adjacent context)
