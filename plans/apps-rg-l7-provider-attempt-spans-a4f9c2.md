---
plan_id: apps-rg-l7-provider-attempt-spans-a4f9c2
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# apps_rg L7 Provider Attempt Spans

Add clean per-provider attempt timing spans to apps_rg provider and L7 receipts so RCAs can read direct-call and fallback timing without reconstructing artifacts.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-28

---

## Context (SCQA)

- **Situation** - L7 binding receipts prove route correlation and provider responses carry scattered timestamps.
- **Complication** - RCAs still need artifact reconstruction to understand provider attempt duration, blocked/credential paths, and Claude-to-OpenAI fallback timing.
- **Question** - How do we emit normalized provider-call timing and fallback timing per path without changing lane behavior?
- **Answer** - Add additive provider attempt spans to provider response/fallback receipts and surface a compact summary in the L7 binding manifest.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Provider span schema and emission | ~8K | ProviderResult remains behavior-compatible | DONE | Direct success, credential block, HTTP/error timeout paths carry normalized spans |
| W2 | W2.1, W2.2 | Fallback and L7 surfacing | ~8K | L7 binding reads section artifacts only | DONE | Fallback receipt carries requested+fallback spans and L7 manifest summarizes them |
| W3 | W3.1, W3.2 | Verification and closeout | ~6K | Focused tests cover contract | DONE | Targeted pytest passed and plan DoD evidence is updated |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Define additive provider attempt span helper | DONE |
| W1.2 | Attach spans to provider responses | DONE |
| W2.1 | Attach spans to availability fallback receipts | DONE |
| W2.2 | Surface spans in section L7 binding manifest | DONE |
| W3.1 | Add focused provider and L7 tests | DONE |
| W3.2 | Run targeted verification and update receipts | DONE |

---

## Out Of Scope

- Changing provider selection or fallback policy.
- Changing agentic_core L7 artifact producers.
- Running full apps_rg E2E generation.
- Reworking unrelated dirty worktree changes.

---

## Wave 1 - Provider Span Emission

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: A

**Authorization**: USER_APPROVED - user approved implementation on 2026-06-28.

**Phases**:
- **W1.1** - Define additive provider attempt span helper | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Attach spans to provider responses | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Spans include provider, model, attempted, status, start/end UTC, duration seconds, timeout, error, and progress where available.
- Existing provider response timestamp fields remain for backward compatibility.

---

## Wave 2 - Fallback And L7 Surfacing

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: B

**Phases**:
- **W2.1** - Attach spans to availability fallback receipts | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** - Surface spans in section L7 binding manifest | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Claude availability fallback receipts include both requested and fallback provider spans.
- `section_l7_binding_manifest.json` includes provider attempt span refs and a compact timing summary when `provider_response.json` exists.

---

## Wave 3 - Verification

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: C

**Phases**:
- **W3.1** - Add focused provider and L7 tests | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** - Run targeted verification and update receipts | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Focused provider and L7 manifest tests pass.
- The plan file records final evidence and leaves unrelated worktree changes untouched.

---

## Execution Details

### W1.1 - Span Helper
**Scope**: Add a small apps_rg provider-local helper for normalized attempt spans.

**Commands**:
```bash
python -m pytest tests/unit/apps_rg/runtime/providers/test_external_provider.py -q
```

### W2.2 - L7 Manifest
**Scope**: Read provider spans from `provider_response.json` and summarize them in the binding manifest.

**Commands**:
```bash
python -m pytest tests/unit/apps_rg/test_section_l7_binding_manifest.py -q
```

---

## Gap Register

**GAP-1: Provider timing exists but is scattered**
- Impact: RCA requires stitching provider response, transport timing, and fallback receipts manually.
- Fix: normalized `provider_attempt_spans` emitted with the provider response and fallback receipt.

**GAP-2: L7 binding proves route but not provider attempt timing**
- Impact: L7 closeout lacks the per-path timing summary the user needs.
- Fix: L7 manifest extracts and summarizes provider attempt spans.

---

## Definition of Done

DoD-1: Provider attempt spans emitted on direct provider paths.
- Evidence: `python -m pytest tests/unit/apps_rg/runtime/providers/test_external_provider.py -q`
- Status: DONE

DoD-2: Availability fallback receipts include requested and fallback provider spans.
- Evidence: `python -m pytest tests/unit/apps_rg/runtime/providers/test_availability_fallback.py -q`
- Status: DONE

DoD-3: L7 binding manifest surfaces provider timing summary.
- Evidence: `python -m pytest tests/unit/apps_rg/test_section_l7_binding_manifest.py -q`
- Status: DONE

DoD-4: Existing L7 lane integration contract remains compatible.
- Evidence: `python -m pytest tests/unit/apps_rg/runtime/test_section_l7_binding_lane_integration.py -q`
- Status: DONE

DoD-5: Scope stays apps_rg-local with no agentic_core changes.
- Evidence: `git diff --name-only`
- Status: DONE

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=apps-rg-l7-provider-attempt-spans-a4f9c2 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=apps-rg-l7-provider-attempt-spans-a4f9c2 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=apps-rg-l7-provider-attempt-spans-a4f9c2 reason="<summary>" added="<waves/phases>" authorized="yes"
```

---

## Supersedes

| Predecessor slug | Reason |
|---|---|

_None - net-new plan._

---

## Marker Quick Reference

```
WAVE_START: plan=apps-rg-l7-provider-attempt-spans-a4f9c2 wave=<N>
WAVE_COMPLETE: plan=apps-rg-l7-provider-attempt-spans-a4f9c2 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=apps-rg-l7-provider-attempt-spans-a4f9c2 phase=<W1.1>
PLAN_COMPLETE: plan=apps-rg-l7-provider-attempt-spans-a4f9c2 note="<final outcome>"
```
