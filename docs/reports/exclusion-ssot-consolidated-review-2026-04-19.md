# Exclusion SSOT — Consolidated Review

**Date**: 2026-04-19  
**Trigger**: Post-LFS-purge realization that `06_data` (3–4 months stale) sat uncontested in `config/excluded_paths.yaml` despite having **zero commits** touching it in git history — symptomatic of multiple unreconciled exclusion SSOTs across the repo.  
**Method**: ADG SQLite queries + targeted grep for concrete literals (`EXCLUDE_DIRS`, `SOVEREIGN_EXCLUDED_FOLDERS`, etc.) + filesystem enumeration of `*ignore*` / `*exclud*` artifacts.  
**Prior art**: `docs/reports/gitignore-ssot-duplication-analysis.md` identified 3 of the SSOTs; this review finds **8**.

---

## TL;DR

There is no single SSOT. There are **8 surfaces** defining exclusion/ignore scope, split across four tools (git, pre-commit, Windsurf, Docker) and two languages (YAML, Python). At least three of them drift silently, two are hand-maintained, and one (`06_data`) is demonstrably dead.

| # | Surface | Kind | Scope | Authoritative? | Generated? |
|---|---|---|---|---|---|
| 1 | `config/excluded_paths.yaml` | YAML | git + pre-commit + scanners | Claims primary SSOT | No — hand-edited |
| 2 | `.gitignore` | generated | git | No | ✅ from #1 (hook) |
| 3 | `.pre-commit-config.yaml::exclude` | regex-in-YAML | pre-commit only | No | Manual with `precommit_excludes` (#1) sync check only |
| 4 | `.codeiumignore` | glob | Windsurf indexing | Separate authority | No — hand-edited |
| 5 | `.gitattributes` | attrs | LFS filter | Separate authority | No — hand-edited |
| 6 | `ops_scripts/dev_tools/L0_routing_scripts/.dockerignore` | glob | Docker only | Localized | No — hand-edited |
| 7 | `agentic_core/L0_routing/config/path_constants.py::GLOBAL_EXCLUDED_DIRS` + `SOVEREIGN_EXCLUDED_FOLDERS` + `DISCOVERY_EXCLUDED_TERRITORIES` | Python frozenset | 15+ runtime scanners, agents, enforcers | De-facto runtime SSOT | No — hand-edited |
| 8 | Per-file hardcoded sets (e.g. `PascalSovereigntyAgent.py:224`) | Python literal | one agent | Shadow SSOT | No |

---

## 1 — Inventory

### 1.1 File-level artifacts (6 files)

```
config/excluded_paths.yaml                                  163 lines   SSOT (YAML)
.gitignore                                                   99 lines   generated
.codeiumignore                                               41 lines   hand
.pre-commit-config.yaml  [exclude block, ~48 regex entries]             hand
.gitattributes           [9 filter=lfs rules]                           hand
ops_scripts/dev_tools/L0_routing_scripts/.dockerignore      982 bytes   hand
```

### 1.2 Python code-level SSOTs (`@c:\Git\Agentic-Workflow\agentic_core\L0_routing\config\path_constants.py:248-310`)

```python
SOVEREIGN_EXCLUDED_FOLDERS  # 10 entries — runtime scanning guard
GLOBAL_EXCLUDED_DIRS        # 17 entries — broader scanning guard
DISCOVERY_EXCLUDED_TERRITORIES  # 6 entries — runtime_shared, legacy_code, legacy_engines, archives, stubs, examples
```

Consumed by **at least 18 modules** (sampled via grep; full list below):

- `@c:\Git\Agentic-Workflow\agentic_core\utils\fs_util.py:34` — default exclude set for `find_python_files()`
- `@c:\Git\Agentic-Workflow\agentic_core\runtime\utils\file_cache_util.py:81,174` — `FileCache.EXCLUDED_DIRS`
- `@c:\Git\Agentic-Workflow\agentic_core\runtime\utils\sovereign_index_util.py:91`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\airlock_guardrail.py:13,69`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\credential_guard.py:100,264`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\hardcoded_path_refactorer_enforcer.py:2-6,182`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\import_surgeon_enforcer.py:104,182`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\module_collision_guardrail.py:112,210`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\ssot_guardrail.py:40`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\ssot_scanner_enforcer.py:16,406`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\HygieneGuardianAgent.py:98-102,421,602`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\SprawlInspectorAgent.py:100,233`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\gravity_validator.py`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\GravityLeakRepairAgent.py`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\DuplicateCodeDetectorAgent.py`
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\utils\credential_scanner_util.py`
- plus 10+ `ops_scripts/dev_tools/L0_routing_scripts/run_guardian_*.py` scripts

### 1.3 Loaders and sync-checkers (Python)

- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\config\exclusion_loader.py` — loads YAML, exposes `EXCLUDED_DIRS`, `EXCLUDED_FILE_PATTERNS` frozensets, **and explicitly acknowledges dual-SSOT reality** via `verify_against_ssot(ssot_frozenset)`.
- `@c:\Git\Agentic-Workflow\tools\generate\generate_gitignore.py` — generates `.gitignore` + `.pre-commit-config` exclude block from YAML.
- `@c:\Git\Agentic-Workflow\tools\generate\check_exclusion_sync.py` — checks YAML `precommit_excludes` ↔ `.pre-commit-config.yaml`.
- `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\config\structure_blueprint\ssot.py` — defines structure SSOT, overlaps with `path_constants.py`.

### 1.4 Shadow SSOTs (hardcoded)

Example — not imported from `path_constants`:

```python
# @c:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\PascalSovereigntyAgent.py:224
exclude_dirs = {".git", "archives", "__pycache__", "node_modules", "venv", ".env"}
```

168 grep matches for exclusion-set literal names across 57 Python files — a non-trivial fraction of these are hardcoded instead of imports.

---

## 2 — Drift analysis

### 2.1 YAML ↔ `path_constants.py` (structural SSOT vs runtime SSOT)

Entries in **YAML `all_dirs` but NOT in `GLOBAL_EXCLUDED_DIRS ∪ SOVEREIGN_EXCLUDED_FOLDERS`**:

- `06_data` — **dead** (0 git commits touching it — see §3.1)
- `data/cache`, `data/corpus`, `data/external`, `data/manifests`, `data/memory`, `data/monitoring`, `data/processed`, `data/prompt_governance`, `data/rag_seeds`, `data/snapshots`, `data/ssot_artifacts`, `data/store`
- `artifacts/_legacy_adg_archives`, `artifacts/adg_clean`, `artifacts/reports/test_enforcement`
- `docs/reference/_archive`, `docs/windsurf`, `logs`, `raw`, `shared`
- `.idea`, `.vscode`, `.DS_Store` (IDE)
- `_compat`, `.hypothesis`
- `google`, `gapic`, `pip`, `dist-info`, `licenses`, `src` (vendor)

Entries in **`GLOBAL_EXCLUDED_DIRS` but NOT in YAML**:

- `.github` — git-host meta, present in Python but not `.gitignore` (correct — we track it)
- `.windsurf` — **LIKELY ERROR**: Python excludes it, but the repo deliberately tracks `.windsurf/mcp_config.json`, rules, plans, skills. If a scanner uses `GLOBAL_EXCLUDED_DIRS` it will skip our own governance configs.
- `.nox`, `eggs`, `*.egg-info`, `htmlcov`

Entries in **`DISCOVERY_EXCLUDED_TERRITORIES`**:

- `runtime_shared`, `legacy_code`, `legacy_engines`, `archives`, `stubs`, `examples` — only `archives` appears in YAML.

### 2.2 `.codeiumignore` ↔ everything

`.codeiumignore` uniquely includes glob negation:

```
artifacts/windsurf/
!artifacts/windsurf/session_state.json
```

No other surface can express this. YAML→`.gitignore` generator drops negations. `.codeiumignore` is therefore **not** derivable from the YAML SSOT as-is.

Also unique to `.codeiumignore`: `**/*.pb`, `.codeium/windsurf/cascade/`, `tools/adg/cache/__pycache__/` (narrow scope — excludes only pycache, not the module).

### 2.3 `.pre-commit-config.yaml::exclude`

Syncs via `check_exclusion_sync.py` — passes today (verified during T6e earlier in session). But `precommit_excludes` contains 30+ patterns found nowhere else (`temp_[^/]*/.*`, `_temp_cmd.*`, `runtime_state.*\.json`, `guardian_.*\.(txt|json)`, `v15_d_evidence_.*\.json`, `v15_p2_evidence_temp\.json`, `v15_d_inventory_p4\.json`, `core/.*`).

### 2.4 `.gitattributes`

Orthogonal concern — defines LFS *filter* not exclusion — but after today's history purge, `.gitattributes` still declares `*.sqlite`, `*.zip`, `*.pkl`, `*.gz` as `filter=lfs`. These patterns now overlap with YAML `file_patterns` that declare them *excluded from git entirely*. A future `*.zip` file would either be LFS-tracked or gitignored depending on `.gitignore`'s evaluation order. Risk: low today (gitignore wins), but worth documenting.

### 2.5 `.dockerignore`

Lives only under `ops_scripts/dev_tools/L0_routing_scripts/.dockerignore`. Repo has no root-level Dockerfile. This file is scoped to that one script directory. Possibly stale — worth auditing separately.

---

## 3 — Staleness review

### 3.1 `06_data` — confirmed dead

```
$ git log --all --oneline --follow -- 06_data
# (zero commits)
```

The entry was added defensively during the LFS purge session today (2026-04-19). It is now safe to remove from `config/excluded_paths.yaml` — the directory never existed in the repo history. Leaving it in place is harmless but misleading.

### 3.2 v15_* relics

`config/excluded_paths.yaml` `precommit_excludes` contains:

- `v15_d_evidence_.*\.json`
- `v15_p2_evidence_temp\.json`
- `v15_d_inventory_p4\.json`

v15 (Wave 15) predates the current Wave-16 / Wave-G / Wave-I work. These files likely don't exist anymore. Candidates for deletion from the SSOT.

### 3.3 `core/.*`

`precommit_excludes` has `core/.*` with comment "Core directory (legacy)". `core/` is not in the current repo structure. Safe to delete.

### 3.4 `.backup/guardian_tests/.*`

Legacy guardian backup scheme. `.backup/` is present in YAML `archive_dirs` already, making `.backup/guardian_tests/.*` redundant.

---

## 4 — Risk matrix

| Risk | Impact | Likelihood | Why it happens |
|---|---|---|---|
| Scanner misses files because `GLOBAL_EXCLUDED_DIRS` drops `.windsurf` but devs track files under `.windsurf/` | Medium — governance artifacts invisible to scanners | High — already happening | Python SSOT diverged from YAML |
| New pattern added to YAML, forgotten in `.codeiumignore`, Windsurf indexes noise | Low — just noise | Medium | `.codeiumignore` is hand-maintained |
| Hardcoded `exclude_dirs` in one agent becomes stale (e.g. misses `.sovereign_healing_backup`) | Medium — scanner produces bad data | Medium — 1 known occurrence today | Copy-paste pattern |
| `v15_*` patterns increase precommit regex cost forever | Very low — regex is cheap | High | Nobody deletes dead entries |
| `06_data`-class entries accrete in YAML | Low individually, high cumulatively | High — just happened today | No review cadence |
| LFS filter rule + gitignore disagree on `*.zip` / `*.gz` / `*.pkl` | Low — gitignore wins | Low | Independent evolution |

---

## 5 — Recommendations

Scored for HITL decision. Each is independent — can pick multiple.

### R1 — Remove confirmed-dead entries immediately (score 0.92)

Delete from `config/excluded_paths.yaml`:

- `06_data` (0 commits, added defensively today, no longer needed)
- `v15_d_evidence_.*\.json`, `v15_p2_evidence_temp\.json`, `v15_d_inventory_p4\.json` (v15 is retired)
- `core/.*` (directory does not exist)
- `.backup/guardian_tests/.*` (redundant; `.backup/` already excluded at category level)

Blast radius: trivial. Regenerate `.gitignore` and rerun `check_exclusion_sync.py`. ~5 minutes of work.

### R2 — Promote `path_constants.py` to derive from YAML (score 0.78)

Today, `agentic_core/L0_routing/config/path_constants.py` hand-defines `SOVEREIGN_EXCLUDED_FOLDERS`, `GLOBAL_EXCLUDED_DIRS`, `DISCOVERY_EXCLUDED_TERRITORIES` as literal frozensets. Refactor to:

```python
from agentic_core.L5_safety.config.exclusion_loader import (
    get_excluded_directories,
)

SOVEREIGN_EXCLUDED_FOLDERS = get_excluded_directories()  # or a filtered subset
```

Or add new YAML categories (`sovereign_excluded`, `global_excluded`, `discovery_excluded_territories`) and generate the Python constants from them at build time.

Blast radius: medium. 18+ consumers — all import from `path_constants`, so swapping the source is one-location change. Risk: circular-import between L0 and L5. Mitigation: put the loader under L0 instead.

Trade-off: loses the performance guarantee of frozenset-at-import-time unless we cache the load.

### R3 — CI gate enforcing no hardcoded exclusion sets (score 0.71)

Add `ops_scripts/ci/check_hardcoded_exclusions.py` that greps for the pattern `{"\.git", ...}` / `{"__pycache__", ...}` in agent and enforcer code and fails if found outside `path_constants.py` and `exclusion_loader.py`.

Known violator today: `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\reasoning\PascalSovereigntyAgent.py:224`.

Blast radius: small. One gate file. Needs allowlist for `exclusion_loader.py` fallback set, the two loader modules themselves, and probably `test_*.py` fixtures.

### R4 — Generate `.codeiumignore` from SSOT (score 0.66)

Extend `excluded_paths.yaml` with a `codeium_specific:` section for patterns that matter only to Windsurf indexing (e.g. `.codeium/windsurf/cascade/`, `**/*.pb`). Add a `--write-codeiumignore` mode to `generate_gitignore.py`.

Caveat: `.codeiumignore` has negations (`!artifacts/windsurf/session_state.json`). Need explicit `codeium_negations:` key or similar.

Blast radius: small. Benefit modest — `.codeiumignore` changes rarely.

### R5 — Periodic staleness audit (score 0.59)

Quarterly job: for each literal path in `excluded_paths.yaml`, check `git log -- <path>` for commits in the last 365 days AND filesystem existence. Flag and report. Optionally auto-remove after 2 consecutive flags.

Overkill for a small repo. Mentioned for completeness.

### R6 — Do nothing (score 0.22)

Current state works for practical purposes: `.gitignore` is generated, `.pre-commit-config.yaml::exclude` is gate-checked, LFS is purged, `.codeiumignore` is small enough to hand-maintain. Drift is tolerable.

Risks: `.windsurf` skip in `GLOBAL_EXCLUDED_DIRS` remains latent; hardcoded `PascalSovereigntyAgent.py` set continues to diverge; dead entries keep accreting.

---

## 6 — Suggested execution order

If you pick multiple recommendations, this is the lowest-risk order:

1. **R1** — delete dead entries (5 minutes, reversible, unblocks analysis)
2. **R3** — CI gate against hardcoded sets (prevents regression while R2 is designed)
3. **R2** — consolidate Python SSOT into YAML-derived (largest structural win)
4. **R4** — generate `.codeiumignore` (nice-to-have, depends on R2)
5. **R5** — staleness audit (only if cadence shows repeated drift)

---

## 7 — Artefacts referenced

- Prior report: `@c:\Git\Agentic-Workflow\docs\reports\gitignore-ssot-duplication-analysis.md` (identified 3 of 8 surfaces)
- Existing plan: `@c:\Git\Agentic-Workflow\.windsurf\plans\scanner-exclusion-sync-two-wave-6d6151.md`
- Gap analysis: `@c:\Git\Agentic-Workflow\docs\tools\exclusion_gaps_manual_fix_2026.md`
- SSOT conflicts: `@c:\Git\Agentic-Workflow\docs\reports\ssot_conflicts_analysis.md`
- Primary YAML: `@c:\Git\Agentic-Workflow\config\excluded_paths.yaml`
- Python runtime SSOT: `@c:\Git\Agentic-Workflow\agentic_core\L0_routing\config\path_constants.py:248-310`
- Loader: `@c:\Git\Agentic-Workflow\agentic_core\L5_safety\config\exclusion_loader.py`
- Sync checker: `@c:\Git\Agentic-Workflow\tools\generate\check_exclusion_sync.py`
- Generator: `@c:\Git\Agentic-Workflow\tools\generate\generate_gitignore.py`

## 8 — Method note

ADG SQLite snapshot: `artifacts/adg/adg_indexed_04192026_1113.sqlite` (76,109 nodes / 550,916 edges). ADG `find_node` queries returned no nodes for the config filenames themselves (expected — ADG indexes Python symbols, not YAML/dotfiles). `nodes_by_file` confirmed `tools/generate/generate_gitignore.py` as a tracked L_TOOLS module. Consumer discovery used literal-grep for exclusion constant names (`GLOBAL_EXCLUDED_DIRS`, `SOVEREIGN_EXCLUDED_FOLDERS`, `EXCLUDE_DIRS`, etc.) per constitutional grep-for-literals permission. Had the ADG indexed the constant-import edges, `adg_edge_fanin` on those symbols would have given identical results.
