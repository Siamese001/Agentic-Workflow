# ADG Config SSOT Remediation — Deferred Scope

**Slug:** `adg-config-ssot-deferred-d7e3a1`
**Status:** Not Started
**Parent Plan:** `adg-config-ssot-audit-c7e4a2` (COMPLETED 2026-05-06)
**Tier:** T3 (cross-layer, config-discipline)
**Pattern Source:** Explicit non-goals from parent plan §8

## §1 Goal

Document and track deferred scope items explicitly excluded from the ADG Config SSOT Remediation plan (`adg-config-ssot-audit-c7e4a2`). These items were identified during the parent plan's W1-W6 execution as out-of-scope but may require future work.

## §2 Deferred Scope Items (from Parent Plan §8)

The following items were **explicitly NOT in scope** for the parent plan and are captured here for future triage:

| ID | Item | Rationale for Deferral | Estimated Effort | Dependencies |
|----|------|------------------------|------------------|--------------|
| D-01 | Memory MCP `knowledge_graph` schema changes | Separate component with its own lifecycle; no SSOT issues identified during parent plan | TBD | Memory MCP stability review |
| D-02 | Redis cluster topology / Sentinel migration | Infrastructure concern, not config-SSOT; requires ops coordination | TBD | Redis operational readiness |
| D-03 | ADG schema graduation | Separate plan track already exists; parent plan focused on config surface only | TBD | ADG schema graduation plan |
| D-04 | `chromadb` / `vector_db` cache layout | Different config surface (vector_db, not ADG); no duplications found | TBD | Vector DB config audit |
| D-05 | OTel runtime ADG path resolution | Separate config surface (runtime ADG ≠ static ADG); constitutional §23 distinguishes | TBD | OTel runtime ADG review |

## §3 Parent Plan Completion Summary

All 11 SSOT items (S-01 through S-11) across 6 waves were **completed**:

- **W1 (S-01, S-09):** Snapshot resolver consolidation — 22 CI gates migrated to `path_resolver.latest_sqlite()`
- **W2 (S-02, S-03):** Hardcoded path purge + wrong-repo deletion — `p2_triage2.py` deleted
- **W3 (S-04, S-08):** ADG_REDIS_URL SSOT + MCP consistency gate — All defaults removed, gate created
- **W4 (S-05, S-06):** Dead MCP files + generator shim — 5 deprecated files deleted
- **W5 (S-07, S-10):** Numbered queries + scan_cache location — 6 files deleted, canonical path established
- **W6 (S-11):** Archive grep-noise reduction — `.codeiumignore` updated

**Files:** Created 2, Deleted 13, Modified 40+
**Commit:** `d4bad2ff3b` + `5cac322664` (ADG Config SSOT Remediation: W1-W6)

## §4 When to Activate This Plan

This deferred scope plan activates when:
1. Any D-item becomes a blocking issue for other work
2. A new SSOT audit identifies related duplications
3. Operational needs (Redis Sentinel, Memory MCP schema changes) require attention

## §5 References

- Parent Plan: `.windsurf/plans/adg-config-ssot-audit-c7e4a2.md`
- Completion Evidence: Git commits `d4bad2ff3b`, `5cac322664`
- Pattern Source: Qwen vLLM Windows/WSL2 SSOT incident (memory `01483ea2-59a4-41a3-8d6e-7132995f3029`)
- Constitutional: §22 (graph-layer), §31 (SSOT folder routing)
