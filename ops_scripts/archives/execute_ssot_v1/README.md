# Archived: execute_ssot Pipeline

**Archived**: 2026-04-10  
**Reason**: Pipeline delivered no end-to-end value. ADG analysis confirmed zero production fan-in for all pipeline files.
**HITL Approval**: Full Archive approved by user.

## Wave 3 Archive (2026-04-10): execute_ssot Pipeline

This archive contains the complete execute_ssot pipeline that was deprecated as part of the SSOT revamp. The pipeline was an orchestration wrapper that called independent L5 agents.

### Key Findings:
- **Agent Independence Confirmed**: All agents (FileClassificationAgent, FileClassificationHealerAgent, etc.) have extensive fan-in outside the pipeline (7-14 consumers each)
- **Minimal Impact**: Archiving removes only 1-2 consumers from agents with 7-14 total consumers
- **Zero Production Value**: Pipeline files had zero/intra-pipeline fan-in only

## What Was Kept

- `agentic_core/adg/applications/execute_ssot_integration.py` — `build_pre_run_report` has 7 production consumers (all app entrypoints)
- `agentic_core/adg/_compat/execute_ssot_integration.py` — backward compat shim

## What Was Archived

### Source Files (13)
- 9 pipeline files from `ops_scripts/dev_tools/L0_routing_scripts/execute_ssot_*.py` — zero/intra-pipeline fan-in
- `_ssot_pipeline.py` — zero fan-in
- `_patch_execute_ssot_routing.py` — zero fan-in

### Duplicate Files (2)
- `PreRunADGReport.py` — exact duplicate of `execute_ssot_integration.py`, only consumer was dead `_ssot_pipeline.py`
- `_compat_PreRunADGReport.py` — compat shim for the duplicate

### Test Files (20)
- 18 placeholder files (`assertTrue(True)`) — no real coverage
- 2 real test files testing dead pipeline code (meta_learning, retrieval hooks)

## Agent Independence

Agents called by the pipeline (`FileClassificationAgent`, `LocationHealerAgent`, etc.) are **independent** — they have 7-14 consumers outside the pipeline and continue functioning through `agentic_core/L5_safety/reasoning/`.

## Collateral Files (6)

Additional files with pre-existing broken imports from nonexistent `execute_ssot.py` monolith:
- `artifacts/reports/evidence/run_healmode.py` — not version-controlled
- `artifacts/reports/evidence/run_legacy_main_domains_capture.py` — not version-controlled
- `ops_scripts/maintenance/verify_universal_healing.py` — zero fan-in
- `ops_scripts/root_scripts/_ssot_dry_run.py` — zero fan-in
- `tests/architecture/ssot/test_ssot_pipeline_protocol.py` — zero fan-in
- `tests/architecture/test_ssot_pipeline_protocol.py` — zero fan-in

## ADG Evidence

| Symbol | Node ID | Production Fan-in | Pipeline Fan-in |
|--------|---------|-------------------|-----------------|
| `build_pre_run_report` | 18337 | 7 (apps_*) | 0 |
| `FileClassificationAgent` | 17380 | 12 | 2 |
| `FileClassificationHealerAgent` | 17381 | 5 | 2 |
| All pipeline modules | various | 0 | intra-only |
