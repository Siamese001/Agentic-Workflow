---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\method-a-consumer-migration-a3f9c2.md'
original_relative_path: 'method-a-consumer-migration-a3f9c2.md'
source_sha256: c9c75231d5cf6dc7f8b90e5fdfd81a4cdf7efa1182796b516d0baab2c2a5ed52
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-10'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Method A Consumer Migration — Execution Plan

**Created:** 2026-04-10
**Objective:** Complete Method A — archive 6,749-line structure_blueprint package, migrate ~95 consumer files to L0 path_constants, kill the shim.

## Key Finding

`agentic_core/L0_routing/config/path_constants.py` (628 lines) already contains **literal copies** of every top-consumed symbol from the L5 structure_blueprint package. The L0 file's own docstring says: *"Pure SSOT for structural paths... extracted from L5_safety.config.structure_blueprint."*

This means migration is **import path rewrites only** — no new data definitions needed.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W0 | P0 | Strip lifecycle traces from L0 path_constants.py | 2K | File is 628 lines | TODO | Clean file, tests pass |
| W1 | P1 | Redirect top-3 symbols (172 edges, ~60 files) | 15K | Mechanical import rewrite | TODO | Zero imports of top-3 from L5 |
| W2 | P2 | Redirect remaining path constants (~80 edges, ~35 files) | 10K | Same mechanical rewrite | TODO | Zero imports from L5 for constants |
| W3 | P3 | Handle low-consumer modules (≤10 edges total) | 5K | Some consumers may themselves be archivable | TODO | Zero remaining L5 imports |
| W4 | P4 | Archive package + kill shim | 3K | All consumers migrated | TODO | Package archived, shim gone |
| W5 | P5 | Verification + ADG regen | 3K | All waves complete | TODO | Full test suite + CI gate pass |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P0 | Clean L0 path_constants.py | 1 file | Lifecycle trace noise (lines 18-24, 92-106) | 2K | TODO |
| P1 | Top-3 symbol migration | ~60 files | SOVEREIGN_EXCLUDED_FOLDERS (91), GLOBAL_EXCLUDED_DIRS (56), DISCOVERY_EXCLUDED_TERRITORIES (32) | 15K | TODO |
| P2 | Remaining constants migration | ~35 files | AGENTIC_CORE_DIR, PROJECT_ROOT_WHITELIST, REPORTS_DIR, TESTS_DIR, DEPTH_RULES, get_validated_project_root, etc. | 10K | TODO |
| P3 | Low-consumer module cleanup | ~10 files | ENFORCED_TERRITORIES, safe_path_join, FORBIDDEN_* patterns, classification/derived/artifacts consumers | 5K | TODO |
| P4 | Archive + shim kill | 12 files (10 package + shim + __init__) | Pre-commit hooks, archive README | 3K | TODO |
| P5 | Full verification | 0 edits | Test suite, CI gate, ADG regen | 3K | TODO |

## Consumer → Target Mapping

### P1: Top 3 symbols (172 import edges)
```
FROM: from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
  TO: from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS

FROM: from agentic_core.L5_safety.config.structure_blueprint.ssot import GLOBAL_EXCLUDED_DIRS
  TO: from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS

FROM: from agentic_core.L5_safety.config.structure_blueprint.ssot import DISCOVERY_EXCLUDED_TERRITORIES
  TO: from agentic_core.L0_routing.config.path_constants import DISCOVERY_EXCLUDED_TERRITORIES
```

### P2: Path constants (~80 edges)
Same pattern — rewrite `structure_blueprint[.ssot]` → `L0_routing.config.path_constants`

### P3: Low-consumer symbols NOT in L0 (need individual handling)
- `ENFORCED_TERRITORIES` (4 consumers) — add to L0 or inline
- `safe_path_join` (2 consumers) — add to L0 path_util.py or inline
- `has_forbidden_layer_prefix` (2 consumers) — inline at consumer
- `check_forbidden_signals` (2 consumers) — inline at consumer
- `SOVEREIGN_TERRITORIES` / `SOVEREIGN_REGISTRY` (2 each) — use get_all_territories()
- `FORBIDDEN_*` patterns (2 each) — add to L0 or inline
- `load_territories` (2 consumers) — redirect to yaml_loader if still needed

## Risks
- **Circular imports:** L0 path_constants imports lifecycle_trace_contract (L_RUNTIME). Stripping traces (P0) eliminates this.
- **Test mirror paths:** Some test files import from structure_blueprint for test constants. These need migration too.
- **ADG staleness:** After migration, ADG snapshot is stale. P5 regenerates.

## Gap Register
- None identified yet. Will update per-wave.
