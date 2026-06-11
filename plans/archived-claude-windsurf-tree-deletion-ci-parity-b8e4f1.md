---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\windsurf-tree-deletion-ci-parity-b8e4f1.md'
original_relative_path: 'windsurf-tree-deletion-ci-parity-b8e4f1.md'
source_sha256: 4b10121c0fdee13021f6ccd456863dd7c60666fba9c4b5b8841f4759fdaf13c7
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: windsurf-tree-deletion-ci-parity-b8e4f1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: true
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# `.windsurf/` folder deprecation and deletion — CI parity plan

Retire the read-only `.windsurf/` mirror tree after Cursor-only operation (~11+ days) and CI path migration from [windsurf-gha-cutover-d9f2a7](windsurf-gha-cutover-d9f2a7.md). **`.cursor/` remains SSOT.** Full tree deletion is **not** safe today.

> **plan_id discipline:** `plan_id` matches filename stem `windsurf-tree-deletion-ci-parity-b8e4f1`.

**Parent / prerequisite:** [windsurf-gha-cutover-d9f2a7](windsurf-gha-cutover-d9f2a7.md) (COMPLETED — GHA + CI path migration) · [cursor-governance-two-tier-b4e8f2](cursor-governance-two-tier-b4e8f2.md) (mirror frozen)

**Chat origin:** 2026-05-25 — user requested deprecation/deletion plan; delivered in chat only until this file was written.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: Not Started  
CURRENT_WAVE: NONE  
LAST_COMPLETED_WAVE: NONE  
LAST_UPDATED: 2026-05-25

PLAN_CREATED: slug=windsurf-tree-deletion-ci-parity-b8e4f1 path=.cursor/plans/windsurf-tree-deletion-ci-parity-b8e4f1.md status=Not Started

NOTION_PAGE_ID: 36b27693-f55c-81e7-beca-d0c788365473  
NOTION_PAGE_URL: https://www.notion.so/windsurf-tree-deletion-ci-parity-b8e4f1-36b27693f55c81e7becad0c788365473

DELETION_READINESS_TODAY: false — [windsurf_deletion_readiness.json](../../artifacts/cursor/windsurf_deletion_readiness.json)

---

## Context (SCQA)

- **Situation** — `.windsurf/` holds ~958 files (~11 MB): 544 plans, 165 scripts, 76 skills, hooks/MCP mirror, state. `.cursor/` is active SSOT (~2,693 files). User runs Cursor only (11+ days). [windsurf-gha-cutover-d9f2a7](windsurf-gha-cutover-d9f2a7.md) already migrated live CI/workflows off `.windsurf/` paths.
- **Complication** — Constitutional gates still require `.windsurf/hooks.json`, `.windsurf/mcp_config.json`, `check_windsurf_config_schema.py`, dual-write `artifacts/windsurf/`, and 700+ tests under `tests/**/windsurf/`. Deleting the tree without gate migration breaks CI.
- **Question** — How do we deprecate then delete `.windsurf/` without breaking governance?
- **Answer** — Three modes: **A** mirror-only (today) → **B** slim stub → **C** `git rm -r .windsurf/` after gate proof and 7-day soak.

---

## Current inventory (baseline)

| Tree | Files | Size | Role |
|------|-------|------|------|
| `.windsurf/` | ~958 | ~11 MB | Legacy mirror — **deprecate → delete** |
| `.cursor/` | ~2,693 | ~41 MB | **SSOT** — keep |

Top-level `.windsurf/`: `plans/` (544), `scripts/` (165), `skills/` (76), `rules/` (56), `schemas/`, `state/`, `workflows/`, `hooks.json`, `mcp_config.json`.

**Readiness gate (today):**

```bash
python ops_scripts/ci/check_windsurf_deletion_readiness.py
# deletion_safe: false — policy + mirror peers required
```

---

## Deletion strategy

| Mode | Contents | When |
|------|----------|------|
| **A — Mirror-only (NOW)** | Full `.windsurf/` tree | Current policy |
| **B — Slim stub** | `DEPRECATED.md` + optional `rules/README.md` | After W4 gate migration |
| **C — Full delete** | Directory removed | After B + `deletion_safe: true` + 7-day CI green |

**Operator assumption:** Cursor-only IDE on this repo; Windsurf IDE not used for authoring.

---

## Wave Structure

| Wave | Phase IDs | Focus | Status | Success Criteria |
|------|-----------|-------|--------|------------------|
| W0 | W0.1–W0.2 | Go/no-go + baseline proof | 🔲 TODO | Readiness JSON + rewrite dry-run clean |
| W1 | W1.1–W1.4 | CI reference burndown | 🔲 TODO | Active code reads `.cursor/` only |
| W2 | W2.1–W2.3 | Duplicate content retirement | 🔲 TODO | `.windsurf/plans` dupes removed or archived |
| W3 | W3.1–W3.2 | `artifacts/windsurf` namespace | 🔲 TODO | Dual-write removed; cursor-only logs |
| W4 | W4.1–W4.2 | Retire mirror gates → stub | 🔲 TODO | `deletion_safe: true` |
| W5 | W5.1 | `git rm -r .windsurf/` + soak proof | 🔲 TODO | Tree absent; CI green 7 days |

---

## Status Tables

### Wave Progress

| Wave | Focus | Status |
|------|-------|--------|
| W0 | Go/no-go | 🔲 TODO |
| W1 | Reference burndown | 🔲 TODO |
| W2 | Content retirement | 🔲 TODO |
| W3 | Artifact namespace | 🔲 TODO |
| W4 | Gate retirement / stub | 🔲 TODO |
| W5 | Full tree deletion | 🔲 TODO |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Operator confirms Cursor-only; branch protection audit | 🔲 TODO |
| W0.2 | `rewrite_windsurf_refs_to_cursor.py --dry-run` clean | 🔲 TODO |
| W1.1 | Retarget `check_skill_frontmatter` → `.cursor/skills` | 🔲 TODO |
| W1.2 | Retarget `check_hook_consolidation` → `.cursor/hooks.json` | 🔲 TODO |
| W1.3 | Retarget plan/AG gates off `.windsurf/scripts` | 🔲 TODO |
| W1.4 | `.pre-commit-config.yaml` — MCP hooks cursor-only | 🔲 TODO |
| W2.1 | Dedupe `.windsurf/plans/` vs `.cursor/plans/` | 🔲 TODO |
| W2.2 | Remove mirrored scripts/skills/workflows | 🔲 TODO |
| W2.3 | Ledger SSOT `.cursor/state/refactor_decisions/` only | 🔲 TODO |
| W3.1 | Stop dual-write in `_governance_paths.py` | 🔲 TODO |
| W3.2 | Migrate `artifacts/windsurf/` logs | 🔲 TODO |
| W4.1 | Rename/replace `check_windsurf_config_schema` → cursor-only | 🔲 TODO |
| W4.2 | Flip `check_windsurf_deletion_readiness` → `deletion_safe: true` | 🔲 TODO |
| W5.1 | `git rm -r .windsurf/` + test rename + closeout receipt | 🔲 TODO |

---

## W0 — Go/no-go

**Commands:**

```bash
python ops_scripts/ci/check_windsurf_deletion_readiness.py
python ops_scripts/ci/check_cursor_governance_mirror_health.py
python ops_scripts/maintenance/rewrite_windsurf_refs_to_cursor.py --dry-run
```

**Acceptance:** Operator confirms no Windsurf IDE authoring; dry-run shows zero unexpected `.windsurf` refs outside `_archive` / `_legacy_*`.

---

## W1 — CI reference burndown (P0)

| File | Change |
|------|--------|
| `ops_scripts/ci/check_skill_frontmatter.py` | `SKILLS_ROOT` → `.cursor/skills` |
| `ops_scripts/ci/check_hook_consolidation.py` | `HOOKS_JSON_PATH` → `.cursor/hooks.json` |
| `ops_scripts/ci/check_decision_required.py` | triggers → `.cursor/schemas/` |
| `ops_scripts/ci/check_agentic_core_addition.py` | schema → `.cursor/schemas/` |
| `ops_scripts/ci/run_contract_gates.py` | skills_dir → `.cursor/skills` |
| `ops_scripts/ci/check_apps_test_surface_parity.py` | scripts → `.cursor/scripts` |
| `.pre-commit-config.yaml` | Remove `.windsurf/mcp_config.json` triggers |

**Tool:** `python ops_scripts/maintenance/rewrite_windsurf_refs_to_cursor.py`

---

## W2 — Duplicate content retirement

- `.windsurf/plans/` — diff vs `.cursor/plans/` + `_archive/windsurf_legacy/`; delete windsurf-only dupes.
- `.windsurf/scripts|skills|workflows/` — delete after `.cursor/` parity confirmed.
- Notion: `python tools/notion/migrate_plan_paths_windsurf_to_cursor.py` if any `.windsurf/plans` paths remain.

---

## W3 — Artifact namespace

- [_governance_paths.py](../../ops_scripts/ci/_governance_paths.py) — remove `append_governance_artifact_jsonl` dual-write to `artifacts/windsurf/`.
- Workflows — `artifacts/cursor/` only.
- Gate: `rg 'artifacts/windsurf'` → archives/docs only.

---

## W4 — Gate retirement (Mode B)

| Gate | Target |
|------|--------|
| `check_windsurf_config_schema.py` | Validate `.cursor/hooks.json` + `.cursor/mcp.json` only; rename to `check_cursor_config_schema.py` |
| `check_cursor_governance_mirror_health.py` | Delete or invert to `check_no_windsurf_tree.py` |
| `check_windsurf_deletion_readiness.py` | Policy: `deletion_safe: true` when blockers empty |
| `check_mcp_editor_parity.py` | Single-file schema |

**Stub (optional before W5):**

```
.windsurf/
  DEPRECATED.md
  rules/README.md
```

---

## W5 — Full tree deletion (Mode C)

**Pre-delete checklist:**

- [ ] `deletion_safe: true` in [artifacts/cursor/windsurf_deletion_readiness.json](../../artifacts/cursor/windsurf_deletion_readiness.json)
- [ ] `rg '\.windsurf'` outside `_archive` / legacy → documented only
- [ ] [structure_policy.yaml](../../config/structure_blueprint/structure_policy.yaml) updated
- [ ] Notion Plans: no `Plan File Path` under `.windsurf/plans/`
- [ ] 7-day CI green on `main`

**Command:**

```bash
git rm -r .windsurf/
```

**Post-delete:** Rename `tests/unit/ops_scripts/hooks/windsurf/` → `governance/`; archive `docs/standards/windsurf/`; update `AGENTS.md` Notion map.

**Receipt:** `docs/reports/cursor/windsurf_folder_deletion_closeout_<date>.md`

---

## CI gate dependency map

```text
hard_blockers_today:
  check_windsurf_config_schema  → .windsurf/hooks.json + mcp_config.json
  check_cursor_governance_mirror_health → requires mirror peers
  check_skill_frontmatter → .windsurf/skills (bug: doc says cursor)
  check_hook_consolidation → .windsurf/hooks.json
  pre-commit MCP mirror files
  dual-write artifacts/windsurf

W1 → W3 → W4 → deletion_safe:true → W5 git rm
```

---

## Out of scope

- Re-running [windsurf-gha-cutover-d9f2a7](windsurf-gha-cutover-d9f2a7.md) (already COMPLETED)
- Windsurf IDE hook 1:1 port (see [cursor_windsurf_hook_migration_inventory.md](../../docs/reports/cursor_windsurf_hook_migration_inventory.md))
- `agentic_core` / `apps_rg` product runtime
- Weakening gates to greenwash deletion

---

## Definition of Done

| DoD | Criterion | Status |
|-----|-----------|--------|
| DoD-1 | Zero active CI reads of `.windsurf/` (except archive baselines) | 🔲 TODO |
| DoD-2 | `artifacts/windsurf/` dual-write removed | 🔲 TODO |
| DoD-3 | `deletion_safe: true` | 🔲 TODO |
| DoD-4 | `.windsurf/` absent from repo | 🔲 TODO |
| DoD-5 | Closeout receipt + Notion Completed | 🔲 TODO |

---

## Suggested timeline (Cursor-only)

| Week | Wave |
|------|------|
| 1 | W0 + W1 |
| 2 | W2 + W3 |
| 3 | W4 (stub or empty gates) |
| 4 | W5 + 7-day soak |

---

## References

- Deprecation plan chat: 2026-05-25 (this file materialized from that session)
- [windsurf_gha_cutover_closeout.md](../../docs/reports/cursor/windsurf_gha_cutover_closeout.md)
- [windsurf_gha_metadata_reconcile_20260525_receipt.md](../../docs/reports/cursor/windsurf_gha_metadata_reconcile_20260525_receipt.md)
- [governance_two_tier_closeout.md](../../docs/reports/cursor/governance_two_tier_closeout.md)
- [rewrite_windsurf_refs_to_cursor.py](../../ops_scripts/maintenance/rewrite_windsurf_refs_to_cursor.py)
- [check_windsurf_deletion_readiness.py](../../ops_scripts/ci/check_windsurf_deletion_readiness.py)
- Transferred from gha cutover phase **W1.D1** (OUT_OF_BAND)
