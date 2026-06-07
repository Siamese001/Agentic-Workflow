---
slug: cursor-naming-rename-w5-b4f1a9
plan_type: platform_core_change
status: Not Started
created: 2026-06-07
owner: Claude Code
supersedes: []
relates_to:
  - cursor-windsurf-codeium-decommission-dec0de   # this plan is the split-out W5 (live-wiring rename)
---

# Cursor/Windsurf Live-Wiring Rename — Neutral Names for the Governance Engine

> Split out of [cursor-windsurf-codeium-decommission-dec0de](../.claude/plans/cursor-windsurf-codeium-decommission-dec0de.md)
> at its W5 gate (2026-06-07, decision `deletion_strategy selected=split_w5_to_own_plan`). The parent
> plan already delivered a **brand-free prose surface** (W3 P3.1 + W4). What remains is the
> high-blast-radius **internal rename of live wiring that is merely *named* after the deprecated IDEs**.
> Blast-radius map: parent plan `## P5.1 Blast-Radius Map`.

## Context (SCQA)

- **Situation.** The live Claude Code governance engine still carries Cursor/Windsurf *names*:
  ~30 `post_cursor_agent_*.py` scripts, the `artifacts/cursor/` audit + session-state sink,
  `tools/windsurf/` plan-lifecycle tools, and the `.cursor/state/` Author-Gate ledger root.
  All are functionally live and load-bearing.
- **Complication.** P5.1 found ~**800+ reference updates** across 4 coupled renames, with **live
  session-state** (`before_mcp_execution.py`) **and a live decision ledger** (`refactor_decision_ledger.sqlite`)
  inside the blast radius, **two boundary-protected `agentic_core/` edits** required, a self-referential
  shell guard, a GitHub Actions workflow that hard-codes the ledger path, and a **partially-started
  prior rename** to reconcile. A single-wave rename is unsafe.
- **Question.** How to reach neutral names without losing capture/session state or breaking the
  governance chain / CI?
- **Answer.** One isolated sub-wave per rename target, lowest-risk first, each with its own
  gate-verify and (where core is touched) Author-Gate + migration receipt. Dual-read migration for
  stateful paths. A dedicated rollback tag before any change.

> **Critical correction inherited from P5.1:** `.cursor/` is **NOT dead** — `.cursor/state/` holds the
> live Author-Gate ledger + `plan_registration_cache.json` + `author_gate_queue/`
> (`agentic_core/L0_routing/config/path_constants.py:189 CURSOR_STATE_DIR`, GH-workflow upload). The
> ledger rename is **migrate-then-delete**, never delete.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | R1.1–R1.2 | Safety prep + ledger-drift resolution | ~8k | `.cursor/state` vs `.claude/state` resolvable from refs | ✅ Done (2026-06-07) | Tag `pre-w5-rename-b4f1a9`@d345db6 set. **Ledger drift RESOLVED:** authoritative = `.claude/state/refactor_decisions/refactor_decision_ledger.sqlite` (live 188KB, `ledger_paths.py` SSOT, §30). `.cursor/state/` is empty; `path_constants.CURSOR_STATE_DIR` is a dead constant → **W5 needs no data migration** (see R1.2 note). |
| W2 | R2.1–R2.2 | `tools/windsurf/` → `tools/plan_lifecycle/` (lowest risk) | ~10k | Compat shim viable; prior `rewrite_windsurf_refs_to_cursor.py` map reusable | ⬜ Not Started | 3 tools moved + shim; importlib consumer + CLI + companion updated; smoke run exits 0 |
| W3 | R3.1–R3.2 | `post_cursor_agent_*.py` → `post_agent_*.py` | ~14k | Dispatch + deny-token guard editable atomically | ⬜ Not Started | Scripts renamed; dispatch/CI/tests updated; after-agent chain fires; gates green |
| W4 | R4.1–R4.3 | `artifacts/cursor/` → `artifacts/governance/` (highest risk) | ~16k | Dual-read migration preserves in-flight session-state | ⬜ Not Started | Dual-read live; writers updated; no lost session-state; gates green |
| W5 | R5.1–R5.3 | Ledger **dead-pointer cleanup** (core + CI) — *risk downgraded by R1.2* | ~6k | Data already at `.claude/state`; no migration | ⬜ Not Started | Dead `path_constants.CURSOR_STATE_DIR` removed (Author-Gate); GH workflow repointed to `.claude/state`; schema-doc comment fixed; empty `.cursor/state` deleted |
| W6 | R6.1–R6.2 | Deferred dec0de W3 config + final guard restore | ~8k | `_legacy_windsurf` importers migrated by now | ⬜ Not Started | `excluded_paths`/`path_constants` mirror cleaned + drift gate green; `T6a` retired or repointed; shell guard restored at new tokens |
| W7 | R7.1 | Verify zero-brand + close | ~4k | All prior waves green | ⬜ Not Started | Repo scan: only intentional history remains; both plans closed |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| R1.1 | Rollback tag | git tag | — | ~1k | ✅ Done — `pre-w5-rename-b4f1a9`@d345db6 |
| R1.2 | Resolve ledger drift | `path_constants.py`, `.github/workflows/author-gate-gates.yml`, `decision_ledger.schema.sql`, `.cursor/state/**`, `.claude/state/**` | Two locations referenced; must pick authoritative + reconcile data | ~7k | ✅ Done — authoritative=`.claude/state`; `.cursor/state` empty; no data migration needed |
| R2.1 | Move `tools/windsurf/` → `tools/plan_lifecycle/` + compat shim | `tools/windsurf/**` (3 tools) | Sunset shim; importlib string consumer | ~6k | ⬜ |
| R2.2 | Update consumers | `post_cursor_agent_wave_lifecycle_capture.py`, `agents-tier1-companion.md`, CLI refs, CI gates | importlib module string | ~4k | ⬜ |
| R3.1 | Rename `post_cursor_agent_*.py` → `post_agent_*.py` | ~30 scripts + `_legacy_cursor/` | Atomic with dispatch + deny-token | ~9k | ⬜ |
| R3.2 | Update dispatch + CI + tests | `after_agent_governance_dispatch.py`, `lib/claude_hook_common.py`, `lib/mcp_before_hygiene.py`, `check_post_cursor_agent_*.py`, `check_cursor_optimized_config.py`, ~50 tests | Reconcile already-renamed `hooks/cursor/test_post_agent_*` | ~5k | ⬜ |
| R4.1 | Add dual-read for `artifacts/cursor/` ↔ `artifacts/governance/` | `before_mcp_execution.py`, shared path helper | In-flight session_state must not be lost | ~6k | ⬜ |
| R4.2 | Migrate writers | ~50 writer scripts + CI + calibration | High count | ~6k | ⬜ |
| R4.3 | Cut over + drop legacy read | path helper | Order-sensitive | ~4k | ⬜ |
| R5.1 | Author-Gate + edit `CURSOR_STATE_DIR` | `agentic_core/L0_routing/config/path_constants.py:189` | Boundary edit → receipt | ~4k | ⬜ |
| R5.2 | Migrate ledger data + update workflow | `.cursor/state/**` → `.claude/state/**`, `.github/workflows/author-gate-gates.yml`, schema doc | Live SQLite; CI artifact path | ~5k | ⬜ |
| R5.3 | Update consumers | `refactor-decision-memory` skill, `decision_ledger.schema.sql` | path refs | ~3k | ⬜ |
| R6.1 | Clean dec0de-deferred config | `config/excluded_paths.yaml` + `path_constants.py` frozensets + `T6a` in `.pre-commit-config.yaml` | Drift gate; Author-Gate for core | ~5k | ⬜ |
| R6.2 | Restore shell guard | `before_shell_execution.py` | Drop dead tokens / guard new names | ~3k | ⬜ |
| R7.1 | Zero-brand scan + close | whole repo, Notion | Distinguish history from leakage | ~4k | ⬜ |

## Wave Detail

### W1 — Safety prep + ledger-drift resolution ✅ DONE (2026-06-07)
- **R1.1** ✅ `git tag pre-w5-rename-b4f1a9` @ `d345db6`.
- **R1.2** ✅ **RESOLVED. Authoritative ledger = `.claude/state/refactor_decisions/refactor_decision_ledger.sqlite`.**
  Evidence (DIRECTLY OBSERVED): (1) only ledger DB on disk is at `.claude/state/...` (188 KB, mtime 2026-06-07 15:06);
  (2) `tools/refactor_decisions/ledger_paths.py:3,16` declares the writable SSOT there; (3) `ops_scripts/ci/_governance_paths.py:17`
  resolves `CURSOR_STATE_DIR → .claude/state`; (4) constitutional §30.
  - `.cursor/state/` on disk = empty (only an empty `author_gate_queue/`). **No live ledger data there.**
  - `agentic_core/L0_routing/config/path_constants.py:189 CURSOR_STATE_DIR=".cursor/state"` is a **dead constant**
    (only refs: its own def + `__all__` export; no functional importer — the live code uses `ledger_paths.py` / `_governance_paths.py`).
  - `.github/workflows/author-gate-gates.yml` uploads from `.cursor/state/...` → **already a broken/empty-path upload**.
  - **Correction to P5.1 / dec0de W2:** the earlier "deleting `.cursor/` destroys the live ledger" warning was DERIVED from
    stale path *references*; disk truth shows `.cursor/state` is empty. W5 ledger work is therefore **dead-pointer cleanup**, not
    data migration — `.cursor/state` is safe to delete.

### W2 — `tools/windsurf/` → `tools/plan_lifecycle/` (lowest risk first)
- **R2.1** `git mv` the 3 tools; leave a compat shim at `tools/windsurf/` for the sunset window.
- **R2.2** Update the importlib string in `post_cursor_agent_wave_lifecycle_capture.py`, the
  `agents-tier1-companion.md` CLI line, and CI gates. Reuse the map in
  `ops_scripts/maintenance/rewrite_windsurf_refs_to_cursor.py`.
- **Gate:** `python -m tools.plan_lifecycle.wave_execution_state status` exits 0.

### W3 — `post_cursor_agent_*.py` → `post_agent_*.py`
- **R3.1/R3.2** Rename scripts AND update dispatch wiring (`_AG_CHAIN`, `_SCRIPT_EXTRA_ARGS`,
  `lib/claude_hook_common.py`, `lib/mcp_before_hygiene.py`), the deny-token list in
  `check_cursor_optimized_config.py`, the alive/payload/wiring CI gates, and ~50 tests — atomically.
  Reconcile the already-renamed `tests/unit/ops_scripts/hooks/cursor/test_post_agent_*.py`.
- **Gate:** run the after-agent dispatch once → audit rows still produced; `check_ag_hook_wiring.py` green.

### W4 — `artifacts/cursor/` → `artifacts/governance/` (highest risk)
- **R4.1** Introduce a path helper with **dual-read** (read new, fall back to old) and write-new; migrate
  existing `session_state_*.json`. **R4.2** Update ~50 writers. **R4.3** Drop legacy read after one cycle.
- **Gate:** full `run_contract_gates.py`; verify no session-state loss across a live turn.

### W5 — `.cursor/state/` → `.claude/state/` ledger (core + CI)
- **R5.1** Author-Gate (`platform_core_change`) + edit `CURSOR_STATE_DIR` with migration receipt.
- **R5.2** Migrate ledger SQLite + queue/cache; update `.github/workflows/author-gate-gates.yml` (4 refs +
  upload path) and `decision_ledger.schema.sql` header atomically. **R5.3** Update the
  `refactor-decision-memory` skill path.
- **Gate:** AG ledger row count preserved; CI artifact upload resolves new path.

### W6 — Deferred dec0de W3 config + guard restore
- **R6.1** Now that `_legacy_windsurf` importers are migrated (W2–W3), clean the windsurf entries in
  `config/excluded_paths.yaml` + the `agentic_core/.../path_constants.py` frozenset mirror (Author-Gate +
  receipt), keep the drift gate green; retire or repoint `T6a no-active-windsurf-authoring`.
- **R6.2** Update `before_shell_execution.py` to drop dead tokens / guard the new names.

### W7 — Verify + close
- **R7.1** Repo-wide scan; remaining `cursor|windsurf` hits must be intentional history. Close this plan
  and flip dec0de W5/W6 to done.

## Definition of Done

| # | Criterion | Verify / Defer |
|---|-----------|----------------|
| 1 | Rollback tag `pre-w5-rename-b4f1a9` exists before any change | Verify: `git tag` |
| 2 | Authoritative Author-Gate ledger location decided + documented before any ledger move | Verify: decision note in plan |
| 3 | `tools/plan_lifecycle/` live with compat shim; `python -m tools.plan_lifecycle.wave_execution_state status` exits 0 | Verify: exit code |
| 4 | After-agent governance chain still fires post script-rename (audit rows produced) | Verify: run dispatch, inspect artifact dir |
| 5 | No Author-Gate ledger rows lost across the ledger migration | Verify: row count before/after |
| 6 | No session-state lost across `artifacts/cursor/`→`artifacts/governance/` cutover | Verify: live turn + file check |
| 7 | Each `agentic_core/` edit carries a migration receipt + Author-Gate PASS | Verify: receipt path |
| 8 | `python ops_scripts/ci/run_contract_gates.py` exits 0 after each wave | Verify: command output |
| 9 | GitHub Actions `author-gate-gates.yml` resolves the new ledger path (CI green) | Verify: workflow run |
| 10 | Repo scan finds only intentional historical Cursor/Windsurf mentions | Verify: Grep with allowlist |

**Verification vs Deferral:** W2 (tools rename) and W3 (script rename) are the committed low/medium-risk
core. W4 (session-state) and W5 (ledger + core + CI) are high-risk and each independently deferral-eligible
— if any wave's pre-flight shows unacceptable blast radius, stop and re-gate rather than forcing it.

## Risk / blast-radius notes
- **Highest risk:** W4 (`artifacts/cursor/` live session-state) and W5 (live ledger + core + GH workflow).
- **Self-referential guard:** `before_shell_execution.py` blocks `.windsurf`/`post_cursor_agent` shell
  tokens — neutralize for rename waves, restore in R6.2. Use native file tools / `git mv` where possible.
- **Boundary edits:** R5.1 + R6.1 touch `agentic_core/` → Author-Gate + receipt each.
- **Prior in-flight rename:** reconcile `hooks/cursor/test_post_agent_*` + `rewrite_windsurf_refs_to_cursor.py`.
