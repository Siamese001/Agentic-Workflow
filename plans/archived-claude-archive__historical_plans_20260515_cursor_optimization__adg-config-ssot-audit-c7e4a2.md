---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\adg-config-ssot-audit-c7e4a2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\adg-config-ssot-audit-c7e4a2.md'
source_sha256: 19c15782cb3727daff885900e32ed1cc7d8737d4ce421012f290be54319982ba
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Config SSOT Audit & Remediation

**Slug:** `adg-config-ssot-audit-c7e4a2`
**Status:** Completed
**Authored:** 2026-05-06
**Tier:** T3 (cross-layer, multi-file, config-discipline)
**Pattern source:** Qwen vLLM Windows/WSL2 SSOT incident (memory `01483ea2-59a4-41a3-8d6e-7132995f3029`) — stale systemd unit shadowed canonical Docker container; same failure class found across ADG.

## §1 Goal

Eliminate config-SSOT duplications in MCP ADG and ADG CI surface so a single canonical source governs each ADG runtime parameter (snapshot path, Redis URL, MCP entry, layer overrides, generator entrypoint). Each remediation item is gated by an Author-Gate decision because most are judgment calls (delete vs deprecate, fold-into-helper vs leave-as-is).

## §2 Non-Goals

- Refactoring ADG schema, MV definitions, or graph projection logic
- Changing ADG generation algorithm or scanner behavior
- Touching `archives/` content (covered by §12 import gate, not in scope here)
- Memory MCP, Redis MCP internal logic — only the `ADG_REDIS_URL` config surface they share

## §3 Files In Scope (per item)

See §6 wave structure. Each remediation item lists its own scope. No file outside the listed set is touched without an explicit user-approved scope extension.

## §4 Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | S-01, S-09 | Snapshot resolver consolidation + sentinel resilience | ~12k | ✅ DONE | All CI gates use `path_resolver.latest_sqlite`; sentinel test added |
| W2 | S-02, S-03 | Hardcoded path purge + wrong-repo diag deletion | ~6k | ✅ DONE | Zero hardcoded `adg_indexed_<ts>` outside `tools/archive/`; `p2_triage2.py` deleted |
| W3 | S-04, S-08 | `ADG_REDIS_URL` SSOT module + MCP env consistency | ~8k | ✅ DONE | All hardcoded defaults removed; MCP consistency gate created and passing |
| W4 | S-05, S-06 | Dead MCP server file deletion + generator shim decision | ~5k | ✅ DONE | 5 deprecated files deleted (4 MCP servers + 1 generator shim) |
| W5 | S-07, S-10 | Numbered query files + cache file consolidation | ~7k | ✅ DONE | 6 numbered query files deleted; scan_cache canonical path established |
| W6 | S-11 | Archive grep-noise reduction | ~3k | ✅ DONE | `.codeiumignore` excludes ADG backup archives; grep noise reduced |

## §5 Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| S-01 | Snapshot resolver consolidation | ~17 CI gates listed below; `path_resolver.py` | Each gate has its own `_latest_snapshot()` with subtly different logic (mtime vs name sort, sentinel filter vs not). Drift already caused one prod-failure precedent | 8k | Not Started |
| S-02 | Purge hardcoded snapshot paths | `tools/debug/_a3b_probe.py`, `_adg_high_edge_lookup.py`, `_adg_high_only.py`, `_adg_node_breakdown.py`, `_adg_delta.py`, `tools/notion/adg_verified_closure.py`, `tools/diag/scan_adg_import_orphans.py` | Each file binds to a frozen-in-time snapshot; goes stale instantly after `tools/generate_full_adg.py` runs | 4k | Not Started |
| S-03 | Delete wrong-repo diag relic | `tools/diag/p2_triage2.py` | Hardcoded `C:\Git\Agentic-Workflow\artifacts\adg\...` — points at NON-`FRESH` repo. Direct Qwen pattern | 2k | Not Started |
| S-04 | `ADG_REDIS_URL` SSOT module | New: `tools/adg/cache/redis_config.py`. Edits: `tools/adg/{adg_mv_project,adg_redis_ingest,mv_reader,core/service,cache/{__init__,redis_cache}}.py`, `tools/memory/adg_memory_server.py` | Default `redis://localhost:6379/0` hardcoded in 12+ places. Port migration is a 12-site sweep | 5k | Not Started |
| S-05 | Dead MCP server file purge | `tools/adg/mcp/{server_clean,server_debug,server_launcher}.py`, `tools/adg/adg_mcp_entry.py` | 4 dead entry points all carry `# DEPRECATED` headers but live alongside canonical `server.py`. Same risk as Qwen WSL2 unit | 3k | Not Started |
| S-06 | Generator shim decision | `tools/generate_full_adg.py` (shim), `tools/generate/generate_full_adg.py` (canonical) | Two ways to invoke; ~90 doc/code refs split across both forms. Low risk but high noise | 2k | Not Started |
| S-07 | `adg_align_query[1-7].py` triage | `tools/adg/queries/adg_align_query{1..7}.py` | 7 numbered iterations, no clear active version. Snapshot-of-snapshots tech debt | 4k | Not Started |
| S-08 | MCP env consistency gate | `.windsurf/mcp_config.json`, new `ops_scripts/ci/check_mcp_adg_redis_consistency.py` | `adg_sqlite.env.ADG_REDIS_URL` and `memory.env.ADG_REDIS_URL` must match by hand. Drift undetectable | 3k | Not Started |
| S-09 | Sentinel resilience hardening | `tools/adg/shared_modules/path_resolver.py` + new test | Validate `%m%d%Y_%H%M` is the only filter; add explicit sentinel-rejection test that fails if a future stub like `adg_indexed_99999999_9999.sqlite` is selected | 2k | Not Started |
| S-10 | `scan_result_cache.json` location | `artifacts/adg/scan_result_cache.json` vs `artifacts/adg/cache/scan_result_cache.json` | Both exist. Need to identify reader, declare canonical, delete other | 3k | Not Started |
| S-11 | Archive grep-noise reduction | `.codeiumignore`, `.gitignore` for greps | `tools/archive/adg_root_oneshots_w5.10/`, `tools/archive/tools_graveyard_w5.12/adg_backups/` keep showing up in `grep_search` results, polluting investigation | 2k | Not Started |

## §6 Author-Gate Queue Seeds

Each item is an Author-Gate decision because the remediation choice is judgment (delete vs deprecate vs fold-into-helper). Confidences are deliberately mid-range (0.55–0.78); none clear the dominance threshold (top ≥0.85 AND gap ≥0.12), so all 11 surface to the user.

```
AG_QUEUE_SEED: plan=adg-config-ssot-audit-c7e4a2 id=S-01 depends_on= title=Snapshot resolver consolidation across ~17 CI gates
AG_QUEUE_SEED: plan=adg-config-ssot-audit-c7e4a2 id=S-02 depends_on=S-01 title=Purge hardcoded snapshot paths in tools/debug + tools/notion
AG_QUEUE_SEED: plan=adg-config-ssot-audit-c7e4a2 id=S-03 depends_on= title=Delete or fix tools/diag/p2_triage2.py wrong-repo path
AG_QUEUE_SEED: plan=adg-config-ssot-audit-c7e4a2 id=S-04 depends_on= title=ADG_REDIS_URL SSOT module + 12-site sweep
AG_QUEUE_SEED: plan=adg-config-ssot-audit-c7e4a2 id=S-05 depends_on= title=Delete deprecated MCP server entry files (4 files)
AG_QUEUE_SEED: plan=adg-config-ssot-audit-c7e4a2 id=S-06 depends_on= title=Generator shim retain-or-retire decision
AG_QUEUE_SEED: plan=adg-config-ssot-audit-c7e4a2 id=S-07 depends_on= title=adg_align_query[1-7] numbered files triage
AG_QUEUE_SEED: plan=adg-config-ssot-audit-c7e4a2 id=S-08 depends_on=S-04 title=MCP env consistency CI gate (adg_sqlite vs memory ADG_REDIS_URL)
AG_QUEUE_SEED: plan=adg-config-ssot-audit-c7e4a2 id=S-09 depends_on=S-01 title=Sentinel-rejection test for path_resolver
AG_QUEUE_SEED: plan=adg-config-ssot-audit-c7e4a2 id=S-10 depends_on= title=scan_result_cache.json canonical location
AG_QUEUE_SEED: plan=adg-config-ssot-audit-c7e4a2 id=S-11 depends_on= title=Archive grep-noise reduction via .codeiumignore
```

## §7 Per-Item Remediation Detail

### S-01 · Snapshot resolver consolidation

**Problem:** ~17 CI gates each define their own `_latest_snapshot()` / `_find_latest_sqlite()` / `_latest_sqlite()` helper. Examples: `executor_theater_gate.py`, `check_unresolved_edges_ratchet.py`, `check_three_bucket_impossible_states.py`, `check_test_harness_coverage.py`, `check_test_concentration_ratio.py`, `check_runtime_trace_topology.py`, `check_runtime_proof_view_well_formed.py`, `check_registry_graph_integrity.py`, `_adg_wiring_gate_base.py`, `run_adg_three_graph_tests.py`, plus 7+ more. Each has subtly different sort logic (mtime vs name vs both, sentinel-filter vs not). `check_schema_graduation_readiness.py` already migrated to canonical resolver in 2026-04-30 incident (sentinel `adg_indexed_99999999_9999.sqlite` shadowed real snapshot).

**Options to surface:**
- A: Big-bang sweep — replace all ~17 helpers with `from tools.adg.shared_modules.path_resolver import latest_sqlite`. One PR. ⭐ recommended for highest leverage.
- B: Incremental ratchet — add CI gate `check_canonical_snapshot_resolver.py` that fails on new `glob("adg_indexed_*.sqlite")` outside the canonical helper; migrate gates lazily as touched.
- C: Leave each gate independent; document precedent only. Reject.

### S-02 · Hardcoded snapshot paths

**Problem:** `tools/debug/_a3b_probe.py:3`, `_adg_high_edge_lookup.py:3`, `_adg_high_only.py:3`, `_adg_node_breakdown.py:7`, `_adg_delta.py:8-9`, `tools/notion/adg_verified_closure.py:140` (defaults to `adg_indexed_05022026_1651.sqlite`, 4 days stale on the day of audit), `tools/diag/scan_adg_import_orphans.py:7` (docstring only).

**Options:** A) delete debug scripts (one-shot probes); B) refactor to use `path_resolver`; C) leave (forever stale).

### S-03 · `tools/diag/p2_triage2.py` wrong-repo path

**Problem:** Line 6: `OLD = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04152026_1108.sqlite"`. Repo is `Agentic-Workflow-FRESH`, not `Agentic-Workflow`. **Exact Qwen pattern.**

**Options:** A) delete the file (one-shot triage script, dated naming `p2_triage2`); B) fix path to use `path_resolver`; C) move to `tools/archive/`.

### S-04 · `ADG_REDIS_URL` SSOT module

**Problem:** Default `redis://localhost:6379/0` hardcoded in 12+ files as fallback when env var unset. No single source of truth for the default. Port change = 12-site sweep with no fail-safe.

**Sites:** `tools/adg/adg_mv_project.py:35`, `tools/adg/adg_redis_ingest.py:41`, `tools/adg/mv_reader.py:20`, `tools/adg/cache/__init__.py:24`, `tools/adg/cache/redis_cache.py:31`, `tools/adg/core/service.py:45`, `tools/memory/adg_memory_server.py:129`, plus tests at `tests/unit/tools/adg/test_mv_*.py`.

**Options:**
- A: New module `tools/adg/cache/redis_config.py` exporting `DEFAULT_ADG_REDIS_URL`; all sites import.
- B: Constant in existing `tools/adg/cache/__init__.py`; 11 sites import.
- C: Leave as-is (12-site config drift accepted).

### S-05 · Deprecated MCP server entry files

**Problem:** `tools/adg/mcp/server.py` is canonical (referenced by `.windsurf/mcp_config.json`). Co-resident files all carry `# DEPRECATED: canonical launch path is python -m tools.adg.mcp.server` headers but remain in the tree:
- `tools/adg/mcp/server_clean.py`
- `tools/adg/mcp/server_debug.py`
- `tools/adg/mcp/server_launcher.py`
- `tools/adg/adg_mcp_entry.py`

Same risk as Qwen WSL2 unit: a future operator reads one of these and assumes it's live.

**Options:** A) delete all 4 (in-tree fully covered by canonical); B) move to `tools/archive/adg_mcp_deprecated_entries/`; C) leave (deprecation comments deemed sufficient).

### S-06 · Generator shim retain-or-retire

**Problem:** `tools/generate_full_adg.py` is a 21-line compat shim that delegates to `tools/generate/generate_full_adg.py`. Both invocations appear in ~90 doc/code references. Constitutional §31 SSOT folder routing would land any NEW such shim under `ops_scripts/ci/`, but this shim is grandfathered.

**Options:** A) keep shim, document explicitly as the SSOT entrypoint and migrate `tools/generate/...` references to it; B) delete shim, migrate all callers to `tools/generate/generate_full_adg.py`; C) leave (status quo).

### S-07 · `adg_align_query[1-7].py` triage

**Problem:** `tools/adg/queries/adg_align_query.py` plus `_query2.py … _query7.py`. Seven numbered iterations. No `__init__.py` declaration of which is current.

**Options:** A) audit each, keep one canonical, archive others; B) consolidate into single CLI subcommand pattern; C) leave.

### S-08 · MCP env consistency gate

**Problem:** `mcp_config.json` defines `ADG_REDIS_URL` for both `adg_sqlite` and `memory` servers, hand-set to identical strings. No gate enforces equality. Drift = silent split-brain (memory MCP reads stale projection while adg_sqlite reads fresh).

**Options:** A) new pre-commit gate `check_mcp_adg_redis_consistency.py` that asserts `adg_sqlite.env.ADG_REDIS_URL == memory.env.ADG_REDIS_URL`; B) collapse to a single shared env var via launcher; C) document only.

### S-09 · Sentinel-rejection test

**Problem:** `path_resolver.latest_sqlite` already validates `%m%d%Y_%H%M`, but no regression test asserts the sentinel `adg_indexed_99999999_9999.sqlite` is rejected. The 2026-04-30 incident has no test coverage.

**Options:** A) add unit test `test_latest_sqlite_rejects_sentinel`; B) add CI assertion that scans `artifacts/adg/` for stub-sized files (<1MB) and warns; C) both.

### S-10 · `scan_result_cache.json` canonical location

**Problem:** Both `artifacts/adg/scan_result_cache.json` (15-match grep) AND `artifacts/adg/cache/scan_result_cache.json` (939-match grep — the larger active file) exist.

**Options:** A) declare `cache/` subpath canonical, delete the other, add gate; B) declare top-level canonical (move 939-match file up); C) read both, prefer larger (status quo).

### S-11 · Archive grep-noise reduction

**Problem:** `tools/archive/adg_root_oneshots_w5.10/` and `tools/archive/tools_graveyard_w5.12/adg_backups/` resurface in every ADG-related grep with hundreds of matches each, polluting investigation. They are tombstoned but visible.

**Options:** A) extend `.codeiumignore` to exclude `tools/archive/**` for Fast Context; B) move to `archives/` (covered by constitutional §12 import block, also gitignored); C) leave.

## §8 Non-Goals & Deferrals

The following are NOT in this plan's scope and will be filed as `DEFERRED_SCOPE:` markers if surfaced during execution:
- Memory MCP knowledge_graph schema changes
- Redis cluster topology / Sentinel migration
- ADG schema graduation (separate plan track)
- `chromadb` / `vector_db` cache layout
- OTel runtime ADG path resolution (separate config surface)

## §9 Verification

Each phase ends with:
1. Targeted pytest run for the touched module(s)
2. Full ADG CI gate sweep: `python ops_scripts/ci/run_contract_gates.py`
3. `python tools/generate_full_adg.py` clean run (no regressions)
4. Memory MCP + adg_sqlite MCP `_health` checks

## §10 Success Criteria (plan-wide)

- Zero `glob("adg_indexed_*.sqlite")` calls outside `tools/adg/shared_modules/path_resolver.py` and explicit allowlist
- Zero hardcoded `artifacts/adg/adg_indexed_<specific_ts>` paths in non-archive Python
- One module exports `DEFAULT_ADG_REDIS_URL`; all consumers import it
- `tools/adg/mcp/` contains exactly one server entry file (`server.py`)
- CI gate enforces `mcp_config.json` `adg_sqlite ↔ memory` `ADG_REDIS_URL` equality
- Sentinel-rejection test on `path_resolver`
- `tools/diag/p2_triage2.py` either deleted or path-fixed
- Author-Gate ledger has 11 entries linking each remediation to its decision

## §11 References

- Constitutional §22 (graph-layer primary), §25 (MCP serialization), §28 (SQLite-direct fallback), §31 (SSOT folder routing), §35 (Author-Gate queue drain)
- `adg-canonical-invariants.md` — SQLite=truth, Redis=hot projection
- Memory `01483ea2-59a4-41a3-8d6e-7132995f3029` — Qwen Windows/WSL2 SSOT incident (pattern source)
- Memory `da4a7d9a-...` — SSOT folder routing pattern (helper + hook + CI gate + bypass)
