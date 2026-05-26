---
plan_id: unify-bullets-graph-compose-prompt-a3f7e2
plan_type: enhancement
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Unify bullets — graph-skill compose prompts (Qwen)

Compose six Unify employment bullets from C0.3-bound graph skills and fact atoms; JD and briefing in U0 for targeting only (not proof). Replaces “rewrite from canonical bullets” C0 framing that caused verbatim archive copy.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Completed
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-05-26
PLAN_COMPLETED: 2026-05-26
COMPLETION_NOTE: W1 DONE (GRAPH_BULLET_EVIDENCE_PACK + compose I0/U0 + path framing + pytest). W2 LIVE REAL_LLM deferred to graph-skills-deferred-followup-d7f2a8.
NOTION_PAGE_ID: 36c27693-f55c-8122-9714-fd02e06b923c
NOTION_PLAN_URL: https://www.notion.so/unify-bullets-graph-compose-prompt-a3f7e2-36c27693f55c81229714fd02e06b923c

---

## Context (SCQA)

- **Situation** — `unify_bullets` compiles via `unify_bullets_pa` + `unify_bullet_tailor_v1.yaml`. Graph authority is on INPUT_AUTHORITY and skill phrase capsule, but C0 still dumps full `claim_text` as “rewrite from these,” so Qwen echoes ledger/archive bullet prose.
- **Complication** — Pool selection collapses (identical paths); output is structurally isomorphic to base resume themes without using base resume at runtime.
- **Question** — How do we retarget Qwen prompts so bullets are organically composed from graph-bound skills + facts, with JD/briefing shaping emphasis only?
- **Answer** — Replace C0 with `GRAPH_BULLET_EVIDENCE_PACK`, reframe I0/U0 to compose (not rewrite), enrich U0 JD block, optional per-path framing; keep slot IDs and metric locks.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.4 | Plan + prompt implementation | ~8k | Fixture bypass for compile tests | ✅ DONE | C0 pack + I0/U0 + template + tests green |
| W2 | W2.1 | Live unify_bullets smoke | ~4k | qwen_vllm | ⏭️ DEFERRED | → graph-skills-deferred-followup-d7f2a8 |

### Phase Progress

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Plan disk + Notion | `.cursor/plans/`, Notion Plans DB | Registration | ~1k | ✅ DONE |
| W1.2 | Graph evidence pack | `unify_bullets_graph_evidence.py`, `unify_bullets_pa.py` | C0 shape | ~3k | ✅ DONE |
| W1.3 | Template + capsule | `unify_bullet_tailor_v1.yaml`, `graph_skill_phrase_capsule.py` | SSOT drift | ~1k | ✅ DONE |
| W1.4 | Tests + path framing | `bullet_lane_self_consistency.py`, unit tests | Pool diversity | ~2k | ✅ DONE |

---

## Definition of Done

| ID | Criterion | Verification |
|----|-----------|--------------|
| D1 | Compiled prompt contains `GRAPH_BULLET_EVIDENCE_PACK` | pytest compile guard |
| D2 | Compiled prompt forbids `CANONICAL UNIFY FACTS` / `rewrite from these` | pytest substring guard |
| D3 | Each slot block lists bound skills when `selected_skill_rows` present | unit test on formatter |
| D4 | `unify_bullet_tailor_v1.yaml` purpose/oath match compose model | file read + drift test |
| D5 | Targeted pytest for unify bullets PA passes | `pytest tests/unit/apps_rg/test_unify_bullets_graph_compose_prompt.py` |

### Verification vs Deferral

| Item | In scope (W1) | Deferred (W2) |
|------|---------------|---------------|
| Prompt C0/I0/U0 | Yes | — |
| X2 verbatim-archive gate | — | W2 |
| Live REAL_LLM 15-path diversity | — | W2 |

---

## Execution detail (W1)

### Files

- `apps_rg/runtime/sections/unify_bullets_graph_evidence.py` — slot evidence pack + path framing
- `apps_rg/runtime/sections/unify_bullets_pa.py` — wire C0/I0/U0/JD
- `apps_rg/prompt_assembly/templates/unify_bullet_tailor_v1.yaml` — purpose, oath, composition_rules
- `apps_rg/runtime/graph_skill_phrase_capsule.py` — cross-ref to evidence pack
- `apps_rg/runtime/reasoning/bullet_lane_self_consistency.py` — per-path framing for unify_bullets
- `tests/unit/apps_rg/test_unify_bullets_graph_compose_prompt.py`

### Invariants (unchanged)

- `bul_unify_001`..`006` slot IDs; protected metrics on 004/006
- JD/briefing targeting-only (`pa_targeting_only_v1`)
- `ALLOWED_SOURCE_FACT_IDS` / claim_ledger hygiene

---

PLAN_CREATED: slug=unify-bullets-graph-compose-prompt-a3f7e2 path=.cursor/plans/unify-bullets-graph-compose-prompt-a3f7e2.md status=Not Started

WAVE_COMPLETE: plan=unify-bullets-graph-compose-prompt-a3f7e2 wave=1 note="+3 tests, 6 files, scope=unify-bullets-graph-compose-prompts"

DEFERRED_SCOPE: plan=unify-bullets-graph-compose-prompt-a3f7e2 wave=W2 gap="LIVE REAL_LLM unify_bullets path diversity + verbatim-archive X2 gate" impact=graph-skills-deferred-followup-d7f2a8

PLAN_COMPLETE: plan=unify-bullets-graph-compose-prompt-a3f7e2 note="W1 prompt compose shipped; W2 LIVE proof in deferred follow-on"
