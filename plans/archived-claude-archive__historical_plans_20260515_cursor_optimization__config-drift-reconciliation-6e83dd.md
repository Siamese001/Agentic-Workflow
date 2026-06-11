---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\config-drift-reconciliation-6e83dd.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\config-drift-reconciliation-6e83dd.md'
source_sha256: 3cb1d7ed16fae5a453f9aa8ed62ca6f78c8f48c403a76433133edf9bab8a583d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Config Drift Reconciliation Plan

Reconcile MCP config + AGENTS.md drift by symlinking the actual-read paths, slimming AGENTS.md via `.windsurf/rules/` split, marking machine-derived sections as autogen blocks, and wiring all sync checks into a PR-blocking GitHub Actions workflow.

## Objective

Eliminate the recurring drift between `.windsurf/mcp_config.json` ↔ `~/.codeium/windsurf/mcp_config.json` and between `mcp_config.json` ↔ `AGENTS.md` while **preserving cross-tool (Codex/Cursor/Cascade-Code) interop** via a symlinked root `AGENTS.md`.

## Scope

In scope:
- MCP config drift (repo ↔ global)
- AGENTS.md physical location + slimming
- Autogen blocks for MCP table, Notion Workspace Map, Hooks summary, Memory Lifecycle tool listings
- CI gate(s) moved from pre-commit-only to GitHub Actions (not bypassable with `--no-verify`)
- Contributor setup script for symlinks

Out of scope (deferred):
- Migration of procedural runbooks into Skills/Workflows (optional follow-up)
- Delete of subdirectory AGENTS.md support (none exist today)
- Drift items #8 (rules/constitutional/memory triplication) and #12 (ADG CI YAML sync) from earlier audit — separate plans

## Tier & Constraints

- **Tier**: T3 — cross-layer (repo config + CI + docs + contributor onboarding), >5 files.
- **Must preserve**: `AGENTS.md` at repo root (as symlink) for Codex/Cursor/Cascade-Code interop.
- **Must respect**: `.windsurf/rules/*.md` 12,000-char cap per file; `global_rules.md` 6,000-char cap.
- **Must not break**: existing pre-commit hooks `mcp-sync-integrity` (T6b) and `agents-mcp-coverage` (T6c).
- **No PowerShell in runtime**; setup script is contributor-run, one-time, and `.ps1` is acceptable there.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1–P1.3 | MCP config drift kill (symlink + CI gate + contributor script) | ~4k | User has Dev Mode or admin on Windows | TODO | Symlink verified; GHA workflow green; `check_mcp_sync_integrity.py` runs on every PR |
| W2 | P2.1–P2.4 | AGENTS.md relocation + autogen blocks | ~6k | Current AGENTS.md content fits after slimming | TODO | Root `AGENTS.md` is symlink; autogen markers present; regeneration idempotent |
| W3 | P3.1–P3.3 | Content migration into `.windsurf/rules/*.md` with correct triggers | ~5k | Each split rule file stays <12k chars | TODO | No rule file exceeds cap; always-on footprint reduced |
| W4 | P4.1–P4.2 | Additional CI gates + documentation | ~3k | Existing pytest/sync scripts unchanged | TODO | `config-sync-gates.yml` blocks PRs on drift; policy doc updated |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | MCP config symlink setup script | `tools/setup/setup_symlinks.ps1` (new), `tools/setup/setup_symlinks.sh` (new), `docs/guides/MCP_Config_Version_Policy.md` (edit) | Windows requires Dev Mode or admin | ~1.5k | TODO |
| P1.2 | GitHub Actions config-sync workflow | `.github/workflows/config-sync-gates.yml` (new) | Must not duplicate ADG workflow triggers | ~1k | TODO |
| P1.3 | Post-write hook becomes no-op on symlinked machines | `.windsurf/scripts/post_write_mcp_config_sync.py` (edit) | Detect same-inode / same-realpath; skip copy safely | ~1.5k | TODO |
| P2.1 | Relocate AGENTS.md to `.windsurf/AGENTS.md` + symlink root | `AGENTS.md` (remove + re-create as symlink), `.windsurf/AGENTS.md` (new, content moved) | Git must track symlink target, not copy. Windows symlink via setup script. | ~1k | TODO |
| P2.2 | Mark autogen blocks in `.windsurf/AGENTS.md` | `.windsurf/AGENTS.md` (edit) | Existing `<!-- MCP-QUICK-REFERENCE:START -->` kept; add 3 new: `NOTION-MAP`, `HOOKS-SUMMARY`, `MCP-TOOL-LISTINGS` | ~1.5k | TODO |
| P2.3 | Extend `sync_mcp_config.py` to regenerate all 4 autogen blocks | `.windsurf/scripts/sync_mcp_config.py` (edit), `config/notion_databases.yaml` (new) | Fix stale `_default_db_id` in `post_write_mcp_config_sync.py` (drift item #6); source Notion DB IDs from new YAML | ~2k | TODO |
| P2.4 | New `check_agents_md_sync.py` gate | `ops_scripts/ci/check_agents_md_sync.py` (new), `.pre-commit-config.yaml` (edit — add T6d hook), `config-sync-gates.yml` (edit — wire) | Must diff regenerated vs current for all 4 blocks | ~1.5k | TODO |
| P3.1 | Inventory AGENTS.md content; tag each section by target trigger mode | `.windsurf/AGENTS.md` (read-only analysis in plan evidence) | Pick `always_on` vs `model_decision` vs `glob` per section; respect 12k cap | ~1.5k | TODO |
| P3.2 | Move stable sections to `.windsurf/rules/agents-core.md` (always_on) + `agents-mcp-routing.md` (model_decision) + `agents-memory-lifecycle.md` (model_decision) | `.windsurf/rules/agents-core.md` (new), `.windsurf/rules/agents-mcp-routing.md` (new), `.windsurf/rules/agents-memory-lifecycle.md` (new), `.windsurf/AGENTS.md` (edit — leave thin summary + autogen blocks only) | Autogen MCP/Notion/Hooks blocks stay in AGENTS.md for cross-tool interop; behavioral rules move out | ~2k | TODO |
| P3.3 | Update `RULES_INDEX.md` and cross-references | `.windsurf/RULES_INDEX.md` (edit) | Any rule/skill that linked into AGENTS.md now links to the rules file | ~1k | TODO |
| P4.1 | Wire `check_exclusion_sync.py` and `check_agents_md_sync.py` into `config-sync-gates.yml` | `.github/workflows/config-sync-gates.yml` (edit) | Single workflow, short timeout, no heavy deps | ~0.5k | TODO |
| P4.2 | Update `MCP_Config_Version_Policy.md` with symlink-as-primary + sync fallback | `docs/guides/MCP_Config_Version_Policy.md` (edit), `.windsurf/rules/mcp-config-ssot.md` (edit) | Explain the two contributor paths; keep the SSOT rule consistent | ~1k | TODO |

## Detailed Changes (per phase)

### W1 — MCP config drift kill

**P1.1 Symlink setup script**
- `tools/setup/setup_symlinks.ps1` — Windows PowerShell; creates `~/.codeium/windsurf/mcp_config.json` → `.windsurf/mcp_config.json`. Idempotent. Detects existing file and backs it up before replacing with symlink. Requires Dev Mode or admin (document this).
- `tools/setup/setup_symlinks.sh` — POSIX equivalent (macOS/Linux/WSL).
- README line added to root README.md pointing to this setup step.

**P1.2 GitHub Actions workflow**
- `.github/workflows/config-sync-gates.yml` — runs on every PR targeting any branch, paths: `[".windsurf/**", "AGENTS.md", "config/**", "ops_scripts/ci/check_*sync*.py", ".pre-commit-config.yaml"]`. Steps:
  1. `check_mcp_sync_integrity.py` (without `--check-global` — global file doesn't exist in CI)
  2. `check_agents_mcp_coverage.py`
  3. `check_exclusion_sync.py` (NEW wiring — was not in CI)
  4. `check_agents_md_sync.py` (NEW gate, see P2.4)
  5. `_validate_pytest_config.py --strict`
- Fail-closed. No warn-only modes. ~30s total.

**P1.3 Post-write hook no-op detection**
- In `post_write_mcp_config_sync.py`, before `sync_global_config()`, check `Path.samefile(SSOT, GLOBAL)` (or `os.path.realpath` equivalence). If same file (symlink in place), print `[mcp_sync] SSOT and global are the same file (symlinked); skipping copy.` and return 0.
- Keeps the hook useful for contributors who skip the symlink setup, harmless for those who did.

### W2 — AGENTS.md relocation + autogen blocks

**P2.1 Physical move + symlink**
- Git mv `AGENTS.md` → `.windsurf/AGENTS.md`.
- Root `AGENTS.md` becomes a symlink created by `setup_symlinks.ps1`/`.sh` (extend those scripts to also create this symlink).
- Commit: `.windsurf/AGENTS.md` is the tracked file. Root symlink is per-machine (not committed on Windows where git-symlink support is fragile). Add `AGENTS.md` to `.gitignore` IF and only if symlink-commit is decided unreliable; otherwise commit the symlink.
- Decision flag in the setup script: `--commit-root-symlink` to let power users try git-tracked symlink.

**P2.2 Autogen block markers**
- In `.windsurf/AGENTS.md`, wrap these sections with BEGIN/END markers:
  - `<!-- MCP-QUICK-REFERENCE:START/END -->` (already present)
  - `<!-- NOTION-MAP:START/END -->` (new)
  - `<!-- HOOKS-SUMMARY:START/END -->` (new) — auto-generated from `.windsurf/hooks.json`
  - `<!-- MCP-TOOL-LISTINGS:START/END -->` (new) — currently hand-written in Memory Lifecycle; derive from `mcp_config.json` capability metadata
- Human-authored narrative stays outside the markers.

**P2.3 Generator + Notion DB SSOT**
- `config/notion_databases.yaml` (new): 8 databases with `id`, `name`, `read_trigger`, `write_trigger`, `query_tool`. Includes the MCP Registry DB ID.
- `sync_mcp_config.py` gets `generate_notion_map()`, `generate_hooks_summary()`, `generate_mcp_tool_listings()`; `sync_agents_md()` writes all 4 blocks.
- Fix `post_write_mcp_config_sync.py:106` — replace hardcoded `_default_db_id = "59693bbc71b14c63bc9fb31eb8b08a0e"` with `load_notion_databases_yaml()["mcp_registry"]["id"]` so the Notion upsert targets the correct DB (`e7b149b4-…`). This fixes active drift item #6.

**P2.4 `check_agents_md_sync.py`**
- Regenerates all 4 autogen blocks in memory, extracts corresponding blocks from AGENTS.md, diffs. Fails if any block drifted.
- Added as T6d pre-commit hook (staged-file-scoped to `AGENTS.md`, `mcp_config.json`, `notion_databases.yaml`, `hooks.json`).
- Wired into `config-sync-gates.yml`.

### W3 — Content migration

**P3.1 Inventory**
- Evidence-only: read current `.windsurf/AGENTS.md` and tag each H2 section with proposed target: stay-in-AGENTS, move-to-rules-always-on, move-to-rules-model-decision, move-to-rules-glob, delete-redundant.
- Output: inline table in plan `docs/reports/plans/config-drift-reconciliation-audit.md` (created in W3 execution, not now).

**P3.2 Move**
Proposed splits (sizes are estimates; will validate against 12k cap before writing):
- `.windsurf/rules/agents-core.md` (`trigger: always_on`, ~3k chars): Plan First/Execute Second, SR_INTAKE/SR_PLAN/SR_APPROVAL template, Layer Separation table, Constitutional Constraints bullet list, citation of constitutional.md.
- `.windsurf/rules/agents-mcp-routing.md` (`trigger: model_decision`, ~5k chars): auto-routing rules table (event → Notion write), sync enforcement gates list, MCP authority detail prose that's too long for always_on.
- `.windsurf/rules/agents-memory-lifecycle.md` (`trigger: model_decision`, ~3k chars): memory read/write/maintain tables, entity type conventions table.
- `.windsurf/AGENTS.md` (final, ~4k chars): brief intro paragraph + 4 autogen blocks (MCP Quick Reference, Notion Map, Hooks Summary, MCP Tool Listings) + cross-references into the 3 rule files above + Windsurf Configuration Docs pointer.

**P3.3 RULES_INDEX update**
- Add the 3 new rule files to `RULES_INDEX.md`.
- Any in-repo link to `AGENTS.md#<section>` that now lives in rules gets updated.

### W4 — CI + docs

**P4.1** See P1.2 (workflow extension).

**P4.2 Policy doc**
- `docs/guides/MCP_Config_Version_Policy.md`: add "Preferred: symlink setup" as primary path, "Fallback: post-write hook" as secondary, "Verification: `check_mcp_sync_integrity.py`" as guarantee.
- `.windsurf/rules/mcp-config-ssot.md`: update Sync Contract section to reflect symlink-as-primary, no-op detection in post-write hook, PR-blocking CI gate.

## Gap Register

| ID | Gap | Mitigation |
|---|---|---|
| G1 | Windows symlink requires Dev Mode OR admin | Setup script detects + errors with clear instructions; fallback is the existing post-write hook (no regression) |
| G2 | Git symlink tracking on Windows is fragile | Default: root symlink is per-machine, created by setup script; tracked file is `.windsurf/AGENTS.md`. Opt-in flag for experimenters. |
| G3 | AGENTS.md slim might lose context when Codex/Cursor read only root file | Autogen blocks keep MCP table, Notion map, hooks summary, tool listings at root; behavioral rules moved out are documented via cross-references |
| G4 | 12k char cap on rule files | Phase P3.1 validates sizes against cap before P3.2 writes; can add 4th rule file if needed |
| G5 | Contributors on machines without symlink still drift between writes | Post-write hook still runs; CI gate blocks PRs; symlink is strongly recommended not mandatory |
| G6 | Notion DB ID stale default already in production code | P2.3 fixes as part of generator refactor — gate P2.4 will fail PRs that reintroduce hardcoded IDs |

## Verification Steps

Per phase (executed at phase completion):

- **P1.1**: run setup script on Windows + WSL; verify `Get-Item $env:USERPROFILE\.codeium\windsurf\mcp_config.json | Select LinkType` shows `SymbolicLink`; edit `.windsurf/mcp_config.json`, confirm change visible in global path immediately.
- **P1.2**: push branch with intentional mcp_config drift → GHA workflow fails. Revert → passes.
- **P1.3**: run post-write hook with symlink in place → prints skip message, exit 0. Without symlink → copies as before.
- **P2.1**: `git log --follow .windsurf/AGENTS.md` shows the move; `ls -la AGENTS.md` (WSL) shows symlink.
- **P2.2/P2.3**: `python .windsurf/scripts/sync_mcp_config.py` regenerates idempotently (diff empty on second run). Notion MCP Registry row upserts to correct DB ID.
- **P2.4**: manually corrupt Notion map in AGENTS.md → `check_agents_md_sync.py` fails with clear message. Regenerate → passes.
- **P3.1**: inventory table documents every AGENTS.md H2 section.
- **P3.2**: `wc -c` on each new rule file <12000. Cascade invoked with a T2 task still cites the moved rule via model_decision activation.
- **P3.3**: `RULES_INDEX.md` lists all rule files; no broken in-repo links to old AGENTS.md sections.
- **P4.1**: full PR-target-branch run on a test branch shows all 5 sync gates pass.
- **P4.2**: docs describe both symlink and fallback paths accurately; SSOT rule mentions no-op detection.

## Success Criteria

1. `.windsurf/mcp_config.json` and `~/.codeium/windsurf/mcp_config.json` are the same file on disk on the primary dev machine (verified via symlink).
2. Root `AGENTS.md` is a symlink to `.windsurf/AGENTS.md` (or removed + per-machine recreated) — no duplicate content.
3. MCP Quick Reference, Notion Workspace Map, Hooks Summary, MCP Tool Listings in AGENTS.md are all regenerated from SSOT sources with no hand-edit drift possible.
4. GitHub Actions `config-sync-gates.yml` passes on clean main, fails on any introduced drift (MCP config, AGENTS.md autogen blocks, excluded_paths, pytest config).
5. No `.windsurf/rules/*.md` file exceeds 12,000 characters.
6. Notion MCP Registry hardcoded DB ID drift (audit item #6) is eliminated.
7. No behavioral regression: existing ADG, pre-commit, and Windsurf hooks continue to function.

## Rollback Checkpoints

- After P1.2: branch tag `rollback/w1-complete` — MCP config drift eliminated, no AGENTS.md changes yet. Safe stopping point.
- After P2.4: branch tag `rollback/w2-complete` — AGENTS.md relocated + autogen enforced, content not yet split. Safe stopping point.
- After P3.3: branch tag `rollback/w3-complete` — full content migration done.
- P4 is additive (docs + workflow refinement) — no rollback needed.

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Windows symlink creation fails for contributor without Dev Mode | High | Low | Post-write hook fallback works unchanged |
| Autogen regeneration produces unstable output (ordering, whitespace) | Medium | High | Deterministic key sorting + snapshot test before CI wiring |
| `.windsurf/rules/*.md` split changes Cascade behavior (rules loaded differently) | Medium | Medium | Stage-wise: keep always-on content equivalent in P3.2 before relying on model_decision activation |
| Root AGENTS.md as symlink breaks cross-tool discovery on some CI systems | Low | Medium | Keep `.windsurf/AGENTS.md` itself well-formed; tools that don't resolve symlinks can point directly at `.windsurf/AGENTS.md` |
| GHA workflow adds meaningful CI latency | Low | Low | All 5 checks are pure Python stdlib + YAML parse; <30s total |

## Deliverables

New files (9):
- `tools/setup/setup_symlinks.ps1`
- `tools/setup/setup_symlinks.sh`
- `.github/workflows/config-sync-gates.yml`
- `config/notion_databases.yaml`
- `ops_scripts/ci/check_agents_md_sync.py`
- `.windsurf/AGENTS.md` (moved from root)
- `.windsurf/rules/agents-core.md`
- `.windsurf/rules/agents-mcp-routing.md`
- `.windsurf/rules/agents-memory-lifecycle.md`

Modified files (7):
- `AGENTS.md` (becomes symlink or removed in favor of per-machine recreation)
- `.windsurf/scripts/sync_mcp_config.py`
- `.windsurf/scripts/post_write_mcp_config_sync.py`
- `.pre-commit-config.yaml` (add T6d)
- `.windsurf/rules/mcp-config-ssot.md`
- `.windsurf/RULES_INDEX.md`
- `docs/guides/MCP_Config_Version_Policy.md`

## Open Questions (non-blocking, surface during execution)

- Should we ALSO symlink `global_rules.md` in this plan or defer? (Tentative: defer — separate drift surface, not in original complaint.)
- Preferred behavior when a contributor has neither symlink nor runs pre-commit? (Tentative: GHA blocks their PR — enforced boundary.)
