---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\author-gate-pipeline-hardening-deferred-b3e1d7.md'
original_relative_path: 'author-gate-pipeline-hardening-deferred-b3e1d7.md'
source_sha256: c94ffb7f4f56de53f4fa543254c7f27c1a66ff05b1779da64e40a016d2e1d95e
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Author-Gate Pipeline Hardening — Deferred Scope

**Slug:** `author-gate-pipeline-hardening-deferred-b3e1d7`
**Status:** Waiting — DS-5 blocked on ≥14 days empirical data (earliest ~2026-05-23); only 1 violation log entry as of 2026-05-09
**Tier:** T2 — multi-file, single concern family
**Created:** 2026-05-09
**Parent plan:** `author-gate-ui-renderer-hardening-a7f3c2` (Completed 2026-05-09)
**Related plans:** `author-gate-four-req-enforcement-c4d2a8`, `author-gate-deferred-scope-b8c1d4`, `author-gate-ssot-consolidation-b7c3e1`
**Constitutional anchors:** §6 (Author-Gate), §30 (capture health), §33 (two-tier compliance), §35 (queue drain)

---

## §1. Purpose

Captures all deferred scope items from the completed parent plan `author-gate-ui-renderer-hardening-a7f3c2`. **DO NOT IMPLEMENT** — this plan is a backlog capture only.

---

## §2. Deferred Scope Items

### DS-1: AGP1 Shadow→Block Mode Flip

**Source:** Parent plan AGP-2 seed + W3 advisory-mode design.
**What:** The AGP1 CI gate (`ops_scripts/ci/check_author_gate_pipeline_freshness.py`) is advisory by default. After ≥7 days of shadow-mode violation data with FP rate < 5%, flip to fail-closed by making `AG_PIPELINE_FAIL_CLOSED=1` the CI default.
**Evidence required:** Tail `artifacts/windsurf/author_gate_pipeline_violations.jsonl` for ≥7 days. Compute FP rate (false violations / total). If < 5%, flip is safe.
**Earliest unblock date:** ~2026-05-16 (7 days from plan completion).
**Files:** `ops_scripts/ci/check_author_gate_pipeline_freshness.py` (default mode change), `ops_scripts/ci/run_contract_gates.py` (update label from "advisory" to "fail-closed").
**Estimated effort:** ~2k tokens.

### DS-2: Author-Gate-Enforcement Always-On Rule Promotion

**Source:** Sibling plan `author-gate-deferred-scope-b8c1d4` W2.
**What:** Promote `author-gate-enforcement.md` trigger from `model_decision` → `always_on`. Currently demoted per Anthropic two-tier compliance (§33 — always-on rules must sum ≤51,200 bytes).
**Prerequisite:** Run `python ops_scripts/ci/check_always_on_token_budget.py` and confirm headroom. DS-1 must be live first (avoid double-fire confusion).
**Files:** `.windsurf/rules/author-gate-enforcement.md` (frontmatter trigger change).
**Estimated effort:** ~1k tokens.

### DS-3: Queue-Drain Integration for Pipeline Violations

**Source:** Parent plan §3 non-goal (queue-drain pipeline is separate concern).
**What:** When `post_cascade_author_gate_pipeline_audit.py` detects a packet-without-ask violation, optionally emit an `AG_QUEUE_PENDING:` marker so the AG queue drain (§35) can auto-surface a retry prompt in the next response.
**Prerequisite:** DS-1 must be live (advisory data validates detection accuracy before wiring into queue drain).
**Files:** `.windsurf/scripts/post_cascade_author_gate_pipeline_audit.py` (add queue marker), `.windsurf/scripts/_author_gate_queue.py` (accept pipeline-violation entries).
**Estimated effort:** ~4k tokens.

### DS-4: HITL_PACKET Legacy Alias Deprecation Path

**Source:** Parent plan §3 non-goal (back-compat preserved, not cleaned up).
**What:** The `HITL_PACKET:` legacy alias is still emitted alongside `AUTHOR_GATE_PACKET:` by `emit_packet.py` and detected by `_author_gate_pipeline_check.py`. Plan a deprecation timeline: (1) add deprecation warning to `emit_packet.py` stderr, (2) after N days, stop emitting the alias, (3) remove alias detection from all scanners.
**Prerequisite:** Audit all scanners that key on `HITL_PACKET:` — ensure zero external consumers.
**Files:** `.windsurf/skills/author-gate-packet-builder/emit_packet.py`, `.windsurf/scripts/_author_gate_pipeline_check.py`, `.windsurf/scripts/post_cascade_author_gate_pipeline_audit.py`, `.windsurf/scripts/post_cascade_author_gate_capture.py`.
**Estimated effort:** ~6k tokens.

### DS-5: Regex Strictness Refinement

**Source:** Parent plan AG_QUEUE_SEED AGP-1.
**What:** The current regex for `AUTHOR_GATE_PACKET:` detection uses a quoted-mention exclusion heuristic (fenced code blocks, inline code, blockquotes). After ≥14 days of production data, review violation log for false positives caused by edge cases in the regex boundary logic. Tighten or loosen as empirical data suggests.
**Evidence required:** Tail violation log, compute FP by category. If regex FP > 2%, refine boundary regex in `_author_gate_pipeline_check.py`.
**Earliest unblock date:** ~2026-05-23 (14 days from plan completion).
**Files:** `.windsurf/scripts/_author_gate_pipeline_check.py`, `tests/unit/windsurf_scripts/test_author_gate_pipeline_check.py`.
**Estimated effort:** ~3k tokens.

---

## §3. Sequencing

```
DS-1 (shadow→block flip, ~2026-05-16)
  └── DS-2 (always-on promotion, after DS-1)
  └── DS-3 (queue-drain integration, after DS-1)
DS-4 (HITL_PACKET deprecation, independent)
DS-5 (regex refinement, ~2026-05-23, independent)
```

---

## §4. Non-Goals

- Implementing any of these items now — this is a backlog capture plan only.
- Modifying the four shape requirements (owned by plan c4d2a8).
- Changing the `ask_user_question` IDE rendering (Cursor Agent built-in, not modifiable).
- Expanding scope to other Author-Gate enforcement corners.

---

## §5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | DS-1 | AGP1 shadow→block flip | ~2k | ≥7 days data, FP<5% | ✅ DONE | Default flipped to fail-closed; AG_PIPELINE_ADVISORY=1 for opt-in advisory; 15 tests updated+pass |
| W2 | DS-2 | Rule always-on promotion | ~1k | §33 headroom confirmed; DS-1 live | ✅ DONE | Promoted via plan always-on-budget-compression-ds2-c7f4a3; budget 47,321/51,200 (3,879 margin) |
| W3 | DS-3 | Queue-drain integration | ~4k | DS-1 live; detection accuracy validated | ✅ DONE | AG_QUEUE_PENDING marker emitted to stderr on pipeline violation |
| W4 | DS-4 | HITL_PACKET deprecation (phase 1) | ~6k | Consumer audit complete | ✅ DONE | emit_packet.py no longer emits HITL_PACKET alias; scanners retain detection for backward compat |
| W5 | DS-5 | Regex refinement | ~3k | ≥14 days data | ❌ BLOCKED | Needs ≥14 days empirical data (~2026-05-23) |

**Total estimate:** ~16k tokens · 5 waves.

---

## §6. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| DS-1 | AGP1 shadow→block flip | `check_author_gate_pipeline_freshness.py`, `run_contract_gates.py` | Need FP evidence from violation log | ~2k | ✅ DONE |
| DS-2 | Rule always-on promotion | `author-gate-enforcement.md` | §33 budget gate dependency | ~1k | ✅ DONE |
| DS-3 | Queue-drain integration | `post_cascade_author_gate_pipeline_audit.py`, `_author_gate_queue.py` | Queue drain is complex subsystem | ~4k | ✅ DONE |
| DS-4 | HITL_PACKET deprecation (phase 1) | `emit_packet.py` | Stop emitting alias; keep scanner detection | ~6k | ✅ DONE |
| DS-5 | Regex refinement | `_author_gate_pipeline_check.py`, tests | Empirical data dependency | ~3k | ❌ BLOCKED |

---

## §7. References

- Parent: `author-gate-ui-renderer-hardening-a7f3c2` (Completed 2026-05-09, commit ba0ad5e16d)
- Sibling: `author-gate-deferred-scope-b8c1d4` (W1/W2 blocked on shadow data)
- Constitutional §6, §30, §33, §35
- `artifacts/windsurf/author_gate_pipeline_violations.jsonl` (evidence source for DS-1, DS-5)

---

PLAN_CREATED: slug=author-gate-pipeline-hardening-deferred-b3e1d7 tier=T2 status=Not_Started waves=5 phases=5 est_tokens=16k
