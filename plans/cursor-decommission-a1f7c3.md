---
slug: cursor-decommission-a1f7c3
status: Completed
plan_type: platform_core_change
tier: T3
created: 2026-06-07
completed: 2026-06-07
end_state: zero `.cursor` directory; `.codex/` is the sole SSOT tree
decision_ref: "DECISION_CAPTURED architecture_choice selected=full_relocation_zero_cursor confidence=0.78"
---

> ✅ **COMPLETED 2026-06-07, merged to main (`5b13233ff2`).** `.cursor` → `.codex` relocation done:
> engine → `.codex/governance/scripts`, plans → `.codex/plans`, state+ledger → `.codex/state`,
> schemas/templates → `.codex/`; `.cursor` = 0 tracked files; anti-regression gate
> `ops_scripts/ci/check_no_cursor_refs.py` added + wired into `run_contract_gates`.
> (On-disk `status:` was stale `Not Started`; corrected to `Completed` to match the authoritative
> Notion Plans row on 2026-06-07.) The **windsurf/codeium** brand removal this plan did NOT cover is
> handled by [cursor-windsurf-codeium-decommission-dec0de](cursor-windsurf-codeium-decommission-dec0de.md)
> — complementary, not superseded.

# Cursor Decommission — Full Relocation to `.codex/` SSOT

## Context (SCQA)

- **Situation.** Cursor is no longer used. `AGENTS.md` already declares `.codex/` the
  always-on SSOT, but the repo still carries a large `.cursor/` tree (~3,300 files) that
  splits into three classes: dead mirrors, live runtime data, and the live governance
  script engine that `.codex/hooks/` shells into.
- **Complication.** `.cursor/` is *not* inert. The governance engine under
  `.cursor/scripts/**` (364 files) is invoked by `.codex/hooks/` via `subprocess` +
  `importlib`; plans, ledgers, schemas, and templates under `.cursor/` are read at
  runtime; and **49 pre-commit glob lines** plus ~110 code references hard-code
  `.cursor/...` paths. Naively deleting or moving anything breaks hooks and CI.
- **Question.** How do we reach a **zero-`.cursor`** end-state (the selected option)
  without breaking the governance hook chain, the decision/author-gate ledgers, or CI?
- **Answer.** Stage the migration so that **path indirection lands before any move**,
  then relocate in dependency order (leaf data → engine → references), each wave
  using `git mv` to preserve history and a scoped test/gate proof, finishing with a
  CI gate that *forbids* re-introduction of `.cursor`.

### Reference inventory (evidence, 2026-06-07)

| `.cursor/` surface | Files | Class | Successor home |
|---|---|---|---|
| `scripts/**` | 364 | **Live engine** (hooks call it) | `.codex/governance/scripts/` |
| `plans/**` | 2148 | **Live data** (plan SSOT) | `.codex/plans/` |
| `state/**` | 32 | **Live data** (ledgers, AG queue, caches) | `.codex/state/` |
| `schemas/**` | 56 | **Live data** (AG packet, ledger DDL) | `.codex/schemas/` |
| `templates/**` | 2 | **Live data** (plan template) | `.codex/templates/` |
| `rules/**` | 65 | **Dead mirror** of `.codex/rules/` (63) | delete |
| `skills/**` | 92 | **Dead mirror** of `.codex/skills/` (87) | delete |
| `workflows/**` | 25 | **Dead mirror** of `.codex/commands/` (24) | delete |
| `agents/**` | 4 | **Dead mirror** of `.codex/agents/` (4) | delete |
| `mcp.json` | 1 | **Dead mirror** of root `.mcp.json` | delete + drop sync |
| `hooks/**`, `hooks.json` | 17 | **Dead** Cursor-native hook registration | delete |
| `reminders/`, `decisions/`, `windsurf_compat/`, `_zero_loss_originals/`, `*MIGRATION*`, `*RECEIPT*`, `RULES_INDEX*` | ~20 | **Historical** | archive to `docs/archive/cursor/` then delete |

External references to rewrite: **~110 code** (`tools/` 405 mention-files, `ops_scripts/` 258, `agentic_core/` 44, `tests/` 223 — most are comments/docstrings; runtime path reads are the ~110 that matter) + **49 pre-commit globs** + `.codex/hooks.json` (1 direct call) + `.codex/hooks/*.py` (`SCRIPTS = REPO_ROOT/".cursor"/"scripts"`).

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W0 | P0.1–P0.4 | Indirection layer + new homes; full reference map | ~40k | Path constants can be centralized | Not Started | All `.cursor` paths resolved through one constants module; new dirs exist; CI green |
| W1 | P1.1–P1.3 | Delete dead mirrors; retarget the few gates pointing at them | ~30k | `.cursor/{rules,skills,workflows,agents,mcp.json,hooks}` have zero runtime readers | Not Started | Dead mirrors gone; pre-commit globs repointed to `.codex/`; CI green |
| W2 | P2.1–P2.4 | Relocate `plans/**` → `.codex/plans/`; rewrite rule + refs + globs | ~70k | 2148 plan files move via `git mv` | Not Started | Plans resolve under `.codex/plans/`; plan gates pass; no `.cursor/plans` refs remain |
| W3 | P3.1–P3.3 | Relocate `state/**` (ledgers, AG queue, caches) | ~45k | `ledger_paths.py` is the path chokepoint | Not Started | Ledger writes/reads hit `.codex/state/`; AG capture + queue drain work; SQLite intact |
| W4 | P4.1–P4.2 | Relocate `schemas/**` + `templates/**` | ~25k | Schema/template paths centralizable | Not Started | AG packet builder + plan template resolve new paths; schema gates pass |
| W5 | P5.1–P5.4 | Relocate governance engine `scripts/**` → `.codex/governance/scripts/` | ~90k | Engine is self-contained + importable from new path | Not Started | `.codex/hooks` invoke new path; all post/pre hooks fire; governance tests pass |
| W6 | P6.1–P6.3 | Reference sweep; AGENTS.md + rules rewrite; add anti-regression gate | ~50k | Comment-only refs acceptable to bulk-edit | Not Started | Zero `.cursor` refs in live trees; `check_no_cursor_refs.py` gate added + green |
| W7 | P7.1–P7.2 | Delete `.cursor/`; full verification | ~20k | All prior waves green | Not Started | `.cursor/` absent; full gate + scoped test suites pass; hooks fire end-to-end |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0.1 | Create `tools/paths/cursor_compat.py` constants module | 1 new | Must enumerate every live `.cursor` subpath | ~12k | Not Started |
| P0.2 | Create new homes (`.codex/{plans,state,schemas,templates,governance}/`) with `.gitkeep` | 5 new | — | ~4k | Not Started |
| P0.3 | Generate exhaustive reference map artifact | 1 artifact | Separate runtime reads from comments | ~16k | Not Started |
| P0.4 | Add `legacy_reference_allowlist` shim entries for in-flight waves | 1 | Avoid CI self-block mid-migration | ~8k | Not Started |
| P1.1 | Delete `.cursor/{rules,skills,workflows,agents}` mirrors | 186 del | Confirm no runtime read first | ~14k | Not Started |
| P1.2 | Delete `.cursor/{mcp.json,hooks.json,hooks/}` + drop `sync_mcp_config` Cursor arm | ~18 del + 2 edit | MCP sync gate logic | ~10k | Not Started |
| P1.3 | Repoint pre-commit globs (`rules/`, `skills/`) to `.codex/` | ~8 edits | 49-line glob block | ~6k | Not Started |
| P2.1 | `git mv .cursor/plans .codex/plans` | 2148 | History preservation | ~20k | Not Started |
| P2.2 | Rewrite `plan-location.md` + `plan-governance` skill + `plan_registration` helpers | ~6 | SSOT path string is everywhere | ~22k | Not Started |
| P2.3 | Rewrite 49→plan-subset pre-commit globs + plan gates | ~12 | `check_plan_*` family | ~18k | Not Started |
| P2.4 | Rewrite `.codex/hooks` plan-path refs | ~3 | — | ~10k | Not Started |
| P3.1 | `git mv .cursor/state .codex/state`; update `ledger_paths.py` chokepoint | ~32 + 1 | SQLite path; drift-mirror logic | ~16k | Not Started |
| P3.2 | Update AG queue helper + `plan_registration_cache` + wave-state writers | ~6 | Live JSONL/marker writers | ~16k | Not Started |
| P3.3 | Update ledger DDL / decision-ledger freshness gate paths | ~4 | pre-commit DDL trigger | ~13k | Not Started |
| P4.1 | `git mv .cursor/schemas .codex/schemas`; update AG packet builder + schema refs | ~10 | `author_gate_packet.schema.json` | ~14k | Not Started |
| P4.2 | `git mv .cursor/templates .codex/templates`; update template readers | ~3 | `execution-plan-template.md` | ~11k | Not Started |
| P5.1 | `git mv .cursor/scripts .codex/governance/scripts` (keep `_legacy_*` or archive) | 364 | Internal sibling imports (`_post_handlers`, `_author_gate_queue`) | ~30k | Not Started |
| P5.2 | Update `.codex/hooks/*.py` `SCRIPTS` const + `sys.path` inserts + `.codex/hooks.json` direct call | ~7 | importlib spec loading | ~20k | Not Started |
| P5.3 | Rewrite ~110 `.cursor/scripts` code references | ~110 | Bulk but mechanical | ~25k | Not Started |
| P5.4 | Repoint remaining pre-commit globs (scripts/schemas/state) | ~25 | — | ~15k | Not Started |
| P6.1 | Bulk-rewrite comment/docstring `.cursor` mentions across live trees | ~hundreds | Cosmetic but noisy | ~22k | Not Started |
| P6.2 | Rewrite `AGENTS.md` + every `.codex/rules/*.md` mention of `.cursor` | ~30 | Rules cite `.cursor` paths | ~16k | Not Started |
| P6.3 | Add `ops_scripts/ci/check_no_cursor_refs.py` (fail on new `.cursor`) + pre-commit | 2 new | Allowlist for `docs/archive/cursor/**` | ~12k | Not Started |
| P7.1 | Archive historical `.cursor` docs → `docs/archive/cursor/`; delete `.cursor/` | bulk del | Final removal | ~10k | Not Started |
| P7.2 | Full verification (gates + scoped suites + live hook fire) | — | — | ~10k | Not Started |

## Execution Detail

### W0 — Indirection layer (do this FIRST or every later wave fights CI)

The reason a "just move it" approach fails: the plan-location rule, ledger paths, AG
queue helper, and 49 pre-commit globs each independently hard-code `.cursor/...`.
Centralize first:

- **P0.1** Add `tools/paths/cursor_compat.py` exporting `PLANS_DIR`, `STATE_DIR`,
  `SCHEMAS_DIR`, `TEMPLATES_DIR`, `GOVERNANCE_SCRIPTS_DIR`, each resolving to the
  **new** `.codex/...` home with a **read-fallback** to the old `.cursor/...` path
  while files are mid-move. Repoint `ledger_paths.py` and the AG-queue/plan-registration
  helpers to import from here (don't relocate data yet — just route through the constant).
- **P0.2** Create the empty successor dirs with `.gitkeep`.
- **P0.3** Emit `artifacts/migration/cursor_reference_map.json` separating *runtime path
  reads* (must rewrite) from *comments/docstrings* (bulk-rewrite in W6) — use ADG +
  ripgrep, not grep-for-deps.
- **P0.4** Add in-flight entries to `.cursor/legacy_reference_allowlist.yaml` /
  `migration_allowlist.json` so the existing `check_cursor_native_config.py` gate does
  not self-block during waves W1–W6.

### W1 — Delete dead mirrors
`.cursor/{rules,skills,workflows,agents}` are near-identical duplicates of the
`.codex/` SSOT (counts: 65/63, 92/87, 25/24, 4/4) with **no runtime readers** (the
`.cursor/rules` hits in `tools/`+`ops_scripts/` are all comment/docstring citations —
verified by sampling). Delete them; repoint the handful of pre-commit gates
(`validate_hitl_rules`, `check_always_on_token_budget`, skill-frontmatter validator)
from `.cursor/rules|skills` to `.codex/rules|skills`. Delete `.cursor/mcp.json` +
`hooks.json` + `hooks/` and remove the Cursor arm of `sync_mcp_config.py`
(root `.mcp.json` is already SSOT).

### W2–W4 — Relocate live data (leaf-first)
Each: `git mv` (history preserved) → flip the W0 constant's primary to new home (drop
fallback) → rewrite the owning rule/helper → repoint that surface's pre-commit globs →
run that surface's scoped gate. Order is plans → state → schemas → templates because
schemas/templates have the fewest cross-refs and plans the most (sequence the riskiest
with the most soak time behind it). **Ledger note:** `refactor_decision_ledger.sqlite`
must move with `git mv` (binary) and the freshness gate path updated in the same commit
or `check_decision_ledger_sqlite_freshness.py` blocks.

### W5 — Relocate the governance engine (highest blast radius)
Move `.cursor/scripts/**` → `.codex/governance/scripts/`. The engine has internal
sibling imports (`_post_handlers`, `_author_gate_queue`, `_ssot_folder_check`,
`_post_cursor_agent_payload`) so it must move as a unit. Update in one wave:
`.codex/hooks/*.py` `SCRIPTS` constant + `sys.path` inserts + the `importlib` spec
path; the **direct** `.codex/hooks.json` call to
`pre_user_prompt_author_gate_reminder.py`; the ~110 code references; and the remaining
pre-commit globs. Keep `_legacy_cursor/` / `_legacy_windsurf/` archive subtrees by
moving them under `docs/archive/cursor/` rather than into the active engine.

### W6 — Sweep + anti-regression gate
Bulk-rewrite cosmetic `.cursor` mentions, rewrite `AGENTS.md` and all `.codex/rules/*.md`
that cite `.cursor` paths, then add `ops_scripts/ci/check_no_cursor_refs.py` (T-new):
fails CI if any tracked file outside `docs/archive/cursor/**` contains `.cursor/`. This
gate is what makes the decommission durable.

### W7 — Delete + verify
Archive historical docs, `git rm -r .cursor`, run full `run_contract_gates.py` + scoped
test suites + a live hook-fire smoke check (submit-prompt, file-edit, stop events).

## Definition of Done

| # | Criterion | Verification |
|---|---|---|
| 1 | `.cursor/` directory does not exist in the repo | `test ! -d .cursor` |
| 2 | `.codex/hooks` governance chain fires (submit/edit/stop) with engine at new path | Live hook smoke run; check `artifacts/cursor/*` (or new) audit JSONL updates |
| 3 | Refactor-decision ledger + AG queue read/write under `.codex/state/` | `python -m tools.capture.append_marker` round-trip; ledger freshness gate green |
| 4 | Plan governance resolves `.codex/plans/`; new plan registers correctly | `check_plan_*` gates green on a test plan |
| 5 | All pre-commit gates pass with `.cursor` globs retargeted | `pre-commit run --all-files` |
| 6 | Full contract gate suite passes | `python ops_scripts/ci/run_contract_gates.py` exits 0 |
| 7 | Anti-regression gate present + green | `python ops_scripts/ci/check_no_cursor_refs.py` exits 0 |
| 8 | Smoke: governance engine entrypoint runs from new home | `python .codex/governance/scripts/pre_prompt_classifier.py --help` exits 0 |

### Verification vs Deferral

| Item | Verified here | Deferred |
|---|---|---|
| Engine relocation correctness | ✅ W5 + DoD #2,#8 | — |
| Ledger/state integrity | ✅ W3 + DoD #3 | — |
| Cosmetic comment cleanup | ✅ W6 | Residual non-tracked notes |
| `docs/archive/cursor/**` historical content | retained read-only | Eventual prune (separate plan) |

## Risks / Rollback

- **Hook breakage mid-move** → W0 read-fallback constant + per-wave `git mv` keeps each
  commit independently green; rollback = `git revert` the single wave commit.
- **Binary SQLite ledger loss** → `git mv` (never copy+delete); verify row count before/after.
- **CI self-block during waves** → P0.4 allowlist entries, removed in W6.
- **Two-tier token budget gate** counts `.codex/rules` after W1 retarget — confirm
  always-on byte sum still ≤51,200 (`check_always_on_token_budget.py`).
