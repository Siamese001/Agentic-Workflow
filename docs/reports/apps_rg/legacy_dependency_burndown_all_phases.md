# apps_rg Legacy Dependency Burndown — All Phases Index

**Plan SSOT:** [.cursor/plans/apps-rg-legacy-dependency-burndown-b7e4a2.md](../../.cursor/plans/apps-rg-legacy-dependency-burndown-b7e4a2.md)  
**Notion plan:** [apps-rg-legacy-dependency-burndown-b7e4a2](https://www.notion.so/apps-rg-legacy-dependency-burndown-b7e4a2-36527693f55c81788c13f1c889dccaf1)  
**Last synced:** 2026-05-19  
**Current wave:** `D3_PARTIAL`

## Phase summary

| Phase | Title | Status | Evidence |
|-------|-------|--------|----------|
| A | competencies contract | DONE | plan + w11_m4c |
| B | PA parity | MOSTLY_DONE | plan only |
| C | Rg migration | **PASS** | [phase_c.md](legacy_dependency_burndown_phase_c.md) · [phase_c.json](legacy_dependency_burndown_phase_c.json) |
| D | dispatch quarantine | **PARTIAL** | [phase_d.md](legacy_dependency_burndown_phase_d.md) · [phase_d.json](legacy_dependency_burndown_phase_d.json) |
| D2 | helper fan-in | **PARTIAL** | [phase_d2.md](legacy_dependency_burndown_phase_d2.md) · [phase_d2.json](legacy_dependency_burndown_phase_d2.json) |
| D3 | blockers + load_base_resume | **PARTIAL** | [phase_d3.md](legacy_dependency_burndown_phase_d3.md) · [phase_d3.json](legacy_dependency_burndown_phase_d3.json) |
| E | gated archive | **BLOCKED** | DELETE_GATE not met |

## Machine index

[legacy_dependency_burndown_all_phases.json](legacy_dependency_burndown_all_phases.json)

## D3 open blocker

- `test_canonical_lane_mock_judge_x3_review_code` — category with &lt;2 terms after repair → `X3_BLOCK`
- Repair stack (~1.2k LOC) remains in `competencies_dispatch`; deferred extract
