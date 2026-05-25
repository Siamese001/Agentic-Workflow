# `apps_exec` — ADG Hotspot Report (W0.1)

Generated: `2026-05-25T13:29:38Z`
Snapshot: `adg_indexed_05252026_0849.sqlite`
Severity (Phase B): **MEDIUM**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05252026_0849.sqlite

## Actionable hotspots (top 5 — deterministic linkage)

Linkage from structured sources only (`gate_results` queue file paths, P-views, `mv_debt_concentration_hotspots`, `refactor_accelerator`). `unknown` = no gate join.

| module_path | linked_gate_ids | violation_refs | impacted_tests_sample | linkage_source | linkage_confidence |
|-------------|-----------------|----------------|----------------------|----------------|-------------------|
| `ADG::Module::apps_exec/config/agent_spec_config.py` | — | — | — | unknown | missing |
| `apps_exec/config/agent_spec_config.py` | — | — | — | unknown | missing |

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 1 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_exec/config/agent_spec_config.py` | `apps_exec/config/agent_spec_config.py` | 4 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **0**


## mv_hotspot_centrality (top 10 within app)

Rows: 1
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3114, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'L_APP', 'apps_exec/config/agent_spec_config.py', 0, 4, 4, 0.0, 0.0, 3114, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '3b248930f8aa1abc4447a4a49932af73e846b854')

## mv_dependency_cone_risk (top 10 within app)

Rows: 1
- ('1ee81e4418a8d8d13532b2d231bd86181d66a5a4', 3114, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'L_APP', 'apps_exec/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 3114, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '3b248930f8aa1abc4447a4a49932af73e846b854')

## mv_chokepoint_bridges

_view not present in this snapshot_

## v_p0_apps_direct_infra (P0 violation — apps directly importing infra)

Rows: 1
- ('__error__', 'no such column: source_file')

## SC/AP Violations (top 30 by severity)

_no violations for this app_

See [adg_action_dispatch_playbook.md](../../docs/reports/cursor/adg_action_dispatch_playbook.md) and latest `artifacts/adg/adg_action_queue_*.json` for FIX-first triage.

## Recommendations (derived)

- **Broadest reachers (most likely to consolidate):**
  - `apps_exec/config/agent_spec_config.py` (fan-out 4)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

