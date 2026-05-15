# apps_rg Three-Bucket ADG Evidence

Generated: 2026-04-29T23:20:43Z
Snapshot: `adg_indexed_04292026_1606.sqlite`

## STATIC bucket (code-derived from AST scan)

- **apps_rg static nodes**: 311

### Top relation_types within apps_rg
| relation_type | count |
|---|---:|
| `imports` | 7903 |
| `reads_from` | 2564 |
| `resolves_callsite` | 1296 |
| `flows_to` | 1219 |
| `controls_flow` | 1000 |
| `exports` | 727 |
| `emits_side_effect` | 508 |
| `unused_import` | 177 |
| `belongs_to_layer` | 172 |
| `antipattern` | 138 |
| `implements` | 120 |
| `applies` | 98 |
| `instantiates` | 49 |
| `routes_through` | 25 |
| `covers` | 12 |

### Top 10 fan-out files in apps_rg
| file | fan_out |
|---|---:|
| `apps_rg/utils/agent_executor_util.py` | 85 |
| `apps_rg/reasoning/RgResumeOrchestrator.py` | 84 |
| `apps_rg/utils/rg_agent_base_util.py` | 81 |
| `apps_rg/utils/authenticity_patterns_util.py` | 81 |
| `apps_rg/engines/resume_orchestrator_engine.py` | 80 |
| `apps_rg/engines/base_rg_engine.py` | 80 |
| `apps_rg/types/AllProvidersDownError.py` | 78 |
| `apps_rg/scripts/generate_resume.py` | 78 |
| `apps_rg/types/trace_registry_types.py` | 77 |
| `apps_rg/config/agent_spec_config.py` | 77 |

### Violations under apps_rg
_no violations_

## REGISTRY bucket (W1 three-bucket lift)

- edges.bucket column present: **True**
- registry-bucket edges total: 281
- registry-bucket edges touching apps_rg: 10

### Top registry edges (any source)
| relation_type | source_file | count |
|---|---|---:|
| `MCP_SERVER_DECLARED` | `.windsurf/mcp_config.json` | 14 |
| `references_mcp_server` | `.windsurf/scripts/sync_mcp_config.py` | 14 |
| `references_mcp_server` | `.windsurf/scripts/pre_mcp_gate.py` | 13 |
| `AGENT_SPEC_DECLARED` | `apps_lic/config/agent_specs.json` | 8 |
| `AGENT_SPEC_DECLARED` | `apps_rg/config/rg_agent_specs.json` | 8 |
| `references_mcp_server` | `tools/archive/tools_graveyard_w5.12/testing/test_new_mcp_config.py` | 8 |
| `references_mcp_server` | `tools/analysis/_mcp_inspect.py` | 6 |
| `references_mcp_server` | `.windsurf/scripts/post_cursor_agent_mcp_preflight_audit.py` | 5 |
| `references_mcp_server` | `tools/archive/mcp_oneshots_w5.4/probe_mcps.py` | 5 |
| `references_mcp_server` | `tools/archive/mcp_yaml_infra_w5.2/generate_mcp_configs.py` | 4 |

## RUNTIME bucket — primary store: file-backed L4 runtime ADG

Authoritative runtime evidence lives in
`agentic_core/L4_state/memory/runtime_adg/` (file-backed,
content-addressable). The latest apps_rg run produced two
RuntimeADGSnapshot blobs at 19:16:34 (618KB + 417KB) plus 3
new entries in `_trace_index.json` (6900 → 6903).

Per-snapshot details captured separately by
`tools/analyze_runtime_adg_payload.py`. Highlights:

- mission=`apps_rg.generate_resume` on both snapshots
- 12,704 + 8,648 = **21,352 record separators**
- 68 + 61 = unique edge_kinds (W1) / (W2)
- Full lifecycle U0→L0→L1→L2→L3→L4→L5→L6 coverage on both
- 6 priority REQs emitted: REQ-L0-ROUTECONTRACT-TELEMETRY-001,
  REQ-L6-{OBS-ANTI-BYPASS,OUTCOME-TRAJECTORY,PROPOSAL-ADMISSION,
  MEMORY-PROMOTION-IFACE}-001, REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001

- runtime-bucket edges in SQLite mirror: 0
  (Runtime store is file-backed; SQLite mirror is
  populated by W2 of three-bucket — pending.)

## L4 Meta-Learning Feedback Loop Evidence

Runtime snapshot (W1=618KB, W2=417KB) shows live emissions of:

| edge_kind | snapshot 1 | snapshot 2 |
|---|---:|---:|
| `adg.feeds_meta_learning` | 20 | 16 |
| `adg.updates_meta_learning_state` | 20 | 18 |
| `adg.stores_learning_state` | (in W2) | 18 |
| `adg.improves_agent_policy` | (yes) | (yes) |
| `adg.writes_learning_snapshot` | (yes) | (yes) |
| `adg.records_learning_event` | (yes) | (yes) |
| `adg.captures_pattern` | (yes) | (yes) |

Together these emissions form the closed feedback loop:

```
U0 intake -> L0 routing -> L1 cognition -> L2 execution
                                                |
                       L3 orchestration <------'
                              |
                              v
       L4 state + meta-learning  <--- captures_pattern
       feeds_meta_learning ------+    records_learning_event
       updates_meta_learning_state |  improves_agent_policy
       stores_learning_state -----+    writes_learning_snapshot
                              |
                              v   (next-run policy bias)
                       updates_routing_strategy
```

All emissions are durable (UWG-only write path; written via
`OTelLifecycleBridge.flush_to_runtime_adg` at end-of-run).
