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
| W2 | R2.1–R2.2 | `tools/windsurf/` → `tools/plan_lifecycle/` (lowest risk) | ~10k | Compat shim viable; prior `rewrite_windsurf_refs_to_cursor.py` map reusable | ✅ Done (2026-06-07) | 3 tools moved (history-preserving) + `sys.modules`-redirect shims; reconciled a **stale prior `plan_lifecycle/wave_execution_state.py` (495 vs live 647 lines)** — restored live content; consumers updated (importlib + doc + 2 CI gates + test); `__init__.py` added. Smoke: `python -m tools.plan_lifecycle.wave_execution_state status` → exit 0; shim redirect verified. Moved modules byte-identical to HEAD (CRLF-only). 49 pre-existing test failures in `test_plan_wave_table_updater` proven NOT caused by W2 (byte-identical module). |
| W3 | R3.1–R3.2 | `post_cursor_agent_*.py` → `post_agent_*.py` | ~14k | Dispatch + deny-token guard editable atomically | ⏸️ Pre-flight done — PAUSED (2026-06-07) | **Map below (W3 detail): 656 refs / 156 .py files, 7 categories.** Rename NOT started — awaiting go-ahead. |
| W4 | R4.1–R4.3 | `artifacts/cursor/` → `artifacts/governance/` (highest risk) | ~16k | Dual-read migration preserves in-flight session-state | ⬜ Not Started | Dual-read live; writers updated; no lost session-state; gates green |
| W5 | R5.1–R5.3 | Ledger **dead-pointer cleanup** (core + CI) — *risk downgraded by R1.2* | ~6k | Data already at `.claude/state`; no migration | ⬜ Not Started | Dead `path_constants.CURSOR_STATE_DIR` removed (Author-Gate); GH workflow repointed to `.claude/state`; schema-doc comment fixed; empty `.cursor/state` deleted |
| W6 | R6.1–R6.2 | Deferred dec0de W3 config + final guard restore | ~8k | `_legacy_windsurf` importers migrated by now | ⬜ Not Started | `excluded_paths`/`path_constants` mirror cleaned + drift gate green; `T6a` retired or repointed; shell guard restored at new tokens |
| W7 | R7.1 | Verify zero-brand + close | ~4k | All prior waves green | ⬜ Not Started | Repo scan: only intentional history remains; both plans closed |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| R1.1 | Rollback tag | git tag | — | ~1k | ✅ Done — `pre-w5-rename-b4f1a9`@d345db6 |
| R1.2 | Resolve ledger drift | `path_constants.py`, `.github/workflows/author-gate-gates.yml`, `decision_ledger.schema.sql`, `.cursor/state/**`, `.claude/state/**` | Two locations referenced; must pick authoritative + reconcile data | ~7k | ✅ Done — authoritative=`.claude/state`; `.cursor/state` empty; no data migration needed |
| R2.1 | Move `tools/windsurf/` → `tools/plan_lifecycle/` + compat shim | `tools/windsurf/**` (3 tools) | Sunset shim; importlib string consumer; **stale prior copy reconciled** | ~6k | ✅ Done |
| R2.2 | Update consumers | `post_cursor_agent_wave_lifecycle_capture.py`, `agents-tier1-companion.md`, CLI refs, CI gates, 1 test | importlib module string | ~4k | ✅ Done |
| R3.1 | Rename `post_cursor_agent_*.py` → `post_agent_*.py` | **30 live** scripts (+ ~12 `_legacy_cursor/` FROZEN) | Atomic with dispatch + deny-token | ~9k | ⏸️ Pre-flight done — map in W3 detail; PAUSED |
| R3.2 | Update dispatch + CI + tests | `after_agent_governance_dispatch.py` (+env `POST_CURSOR_AGENT_DISPATCHER`), `lib/claude_hook_common.py`, `lib/mcp_before_hygiene.py`, `governance_w3_hook_audit_matrix.py` (45), `check_post_cursor_agent_*`, `check_cursor_optimized_config.py`, ~50 tests | Reconcile already-renamed `hooks/cursor/test_post_agent_*` | ~5k | ⏸️ PAUSED |
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

### W3 — `post_cursor_agent_*.py` → `post_agent_*.py`  ⏸️ PRE-FLIGHT DONE — PAUSED before rename (2026-06-07)

- **R3.1/R3.2** Rename scripts AND update dispatch wiring + deny-token + CI gates + tests — atomically.
- **Gate:** run the after-agent dispatch once → audit rows still produced; `check_ag_hook_wiring.py` green.

#### R3.1 Blast-radius map (read-only — `DEGRADED_FALLBACK: reason=governance_scripts+name_literals_outside_adg_import_index`)
**Scope: 656 `post_cursor_agent` refs across 156 `.py` files** (+ docs/plans, left frozen). Categories:

| # | Category | Files | What changes |
|---|----------|-------|--------------|
| 1 | **Rename targets** | **30 live** `.claude/governance/scripts/post_cursor_agent_*.py` | `git mv` → `post_agent_*.py` |
| 2 | **Atomic dispatch core** (must change WITH the mv) | `.claude/hooks/after_agent_governance_dispatch.py` (16: `_AG_CHAIN`, `_SCRIPT_EXTRA_ARGS`, adg-audit, dispatch loader, **env `POST_CURSOR_AGENT_DISPATCHER`**), `post_cursor_agent_dispatch.py` (14, itself a rename target), `_post_cursor_agent_payload.py` (5, rename target), `lib/claude_hook_common.py` (1), `lib/mcp_before_hygiene.py` (1), `_post_handlers/*` | string refs + env-var name |
| 3 | **Self-referential guards** (atomic) | `.claude/hooks/before_shell_execution.py` (deny-token `post_cursor_agent`), `check_cursor_optimized_config.py` (1) | neutralize first, restore at new token |
| 4 | **CI gates** | `governance_w3_hook_audit_matrix.py` (45), `check_post_cursor_agent_payload.py` (17, rename target), `check_post_cursor_agent_alive.py` (14, rename target), `check_hook_consolidation.py` (11), `run_contract_gates.py` (5), `check_marker_ledger_parity.py` (3), `check_writer_allowlist.py` (2), +~6 singles | name literals |
| 5 | **Tests (~50 files)** | `tests/unit/windsurf/**`, `tests/windsurf/**`, `tests/unit/windsurf_scripts/**`, `tests/unit/ops_scripts/hooks/windsurf/**`, `test_check_ag_hook_wiring.py` (28) | imports + name literals |
| 6 | **Other consumers (~20)** | `tools/capture/queue_to_ledger.py`, `tools/author_gate/schema_loader.py`, `tools/cursor/emit_governance_dispatch_shadow_baseline.py`, `tools/ledgers/schema_registry.py`, `apps_qna/router/route_bandit.py`, `ops_scripts/calibration/*`, `tests/conftest.py` | name literals |
| 7 | **FROZEN — do NOT touch** | `_legacy_cursor/post_cursor_agent_*.py` (~12, legacy, dec0de-owned), `docs/**`, `.claude/plans/_archive/**`, `ops_scripts/maintenance/rewrite_*.py` (migration tools) | — |

**Already migrated (reconcile, don't duplicate):** `tests/unit/ops_scripts/hooks/cursor/test_post_agent_*.py` (2 files use the new name).

**Execution order when resumed:** (1) neutralize `before_shell_execution` deny-token → (2) `git mv` 30 scripts (via script) → (3) global `post_cursor_agent`→`post_agent` replace across cat 2/4/5/6 + env var `POST_CURSOR_AGENT_DISPATCHER`→`POST_AGENT_DISPATCHER` → (4) update AG-WIRE matrix + deny-token → (5) **prove chain fires**: run after-agent dispatch, `check_ag_hook_wiring.py`, alive/payload gates → (6) restore guard at new token.

**Top risk:** one missed dispatch/`_AG_CHAIN` ref = governance chain silently dark. Mitigation = the cat-5 gates + a live dispatch run are the proof, not the diff.

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
