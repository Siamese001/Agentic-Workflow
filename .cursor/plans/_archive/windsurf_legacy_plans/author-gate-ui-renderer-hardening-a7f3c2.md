# Plan: Author-Gate UI Renderer Pipeline Hardening

**Slug:** `author-gate-ui-renderer-hardening-a7f3c2`
**Status:** Not Started
**Tier:** T3 — multi-file, cross-component (rules + hooks + CI gates + skills + tests)
**Created:** 2026-05-09
**Related plans:** `author-gate-four-req-enforcement-c4d2a8` (Completed 2026-05-03 — closed last gap in 12-component AG stack), `author-gate-ssot-consolidation-b7c3e1` (parent stack)
**Related rules:** `.windsurf/rules/author-gate-enforcement.md`, `.windsurf/rules/author-gate-decision-points.md`
**Related skills:** `.windsurf/skills/author-gate-packet-builder/`, `.windsurf/skills/author-gate-ui-renderer/`
**Constitutional anchors:** §6 (Author-Gate for ambiguous decisions), §30 (capture health), §35 (queue drain)

---

## §1. Problem Statement

Cascade MAY emit `AUTHOR_GATE_PACKET:` JSON blocks in chat without ever calling `ask_user_question`, leaving the user to manually copy/parse JSON instead of seeing the proper UI surface (options · ⭐ recommended · score · confidence · gap). The user has to call this out verbally — there is no deterministic enforcement that the **packet → render-card → `ask_user_question`** pipeline runs end-to-end.

**Empirical incident (2026-05-09, this session):**
- Turn N: emitted `AUTHOR_GATE_PACKET:` JSON for AG-RGGOV-W5-WIRING-GAP. NO `ask_user_question` call. User had to type "WHY is everything not routing through UI authorgate options STAR Confidence" to force re-route.
- Turn N+1: re-routed via `ask_user_question` with the same packet. User selected D.

**Root cause:** the existing audit (`post_cascade_author_gate_ui_audit.py`) enforces *shape* of the packet (4 requirements: clickable / pros-cons / confidence / dominance star) when `ask_user_question` IS called. It does NOT enforce that `ask_user_question` is called at all when an `AUTHOR_GATE_PACKET:` was emitted. The reverse-direction audit (`post_cascade_ask_user_question_packet_audit.py`) catches `ask_user_question` *without* a packet (vacuum closure). The packet-without-ask direction is unenforced.

---

## §2. Objective

Make it **structurally impossible** for Cascade to emit `AUTHOR_GATE_PACKET:` without a same-response `ask_user_question` call, via a deterministic post-hook audit + CI freshness gate + rule prose update + skill flow update + test coverage.

---

## §3. Non-Goals

- Implement actual `ask_user_question` rendering improvements (UI itself is Cascade-built-in; we cannot modify the IDE's render of the question).
- Modify the four shape requirements (already enforced by `post_cascade_author_gate_ui_audit.py` per plan c4d2a8).
- Add new fields to AUTHOR_GATE_PACKET schema.
- Modify the queue-drain pipeline (constitutional §35 — separate concern).
- Touch the legacy `HITL_PACKET:` alias path (back-compat preserved).

---

## §4. Files In Scope

| Path | Role | Change kind |
|---|---|---|
| `.windsurf/scripts/_author_gate_pipeline_check.py` | NEW pure helper — `decide(response_text) -> Violation \| None` | Create |
| `.windsurf/scripts/post_cascade_author_gate_pipeline_audit.py` | NEW post-hook (Tier 1) | Create |
| `.windsurf/hooks.json` | Register new post-hook | Edit (add 1 entry) |
| `ops_scripts/ci/check_author_gate_pipeline_freshness.py` | NEW CI gate (Tier 5) | Create |
| `ops_scripts/ci/run_contract_gates.py` | Register `AGP1` advisory gate | Edit (add 1 entry) |
| `.windsurf/rules/author-gate-enforcement.md` | Add §"Pipeline Completion Invariant" — packet ⇒ ask_user_question same response | Edit (~40 LOC addition) |
| `.windsurf/skills/author-gate-packet-builder/SKILL.md` | Add explicit "MUST be followed by ask_user_question" callout | Edit (~10 LOC) |
| `.windsurf/skills/author-gate-ui-renderer/SKILL.md` | Promote ask_user_question step from "after render-card" to "MANDATORY same-response" | Edit (~10 LOC) |
| `tests/unit/windsurf_scripts/test_author_gate_pipeline_check.py` | NEW — helper unit tests (~30 cases) | Create |
| `tests/unit/ops_scripts/ci/test_check_author_gate_pipeline_freshness.py` | NEW — CI gate tests (~12 cases) | Create |
| `artifacts/windsurf/author_gate_pipeline_violations.jsonl` | Output log (created at runtime) | N/A (data) |

**Total:** 5 new files · 4 edits · 2 new test files · 1 runtime artifact

---

## §5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1, P1.2 | Pure helper + unit tests | ~5k | `re` regex sufficient to detect both `AUTHOR_GATE_PACKET:` and `ask_user_question` invocation in response text; ≥30 unit-test cases cover happy/violation/edge | ✅ DONE | helper module + 38 passing unit tests; deterministic decide() function |
| W2 | P2.1, P2.2 | Post-cascade audit hook + hooks.json registration | ~3k | Audit script writes JSONL row per violation; bypass env var `AG_PIPELINE_AUDIT_BYPASS=1`; `hooks.json` schema-pure (only command/working_directory/show_output) | ✅ DONE | post-hook fires on responses containing `AUTHOR_GATE_PACKET:`; logs to `artifacts/windsurf/author_gate_pipeline_violations.jsonl`; hooks.json 49 entries, 0 non-schema keys |
| W3 | P3.1, P3.2 | CI freshness gate + run_contract_gates.py registration | ~3k | Gate watches violation JSONL; 7-day staleness window (`AG_PIPELINE_STALENESS_DAYS` override); fail-closed via `AG_PIPELINE_FAIL_CLOSED=1` | ✅ DONE | gate registered as `AGP1 Author-Gate pipeline completion (advisory)`; 15 CI gate tests pass; standalone smoke exits 0 |
| W4 | P4.1, P4.2, P4.3 | Rule prose + skill prose + test suite green | ~4k | Rule prose mirrors c4d2a8 4-row contract table style; skill flow updated to mandate same-response `ask_user_question`; full test suite passes | ✅ DONE | Pipeline Completion Invariant added to rule + both skills; 53 tests green; zero regressions |
| W5 | P5.1, P5.2 | Verify loop — synthetic positive control + smoke + plan close | ~2k | One synthetic packet-only response triggers violation; one packet+ask response passes; plan moves to Completed | ✅ DONE | violation SYNTH-001 captured; compliant response clean; PLAN_COMPLETED marker emitted |

**Total estimate:** ~17k tokens · 5 waves · 11 phases.

---

## §6. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Helper module — `_author_gate_pipeline_check.decide()` | `.windsurf/scripts/_author_gate_pipeline_check.py` | Regex must distinguish real `AUTHOR_GATE_PACKET:` block from quoted/inline mention; must detect `ask_user_question` invocation marker (text rendered by tool surface) | ~3k | ✅ DONE |
| P1.2 | Helper unit tests | `tests/unit/windsurf_scripts/test_author_gate_pipeline_check.py` | ≥30 cases: packet-only / packet+ask / ask-only / no-packet / quoted-packet / multi-packet / legacy HITL_PACKET alias | ~2k | ✅ DONE (38 cases) |
| P2.1 | Post-cascade audit hook | `.windsurf/scripts/post_cascade_author_gate_pipeline_audit.py` | Fail-soft per Anthropic two-tier compliance; idempotent JSONL write; bypass env var; correct exit codes per `pre_run_gate.py` pattern | ~2k | ✅ DONE |
| P2.2 | hooks.json registration | `.windsurf/hooks.json` | Schema purity (constitutional §27 — only `command`/`working_directory`/`show_output`); no JSON corruption (memory 3ba710ed lesson — re-read before edit) | ~1k | ✅ DONE |
| P3.1 | CI freshness gate | `ops_scripts/ci/check_author_gate_pipeline_freshness.py` | Staleness math; bypass + fail-closed env vars; emits structured report under `artifacts/notion/` or `artifacts/windsurf/` | ~2k | ✅ DONE |
| P3.2 | run_contract_gates.py registration | `ops_scripts/ci/run_contract_gates.py` | Insertion order — register after existing AG-WIRE / AG-FRESH gates; advisory by default | ~1k | ✅ DONE |
| P4.1 | Rule update — `author-gate-enforcement.md` | `.windsurf/rules/author-gate-enforcement.md` | Add "Pipeline Completion Invariant" section after the 4-row contract table; mirror c4d2a8 prose style; cross-ref this plan slug | ~2k | ✅ DONE |
| P4.2 | Skill updates — packet-builder + ui-renderer | `.windsurf/skills/author-gate-packet-builder/SKILL.md`, `.windsurf/skills/author-gate-ui-renderer/SKILL.md` | Promote ask_user_question from "renderer follow-up" to "MANDATORY same-response"; add forbidden-pattern callout | ~1k | ✅ DONE |
| P4.3 | CI gate tests | `tests/unit/ops_scripts/ci/test_check_author_gate_pipeline_freshness.py` | ≥12 cases mirroring c4d2a8 freshness gate test pattern (pure evaluate() + main() + bypass + fail-closed) | ~1k | ✅ DONE (15 cases) |
| P5.1 | Synthetic positive control | (smoke run only — no new files) | Synthesize a response containing `AUTHOR_GATE_PACKET:` with NO `ask_user_question` → confirm violation logged; then with `ask_user_question` → confirm clean | ~1k | ✅ DONE |
| P5.2 | Plan close + Notion patch | (plan file + Notion Plans DB row) | Status=Completed; emit `PLAN_COMPLETED:` marker; update `Last Validated` if applicable | ~1k | ✅ DONE |

---

## §7. ADG_HOTSPOT_REPORT

This is an **infrastructure-class plan** — the surface area is `.windsurf/scripts/`, `.windsurf/rules/`, `.windsurf/skills/`, `ops_scripts/ci/`. These directories are deliberately outside the agentic_core ADG scan scope (the ADG indexes domain code under `agentic_core/`, `apps_*/`, `tools/`, `infrastructure/`).

| Hotspot | File | Layer | Fan-in (qualitative) | Fan-out (qualitative) | Archetype | Surface intersection | Impact |
|---|---|---|---|---|---|---|---|
| Author-Gate emit pipeline | `.windsurf/skills/author-gate-packet-builder/emit_packet.py` | infra/skill | HIGH (every Author-Gate decision touches it) | LOW (isolated emitter) | SAFETY_GATEKEEPER | Execution + Observability | HIGH — regressions cascade across every refactor decision |
| UI render → ask flow | `.windsurf/skills/author-gate-ui-renderer/render_card.py` | infra/skill | HIGH (consumes every emitted packet) | MED | SAFETY_GATEKEEPER | Execution + Observability | HIGH — same blast radius as emitter |
| Existing post-hook audits | `.windsurf/scripts/post_cascade_author_gate_ui_audit.py`, `.windsurf/scripts/post_cascade_ask_user_question_packet_audit.py` | infra/hook | LOW (only the orchestrator) | LOW | SAFETY_GATEKEEPER | Observability | MED — failures here = silent enforcement bypass |
| Constitutional rule body | `.windsurf/rules/author-gate-enforcement.md` | infra/rule | EVERY task that hits an AG decision point | LOW | SAFETY_GATEKEEPER | Execution | HIGH — wording determines what Cascade enforces |

The 5 Surfaces touched: **Execution** (the flow gates whether a decision proceeds), **Observability** (audit + violation logs), **Security** (governance integrity — bypassed AGs = governance erosion). Not touched: Write, State.

---

## §8. ADG_GRAPH_LAYER_EVIDENCE

Per constitutional §22, T2/T3 plans must cite ≥3 MVs + semantic edges + P-views. **This plan is infrastructure-class** (rules / hooks / skills / CI gates — not agentic_core domain code). The agentic_core ADG does not index `.windsurf/scripts/`, `.windsurf/rules/`, `.windsurf/skills/`, or `ops_scripts/ci/`. The graph-layer primitives that drive T2/T3 *refactoring* plans do not have a counterpart for *governance-enforcement* plans.

**Substitute evidence (governance-pipeline graph):**

```
AUTHOR_GATE_PACKET emission
  ├─ flows_to → render_card.py (ui-renderer skill)
  │             ├─ flows_to → ask_user_question (built-in tool)  ← MANDATORY (this plan adds enforcement)
  │             └─ emits_side_effect → user-facing UI
  ├─ flows_to → post_cascade_author_gate_ui_audit.py  (existing — shape audit)
  ├─ flows_to → post_cascade_author_gate_pipeline_audit.py  (NEW — pipeline-completion audit)
  │             └─ writes_to → artifacts/windsurf/author_gate_pipeline_violations.jsonl
  └─ controls_flow → ops_scripts/ci/check_author_gate_pipeline_freshness.py  (NEW CI gate)
```

**Three "MV-equivalent" pre-classified concerns this plan touches:**
1. **Author-Gate hook wiring invariant** (existing AG-WIRE gate per memory 6e7e9afe) — adjacent enforcement layer.
2. **Author-Gate UI shape invariant** (existing 4-row contract per plan c4d2a8) — sibling to the new pipeline-completion invariant.
3. **Ask-without-packet vacuum closure** (existing `check_ask_user_question_packet_freshness.py`) — reverse-direction sibling to new gate.

The new gate (AGP1) is the **fourth corner** of the Author-Gate enforcement square: shape + wiring + ask-without-packet + **packet-without-ask** (this plan).

---

## §9. Test Surface

| Test file | New cases | Type | Acceptance |
|---|---|---|---|
| `tests/unit/windsurf_scripts/test_author_gate_pipeline_check.py` | ~30 | helper unit | All pass; covers packet-only / packet+ask / ask-only / no-packet / quoted-packet / multi-packet / legacy `HITL_PACKET:` alias |
| `tests/unit/ops_scripts/ci/test_check_author_gate_pipeline_freshness.py` | ~12 | CI gate unit | All pass; mirrors c4d2a8 freshness-gate test pattern (pure evaluate() + main() + bypass + fail-closed) |
| Existing AG suite | 0 new | regression | Existing tests still pass — no shape requirement changed |

**Total new tests:** ~42 · zero existing tests modified.

---

## §10. Bypass + Escape Hatches

| Env var | Effect | Use case |
|---|---|---|
| `AG_PIPELINE_AUDIT_BYPASS=1` | Audit emits warning row but does not flag violation | Scripted batch runs, acknowledged exploratory sessions |
| `AG_PIPELINE_FAIL_CLOSED=1` | CI gate exits non-zero on any unresolved violation in window | Strict CI mode (default = advisory) |
| `AG_PIPELINE_STALENESS_DAYS=N` | Override default 7-day staleness window | Tighter / looser drift tolerance per branch |

All bypass usage durably logged with `reason: "bypass"` per established pattern.

---

## §11. Acceptance Criteria

1. ✅ Post-hook fires deterministically when `AUTHOR_GATE_PACKET:` appears in response without `ask_user_question`
2. ✅ Violation row persisted in `artifacts/windsurf/author_gate_pipeline_violations.jsonl`
3. ✅ CI gate AGP1 registered + visible in `run_contract_gates.py` output
4. ✅ All 42 new tests green; zero existing AG tests regress
5. ✅ Rule §"Pipeline Completion Invariant" present + cross-references this plan slug
6. ✅ Both skills updated to mandate same-response `ask_user_question`
7. ✅ `hooks.json` schema-pure (constitutional §27); JSON parses cleanly
8. ✅ Synthetic positive control (W5.P1) demonstrates violation captured + clean response passes
9. ✅ Plan registered in Notion Plans DB with `AI Summary` populated (per `notion-plans-taxonomy.md`)

---

## §12. AG_QUEUE_SEED — Anticipated Author-Gate Decisions

```
AG_QUEUE_SEED: plan=author-gate-ui-renderer-hardening-a7f3c2 id=AGP-1 depends_on= title=Regex strictness — strict packet-marker boundary vs lenient with quoted-mention exceptions
AG_QUEUE_SEED: plan=author-gate-ui-renderer-hardening-a7f3c2 id=AGP-2 depends_on=AGP-1 title=Default mode — advisory (log only) vs fail-closed (block response) for first 14 days
AG_QUEUE_SEED: plan=author-gate-ui-renderer-hardening-a7f3c2 id=AGP-3 depends_on= title=Rule prose location — append to existing author-gate-enforcement.md vs new sibling rule file
```

---

## §13. References

- Plan `author-gate-four-req-enforcement-c4d2a8.md` (sibling pattern — pure helper + Windsurf hook + CI gate + bypass env var + durable test surface)
- Plan `author-gate-pipeline-hardening-d7e3f9.md` (parent stack)
- Plan `author-gate-deferred-scope-b8c1d4.md` (W3 sibling — `check_ag_hook_wiring.py`)
- Constitutional §6 (Author-Gate for ambiguous decisions), §27 (Windsurf config schema purity), §30 (capture health), §35 (queue drain)
- Memory `f220bb61` (4-req enforcement landing)
- Memory `6e7e9afe` (W3 hook-wiring CI gate)

---

PLAN_CREATED: slug=author-gate-ui-renderer-hardening-a7f3c2 tier=T3 status=Not_Started waves=5 phases=11 est_tokens=17k
