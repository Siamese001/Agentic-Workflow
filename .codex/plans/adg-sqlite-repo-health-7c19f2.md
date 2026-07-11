# ADG SQLite Repo-Health Hardening

**Status:** APPROVED — direct user implementation request on 2026-07-11  
**Base:** `main@f7ad1899ad07a509b93981340ee2c5eb54900901`  
**Branch:** `agent/adg-sqlite-repo-health`

## Objective

Make the canonical `adg_indexed_*.sqlite` artifact the highest-value source for repository-health decisions. Add transparent, confidence-aware health signals and ranked remediation hotspots while hardening SQLite integrity, indexing, and query-planner metadata.

## Constraints

- SQLite remains authoritative; Redis and NetworkX projections remain optional accelerators/derived stores.
- Do not create another redundant JSON health sidecar.
- Preserve the existing A→F materialization dependency order.
- `UNKNOWN` must never be promoted to a passing/healthy verdict.
- Scores must retain raw values, thresholds, source tables, and evidence—not hide risk behind one opaque number.
- Older snapshots without Phase G must remain readable by MCP health diagnostics.

## Work units

1. Add `phase_g_repo_health.py` with four physical materialized tables:
   - `mv_repo_health_signals`
   - `mv_repo_health_dimensions`
   - `mv_repo_health_summary`
   - `mv_repo_health_hotspots`
2. Add SQLite finalization that:
   - installs query-shaped composite indexes;
   - stamps `application_id` / `user_version` and hardening metadata;
   - runs `foreign_key_check`, `quick_check`, and `PRAGMA optimize`;
   - fails on structural corruption and optionally fails on FK violations under `ADG_STRICT_FOREIGN_KEYS=1`.
3. Integrate Phase G and hardening into the shared materialized-view connection.
4. Expose Phase G through the existing `adg_health` report using read-only, fail-soft access.
5. Fix WAL checkpoint handling when callers pass a SQLite file rather than its directory.
6. Add deterministic micro-evals for scoring, idempotency, missing-evidence behavior, integrity metadata, query indexes, health reading, and WAL checkpoint targeting.

## Health model

Dimensions and default weights:

| Dimension | Weight | Primary signals |
|---|---:|---|
| Governance safety | 0.25 | active HIGH findings, write bypasses, gateway bypasses, dynamic execution |
| Graph truth | 0.20 | authoritative edge ratio, unresolved edge ratio, FK violations, SQLite quick-check |
| Test protection | 0.18 | high-risk modules protected by coverage, P1 urgent gaps, coverage inventory |
| Architecture | 0.17 | import cycles, cross-layer dependency ratio, unknown/orphan ratio |
| Change safety | 0.10 | violation, bypass, debt, and cross-layer deltas |
| Maintainability | 0.10 | debt/module, risk concentration, high-fan defect hotspots |

Overall scores are weight-normalized over available dimensions. Confidence measures evidence availability. Confidence below the contract floor emits `UNKNOWN` even when the numeric score is high.

## Validation

- Unit tests use synthetic SQLite snapshots and run zero models.
- Verify Phase G idempotency and stable schema.
- Verify missing optional MVs lower confidence instead of silently producing green.
- Verify `PRAGMA quick_check`, FK counts, application/user version, composite indexes, and optimizer metadata.
- Verify health diagnostics remain fail-soft on legacy snapshots.
- Run targeted pytest files; inspect the resulting PR diff and changed-file list.

## Rollback

Revert the Phase G/orchestrator commit. Existing A→F tables and all canonical nodes/edges/violations remain unchanged; Phase G tables are derived and rebuildable.