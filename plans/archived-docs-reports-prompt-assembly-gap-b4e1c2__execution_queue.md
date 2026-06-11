---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\prompt-assembly-gap-b4e1c2\\execution_queue.md'
original_relative_path: 'prompt-assembly-gap-b4e1c2\\execution_queue.md'
source_sha256: 44e7c1b3b9ab38743bdca00ccd72cf4781e86d07af84a2377c8de1bf4dceb5c1
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# W8 — Consolidated Execution Queue

**Parent plan**: `.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md`
**Purpose**: Single queue that orders all code-wave work derived from the
gap analysis + ADR-PROMPT-ASSEMBLY-001 + ADR-PROMPT-ASSEMBLY-002, with
dependencies, rollback checkpoints, and Author-Gate entry points.

Tranches are labeled `EQ-n` (execution queue). Each spawns its own T2/T3
child plan with full ADG evidence at kickoff time.

---

## 1. Dependency graph

```
EQ-1  CompiledPromptArtifact schema extension (nonce + structured slots)
      │
      ├─► EQ-2  Provider adapters (Anthropic, OpenAI GPT-4.1, OpenAI o-series)
      │         │
      │         ├─► EQ-4  Provider-matrix golden tests
      │         └─► EQ-5  Response-schema threading verification
      │
      ├─► EQ-3  Slot extension (M0 added; E0/H0 activation paths)
      │         │
      │         └─► EQ-4  (tests depend on final slot shape)
      │
      └─► EQ-6  Replay-verifier shim (90-day back-compat window)

EQ-7  Token counter (provider-aware, lazy-loaded, heuristic fallback)
      │
      └─► EQ-8  History compressor + deterministic eviction
                │
                └─► EQ-9  Cache-prefix stability gate

EQ-10 I0 mixin bank:
       - I0_AGENTIC_STANDING_V1
       - I0_MODEL_IDENTITY_V1
       - I0_GROUND_IN_QUOTES_V1
       (no downstream dependency — parallel with EQ-1..EQ-9)

EQ-11 Routing-meta thinking_level knob + AgentSpec fields:
       - parallel_tool_calls
       - expose_model_identity
       (depends on EQ-2 adapters for wiring)

EQ-12 Apply-patch schema + validator (apps_rg)
       (depends on EQ-3 R0 variant support)

EQ-13 Gemini adapter (follow-on after EQ-2 stabilizes)

EQ-14 Documentation final pass — reconcile all refs once EQ-1..EQ-13 complete

EQ-15 LLM-based conversation summarizer (scheduled; was deferred)
       (depends on EQ-8 rule-based compressor)

EQ-16 Cross-provider thinking-token billing reconciliation (scheduled; was deferred)
       (depends on EQ-11 thinking-level knob)

EQ-17 Synthesis slot Y0 producer/consumer wiring (scheduled; was deferred)
       (depends on EQ-3 slot extension)

EQ-18 Apply-patch multi-file batching (scheduled; was deferred)
       (depends on EQ-12 single-file apply-patch)

EQ-19 Anti-pattern lint gate forbidding assistant prefill (scheduled; was deferred)
       (independent — parallel)
```

---

## 2. Tranche detail

| ID | Title | ADR ref | Dependencies | Rollback checkpoint | Author-Gate? |
|----|-------|--------|--------------|--------------------|--------------|
| EQ-1 | `CompiledPromptArtifact` schema: add `idempotency_nonce`, structured slots | PA-001 Q2, PA-002 §9 | — | Tag `pre-EQ1` on main; shim accepts both schemas for 90 d | **Yes** — schema change · **Done 2026-04-23** |
| EQ-2 | Anthropic + OpenAI (GPT-4.1 + o-series) provider adapters | PA-001 Q2, Q3 | EQ-1 | Feature flag `USE_STRUCTURED_ADAPTER=1`; flip off to fall back to legacy flattener | **Yes** — architectural · **Done 2026-04-23** |
| EQ-3 | Slot extension — `M0` + `E0`/`H0` activation wiring | PA-001 Q1 | EQ-1 | Slot-order validator supports both 5-slot and 8-slot during shim window | **Yes** — contract change · **Done 2026-04-23** |
| EQ-4 | Provider-matrix golden tests | `test_plan_matrix.md` | EQ-2, EQ-3 | N/A (tests only) | No · **Done 2026-04-24** |
| EQ-5 | Response-schema threading end-to-end | PA-001 Q4, PA-002 §audit | EQ-2 | Feature flag on gateway; default off until verified | **Yes** — external API contract · **Done 2026-04-24** |
| EQ-6 | Replay-verifier shim (90-day back-compat) | PA-002 §9 | EQ-1 | Removable independently when cutover date passes | No · **Done 2026-04-24** |
| EQ-7 | Provider-aware token counter | PA-002 §6 | — | Heuristic fallback always available | No · **Done 2026-04-24** |
| EQ-8 | History compressor + deterministic eviction | PA-002 §7, §8 | EQ-7 | Feature flag `USE_DETERMINISTIC_EVICTION=1` | **Yes** — new component in dispatch path · **Done 2026-04-24** |
| EQ-9 | Cache-prefix stability CI gate | PA-002 §10 | EQ-3 | Gate is additive; can be disabled via env | No · **Done 2026-04-24** |
| EQ-10 | I0 mixin bank (3 new mixins) | PA-002 §3, §4, §5 | — | Mixins opt-in per AgentSpec | No · **Done 2026-04-24** |
| EQ-11 | Routing-meta + AgentSpec fields | PA-002 §11, §13 | EQ-2 | Fields default to legacy behavior | No · **Done 2026-04-24** |
| EQ-12 | Apply-patch validator + R0 variant | PA-002 §14 | EQ-3 | R0 variant is opt-in per agent | No · **Done 2026-04-24** |
| EQ-13 | Gemini adapter | PA-001 Q2 (follow-on) | EQ-2 | Adapter registered only when Gemini model selected | **Yes** — new provider surface · **Done 2026-04-24** |
| EQ-14 | Final doc + registry sync | all | EQ-1..EQ-13 | N/A | No · **Done 2026-04-24** (in-flight) |
| EQ-15 | LLM-based convo summarizer | PA-002 §7 | EQ-8 | Feature flag; rule-based stays default | **Yes** — non-determinism entry point · **Done 2026-04-24** (shim) |
| EQ-16 | Thinking-token billing reconciliation | PA-002 §11 | EQ-11 | N/A (observability-only) | No · **Done 2026-04-24** |
| EQ-17 | Y0 slot producer/consumer wiring | PA-002 taxonomy | EQ-3 | Producer opt-in per meta-learning module | **Yes** — new dispatch path · **Done 2026-04-24** |
| EQ-18 | Apply-patch multi-file batching | PA-002 §14 | EQ-12 | Schema v2 opt-in per agent | No |
| EQ-19 | No-prefill lint gate | PA-001 §Consequences | — | Gate is additive; can be disabled via env | No |

---

## 3. Parallelization

Three streams may run in parallel once EQ-1 merges:

- **Stream A** (adapters): EQ-2 → EQ-5 → EQ-13
- **Stream B** (budget): EQ-7 → EQ-8 → EQ-9
- **Stream C** (governance/mixins): EQ-10, EQ-11, EQ-12 (all independent of each other)

EQ-3 (slot extension) must land before EQ-4 tests can run; EQ-4 gates the
merge of EQ-2 and EQ-3.

---

## 4. Rollback discipline

1. Every tranche tags `pre-EQn-<date>` on `main` before merge.
2. Feature flags (`USE_STRUCTURED_ADAPTER`, `USE_DETERMINISTIC_EVICTION`)
   default **off** at first merge; turned on after one green CI day.
3. 90-day shim windows (EQ-1, EQ-3, EQ-6) tracked on Notion MCP Registry with
   explicit sunset date.
4. Breakage criteria:
   - CI red for > 4 hours → revert tranche.
   - Any provider-matrix golden mismatch not approved by Author-Gate → block.
   - Cache-prefix drift detected in EQ-9 → revert most recent adapter /
     mixin change.

---

## 5. Author-Gate entry points

Each **Yes** row in §2 opens a Author-Gate packet at kickoff with:

- Current state summary
- Proposed change scope
- Rollback path
- Confidence score (expected ≥ 0.85 — most were resolved at ADR drafting)

Low-confidence items (<0.72) DO NOT enter the queue; they return to the
parent plan for re-design.

---

## 6. Previously-deferred scope — now PROMOTED TO SCHEDULED (2026-04-23)

User approved 2026-04-23 — all 5 previously-deferred items enter the active
queue as tranches EQ-15 through EQ-19. Each already has a Notion Wave/Phase
Convergence row via `defer.py` capture; status on those rows flips from
`Todo` (P-band scored) to `Scheduled` when a child plan is opened.

| ID | Title | Source ADR | Dependencies | Notes |
|----|-------|-----------|--------------|-------|
| EQ-15 | LLM-based conversation summarizer (optional upgrade over rule-based compressor) | PA-002 §7 | EQ-8 (rule-based compressor) | Requires hash-stable prompt; own replay discipline. Previously Notion row `EQ-8b / EQ-8b.1`. |
| EQ-16 | Cross-provider thinking-token billing reconciliation | PA-002 §11 | EQ-11 (thinking-level knob) | Unified accounting across Anthropic / OpenAI o-series / Gemini 3. Previously `EQ-11b / EQ-11b.1`. |
| EQ-17 | Synthesis slot `Y0` producer/consumer wiring | PA-002 (slot taxonomy) | EQ-3 (slot extension) | `SlotY0` exists in contracts; needs meta-learning pipeline producer + at least one consumer. Previously `EQ-15 / EQ-15.1`. |
| EQ-18 | Apply-patch multi-file batching | PA-002 §14 | EQ-12 (single-file apply-patch) | Multi-file patch envelope; follow-on to initial schema. Previously `EQ-12b / EQ-12b.1`. |
| EQ-19 | Anti-pattern lint gate forbidding assistant prefill usage (Claude 4.6+) | PA-001 §Consequences | EQ-13 (Gemini adapter) or earlier | CI gate at `ops_scripts/ci/check_no_assistant_prefill.py`; detects `messages[-1]["role"] == "assistant"` on egress. Previously `EQ-16 / EQ-16.1`. |

These 5 tranches feed into §7 completion criteria. Each spawns its own child
T2/T3 plan at kickoff.

---

## 7. Completion criteria

The gap-b4e1c2 plan closes when:

1. EQ-1 through EQ-19 are merged. No further deferrals — all 5 previously-
   deferred items were promoted to scheduled on 2026-04-23.
2. `Prompt Assembly.md` §7 status table shows all rows ✅ or with a linked
   deferred-scope Notion row.
3. The three distilled best-practice reference docs
   (`anthropic_best_practices_2026.md`, `openai_best_practices_2026.md`,
   `gemini_best_practices_2026.md`) have their **captured-on** dates
   refreshed.
4. Cross-map `current_architecture_crossmap.md` shows 30/30 techniques green
   (no residual deferrals after 2026-04-23 promotion).
