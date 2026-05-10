# `apps_lic` — ADG Hotspot Report (W0.1)

Generated: `2026-05-10T21:28:55Z`
Snapshot: `adg_indexed_05102026_1319.sqlite`
Severity (Phase B): **HIGH (canary surface)**
ADG Provenance: backend=sqlite, snapshot=adg_indexed_05102026_1319.sqlite

## Nodes by Layer

| Layer | Count |
|---|---:|
| L_APP | 796 |

## Top Fan-In (incoming imports — most-depended-on files)

| ADG name | Resolved path | Fan-in |
|---|---|---:|
| `ADG::Symbol::apps_lic.sequences.touch_sequence_definitions.SequenceType` | `apps_lic/sequences/touch_sequence_definitions.py` | 30 |
| `ADG::Symbol::apps_lic.engines.ab_variant_engine.ABTrafficAccumulator` | `apps_lic/engines/ab_variant_engine.py` | 30 |
| `ADG::Symbol::apps_lic.signals.types.SignalSource` | `apps_lic/signals/types.py` | 24 |
| `ADG::Symbol::apps_lic.integrations.managed_workflow_dispatcher.dispatch_managed_briefing` | `apps_lic/integrations/managed_workflow_dispatcher.py` | 22 |
| `ADG::Symbol::apps_lic.engines.ab_variant_engine.ABPromotionGate` | `apps_lic/engines/ab_variant_engine.py` | 22 |
| `ADG::Symbol::apps_lic.cert.fec_producer.produce_fec` | `apps_lic/cert/fec_producer.py` | 22 |
| `ADG::Symbol::apps_lic.signals.types.SignalType` | `apps_lic/signals/types.py` | 21 |
| `ADG::Symbol::apps_lic.integrations.apps_research_bridge.AppsResearchBridge` | `apps_lic/integrations/apps_research_bridge.py` | 21 |
| `ADG::Symbol::apps_lic.signals.types.SignalStrength` | `apps_lic/signals/types.py` | 19 |
| `ADG::Symbol::apps_lic.types.TraceRegistry.TraceRegistry` | `apps_lic/types/TraceRegistry.py` | 18 |
| `ADG::Symbol::apps_lic.types.ImmutableStagingBuffer.ImmutableStagingBuffer` | `apps_lic/types/ImmutableStagingBuffer.py` | 18 |
| `ADG::Symbol::apps_lic.signals.types.ResurfacingSignal` | `apps_lic/signals/types.py` | 18 |
| `ADG::Symbol::apps_lic.engines.outreach_antipattern_detector.OutreachAntipatternDetector` | `apps_lic/engines/outreach_antipattern_detector.py` | 18 |
| `ADG::Symbol::apps_lic.engines.recipient_trigger_engine.RecipientTriggerEngine` | `apps_lic/engines/recipient_trigger_engine.py` | 17 |
| `ADG::Symbol::apps_lic.engines.ab_variant_engine.ARM_CONTROL` | `apps_lic/engines/ab_variant_engine.py` | 16 |

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
| `ADG::Module::apps_lic/reasoning/HOPPipelineExecutor.py` | `apps_lic/reasoning/HOPPipelineExecutor.py` | 75 |
| `ADG::Module::apps_lic/config/reasoning_toggles_config.py` | `apps_lic/config/reasoning_toggles_config.py` | 75 |

## Engines + Reasoning Agents

Total files under `engines/` + `reasoning/`: **293**

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
- ... +263 more

## mv_hotspot_centrality

_view not present in this snapshot_

## mv_dependency_cone_risk

_view not present in this snapshot_

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
  - `apps_lic/sequences/touch_sequence_definitions.py` (fan-in 30) — touch only with explicit Author-Gate
  - `apps_lic/engines/ab_variant_engine.py` (fan-in 30) — touch only with explicit Author-Gate
  - `apps_lic/signals/types.py` (fan-in 24) — touch only with explicit Author-Gate
  - `apps_lic/integrations/managed_workflow_dispatcher.py` (fan-in 22) — touch only with explicit Author-Gate
  - `apps_lic/engines/ab_variant_engine.py` (fan-in 22) — touch only with explicit Author-Gate
- **Broadest reachers (most likely to consolidate):**
  - `apps_lic/utils/lic_agent_base_util.py` (fan-out 85)
  - `apps_lic/reasoning/GovernanceShieldAgent.py` (fan-out 83)
  - `apps_lic/config/retry_policy_config.py` (fan-out 82)
  - `apps_lic/utils/PIISanitizerSpecialistAgent_util.py` (fan-out 81)
  - `apps_lic/reasoning/OutreachSignalRouterAgent.py` (fan-out 81)

## Out of Scope (this report)

- Runtime evidence (Runtime bucket gated on three-bucket completion)
- Cross-app comparative analysis (see Phase B comparative audit in conversation)

