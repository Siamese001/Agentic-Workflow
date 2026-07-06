---
plan_id: apps-rg-l2-e1-e5-best-practice-closeout-9d2a31
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# apps_rg L2 E1-E5 Best-Practice Closeout

Make the apps_rg product-visible L2 path use the canonical E1 -> E2 -> E3/E4 -> E5 v4 envelope by default, with signed execution packets, fail-closed validation, same-authority repair, sealed receipt bundles, section-lane integration, and CI/eval enforcement.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-07-05

---

## Context (SCQA)

- **Situation** - apps_rg already has an L2 v4 envelope adapter, a governed L2/Exit bridge, section-lane L2 receipt mirrors, and an apps_eval lane contract.
- **Complication** - Product-visible execution can still fall through flag-driven legacy/stub paths, E1 can synthesize route/request authority from a CPA-only call, determinism uses a random attempt seed, E4 mutates prompt content, and CI defaults are advisory.
- **Question** - How do we make L2 product execution prove the canonical E1-E5 contract instead of relying on local mirrors or optional flags?
- **Answer** - Close the runtime path first, then harden E1-E5 receipts and section/eval consumers around the same canonical receipt bundle.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1, W0.2 | Inventory and baseline fence | ~8K | ADG MCP must be reconnected before structural edits | IN PROGRESS | Gap inventory exists and baseline commands are recorded |
| W1 | W1.1, W1.2, W1.3 | Default product-visible L2 to canonical v4 envelope | ~12K | Legacy/stub paths remain explicit dev-only overrides | TODO | Governed default reaches v4; stub cannot masquerade as canonical |
| W2 | W2.1, W2.2, W2.3 | Signed L2 execution packet and E1 prep hardening | ~18K | CPA-only product calls must reject before E3 | TODO | Deterministic seed/hash behavior and bounded packet fields are tested |
| W3 | W3.1, W3.2, W3.3 | E2 validation and runtime gate receipts | ~18K | UNKNOWN is terminal fail, not pass | TODO | Missing authority fields reject before provider and emit decisive receipts |
| W4 | W4.1, W4.2, W4.3 | E3 lane dispatcher and provider/budget governance | ~18K | MODEL is the first wired lane; others fail closed until implemented | TODO | Alias/live-required rules and attempt receipts are deterministic |
| W5 | W5.1, W5.2, W5.3 | E4 same-authority repair governor | ~18K | Repair context is separate from original prompt authority | TODO | Prompt hash remains stable and disallowed repairs are blocked |
| W6 | W6.1, W6.2, W6.3 | E5 seal and content-addressed receipt bundle | ~18K | Product-visible success requires the bundle | TODO | Mutating any payload/receipt changes seal digest |
| W7 | W7.1, W7.2, W7.3 | Section lanes through canonical E1-E5 | ~20K | Existing section artifacts become mirrors, not authority | TODO | 11 lanes expose required canonical L2 roles or fail closed |
| W8 | W8.1, W8.2, W8.3 | Fail-closed CI and eval ladder fence | ~18K | Offline evals cannot waive runtime gates | TODO | CI gate fails closed and micro/lane/suite evals enforce L2/X2/X1D/X3/L6 |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Establish branch/worktree and governance baseline | IN PROGRESS |
| W0.2 | Record current L2 gap inventory | IN PROGRESS |
| W1.1 | Change product-visible bridge default to v4 | TODO |
| W1.2 | Fence legacy/stub paths behind explicit dev modes | TODO |
| W1.3 | Add bridge tests for default and override behavior | TODO |
| W2.1 | Add execution packet contracts | TODO |
| W2.2 | Harden E1 packet/hash/seed freezing | TODO |
| W2.3 | Add E1 deterministic/rejection tests | TODO |
| W3.1 | Add E2 validator/gate receipt modules | TODO |
| W3.2 | Enforce fail-closed validation before E3 | TODO |
| W3.3 | Add E2 no-provider/no-routing AST tests | TODO |
| W4.1 | Add provider alias normalization | TODO |
| W4.2 | Add E3 lane dispatcher and live-required authenticity checks | TODO |
| W4.3 | Add attempt receipt/provider governance tests | TODO |
| W5.1 | Add repair context/patch contract | TODO |
| W5.2 | Stop prompt mutation during repair | TODO |
| W5.3 | Add repair authority and quarantine tests | TODO |
| W6.1 | Add receipt bundle persistence | TODO |
| W6.2 | Seal full proof digest and rejection proof | TODO |
| W6.3 | Add digest mutation and authority invariant tests | TODO |
| W7.1 | Build canonical packets before section provider calls | TODO |
| W7.2 | Convert section mirrors to canonical receipt derivatives | TODO |
| W7.3 | Update inventory/terminology/eval lane contract | TODO |
| W8.1 | Make CI gate fail closed by default | TODO |
| W8.2 | Add micro-evals and executive_summary lane eval | TODO |
| W8.3 | Add 11-lane suite proof and meta-eval fence | TODO |

---

## Out Of Scope

- Modifying `agentic_core` contract classes unless a later approved scope expansion and core-addition gate require it.
- Treating local/stub/model-mock output as product certification.
- Letting apps_eval override runtime GateVerdict, X3, or sealed L2 authority.
- Replacing existing provider gateway infrastructure with direct SDK or HTTP calls.

---

## Wave 0 - Inventory + Baseline Fence

WAVE_ID: W0
WAVE_STATUS: IN_PROGRESS
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: A

**Authorization**: APPROVED - User approved adjusted plan on 2026-07-05 and requested ADG checkpoint bypass. Bypass is limited to non-structural plan/report scaffolding; production/test implementation remains blocked until ADG MCP reconnects.

**Phases**:
- **W0.1** - Establish branch/worktree and governance baseline | ~3K tokens | PHASE_STATUS: IN_PROGRESS | PHASE_COMPLETE: NO
- **W0.2** - Record current L2 gap inventory | ~5K tokens | PHASE_STATUS: IN_PROGRESS | PHASE_COMPLETE: NO

**Acceptance**:
- Plan file exists under root `plans/`, not `.codex/plans/`.
- Gap inventory exists under `docs/reports/apps_rg/`.
- Baseline commands are recorded without claiming green ADG readiness.

---

## Wave 1 - Product-Visible Default To Canonical V4 Envelope

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: B

**Phases**:
- **W1.1** - Change `l2_execute_apps_rg()` governed/product-visible default to call `run_apps_rg_l2_envelope()` | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** - Preserve package/stub paths only behind explicit non-product/dev overrides | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** - Add bridge tests for default, override, and TypeError-before-flag behavior | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Default governed call reaches v4 envelope.
- Legacy path is unreachable in product-visible mode without explicit override.
- Stub fallback cannot stamp canonical L2 authority.

---

## Wave 2 - Signed L2 Execution Packet + E1 Prep Hardening

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: C

**Phases**:
- **W2.1** - Add `AppsRgL2ExecutionPacket` or equivalent packet contract | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** - Reject product CPA-only synthetic route/request authority before E3 | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** - Replace random attempt seeds with deterministic replay/prompt/route-derived seeds | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Product CPA-only invocation seals rejection before E3.
- Same packet plus same attempt number produces the same attempt seed.
- Route/policy/blueprint/prompt/sandbox/provider changes alter E1 hashes.

---

## Wave 3 - E2 Validation + Runtime Gate Receipts

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: D

**Phases**:
- **W3.1** - Add validation/gate modules for signature, authority, sandbox, budget, replay, and evidence references | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** - Emit decisive validation receipts and sealed rejection packets | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** - Add AST tests proving E2 has no provider, C0, PA, L0, L3, Exit, UWG, or L4 behavior | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Missing route/signature/capability/sandbox/L5/budget fails before provider.
- UNKNOWN gate status fails.
- E2 failure never calls E3.

---

## Wave 4 - E3 Exec Lane Dispatcher + Provider/Budget Governance

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: E

**Phases**:
- **W4.1** - Add provider alias normalization | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** - Add explicit lane dispatcher and fail-closed unsupported lanes | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** - Enforce live-required authenticity and budget/timeout/output ceilings | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Unsupported lanes return `E3_UNSUPPORTED_EXECUTION_LANE`.
- External aliases resolve to live providers in live-required mode.
- Local/stub aliases fail live-required authenticity checks.
- Attempt receipt has a non-empty output digest.

---

## Wave 5 - E4 Same-Authority Repair Governor

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: F

**Phases**:
- **W5.1** - Add repair context/patch contract | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** - Preserve original prompt authority and stop mutating prompt blocks/user instruction | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.3** - Add unknown-cause, disallowed-repair, quarantine, oscillation, and budget tests | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- E4 never appends system prompt blocks.
- Original prompt hash remains unchanged across repair.
- Unknown repair cause is not silently JSON-repaired.

---

## Wave 6 - E5 Seal + Content-Addressed Receipt Bundle

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: G

**Phases**:
- **W6.1** - Add receipt bundle persistence | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W6.2** - Expand seal digest coverage over packet, receipts, output, proposed diff, checks, model/provider refs, and evidence refs | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W6.3** - Add mutation tests and E2 rejection no-provider proof | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Any payload or receipt mutation changes seal digest.
- `state_diff_authorized` is never true.
- `is_uwg_write_authority` is never true.
- Product-visible success requires receipt bundle.

---

## Wave 7 - Section Lanes Through Canonical E1-E5

WAVE_ID: W7
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: H

**Phases**:
- **W7.1** - Build canonical L2 packet before section provider calls | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W7.2** - Convert existing section artifacts into compatibility mirrors derived from canonical receipts | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W7.3** - Update inventory, terminology, handoff receipts, and apps_eval required roles | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- All 11 lanes emit required L2 receipt roles or ScorecardRow failures.
- Section mirror cannot claim product certification without canonical receipt bundle.

---

## Wave 8 - Fail-Closed CI + Eval Ladder Fence

WAVE_ID: W8
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: I

**Phases**:
- **W8.1** - Make `check_apps_rg_l2_v4_envelope.py` fail closed by default with explicit advisory override | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W8.2** - Add E1-E5 micro-evals and executive_summary lane eval | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W8.3** - Add 11-lane suite proof and meta-eval grader-only fence | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `python -m pytest tests/_apps_contract/test_apps_rg_l2_envelope.py -q`
- `python -m pytest tests/unit/apps_rg/test_one_spine_l2_receipt_w5b.py -q`
- `python -m pytest tests/unit/apps_rg/test_one_spine_certification_w8.py -q`
- `python ops_scripts/ci/check_apps_rg_l2_v4_envelope.py`
- UNKNOWN is not PASS and mock/stub is not ALLOW.

---

## Execution Details

### W0.1 - Baseline Fence
**Scope**: Record current repo state and MCP readiness without making structural edits.

**Commands**:
```bash
git status --short --branch
git worktree list --porcelain
python scripts/governance/codex_readiness.py --json
python ops_scripts/ci/check_apps_rg_l2_v4_envelope.py
python -m pytest tests/_apps_contract/test_apps_rg_l2_envelope.py --collect-only -q
```

### W0.2 - Gap Inventory
**Scope**: Read the L2 bridge/envelope, section-lane, eval registry, and CI gate files named in the user-provided grounding. Record exact current gaps before implementation.

**Files inspected**:
- `apps_rg/runtime/bindings/l2_envelope_adapter.py`
- `apps_rg/runtime/bindings/l2_binding_adapter.py`
- `apps_rg/runtime/bindings/l2_envelope_contracts.py`
- `apps_rg/runtime/spine/governed_l2_exit_compose.py`
- `apps_rg/runtime/section_l2_lane_integration.py`
- `apps_rg/runtime/section_l2_spine_receipt.py`
- `apps_rg/runtime/spine/l2_handoff_receipt.py`
- `ops_scripts/ci/check_apps_rg_l2_v4_envelope.py`
- `apps_eval/registries/apps_rg_lane_contract.json`

---

## Gap Register

**GAP-1: ADG MCP transport is closed**
- Active-session `mcp__adg_sqlite.adg_health` returns `Transport closed`.
- Structural implementation and graph-backed test selection remain blocked until reconnect.

**GAP-2: Product-visible L2 bridge is still flag-driven**
- `_use_v4_l2_envelope()` requires `APPS_RG_L2_USE_V4_ENVELOPE=1`.
- Default `_l2_execute_apps_rg_core()` can return legacy package-driven stub behavior.

**GAP-3: CPA-only authority can be synthesized**
- `_synth_route_and_vr_from_prompt_artifact()` creates a route and validated request from CPA fields.
- Product mode needs fail-closed packet authority instead.

**GAP-4: Attempt seed is random**
- `_build_determinism_bundle()` uses `uuid.uuid4()` for `attempt_seed`.
- E1 replay proof needs deterministic seed derivation.

**GAP-5: E4 repair mutates prompt authority**
- `_apply_heal_repair_patch()` appends bounded context to `user_instruction` and prompt blocks, and recomputes `compilation_hash`.
- Same-authority repair needs separate repair context while preserving original prompt hash.

**GAP-6: E5 seal digest is under-scoped**
- `_seal_digest_hex()` currently covers a small subset of IDs and compilation hash.
- Content-addressed seal needs whole-proof coverage.

**GAP-7: Section lanes emit local L2 mirrors**
- `prepare_section_l2_before_provider()` writes section packet artifacts, but canonical E1/E2 approval and receipt bundle authority are not yet the section gate.

**GAP-8: apps_eval L2 roles are still lane-local**
- `apps_rg_lane_contract.json` requires `lane_l2_output` and `lane_runtime_payload`, not canonical packet/prep/validation/attempt/seal/bundle roles.

**GAP-9: CI gate is advisory by default**
- `check_apps_rg_l2_v4_envelope.py` exits 0 on failures unless `APPS_RG_L2_V4_ENVELOPE_FAIL_CLOSED=1`.

---

## Definition of Done

DoD-1: Product-visible L2 uses canonical v4 envelope by default
- Evidence: `python -m pytest tests/_apps_contract/test_apps_rg_l2_envelope.py -q`
- Status: TODO

DoD-2: E1-E5 proof is sealed in a content-addressed bundle
- Evidence: digest mutation tests pass and bundle files are emitted for success/rejection paths.
- Status: TODO

DoD-3: Section lanes derive L2 authority from canonical receipt bundle
- Evidence: `python -m pytest tests/unit/apps_rg/test_one_spine_l2_receipt_w5b.py -q`
- Status: TODO

DoD-4: CI/eval ladder is fail closed
- Evidence: `python ops_scripts/ci/check_apps_rg_l2_v4_envelope.py` exits non-zero on constructed failures unless advisory override is explicit.
- Status: TODO

DoD-5: Lane eval proof covers all generated lanes
- Evidence: apps_eval suite rows show all 11 lanes have required L2/X2/X1D/X3/L6 roles or explicit failures.
- Status: TODO

DoD-6: Graph-backed scope and test selection are complete
- Evidence: ADG MCP `adg_health` green plus documented `## DEPENDENCY_GRAPH` and impacted test selection.
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=apps-rg-l2-e1-e5-best-practice-closeout-9d2a31 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=apps-rg-l2-e1-e5-best-practice-closeout-9d2a31 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=apps-rg-l2-e1-e5-best-practice-closeout-9d2a31 reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter and absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

---

## Supersedes

| Predecessor slug | Reason |
|---|---|

_None - net-new plan._

---

## Marker Quick Reference

Wave lifecycle markers:
```
WAVE_START: plan=apps-rg-l2-e1-e5-best-practice-closeout-9d2a31 wave=<N>
WAVE_COMPLETE: plan=apps-rg-l2-e1-e5-best-practice-closeout-9d2a31 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=apps-rg-l2-e1-e5-best-practice-closeout-9d2a31 phase=<W1.1>
PLAN_COMPLETE: plan=apps-rg-l2-e1-e5-best-practice-closeout-9d2a31 note="<final outcome>"
```
