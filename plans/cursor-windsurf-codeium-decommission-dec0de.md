---
slug: cursor-windsurf-codeium-decommission-dec0de
plan_type: platform_core_change
status: Completed
created: 2026-06-07
owner: Claude Code
supersedes:
  - windsurf-deprecation-cursor-ssot-b6e4a9   # prior windsurf→cursor migration; this plan completes the chain to Claude Code SSOT
complements:
  - cursor-decommission-a1f7c3                 # COMPLETED+merged the .cursor→.codex work; this plan covers the windsurf/codeium brand it did not touch
---

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W6
LAST_UPDATED: 2026-06-08

> **CLOSEOUT 2026-06-08 (IDE_archive).** Parent/baseline decommission is complete as a
> scoped parent plan: W1/W2 established the inventory and re-baseline, W3/W4/W6 delivered
> the low-risk surface cleanup and verification, and W5 remains intentionally split to
> [cursor-naming-rename-w5-b4f1a9](cursor-naming-rename-w5-b4f1a9.md) with the
> legacy tree tail in [legacy-windsurf-tree-decommission-9f2c47](legacy-windsurf-tree-decommission-9f2c47.md).
> Verification rerun in `IDE_archive`: `check_no_cursor_refs.py`, `check_always_on_token_budget.py`,
> `check_exclusion_consistency.py`, active-prose scans, legacy-path absence checks.

> ⛔ **RE-BASELINED 2026-06-07 (W2 reconciliation).** The W1 inventory freeze + a dependency check +
> the authoritative Notion row for `cursor-decommission-a1f7c3` reset the scope:
> 1. **The `.cursor` decommission is already DONE and merged to main** (`5b13233ff2`, plan
>    [cursor-decommission-a1f7c3](cursor-decommission-a1f7c3.md) = Completed). `.cursor/` = 0 tracked
>    files (only untracked dead `__pycache__/*.pyc` remain); the live engine is at
>    `.codex/governance/scripts/`. An anti-regression gate `ops_scripts/ci/check_no_cursor_refs.py`
>    now forbids re-introducing `.cursor/` path-construction in `.py` under active roots (markdown/
>    comments allowed — so this plan + its reports do **not** trip it).
> 2. **dec0de's real remaining scope = windsurf + codeium brand removal** (a1f7c3 did not touch it),
>    plus the optional rename of the genuinely-live `post_cursor_agent`/`_legacy_windsurf` wiring.
> 3. `_legacy_windsurf/` and `_legacy_cursor/` are **NOT dead** — live hooks/tests import from them
>    (`post_cursor_agent_plan_registration_capture.py:33`, `post_cursor_agent_plan_scope_audit.py:27`,
>    `tools/windsurf/wave_execution_state.py:50`, the heartbeat-latency test). a1f7c3 deliberately
>    retained them; dec0de touches them only in W5 (rename + importer update), never bulk-delete.
> 4. The original W2 bulk-delete targets `docs/archive/windsurf/` and `_archive/windsurf_legacy*`
>    **don't exist**.
> Net effect: **W2 = reconciliation only (no destructive action).** Remaining real work: W3 (windsurf/
> codeium config) → W4 (docs/rules prose) → W5 (live `post_cursor_agent`/`_legacy_windsurf` rename,
> gated) → W6 (verify incl. `check_no_cursor_refs` + full gates).

# Cursor / Windsurf / Codeium Decommission — Claude Code as Sole SSOT

## Context (SCQA)

- **Situation.** The repo migrated Windsurf → Cursor → Claude Code. Claude Code (`AGENTS.md`,
  `.codex/**`, `.mcp.json`) is the live operating contract. But the previous two IDE eras left a
  large residual footprint: dead config, archived trees, and — most importantly — **live governance
  wiring that still carries Cursor/Windsurf *names*** even though Claude Code's hooks are what
  invoke it.
- **Complication.** "Deprecate all references" collides with blast radius. Three distinct
  categories exist and must NOT be treated the same:
  1. **Pure dead legacy** — safe to delete (`.cursor/` empty `__pycache__` mirrors, `_legacy_windsurf/`
     161 files, `_legacy_cursor/` 11 files, `docs/archive/windsurf/` ~913 files, `_archive/windsurf_legacy*`
     ~450 plans, root `AGENTS.md`).
  2. **Brand-only config** — Windsurf/Codeium-specific, zero Claude value (`.codeiumignore`,
     windsurf lines in `.pre-commit-config.yaml`, `config/excluded_paths.yaml`).
  3. **LIVE Claude Code wiring, historically named** — 26+ `post_cursor_agent_*.py` governance
     scripts (dispatched by `after_agent_governance_dispatch.py` + `lib/codex_hook_common.py`),
     `artifacts/cursor/` write target, `tools/windsurf/` (3 active plan-lifecycle tools consumed by
     a governance capture script + 2 CI gates), `.codex/.cursor/state/refactor_decision_ledger.sqlite`,
     the `before_shell_execution.py` guard that *blocks* `.windsurf`/`post_cursor_agent` shell tokens,
     and ~20 `.codex/rules/` files whose prose says "Cursor Agent".
- **Question.** How to reach a zero-brand Claude-Code SSOT without breaking the governance engine
  that is currently *named* after the deprecated IDEs?
- **Answer.** Stage by risk. Delete dead legacy and brand-only config first (high value, near-zero
  risk), rewrite docs/rules prose next, then perform the live-wiring rename as a final, separately
  gated wave with ADG blast-radius + full gate run. `hooks.json` is already clean (hooks dispatch
  by their own filenames), which materially de-risks the rename.

> **Assumed defaults (scope questions went unanswered 2026-06-07):**
> (1) **Rebrand depth = full, staged** — all references eliminated, but the risky internal rename is
> isolated to W5 so it can be approved or deferred independently.
> (2) **Archive disposal = `git rm` outright** — working tree cleaned; history remains recoverable.
> Override either before executing the affected wave.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1.1–P1.3 | Inventory freeze + safety prep | ~8k | Inventory from 2026-06-07 exploration holds | ✅ Done (2026-06-07) | Frozen manifest written ([inventory_freeze_dec0de.md](../../docs/reports/decommission/inventory_freeze_dec0de.md)); rollback tag `pre-decommission-dec0de`@7729ce863e; 3 plan-path estimates corrected |
| W2 | P2.1–P2.3 | Re-baseline + dead-legacy audit | ~12k | See re-baseline banner | ✅ Done (2026-06-07) | Re-scoped to reality: `_legacy_*` retained (live importers); a1f7c3 retired. No destructive action taken. ⚠️ **REVISED twice (2026-06-07):** P5.1 first flagged `.cursor/state` as holding the live ledger (DERIVED from `path_constants.CURSOR_STATE_DIR` + GH-workflow refs). W1-R1.2 of the split plan then **disk-verified the opposite**: `.cursor/state` is EMPTY; the live ledger is at `.codex/state/refactor_decisions/` (`ledger_paths.py` SSOT). So `.cursor/` IS safe to delete; the `.cursor/state` refs are dead pointers. Cleanup tracked in [cursor-naming-rename-w5-b4f1a9](../../plans/cursor-naming-rename-w5-b4f1a9.md) R5/R6. |
| W3 | P3.1–P3.3 | Remove brand-only config | ~6k | Codeium/Windsurf indexers no longer used | 🟡 Partial (2026-06-07) | ✅ P3.1 `.codeiumignore` deleted (was untracked orphan; repo's prior "eliminated" intent now physically true). ⏭️ P3.2/P3.3 **deferred to W5** (decision `deletion_strategy selected=defer_coupled_to_w5`): pre-commit `T6a no-active-windsurf-authoring` is **live** and still guards `_legacy_windsurf` (331 files, live importers); `excluded_paths.yaml` windsurf entries mirror boundary-protected `agentic_core/L0_routing/config/path_constants.py` (drift gate `check_exclusion_consistency.py`). NOT brand-only as W3 assumed → migrate with the legacy importers in W5. |
| W4 | P4.1–P4.2 | Docs/rules prose → "Claude Code" | ~14k | Prose rewrite is non-functional | ✅ Done (2026-06-07) | 58 prose replacements / 31 rule files: "Cursor Agent"→"Claude Code" (0 residual), dead `.cursor/RULES_INDEX.md` cross-refs retargeted to `AGENTS.md` (0 residual), standalone-"Cursor" titles rebranded. `post_cursor_agent_*`/`artifacts/cursor/`/`L2/cursor_agent`/gate-name identifiers preserved (28 refs intact). Gap A1 (hook-migration-auditor wrong engine path) + A4 folded in. Gate `check_always_on_token_budget.py` PASS. **Kept** (historical/true): conversion-banner provenance, constitutional §0 Windsurf-ban-lifted line, claude-config-lookup legacy-tree explanations. |
| W5 | P5.1–P5.4 | Live-wiring rename (GATED) | ~30k | ADG blast radius clear; hooks.json clean (verified) | ⏭️ Split out (2026-06-07) | P5.1 map done (read-only). P5.2–P5.4 **split to dedicated plan** [cursor-naming-rename-w5-b4f1a9](../../plans/cursor-naming-rename-w5-b4f1a9.md) per DoD #8 (decision `deletion_strategy selected=split_w5_to_own_plan`): ~800+ refs, live ledger + session-state, 2 core edits, prior in-flight rename to reconcile. |
| W6 | P6.1 | Verify brand-free *surface* (reframed) | ~4k | W4 prose done; W5 deferred to own plan | ✅ Done (2026-06-07) | Active prose surface brand-free: `.codex/rules` "Cursor Agent" = 0; `.codex/skills`/`AGENTS.md` residual cleaned (1 docstring). Only intentional historical mention remains: `constitutional.md:12` (Windsurf-ban-lifted, true). P6.2 (shell-guard restore) moved to W5 plan (R6.2) where the renamed tokens land. |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Re-validate inventory | exploration manifest | Counts may have drifted since 2026-06-07 | ~3k | ✅ Done — 3 estimates wrong (see manifest §A) |
| P1.2 | Tag rollback point | git tag | — | ~1k | ✅ Done — `pre-decommission-dec0de`@7729ce863e |
| P1.3 | Establish token-safe deletion (no guard edit) | manifest §E | Guard has no bypass env; use `git rm --pathspec-from-file` so tokens stay out of command text | ~4k | ✅ Done — guard NOT weakened |
| P2.1 | Delete `.cursor/` mirrors + `_legacy_*` | `.cursor/**`, `_legacy_windsurf/`, `_legacy_cursor/` | Confirm `__pycache__` only; nothing imported | ~5k | ⬜ |
| P2.2 | Delete archived trees | `docs/archive/windsurf/`, `_archive/windsurf_legacy*` | Large file count; ensure not referenced by reports | ~4k | ⬜ |
| P2.3 | Retire root `AGENTS.md` | `AGENTS.md` | Sub-app `AGENTS.md` files stay; check sync scripts | ~3k | ⬜ |
| P3.1 | Remove `.codeiumignore` | `.codeiumignore` | Confirm no tool reads it | ~2k | ✅ Done — untracked orphan deleted (T6h gate already retired; no live reader) |
| P3.2 | Clean pre-commit config | `.pre-commit-config.yaml` | NOT generator-emitted (hand-maintained); `T6a` is a **live** gate guarding `_legacy_windsurf` | ~2k | ⏭️ Deferred to W5 |
| P3.3 | Clean `config/excluded_paths.yaml` | `config/excluded_paths.yaml` + `agentic_core/L0_routing/config/path_constants.py` | Entries mirror boundary-protected frozensets; drift gate; needs core edit + receipt | ~2k | ⏭️ Deferred to W5 |
| P4.1 | Rewrite `.codex/rules/**` prose | 31 rule `.md` (actual; not ~20) | "Cursor Agent" → "Claude Code"; markers/identifiers preserved | ~9k | ✅ Done — 58 repl, 0 residual actor-prose |
| P4.2 | Rewrite root contract prose | `AGENTS.md`, `claude-config-lookup.md`, `constitutional.md` | Keep historical-context lines that are still true | ~5k | ✅ Done — `constitutional.md` rebranded (5); `AGENTS.md` already clean; `claude-config-lookup.md` legacy explanations kept (accurate) |
| P5.1 | ADG + consumer map for rename | adg_sqlite, grep | Governance scripts may not be ADG-indexed → grep fallback w/ DEGRADED_FALLBACK | ~6k | ✅ Done (2026-06-07) — map below; ⚠️ found W2 `.cursor`-is-dead claim is WRONG (live ledger inside) |
| P5.2 | Rename `post_cursor_agent_*` → `post_agent_*` | 26+ scripts + dispatch + `lib/codex_hook_common.py` + `mcp_before_hygiene.py` + CI gate `check_cursor_optimized_config.py` | Dispatch wiring + deny-token gate must update atomically | ~10k | ⬜ |
| P5.3 | Rename `artifacts/cursor/` → `artifacts/governance/` | `before_mcp_execution.py`, ~50 writer scripts | Live session-state path; must migrate or dual-read once | ~8k | ⬜ |
| P5.4 | Rename `tools/windsurf/` + `.codex/.cursor/` | `tools/windsurf/**` (3 tools) + 4 consumers; ledger dir | Compat shim during sunset; CI gates reference path | ~6k | ⬜ |
| P6.1 | Zero-brand verification scan | whole repo | Distinguish intentional history mentions from leakage | ~5k | ⬜ |
| P6.2 | Update shell guard + close plan | `before_shell_execution.py`, Notion | Guard should now block the NEW names too / drop dead tokens | ~3k | ⬜ |

## Wave Detail

### W1 — Inventory freeze + safety prep
- **P1.1** Re-run the inventory sweep (Grep for `windsurf`, `codeium`, `cursor`, `.codeiumignore`,
  `.cursorignore`) and write a frozen manifest to `docs/reports/decommission/` listing every path,
  classified Category 1/2/3. This is the source of truth the later waves delete against.
- **P1.2** `git tag pre-decommission-dec0de` as the rollback point.
- **P1.3** The `before_shell_execution.py` guard hard-blocks any shell command containing `.windsurf`
  or `post_cursor_agent`. Add a scoped, time-boxed allowance (or perform deletions via the native
  file tools / `git rm` paths the guard permits) so W2/W5 can proceed. Re-tighten in P6.2.

### W2 — Re-baseline + dead-legacy audit (✅ done — superseded the original "bulk delete" scope)
Outcome of the dependency check (see re-baseline banner + [inventory_freeze_dec0de.md](../../docs/reports/decommission/inventory_freeze_dec0de.md)):
- **`_legacy_windsurf/` retained** — live importers: `post_cursor_agent_plan_registration_capture.py:33`,
  `post_cursor_agent_plan_scope_audit.py:27`, `tools/windsurf/wave_execution_state.py:50`,
  `tools/reports/recover_deferred_scope_pendings.py:43`. Its rename/migration moves to **W5**.
- **`_legacy_cursor/` retained** — imported by active test
  `tests/unit/ops_scripts/hooks/windsurf/test_post_cursor_agent_heartbeat_latency.py:13` +
  `tools/cursor/governance_dedup_e2e_verify.py:40`. Migration → **W5**.
- **`.cursor/` = untracked dead `__pycache__/*.pyc` only** — no git-tracked deletion; physical removal
  sequenced into **W6/P6.2** alongside the `before_shell_execution.py` guard update (the guard protects
  `.cursor` from deletion, so removing it before the guard edit would mean circumventing a safety control).
- **root `AGENTS.md`** retained until W4/W5 — referenced by `sync_mcp_config.py` + pre-commit gates
  (T6c/T6f glob it); retiring it requires handling those refs first.
- **a1f7c3 retired** (stale inventory).
- **No destructive action taken in W2.** Real deletions/renames are now W3 (config) / W5 (live wiring).

### W3 — Remove brand-only config
- **P3.1** `git rm .codeiumignore` after confirming no live reader.
- **P3.2** Remove windsurf/codeium lines from `.pre-commit-config.yaml`. These appear generator-emitted
  — find and fix the generator (`tools/setup/gitignore.py` or similar) so they don't regenerate.
- **P3.3** Drop windsurf/codeium entries from `config/excluded_paths.yaml`.
- **Gate:** `pre-commit run --all-files` (or scoped) succeeds; generated files stable on re-run.

### W4 — Docs/rules prose rebrand
- **P4.1** Rewrite "Cursor Agent" → "Claude Code"/"the agent" across active `.codex/rules/**`.
  **Preserve** machine-relied tokens verbatim: marker grammar (`DECISION_CAPTURED:`,
  `AUTHOR_GATE_PACKET:`, `WAVE_COMPLETE:`, etc.), env-var bypass names, file paths still in use.
  Only prose changes — zero functional edits (constitutional §21 zero-loss overwrite).
- **P4.2** Same for `AGENTS.md`, `claude-config-lookup.md`, `constitutional.md`. Keep historically-true
  lines (e.g. "supersedes AGENTS.md", "legacy Windsurf PowerShell ban lifted") — rewrite only if they
  imply Cursor/Windsurf is still operative.
- **Gate:** rule-lint / `check_always_on_token_budget.py`; manual diff review confirms no marker drift.

### W5 — Live-wiring rename (GATED — approve/defer independently)
- **P5.1** Before any rename: `adg_health` then blast-radius/fan-in on `tools/windsurf/*` consumers and
  the `post_cursor_agent_*` dispatch. Governance scripts may be outside the ADG index — if so, emit
  `DEGRADED_FALLBACK: reason=<...>` and use Grep enumeration. Produce a rename map.
- **P5.2** Atomic rename `post_cursor_agent_*.py` → `post_agent_*.py`: rename files **and** update
  `after_agent_governance_dispatch.py`, `lib/codex_hook_common.py`, `lib/mcp_before_hygiene.py`, and
  `check_cursor_optimized_config.py` deny-token list in the same change. Run the after-agent dispatch
  once to prove the chain still fires.
- **P5.3** Rename `artifacts/cursor/` → `artifacts/governance/`. Update `before_mcp_execution.py`
  (session-state path, ~line 170) and the ~50 writer scripts. Provide a one-time migration/dual-read
  for existing `session_state_*.json` so in-flight state isn't lost.
- **P5.4** Rename `tools/windsurf/` → `tools/plan_lifecycle/` (3 tools) with a compat shim at the old
  path for the sunset window; update the 4 active consumers (governance capture + 2 CI gates). Move
  `.codex/.cursor/state/` → `.codex/state/` (ledger DB) and update the `refactor-decision-memory`
  skill path.
- **Gate:** full `run_contract_gates.py`; smoke-run `python -m tools.plan_lifecycle.wave_execution_state --help`
  exits 0; after-agent dispatch produces audit rows at the new artifact path.

### W6 — Verify zero-brand + register
- **P6.1** Repo-wide Grep for `cursor|windsurf|codeium`. Remaining hits must be *intentional* history
  (ADRs, this plan, changelogs). Document the allowlist.
- **P6.2** Update `before_shell_execution.py` to drop now-dead tokens and (optionally) guard the new
  names. Emit `PLAN_COMPLETE:` and update the Notion Plans row.

## Definition of Done

| # | Criterion | Verify / Defer |
|---|-----------|----------------|
| 1 | No `.codeiumignore`, `.cursorignore`, `.cursorindexingignore`, root `AGENTS.md`, or `.cursor/`/`_legacy_*`/`docs/archive/windsurf/` legacy trees remain | Verify: `git status` + Grep |
| 2 | No "Cursor Agent" / "Windsurf" prose in active `.codex/rules/**` or `AGENTS.md` (history docs allowlisted) | Verify: Grep with allowlist |
| 3 | Live governance chain still fires after rename: after-agent dispatch writes audit rows | Verify: run dispatch, inspect `artifacts/governance/` |
| 4 | `python ops_scripts/ci/run_contract_gates.py` exits 0 | Verify: command output |
| 5 | Smoke run: `python -m tools.plan_lifecycle.wave_execution_state --help` exits 0 (executable surface touched) | Verify: exit code |
| 6 | No brand-only config regenerates on `pre-commit run --all-files` | Verify: re-run, diff |
| 7 | Notion Plans row → Completed; `PLAN_COMPLETE:` emitted | Verify: Notion query |
| 8 | W5 live-wiring rename | **Deferral-eligible:** may be split to a follow-up plan if blast radius is judged too high at P5.1 — W1–W4 still deliver a brand-free *surface* |

**Verification vs Deferral:** W1–W4 (delete dead, strip config, rebrand docs) are the committed core
and are low-risk. W5 (internal rename of live wiring) is the only high-blast-radius wave and is
explicitly deferral-eligible — if P5.1 shows the rename endangers governance/session state, split it
to its own plan and stop after W4 + W6 verification (which then asserts "no functional dependency on
Cursor/Windsurf remains" rather than "no name remains").

## Risk / blast-radius notes
- **Highest risk:** P5.3 (`artifacts/cursor/` rename) — live session-state + audit write target;
  mishandling loses in-flight MCP gate state. Mitigate with dual-read migration.
- **Self-referential guard:** `before_shell_execution.py` blocks the very tokens we must touch
  (`.windsurf`, `post_cursor_agent`). P1.3 must neutralize it for delete/rename waves; P6.2 restores.
- **Generator regeneration:** brand lines in `.pre-commit-config.yaml` come from a generator — fix the
  source (P3.2) or they reappear.
- **ADG coverage:** `.codex/governance/scripts/**` and `tools/**` may be outside the production ADG
  index; expect `DEGRADED_FALLBACK` and use Grep enumeration for the rename map (constitutional §28).

## P5.1 Blast-Radius Map (read-only — 2026-06-07)

`DEGRADED_FALLBACK: reason=governance_scripts+path_literals_outside_adg_import_index` — targets are
string-literal path/script-name references, not Python import edges, so ADG cannot resolve them; grep
(literals exception) is canonical here.

### Rename targets + blast radius

| Target (current) | Proposed new | Refs to update | Risk |
|---|---|---|---|
| `.codex/governance/scripts/post_cursor_agent_*.py` (~30 live + `_legacy_cursor/` copies) | `post_agent_*.py` | **288 files** — dispatch wiring (`after_agent_governance_dispatch.py` `_AG_CHAIN`/`_SCRIPT_EXTRA_ARGS`, `lib/codex_hook_common.py`, `lib/mcp_before_hygiene.py`), CI gates (`check_post_cursor_agent_alive.py`, `check_post_cursor_agent_payload.py`, `check_cursor_optimized_config.py` deny-token, `check_ag_hook_wiring.py`, `check_marker_ledger_parity.py`), ~50 tests, docs | HIGH — dispatch + deny-token guard must change atomically |
| `artifacts/cursor/` | `artifacts/governance/` | **318 occ / 202 files**; live session-state writer `before_mcp_execution.py` | HIGHEST — live state; dual-read migration required |
| `tools/windsurf/` (3 tools: `wave_execution_state.py`, `_plan_wave_table_updater.py`, `plan_driven_closer.py`) | `tools/plan_lifecycle/` | importlib consumer in `post_cursor_agent_wave_lifecycle_capture.py`, `agents-tier1-companion.md`, CLI invocations; **migration map already drafted in `ops_scripts/maintenance/rewrite_windsurf_refs_to_cursor.py`** | MED — compat shim |
| `.cursor/state/` (ledger root) | `.codex/state/` | **boundary-protected** `agentic_core/L0_routing/config/path_constants.py:189` `CURSOR_STATE_DIR=".cursor/state"`; **GitHub Actions** `.github/workflows/author-gate-gates.yml` (4 path refs + artifact upload); `decision_ledger.schema.sql:4` | HIGH — core edit + CI workflow + live ledger data |
| (deferred W3) `config/excluded_paths.yaml` windsurf entries | drop dead `docs/archive/windsurf/legacy-tree` | mirror in `agentic_core/.../path_constants.py` frozensets + drift gate `check_exclusion_consistency.py` | MED — core edit + receipt |

### ⚠️ Safety-critical corrections to earlier waves

1. **W2's "`.cursor/` = dead `.pyc` only" is imprecise — but NOT for the reason first stated here.** Initial P5.1 (DERIVED from refs) claimed `.cursor/state/` holds the live ledger. **W1-R1.2 of the split plan disk-verified the opposite:** `.cursor/state/` is EMPTY (only an empty `author_gate_queue/`); the live Author-Gate ledger is at `.codex/state/refactor_decisions/refactor_decision_ledger.sqlite` (`ledger_paths.py` SSOT). `agentic_core/.../path_constants.py:189 CURSOR_STATE_DIR=".cursor/state"` is a **dead constant** and the GH-workflow upload path is a **dead pointer**. Net: `.cursor/` IS safe to delete (no live data); W5 = dead-pointer cleanup, not data migration.
2. **Possible ledger drift:** both `.cursor/state/` (path_constants, CI, schema) and `.codex/state/` (constitutional §30/§35, settings hooks) are referenced. Authoritative location MUST be determined before the rename, or capture state is lost.
3. **Prior rename partially started:** `tests/unit/ops_scripts/hooks/cursor/test_post_agent_*.py` already use the new `post_agent_` name, and `rewrite_windsurf_refs_to_cursor.py` already maps `tools/windsurf/`→`tools/plan_lifecycle/`. W5 must *reconcile* with this in-flight work, not start clean.

### Boundary / authorization gates for W5
- 2 × `agentic_core/` edits (CURSOR_STATE_DIR + exclusion frozensets) → each needs Author-Gate + migration receipt.
- `before_shell_execution.py` deny-token guard blocks `.windsurf`/`post_cursor_agent` in shell → neutralize for rename (P1.3), restore at new names (P6.2).
- `.github/workflows/author-gate-gates.yml` → must update ledger paths atomically or CI artifact upload breaks.

**Recommendation:** Given (a) 800+ reference updates across 4 coupled renames, (b) live session-state + a live decision ledger in the blast radius, (c) two boundary-protected core edits, and (d) a partially-started prior rename to reconcile — **split W5 into its own dedicated plan** with its own rollback tag and per-target sub-waves. W3(P3.1)+W4 already deliver a brand-free *surface*; W6 can then verify "no functional Cursor/Windsurf dependency in prose" rather than "no name remains."

## Supersedes
- `windsurf-deprecation-cursor-ssot-b6e4a9` (prior windsurf→cursor migration) — flip to Retired when
  this plan reaches W6.

PLAN_COMPLETE: plan=cursor-windsurf-codeium-decommission-dec0de note="Parent/baseline decommission complete in IDE_archive; W5 split and legacy-tree tail remain tracked by child plans."
