# `apps_exec` — ADG Hotspot Report (W0.1)

Generated: `2026-05-25T04:07:57Z`
Snapshot: `adg_indexed_05242026_2005.sqlite`
Severity (Phase B): **MEDIUM**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05242026_2005.sqlite

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
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2796, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'L_APP', 'apps_exec/config/agent_spec_config.py', 0, 4, 4, 0.0, 0.0, 2796, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '3b248930f8aa1abc4447a4a49932af73e846b854')

## mv_dependency_cone_risk (top 10 within app)

Rows: 1
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2796, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'L_APP', 'apps_exec/config/agent_spec_config.py', 0, 0, 0, 0, 0.0, 2796, 'ADG::Module::apps_exec/config/agent_spec_config.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_exec/config/agent_spec_config.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '3b248930f8aa1abc4447a4a49932af73e846b854')

## mv_chokepoint_bridges

_view not present in this snapshot_

## v_p0_apps_direct_infra (P0 violation — apps directly importing infra)

Rows: 1
- ('__error__', 'no such column: source_file')

## SC/AP Violations (top 30 by severity)

Rows: 1

| Severity | Kind | File | Line | Message |
|---|---|---|---:|---|

## Recommendations (derived)

- **Broadest reachers (most likely to consolidate):**
  - `apps_exec/config/agent_spec_config.py` (fan-out 4)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

