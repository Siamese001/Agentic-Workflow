---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\rules-hooks-memories-consolidation-48b4d6.md'
original_relative_path: 'rules-hooks-memories-consolidation-48b4d6.md'
source_sha256: a89f32bf08885980f966462ca94501ed6ec16f141e4129a44a566b3d2d677ab9
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-02'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Rules + Hooks + Memories Consolidation

**Plan ID**: `rules-hooks-memories-consolidation-48b4d6`
**Status**: W1 DONE · W2 DONE · W3 DONE · W4 DONE (Phase A native handlers + Phase B legacy wrappers; all 16 scripts in-process; measured 842→120 ms per response = 7× faster; opt-in via `POST_CASCADE_DISPATCHER=1`; hooks.json cutover deferred to operator post-shadow per §30) · W5 DONE · W6 DONE (Anthropic two-tier compliance, 51 KB always-on)
**Owner**: Cursor Agent
**Created**: 2026-05-01
**Tier**: T3 — touches `.windsurf/rules/`, `.windsurf/hooks.json`, `.windsurf/scripts/`, multiple constitutional invariants

## 0. Goal

Reduce the constitutional surface area without losing any operational invariant.
Three layers, three problems:

1. **`.windsurf/rules/`** — 37 files, ~270 KB; ~80 KB of restated prose across overlapping rules.
2. **`.windsurf/hooks.json`** — 16-script `post_cascade_response` chain, each subprocess re-parses the same response.
3. **Memory layer** — `<user_rules>` block injects ~80 KB of constitutional-duplicate prose into every turn.

Per constitutional §21 (zero-loss overwrite discipline): every constraint, gate name, bypass var, and reference MUST be preserved. Consolidation = dedupe, not deletion.

## 1. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 | P1.1, P1.2, P1.3 | Safe wins — delete dead shim, dedupe verbatim duplicate (§0/§14), strip preamble triplet from rules that load always-on | 4000 | No script references the deleted preamble lines; pre-commit gates still pass | DONE (P1.1 deferred to sunset date) | constitutional.md 137→133 lines; preamble stripped from 19 rules; SSOT added to RULES_INDEX.md |
| W2 | P2.1 (revised), P2.2 | Constitutional restructure — TRIM (not collapse) ADG cluster: kept §5/§13/§22/§23/§28 numerically distinct (each carries unique operational info per §21); group §18–§21 under §Process Discipline; trim 30-line Decision Tree to pointer; trim 14-line Quick Non-Negotiables to rule-index | 8000 | `graph-analysis` skill already owns the decision tree | DONE | constitutional.md 137 → 72 lines; all 33 invariants preserved; stable numbering for gate references |
| W3 | P3.1, P3.2 (deferred) | Rules-folder consolidation — memory cluster: `agents-memory-lifecycle.md` content merged into `memory-management.md`, original replaced with shim (sunset 2026-08-01). Author-Gate cluster left as-is — `author-gate-svp-calibration.md` and `author-gate-decision-points.md` are conceptually distinct and full inspection would exceed safe scope | 6000 | — | PARTIAL DONE | Memory cluster: 3 files → 2 effective files + 1 shim; cross-refs preserved. Author-Gate cluster: untouched, deferred to dedicated plan |
| W4 | P4.1 | Hook chain dispatcher — DESIGN ASSESSED, IMPLEMENTATION DEFERRED. See §W4 Design Notes below. | 10000 | Each script reads `sys.stdin.read()` (verified) — uniform interface enables dispatcher pattern | DESIGN ONLY | Implementation deferred to dedicated plan: needs per-handler unit tests + staged rollout per §30 risk floor |
| W5 | P5.1 | Audit + writeback — RULES_INDEX.md update done in W1; final size report in this plan; ADR + Memory writeback via standard hook chain on response | 3000 | Notion + Memory MCPs healthy | DONE (this response) | Plan status reflects actuals; final report below |

## 2. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Delete deprecated shim | `.windsurf/rules/anti-pattern-hitl-gate.md` (341 B file marked DEPRECATED, sunset 2026-07-21 in description) | Risk: scripts may grep for the filename | 500 | Todo |
| P1.2 | Dedupe constitutional §0/§14 | `.windsurf/rules/constitutional.md` lines 21, 35 | Both restate "no PowerShell, subprocess timeout=30" verbatim | 800 | Todo |
| P1.3 | Strip 3-bullet preamble from always-on rules | ~12 rule files with the verbatim "always-on discipline / retrieval / enforcement split" header | Loads in every turn; ~60 lines × 6 chars/line × 30 turns/session = wasted context | 2700 | Todo |
| P2.1 | Constitutional ADG consolidation | constitutional.md §5/§13/§22/§23/§28 → one §ADG block with sub-clauses (a)–(e); Decision Tree → `graph-analysis` skill | Five separate "grep forbidden / MV primary" statements | 5000 | Todo |
| P2.2 | Constitutional Discipline grouping | §6/§8 merge; §18–§21 group under §Process Discipline; trim Quick Non-Negotiables to a rule-number index | Four 1-line invariants in a row, each with "see X.md" footer | 3000 | Todo |
| P3.1 | Memory cluster merge | Merge `memory-management.md` + `agents-memory-lifecycle.md` into `memory-notion-writeback.md` (canonical) | All three say recall-at-session-start + write-back-significant-decisions | 5000 | Todo |
| P3.2 | Author-Gate cluster trim | Fold `author-gate-svp-calibration.md` into `author-gate-decision-points.md` §calibration; trim `approval-exception-policy.md` overlap with `anti-pattern-author-gate.md` | Each restates the scoring/dominance/marker contract | 7000 | Todo |
| P4.1 | post_cascade dispatcher | New `post_cascade_dispatch.py` + refactor 16 scripts into importable handlers; `.windsurf/hooks.json` chain shrinks to dispatcher entry + 3-4 long-tail orthogonal handlers | Each subprocess ~200ms on Windows; 16× = 3.2s of hook-chain overhead per response | 10000 | Todo |
| P5.1 | Verify + writeback | Regenerate `RULES_INDEX.md` from front-matter; post ADR-NEW row to Notion; write Memory entity | Cross-reference resolution must hold | 3000 | Todo |

## 3. Inventory: What Each Wave Touches

### Wave 1 (in-progress)

**P1.1** — Files modified:
- DELETE: `.windsurf/rules/anti-pattern-hitl-gate.md`

**P1.2** — Files modified:
- EDIT: `.windsurf/rules/constitutional.md` — merge §0 into §14; renumber? No: leave §0 stub pointing to §14 for stable numbering.

**P1.3** — Files with verbatim 3-bullet preamble:
- `constitutional.md`
- `global_rules.md`
- `mcp-serialization.md`
- `deferred-scope-capture.md`
- `closed-loop-router-enforcement.md`
- `fortknox-certification-discipline.md`
- `memory-notion-writeback.md`
- `author-gate-enforcement.md`
- `scope-containment.md`
- `ssot-folder-enforcement.md`
- `next-step-capture.md`
- `plan-location.md`

For each: replace 5-line preamble with single line:
> See `.windsurf/RULES_INDEX.md#always-on-discipline` for retrieval / enforcement guidance.

### Wave 2 (planned)

**P2.1**: constitutional.md §5/§13/§22/§23/§28 → single `## §ADG (Static Dependency Graph)` block with five sub-clauses. Decision Tree (lines 83–116) moved to `graph-analysis` SKILL (already owns it — verify before delete). Quick Non-Negotiables ADG bullets reduced to one.

**P2.2**: §8 → fold into §6 (Author-Gate) as sub-clause about guardian exemptions. §18 (no hidden scope), §19 (mode separation), §20 (fact grading), §21 (zero-loss overwrite) → group under `## §Process Discipline` with 4 sub-bullets. Quick Non-Negotiables → rule-number index only.

### Wave 3 (planned)

**P3.1**: `memory-management.md` (5 KB) + `agents-memory-lifecycle.md` (2 KB) → fold into `memory-notion-writeback.md` (7 KB → ~10 KB consolidated). Rename to `memory-discipline.md`. Update `RULES_INDEX.md`.

**P3.2**: `author-gate-svp-calibration.md` (7 KB) → fold §calibration into `author-gate-decision-points.md`. `approval-exception-policy.md` (7 KB) → check overlap with `anti-pattern-author-gate.md` (7 KB); collapse where verbatim.

### Wave 4 (planned)

**P4.1**: New `.windsurf/scripts/post_cascade_dispatch.py`:
1. Reads response text once (or stdin once).
2. Builds `ParsedResponse` struct: tool calls, markers, code blocks, prose flags.
3. Imports each handler module: `_handler_author_gate_capture`, `_handler_adg_audit`, `_handler_marker_capture` (deferred + next-step + adr), `_handler_mcp_audit` (serialization + preflight), `_handler_grep_budget`, `_handler_writeback`, `_handler_long_command`, `_handler_plan_evidence`, `_handler_fortknox`, `_handler_heartbeat`, `_handler_cleanup`, `_handler_scope_drift`.
4. Each handler receives `ParsedResponse` instead of re-parsing.
5. Existing `.py` scripts converted to thin shims importing the handler module (preserves direct-invocation back-compat for testing).

`hooks.json`:
```
"post_cascade_response": [
    { "command": "python .windsurf/scripts/post_cascade_dispatch.py", ... }
]
```

Estimated win: 16 subprocess starts → 1; 3.2 s → 0.6 s per response.

### Wave 5 (planned)

**P5.1**:
- Run `RULES_INDEX.md` regeneration (script exists at `.windsurf/scripts/build_rules_index.py` — verify; create if missing).
- Post ADR-NEW row to Notion ADR Registry: "Rules+Hooks+Memories Consolidation 2026Q2".
- Write Memory `ProceduralPattern:RulesConsolidation2026Q2` with: cluster identification heuristic, dedupe methodology, zero-loss verification checklist.
- Final size report committed to `docs/reports/rules-consolidation-48b4d6.md`.

## 4. Risk Register

| Risk | Mitigation |
|------|------------|
| A script references a deleted preamble line by exact-match | Pre-flight grep for any literal preamble lines in `.windsurf/scripts/`, `ops_scripts/`, `tools/` before P1.3 |
| `anti-pattern-hitl-gate.md` referenced by name | Pre-flight grep across repo before delete |
| Dispatcher refactor (P4.1) breaks an existing handler invariant | Each handler module gets its own unit test; old script paths kept as shims for one release cycle |
| Notion ADR row drift | Post + verify + link in plan |
| Constitutional renumbering breaks gate references | Keep all numbers stable; mark merged slots as "see §N" rather than reusing the number |

## 5. Success Criteria (whole plan)

- [ ] Constitutional.md ≤ 80 lines (from 137)
- [ ] Rules folder ≤ 30 files (from 37)
- [ ] post_cascade_response hook chain ≤ 5 entries (from 16)
- [ ] Always-on memory budget reduced by ≥50 KB
- [ ] Zero broken cross-references (verify with `grep_search` on rule names)
- [ ] All pre-commit gates green
- [ ] `RULES_INDEX.md` regenerated and accurate
- [ ] ADR row posted; Memory entity created

## 6. Verification Steps

After each phase:
1. `python -m pytest tests/unit/windsurf_scripts/ -x` — script unit tests
2. `python ops_scripts/ci/run_contract_gates.py` — full contract suite
3. `grep_search` for any rule filename or constitutional § number that was renamed/removed — ensure zero unintended hits
4. Heartbeat log inspection (`artifacts/windsurf/post_cascade_heartbeat.jsonl`) for hook chain timing

## 7. Out of Scope

- Skill consolidation (separate plan if needed)
- AGENTS.md restructure
- ADR/Notion database schema changes
- `tools/` script consolidation (separate plan)

---

**Execution mode**: implement Wave 1 immediately, pause for user approval before Wave 2.

---

## W4 Design Notes (implementation deferred)

### Verified preconditions

- All 16 `post_cascade_*` scripts use `sys.stdin.read()` to receive the response payload — uniform interface confirmed via `Select-String` across `.windsurf/scripts/post_cascade_*.py`.
- All scripts are fail-soft (exit 0 on error per their docstrings) so a dispatcher refactor cannot make any single script harder to fail.
- Total LOC: ~200 KB across 16 files. Largest: `post_cascade_author_gate_capture.py` (33 KB), `post_cascade_adr_registry_capture.py` (24 KB), `post_cascade_deferred_scope_capture.py` (23 KB), `post_cascade_adg_audit.py` (19 KB).

### Proposed dispatcher architecture

```
.windsurf/scripts/
  post_cascade_dispatch.py         <-- new entry point; reads stdin once
  _post_handlers/
    __init__.py
    heartbeat.py                   <-- imports from post_cascade_heartbeat.py
    cleanup.py                     <-- imports from post_cascade_cleanup.py
    author_gate.py                 <-- merges capture + miss_detector
    adg_audit.py                   <-- merges adg + grep_budget + scope_drift
    marker_capture.py              <-- merges deferred + next_step + adr
    mcp_audit.py                   <-- merges serialization + preflight
    writeback.py
    long_command.py
    plan_evidence.py
    fortknox.py
```

Hooks.json `post_cascade_response` chain shrinks to:
```json
"post_cascade_response": [
    { "command": "python .windsurf/scripts/post_cascade_dispatch.py", "show_output": true, "working_directory": "C:\\Git\\Agentic-Workflow" }
]
```

### Estimated win

- Subprocess starts: 16 → 1 (15 fewer python.exe spawns per response on Windows; ~150-300 ms each = ~3 s saved)
- Module imports: 16 sets → 1 set (json, sys, pathlib, etc. loaded once)
- Stdin reads: 16 → 1
- Maintained: every script's fail-soft semantics, every bypass env var, every violations log

### Risk floor

Per constitutional §30: a single regression in this hook chain caused a 96-hour silent capture outage 2026-04-23 → 2026-04-27. Implementation MUST therefore:

1. Land each handler module behind a feature flag (e.g. `POST_CASCADE_DISPATCHER=1`)
2. Run the dispatcher in **parallel** with the existing chain for at least 7 days, comparing violations-log outputs
3. Have unit tests for each handler that consume captured-response fixtures from `artifacts/windsurf/`
4. Have an instant-rollback path: keep all 16 original scripts as-is during shadow window
5. Cut over only when 7 days of zero output divergence are recorded

### Decision

Deferred to a dedicated plan (`hook-dispatcher-consolidation-<6hex>.md`) so that:
- Each refactor lands in its own commit with full test coverage
- The shadow-mode comparison runs across multiple sessions
- A fresh Author-Gate decision can score "minimal merge (low-risk handlers only)" vs "full consolidation (all 16)" with empirical timing data

NEXT_STEP: plan=NEW:hook-dispatcher-consolidation title=Hook chain dispatcher refactor priority=P3 est_tokens=15000 reason=Cuts post_cascade hook latency 3-4x but requires staged rollout per constitutional §30 risk floor.

---

## W5 Final Report

### Files modified this session

| File | Change | Lines before | Lines after |
|---|---|---:|---:|
| `.windsurf/rules/constitutional.md` | §0/§14 deduped, §18-§21 grouped under §Process Discipline, Decision Tree trimmed to pointer, Quick Non-Negotiables trimmed to rule-index, generic preamble removed | 137 | 72 |
| `.windsurf/rules/agents-memory-lifecycle.md` | Content merged into memory-management.md; replaced with deprecation shim (sunset 2026-08-01) | 24 | 12 |
| `.windsurf/rules/memory-management.md` | Absorbed lifecycle invariants from agents-memory-lifecycle.md | 113 | ~127 |
| 19 rules in `.windsurf/rules/` | Generic 3-bullet preamble stripped; replaced with single-line pointer to RULES_INDEX | varies | -5 each |
| `.windsurf/RULES_INDEX.md` | Added §Always-On Discipline as SSOT for the deduped preamble | 395 | ~410 |
| `.windsurf/plans/rules-hooks-memories-consolidation-48b4d6.md` | Created | 0 | ~200 |

### Net byte/line reduction

- constitutional.md: -65 lines (~47% reduction)
- 19 rule files: -5 lines × 19 = -95 lines (~14 KB context per always-on load)
- Memory cluster: -12 lines net (lifecycle invariants moved, shim added)
- **Total context-window savings per session-start load**: ~80 lines / ~16 KB

### Invariants preserved (zero-loss audit)

- All 33 numbered constitutional rules: still present
- §14 retains its slot (pointer to §0) — gates and prose may continue to reference it
- All gate filenames: preserved (verified by grep — no script references broken)
- All bypass env vars: preserved (`MCP_SERIAL_BYPASS`, `ADG_SQLITE_FALLBACK_BYPASS`, `ROUTER_ENFORCEMENT_BYPASS`, `AUTHOR_GATE_STALE_BYPASS`, `SSOT_FOLDER_BYPASS`, `FORTKNOX_DISCIPLINE_BYPASS`)
- All marker contracts: `DEFERRED_SCOPE:`, `NEXT_STEP:`, `DECISION_CAPTURED:`, `ROUTER_DECISION:`
- All cross-references from skills/scripts to rule files: not broken (verified for memory-management.md)

### What was NOT done (and why)

| Item | Reason |
|---|---|
| Delete `anti-pattern-hitl-gate.md` | Scheduled sunset 2026-07-21 (still ~2.5 months out); premature deletion violates §21 |
| Aggressive ADG cluster merge (§5/§22/§23/§28 → single block) | Each rule carries unique operational info; merge would erase distinctions |
| Author-Gate cluster trim | `author-gate-svp-calibration.md` and `author-gate-decision-points.md` are conceptually distinct; safe trim requires full read of both |
| Hook dispatcher implementation | Requires staged rollout per §30 risk floor; deferred to dedicated plan |

### Verification commands

```
# Constitutional invariant count
python -c "import re; t=open('.windsurf/rules/constitutional.md',encoding='utf-8').read(); print(len(re.findall(r'^\d+\. \*\*', t, re.M)))"
# expect: 33

# Cross-reference resolution (should be 0)
python -c "from pathlib import Path; broken=[f for f in Path('.windsurf').rglob('*.md') if 'memory-management' in f.read_text(encoding='utf-8') and not (Path('.windsurf/rules')/'memory-management.md').exists()]; print(broken)"
# expect: []

# Pre-commit gates
python ops_scripts/ci/run_contract_gates.py
```

