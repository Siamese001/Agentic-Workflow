# `apps_lic` — ADG Hotspot Report (W0.1)

Generated: `2026-05-25T04:07:57Z`
Snapshot: `adg_indexed_05242026_2005.sqlite`
Severity (Phase B): **HIGH (canary surface)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05242026_2005.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 895 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|
| `ADG::Symbol::apps_lic.runtime.bindings.exit_binding.exit_finalize_apps_lic` | `apps_lic/runtime/bindings/exit_binding.py` | 48 |
| `ADG::Symbol::apps_lic.runtime.bindings.l3_binding.l3_orchestrate_apps_lic` | `apps_lic/runtime/bindings/l3_binding.py` | 39 |
| `ADG::Symbol::apps_lic.sequences.touch_sequence_definitions.SequenceType` | `apps_lic/sequences/touch_sequence_definitions.py` | 30 |
| `ADG::Symbol::apps_lic.engines.ab_variant_engine.ABTrafficAccumulator` | `apps_lic/engines/ab_variant_engine.py` | 30 |
| `ADG::Symbol::apps_lic.signals.types.SignalSource` | `apps_lic/signals/types.py` | 24 |
| `ADG::Symbol::apps_lic.integrations.managed_workflow_dispatcher.dispatch_managed_briefing` | `apps_lic/integrations/managed_workflow_dispatcher.py` | 24 |
| `ADG::Symbol::apps_lic.engines.ab_variant_engine.ABPromotionGate` | `apps_lic/engines/ab_variant_engine.py` | 22 |
| `ADG::Symbol::apps_lic.cert.fec_producer.produce_fec` | `apps_lic/cert/fec_producer.py` | 22 |
| `ADG::Symbol::apps_lic.signals.types.SignalType` | `apps_lic/signals/types.py` | 21 |
| `ADG::Symbol::apps_lic.signals.types.SignalStrength` | `apps_lic/signals/types.py` | 19 |
| `ADG::Symbol::apps_lic.integrations.apps_research_bridge.AppsResearchBridge` | `apps_lic/integrations/apps_research_bridge.py` | 19 |
| `ADG::Symbol::apps_lic.types.TraceRegistry.TraceRegistry` | `apps_lic/types/TraceRegistry.py` | 18 |
| `ADG::Symbol::apps_lic.types.ImmutableStagingBuffer.ImmutableStagingBuffer` | `apps_lic/types/ImmutableStagingBuffer.py` | 18 |
| `ADG::Symbol::apps_lic.signals.types.ResurfacingSignal` | `apps_lic/signals/types.py` | 18 |
| `ADG::Symbol::apps_lic.engines.outreach_antipattern_detector.OutreachAntipatternDetector` | `apps_lic/engines/outreach_antipattern_detector.py` | 18 |

## Top Fan-Out (outgoing imports — broadest reachers)

| ADG name | Resolved path | Fan-out |
|---|---|---:|
| `ADG::Module::apps_lic/utils/lic_agent_base_util.py` | `apps_lic/utils/lic_agent_base_util.py` | 85 |
| `ADG::Module::apps_lic/reasoning/GovernanceShieldAgent.py` | `apps_lic/reasoning/GovernanceShieldAgent.py` | 83 |
| `ADG::Module::apps_lic/config/retry_policy_config.py` | `apps_lic/config/retry_policy_config.py` | 82 |
| `ADG::Module::apps_lic/utils/PIISanitizerSpecialistAgent_util.py` | `apps_lic/utils/PIISanitizerSpecialistAgent_util.py` | 81 |
| `ADG::Module::apps_lic/reasoning/OutreachSignalRouterAgent.py` | `apps_lic/reasoning/OutreachSignalRouterAgent.py` | 81 |
| `ADG::Module::apps_lic/reasoning/OutreachLearningAgent.py` | `apps_lic/reasoning/OutreachLearningAgent.py` | 80 |
| `ADG::Module::apps_lic/engines/control_plane.py` | `apps_lic/engines/control_plane.py` | 80 |
| `ADG::Module::apps_lic/types/app_content_validator_agent_types.py` | `apps_lic/types/app_content_validator_agent_types.py` | 77 |
| `ADG::Module::apps_lic/types/TraceRegistry.py` | `apps_lic/types/TraceRegistry.py` | 77 |
| `ADG::Module::apps_lic/reasoning/OutreachValidationExecutorAgent.py` | `apps_lic/reasoning/OutreachValidationExecutorAgent.py` | 76 |
| `ADG::Module::apps_lic/reasoning/LicHealingOrchestrator.py` | `apps_lic/reasoning/LicHealingOrchestrator.py` | 76 |
| `ADG::Module::apps_lic/utils/manifest_manager_util.py` | `apps_lic/utils/manifest_manager_util.py` | 75 |
| `ADG::Module::apps_lic/types/state_checkpoint_types.py` | `apps_lic/types/state_checkpoint_types.py` | 75 |
| `ADG::Module::apps_lic/config/reasoning_toggles_config.py` | `apps_lic/config/reasoning_toggles_config.py` | 75 |
| `ADG::Module::apps_lic/spine_wiring.py` | `apps_lic/spine_wiring.py` | 73 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **282**

- `apps_lic/engines/HOP1ProfileAnalysisAgent.py`
- `apps_lic/engines/HOP1ProfileAnalysisAgent.py`
- `apps_lic/engines/HOP1ProfileAnalysisAgent.py`
- `apps_lic/engines/HOP2ResearchAgent.py`
- `apps_lic/engines/HOP2ResearchAgent.py`
- `apps_lic/engines/HOP2ResearchAgent.py`
- `apps_lic/engines/HOP3SenderGroundingAgent.py`
- `apps_lic/engines/HOP3SenderGroundingAgent.py`
- `apps_lic/engines/HOP3SenderGroundingAgent.py`
- `apps_lic/engines/HOP4RoutingAgent.py`
- `apps_lic/engines/HOP5GenerationAgent.py`
- `apps_lic/engines/HOP5GenerationAgent.py`
- `apps_lic/engines/HOP5GenerationAgent.py`
- `apps_lic/engines/HOP6ValidationAgent.py`
- `apps_lic/engines/HOP6ValidationAgent.py`
- `apps_lic/engines/HOP6ValidationAgent.py`
- `apps_lic/engines/HOP6ValidationAgent.py`
- `apps_lic/engines/HOP7GateDecisionAgent.py`
- `apps_lic/engines/HOP7GateDecisionAgent.py`
- `apps_lic/engines/HOP7GateDecisionAgent.py`
- `apps_lic/engines/HOP8QAReportAgent.py`
- `apps_lic/engines/HOP8QAReportAgent.py`
- `apps_lic/engines/HOP8QAReportAgent.py`
- `apps_lic/engines/HOP9IntegrationAgent.py`
- `apps_lic/engines/__init__.py`
- `apps_lic/engines/__init__.py`
- `apps_lic/engines/__init__.py`
- `apps_lic/engines/__init__.py`
- `apps_lic/engines/ab_variant_engine.py`
- `apps_lic/engines/ab_variant_engine.py`
- ... +252 more

## mv_hotspot_centrality (top 10 within app)

Rows: 10
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2832, 'ADG::Module::apps_lic/engines/ab_variant_engine.py', 'L_APP', 'apps_lic/engines/ab_variant_engine.py', 127, 12, 139, 0.1339, 0.0112, 2832, 'ADG::Module::apps_lic/engines/ab_variant_engine.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/engines/ab_variant_engine.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '8a948d6202ea28e5e6a6bb7e9e4693cfc6af7f85')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2972, 'ADG::Module::apps_lic/signals/types.py', 'L_APP', 'apps_lic/signals/types.py', 91, 6, 97, 0.048, 0.008, 2972, 'ADG::Module::apps_lic/signals/types.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/signals/types.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'dcf12315eac3ac72607ccba0dfb0dc004ecec678')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2939, 'ADG::Module::apps_lic/runtime/bindings/exit_binding.py', 'L_APP', 'apps_lic/runtime/bindings/exit_binding.py', 82, 24, 106, 0.1729, 0.0072, 2939, 'ADG::Module::apps_lic/runtime/bindings/exit_binding.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/runtime/bindings/exit_binding.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'a450e7a90d5fdca115a5f0149465da2c536be550')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2963, 'ADG::Module::apps_lic/sequences/touch_sequence_definitions.py', 'L_APP', 'apps_lic/sequences/touch_sequence_definitions.py', 67, 8, 75, 0.0471, 0.0059, 2963, 'ADG::Module::apps_lic/sequences/touch_sequence_definitions.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/sequences/touch_sequence_definitions.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '00e9346d1d76a98ba4edd56bafc0108d19609883')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2895, 'ADG::Module::apps_lic/integrations/managed_workflow_dispatcher.py', 'L_APP', 'apps_lic/integrations/managed_workflow_dispatcher.py', 61, 14, 75, 0.075, 0.0054, 2895, 'ADG::Module::apps_lic/integrations/managed_workflow_dispatcher.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/integrations/managed_workflow_dispatcher.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'de046660ad117c0087ec9d28e09bec5cf94dc085')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2900, 'ADG::Module::apps_lic/migrations/campaign_inventory.py', 'L_APP', 'apps_lic/migrations/campaign_inventory.py', 54, 10, 64, 0.0474, 0.0047, 2900, 'ADG::Module::apps_lic/migrations/campaign_inventory.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/migrations/campaign_inventory.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '642bad1c5451df827c804d9726d0029a6324689e')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2940, 'ADG::Module::apps_lic/runtime/bindings/l0_binding.py', 'L_APP', 'apps_lic/runtime/bindings/l0_binding.py', 49, 15, 64, 0.0646, 0.0043, 2940, 'ADG::Module::apps_lic/runtime/bindings/l0_binding.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/runtime/bindings/l0_binding.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '0f5b0b7f1f3d4104a8217b17909c72f4a72453f0')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2943, 'ADG::Module::apps_lic/runtime/bindings/l3_binding.py', 'L_APP', 'apps_lic/runtime/bindings/l3_binding.py', 47, 19, 66, 0.0785, 0.0041, 2943, 'ADG::Module::apps_lic/runtime/bindings/l3_binding.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/runtime/bindings/l3_binding.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '85390f430c60a0def7c71d16f33155f0755511e3')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2885, 'ADG::Module::apps_lic/integrations/apps_research_bridge.py', 'L_APP', 'apps_lic/integrations/apps_research_bridge.py', 42, 14, 56, 0.0517, 0.0037, 2885, 'ADG::Module::apps_lic/integrations/apps_research_bridge.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/integrations/apps_research_bridge.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '5a7743df4f860c36d662fab28aa5165e67d8279a')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2982, 'ADG::Module::apps_lic/types/__init__.py', 'L_APP', 'apps_lic/types/__init__.py', 36, 10, 46, 0.0316, 0.0032, 2982, 'ADG::Module::apps_lic/types/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/types/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'a4c4e42348003504b847c4307eedcdf867c887bd')

## mv_dependency_cone_risk (top 10 within app)

Rows: 10
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2978, 'ADG::Module::apps_lic/types/ImmutableStagingBuffer.py', 'L_APP', 'apps_lic/types/ImmutableStagingBuffer.py', 20, 0, 0, 20, 20.0, 2978, 'ADG::Module::apps_lic/types/ImmutableStagingBuffer.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/types/ImmutableStagingBuffer.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '70ea117a53ae81954ccd9d2ac1bdaa424bef776c')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2981, 'ADG::Module::apps_lic/types/TraceRegistry.py', 'L_APP', 'apps_lic/types/TraceRegistry.py', 18, 0, 0, 18, 18.0, 2981, 'ADG::Module::apps_lic/types/TraceRegistry.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/types/TraceRegistry.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '2d07c55408987338e80d5c4a4d4102764e282876')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2940, 'ADG::Module::apps_lic/runtime/bindings/l0_binding.py', 'L_APP', 'apps_lic/runtime/bindings/l0_binding.py', 13, 0, 0, 13, 13.0, 2940, 'ADG::Module::apps_lic/runtime/bindings/l0_binding.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/runtime/bindings/l0_binding.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '0f5b0b7f1f3d4104a8217b17909c72f4a72453f0')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2939, 'ADG::Module::apps_lic/runtime/bindings/exit_binding.py', 'L_APP', 'apps_lic/runtime/bindings/exit_binding.py', 12, 0, 0, 12, 12.0, 2939, 'ADG::Module::apps_lic/runtime/bindings/exit_binding.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/runtime/bindings/exit_binding.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'a450e7a90d5fdca115a5f0149465da2c536be550')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 3006, 'ADG::Module::apps_lic/utils/lic_agent_base_util.py', 'L_APP', 'apps_lic/utils/lic_agent_base_util.py', 12, 0, 0, 12, 12.0, 3006, 'ADG::Module::apps_lic/utils/lic_agent_base_util.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/utils/lic_agent_base_util.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'f4df35592f8c462a1a559fa15e1a8185c67dad94')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2982, 'ADG::Module::apps_lic/types/__init__.py', 'L_APP', 'apps_lic/types/__init__.py', 10, 0, 0, 10, 10.0, 2982, 'ADG::Module::apps_lic/types/__init__.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/types/__init__.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'a4c4e42348003504b847c4307eedcdf867c887bd')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2955, 'ADG::Module::apps_lic/runtime/u0/adapter.py', 'L_APP', 'apps_lic/runtime/u0/adapter.py', 9, 0, 0, 9, 9.0, 2955, 'ADG::Module::apps_lic/runtime/u0/adapter.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/runtime/u0/adapter.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '28147a83822b4ac1af52ab8d2510aee09803c501')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2819, 'ADG::Module::apps_lic/coordination/touch_scheduler.py', 'L_APP', 'apps_lic/coordination/touch_scheduler.py', 8, 0, 0, 8, 8.0, 2819, 'ADG::Module::apps_lic/coordination/touch_scheduler.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/coordination/touch_scheduler.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', 'f782253a8d7a89f7bd672e7d33eea55a62a6bc6f')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2941, 'ADG::Module::apps_lic/runtime/bindings/l1_binding.py', 'L_APP', 'apps_lic/runtime/bindings/l1_binding.py', 8, 0, 0, 8, 8.0, 2941, 'ADG::Module::apps_lic/runtime/bindings/l1_binding.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/runtime/bindings/l1_binding.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '27e547c5161e9cd25d8a3a15a884ac45195d84a4')
- ('ee3001638c8894973b45414ba0071c02485a5f3b', 2810, 'ADG::Module::apps_lic/config/outreach_experiment_cells.py', 'L_APP', 'apps_lic/config/outreach_experiment_cells.py', 7, 0, 0, 7, 7.0, 2810, 'ADG::Module::apps_lic/config/outreach_experiment_cells.py', 'module', 'L_APP', 'repo_module', 'HIGH', 'apps_lic/config/outreach_experiment_cells.py', 'symbol', 0, 0, 0, 0, 0, 0, 0, '', 0, '', '', '04980a51689a668400f5527fb4e322d2ee82ab63')

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

- **Most-depended-on files (highest blast radius if changed):**
  - `apps_lic/runtime/bindings/exit_binding.py` (fan-in 48) — touch only with explicit Author-Gate
  - `apps_lic/runtime/bindings/l3_binding.py` (fan-in 39) — touch only with explicit Author-Gate
  - `apps_lic/sequences/touch_sequence_definitions.py` (fan-in 30) — touch only with explicit Author-Gate
  - `apps_lic/engines/ab_variant_engine.py` (fan-in 30) — touch only with explicit Author-Gate
  - `apps_lic/signals/types.py` (fan-in 24) — touch only with explicit Author-Gate
- **Broadest reachers (most likely to consolidate):**
  - `apps_lic/utils/lic_agent_base_util.py` (fan-out 85)
  - `apps_lic/reasoning/GovernanceShieldAgent.py` (fan-out 83)
  - `apps_lic/config/retry_policy_config.py` (fan-out 82)
  - `apps_lic/utils/PIISanitizerSpecialistAgent_util.py` (fan-out 81)
  - `apps_lic/reasoning/OutreachSignalRouterAgent.py` (fan-out 81)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

