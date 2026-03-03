# Execute SSOT Mutation Fence Hardening — Phase 3 Evidence

## Wave 1 — Telemetry Inventory

### Telemetry Symbols
```
build_evidence.py:27:parts.append('\n## Follow-ons (out-of-scope)\n- (1) Add policy-level audit to enumerate all durable write entrypoints across L2 tools.\n- (2) Extend protected roots list to include additional repo-critical directories if needed.\n- (3) Add telemetry event for blocked write attempts with target path + agent id.\n')
build_phase2_evidence.py:68:parts.append('1. Add telemetry event emission when protected-root writes are blocked (target path + caller context)\n')
scan_telemetry_symbols.py:2:"""Scan for existing telemetry/emitter primitives."""
scan_telemetry_symbols.py:8:"""Find telemetry-related symbols in the codebase."""
scan_telemetry_symbols.py:10:r'TelemetryEmitter',
scan_telemetry_symbols.py:11:r'TelemetryEvent',
scan_telemetry_symbols.py:14:r'violation_event',
scan_telemetry_symbols.py:15:r'detection_signal_store'
scan_telemetry_symbols.py:40:print(f'Found {len(symbols)} telemetry symbol references')
.backup\phase2\test_location_agent_telemetry.py:2:Quick integration test to verify LocationAgent telemetry works with batch optimization.
.backup\phase2\test_location_agent_telemetry.py:25:# Import RuntimeStateGuard directly to test telemetry
.backup\phase2\test_location_agent_telemetry.py:59:print("LocationAgent telemetry integration verified! ✅")
.nox\integration\Lib\site-packages\pydantic\json_schema.py:103:See the [`GenerateJsonSchema.emit_warning`][pydantic.json_schema.GenerateJsonSchema.emit_warning] and
.nox\integration\Lib\site-packages\pydantic\json_schema.py:1201:self.emit_warning(
.nox\integration\Lib\site-packages\pydantic\json_schema.py:1210:self.emit_warning(
.nox\integration\Lib\site-packages\pydantic\json_schema.py:1272:self.emit_warning('skipped-choice', exc.message)
.nox\integration\Lib\site-packages\pydantic\json_schema.py:1335:self.emit_warning('skipped-choice', exc.message)
.nox\integration\Lib\site-packages\pydantic\json_schema.py:1384:self.emit_warning('skipped-discriminator', str(exc))
.nox\integration\Lib\site-packages\pydantic\json_schema.py:2444:def emit_warning(self, kind: JsonSchemaWarningKind, detail: str) -> None:
.nox\integration\Lib\site-packages\_pytest\terminal.py:1693:def _emit_progress(
.nox\integration\Lib\site-packages\_pytest\terminal.py:1735:self._emit_progress("indeterminate")
.nox\integration\Lib\site-packages\_pytest\terminal.py:1742:self._emit_progress("normal", 0)
.nox\integration\Lib\site-packages\_pytest\terminal.py:1759:self._emit_progress("error" if self._has_failures else "normal", progress)
.nox\integration\Lib\site-packages\_pytest\terminal.py:1763:self._emit_progress("remove")
.nox\integration\Lib\site-packages\pip\_internal\metadata\__init__.py:63:def _emit_pkg_resources_deprecation_if_needed() -> None:
.nox\integration\Lib\site-packages\pip\_internal\metadata\__init__.py:101:_emit_pkg_resources_deprecation_if_needed()
.nox\integration\Lib\site-packages\pygments\lexers\perl.py:406:'Supplier::Preserving','Supply','Systemic','Tap','Telemetry',
.nox\integration\Lib\site-packages\pygments\lexers\perl.py:407:'Telemetry::Instrument::Thread','Telemetry::Instrument::Usage',
.nox\integration\Lib\site-packages\pygments\lexers\perl.py:408:'Telemetry::Period','Telemetry::Sampler','Thread','ThreadPoolScheduler',
.nox\integration\Lib\site-packages\pygments\lexers\_php_builtins.py:3053:'Yaml': ('yaml_emit_file',
.pytest_tmp\test_mutation_dynamic_dunder_i0\agentic_core\L1_cognition\bad_import.py:1:mod = __import__('agentic_core.L6_observability.telemetry')
.pytest_tmp\test_mutation_l2_imports_l60\agentic_core\L2_execution\test_violation.py:1:import agentic_core.L6_observability.telemetry
agentic_core\base_agents\L6ObservabilityBase.py:10:- Telemetry collection
agentic_core\base_agents\L6ObservabilityBase.py:32:- Telemetry collection and export
agentic_core\base_agents\L6ObservabilityBase.py:54:def emit_telemetry(self, event: dict[str, Any]) -> bool:
agentic_core\base_agents\L6ObservabilityBase.py:56:Emit a telemetry event.
agentic_core\base_agents\L6ObservabilityBase.py:58:Override in subclasses for specialized telemetry emission.
agentic_core\base_agents\SovereignBaseAgent.py:83:AuditTrailMixin,  # ADDED: Black Box telemetry
agentic_core\base_agents\SovereignBaseAgent.py:121:# 3. Telemetry Signal
agentic_core\mixins\audit_trail_mixin.py:31:await self.emit_auditable_action("EXECUTE", {"action_id": action.id})
agentic_core\mixins\audit_trail_mixin.py:304:async def emit_auditable_action(
agentic_core\mixins\audit_trail_mixin.py:328:if not hasattr(self, "emit_event"):
agentic_core\mixins\audit_trail_mixin.py:345:await self.emit_event(
agentic_core\mixins\audit_trail_mixin.py:357:def emit_auditable_action_sync(
agentic_core\mixins\feature_flagged_agent_mixin.py:196:def emit_detection_signal(
agentic_core\mixins\feature_flagged_agent_mixin.py:249:return emitter.emit_signal(result)
agentic_core\mixins\golden_context_mixin.py:36:- L6: Observability (dashboards, telemetry, logging)
agentic_core\mixins\hardening_mixin.py:6:Provides a unified way to add circuit breaking, retries, and telemetry
agentic_core\mixins\hardening_mixin.py:33:Integrates circuit breaking, retry logic, and structured telemetry.
agentic_core\mixins\hardening_mixin.py:47:telemetry: SystemTelemetry | None = None,
agentic_core\mixins\hardening_mixin.py:52:component_name: Name for telemetry and circuit breaker
agentic_core\mixins\hardening_mixin.py:58:telemetry: Custom telemetry instance (uses default if None)
agentic_core\mixins\hardening_mixin.py:72:self.telemetry = telemetry or get_telemetry()
agentic_core\mixins\hardening_mixin.py:85:operation: Operation name for telemetry
agentic_core\mixins\hardening_mixin.py:88:metadata: Additional telemetry metadata
agentic_core\mixins\hardening_mixin.py:119:self.telemetry.log_success(
agentic_core\mixins\hardening_mixin.py:131:self.telemetry.log_failure(
agentic_core\mixins\hardening_mixin.py:146:self.telemetry.log_circuit_breaker(
agentic_core\mixins\hardening_mixin.py:159:self.telemetry.log_failure(
agentic_core\mixins\migration_mixin.py:94:if hasattr(self, "emit_event"):
agentic_core\mixins\migration_mixin.py:95:self.emit_event(
agentic_core\mixins\state_validation_mixin.py:133:if hasattr(self, "emit_event"):
agentic_core\mixins\state_validation_mixin.py:134:self.emit_event(
agentic_core\mixins\tracing_mixin.py:58:"""Convert span to dictionary for telemetry export."""
agentic_core\utils\state_util.py:9:"""Check telemetry for past failures on similar tasks.
agentic_core\config\core\domain_constitution_config.py:54:"role": "Truth: Telemetry, Logging, and Audit Trails",
agentic_core\config\core\registry_config.py:150:"telemetry",
agentic_core\config\core\registry_config.py:295:"telemetry": "observability",
agentic_core\L0_routing\enforcement\governance_contracts.py:124:# §3.7 — emit_policy_exception
agentic_core\L0_routing\enforcement\governance_contracts.py:132:def emit_policy_exception(
agentic_core\L0_routing\enforcement\governance_contracts.py:333:"emit_policy_exception",
agentic_core\L0_routing\engines\escalation_router.py:15:from agentic_core.L4_state.enforcement.violation_event_store import ViolationEventStore
agentic_core\L0_routing\engines\timeshift_router.py:19:from agentic_core.L4_state.types.detection_signal_store_types import get_prior_detection_signal
agentic_core\L0_routing\scripts\execute_ssot.py:321:# NEW DATA STRUCTURES FOR TELEMETRY AND VALIDATION
agentic_core\L0_routing\scripts\execute_ssot.py:327:"""Structured violation for enhanced telemetry (Ported from FilesystemSSOTReconciler)."""
agentic_core\L0_routing\scripts\execute_ssot.py:348:"""Telemetry manifest for tracking all reconciliation changes."""
agentic_core\L0_routing\scripts\execute_ssot.py:1164:# Full telemetry captured in state for final report
agentic_core\L0_routing\scripts\territory_ssot_definitions_util.py:81:TERRITORY_L6_TELEMETRY = "L6_Observability/Telemetry"
agentic_core\L0_routing\scripts\territory_ssot_definitions_util.py:210:elif "telemetry" in path_str:
agentic_core\L0_routing\scripts\territory_ssot_definitions_util.py:402:# Monitoring, metrics, coverage, detection, telemetry, observability, cost, reporting
agentic_core\L0_routing\scripts\territory_ssot_definitions_util.py:412:"telemetry",
agentic_core\L0_routing\scripts\validate_drilldown_util.py:147:("observability", "Telemetry", True, True),
agentic_core\L0_routing\types\routing_artifact_types.py:179:"""§15.6 — INCIDENT with mandatory telemetry event emission."""
agentic_core\L0_routing\types\routing_contracts.py:539:# §15.6 — INCIDENT and RESULT telemetry emission
agentic_core\L0_routing\types\routing_contracts.py:543:class TelemetryEmitter:
agentic_core\L0_routing\types\routing_contracts.py:544:"""§15.6 — All INCIDENT and RESULT artifacts must emit telemetry events."""
agentic_core\L0_routing\types\routing_contracts.py:549:def emit_incident(self, incident: IncidentArtifact) -> None:
agentic_core\L0_routing\types\routing_contracts.py:550:"""Emit telemetry for INCIDENT artifact."""
agentic_core\L0_routing\types\routing_contracts.py:560:def emit_result(self, result: ResultArtifact) -> None:
agentic_core\L0_routing\types\routing_contracts.py:561:"""Emit telemetry for RESULT artifact."""
agentic_core\L0_routing\types\routing_contracts.py:570:def emit_route_decision(self, artifact: RouteDecisionArtifact) -> None:
agentic_core\L0_routing\types\routing_contracts.py:571:"""Emit telemetry for ROUTE_DECISION artifact (§3.1 durable sink)."""
agentic_core\L0_routing\types\routing_contracts.py:581:def emit_typed_artifact(self, type_label: str, artifact: Any) -> None:
agentic_core\L0_routing\types\routing_contracts.py:582:"""Emit telemetry for any typed dataclass artifact (§Wave2.1 generic sink)."""
agentic_core\L0_routing\types\routing_contracts.py:649:"TelemetryEmitter",
agentic_core\L0_routing\types\v15_contracts_types.py:23:TelemetryEmitter,
agentic_core\L0_routing\types\v15_contracts_types.py:47:"TelemetryEmitter",
agentic_core\L0_routing\utils\complexity_visitor_util.py:994:if "log_metric" in source or "emit_metric" in source:
agentic_core\L1_cognition\engines\meta_observability.py:10:- Telemetry aggregation
agentic_core\L1_cognition\engines\meta_observability.py:45:- Telemetry aggregation
agentic_core\L1_cognition\reasoning\MetaLearningAgent.py:3:Restored: 2026-01-13 | Version: 2.1.0 (With Telemetry)
agentic_core\L1_cognition\reasoning\MetaLearningAgent.py:22:# Type alias for telemetry callback
agentic_core\L1_cognition\reasoning\MetaLearningAgent.py:42:Supports telemetry callbacks for dashboard observability.
agentic_core\L1_cognition\reasoning\MetaLearningAgent.py:54:telemetry_callback: Optional callback function for dashboard telemetry.
agentic_core\L1_cognition\reasoning\MetaLearningAgent.py:70:# Telemetry callback for dashboard observability (Phase 1.2)
agentic_core\L1_cognition\reasoning\MetaLearningAgent.py:93:# Telemetry hook for dashboard observability
agentic_core\L1_cognition\reasoning\MetaLearningAgent.py:151:# Telemetry hook for dashboard observability
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:2:L1 Cognition Telemetry Emitter - Write-only, ZERO-decision component
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:4:Emits deterministic TelemetryEvent artifacts and forwards them to L4
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:5:telemetry recording via an injected seam. L1 never branches on safety
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:40:class TelemetryEvent:
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:41:"""Immutable telemetry event artifact."""
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:53:) -> "TelemetryEvent":
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:55:Create a new TelemetryEvent with deterministic event_hash.
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:65:New TelemetryEvent with computed event_hash
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:83:class TelemetryEmitter:
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:85:Write-only telemetry emitter with injected recording seam.
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:91:def emit(self, *, event: TelemetryEvent, record_fn) -> None:
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:93:Emit telemetry event via injected recording function.
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:96:event: TelemetryEvent to emit
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:103:) -> TelemetryEvent:
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:105:Convenience constructor for TelemetryEvent.
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:115:New TelemetryEvent
agentic_core\L1_cognition\telemetry\telemetry_emitter.py:117:return TelemetryEvent.create(trace_id, stage, kind, commit_tick, details)
agentic_core\L1_cognition\validators\dark_reasoning_visitor_validator.py:26:without leaving a trace in the L6 observability layer (logging, telemetry).
agentic_core\L2_execution\enforcement\SovereignLLMGateway.py:202:self._emit_token_artifact(fail_artifact)
agentic_core\L2_execution\enforcement\SovereignLLMGateway.py:274:self._emit_token_artifact(fail_artifact)
agentic_core\L2_execution\enforcement\SovereignLLMGateway.py:292:self._emit_token_artifact(pass_artifact)
agentic_core\L2_execution\enforcement\SovereignLLMGateway.py:378:def _emit_token_artifact(self, artifact: Any) -> None:
agentic_core\L2_execution\enforcement\SovereignLLMGateway.py:379:"""§Wave1.8 — Emit TokenEnforcementArtifact via TelemetryEmitter."""
agentic_core\L2_execution\enforcement\SovereignLLMGateway.py:381:from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter
agentic_core\L2_execution\enforcement\SovereignLLMGateway.py:383:emitter = TelemetryEmitter()
agentic_core\L2_execution\enforcement\SovereignLLMGateway.py:384:emitter.emit_typed_artifact("TOKEN_ENFORCEMENT", artifact)
agentic_core\L2_execution\enforcement\SovereignLLMGateway.py:386:except Exception as _emit_exc:
agentic_core\L2_execution\enforcement\SovereignLLMGateway.py:389:_emit_exc,
agentic_core\L2_execution\types\mcp_tool_types.py:307:# Emit enforcement artifact via TelemetryEmitter
agentic_core\L2_execution\types\mcp_tool_types.py:309:from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter
agentic_core\L2_execution\types\mcp_tool_types.py:311:emitter = TelemetryEmitter()
agentic_core\L2_execution\types\mcp_tool_types.py:312:emitter.emit_typed_artifact("TOOL_ENFORCEMENT", artifact)
agentic_core\L2_execution\types\mcp_tool_types.py:314:except Exception as _emit_exc:
agentic_core\L2_execution\types\mcp_tool_types.py:317:_emit_exc,
agentic_core\L2_execution\types\self_healing_trigger_types.py:158:def emit_self_healing_trigger(
agentic_core\L2_execution\types\self_healing_trigger_types.py:208:"emit_self_healing_trigger",
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:41:from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:135:_l3_emitter = TelemetryEmitter()
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:136:_l3_emitter.emit_typed_artifact("L3_ROUTE_DECISION", l3_artifact)
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:179:# §3.1 — Durable emission to TelemetryEmitter sink + flush to artifacts
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:181:_emitter = TelemetryEmitter()
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:182:_emitter.emit_route_decision(route_artifact)
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:217:_hil_emitter = TelemetryEmitter()
agentic_core\L3_orchestration\reasoning\OrchestrationHandshakeAgent.py:218:_hil_emitter.emit_typed_artifact("HIL_EVIDENCE_PACK", _hil_pack)
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:23:from agentic_core.runtime.core.telemetry import TraceEvent
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:65:telemetry: Any | None = None,
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:84:telemetry: TelemetryRecorder instance (injected)
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:104:self.telemetry = self._ensure_dep(telemetry, "TelemetryRecorder")
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:218:self.telemetry.record(
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:242:self.telemetry.record(
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:261:self.telemetry.record(
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:293:self.telemetry.record(
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:309:self.telemetry.record(
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:333:"""Check telemetry for past failures on similar tasks."""
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:364:self.telemetry.record(
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:375:self.telemetry.record(
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:400:self.telemetry.record(
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:425:self.telemetry.record(
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:438:"""Handle execution errors with unified telemetry."""
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:440:self.telemetry.record(
agentic_core\L3_orchestration\reasoning\SubatomicHopAgent.py:454:self.telemetry.record(
agentic_core\L3_orchestration\types\cognitive_diff_types.py:213:def emit_cognitive_diff_bundle(
agentic_core\L3_orchestration\types\cognitive_diff_types.py:245:"emit_cognitive_diff_bundle",
agentic_core\L3_orchestration\types\rag_provider_types.py:38:"""Standard RAG result with telemetry."""
agentic_core\L3_orchestration\types\rag_provider_types.py:65:RagResult with documents and telemetry
agentic_core\L4_state\config\ledger_retention_config.py:15:# Telemetry
agentic_core\L4_state\enforcement\replay_bundle_store.py:179:for vh in bundle.prior_violation_event_hashes:
agentic_core\L4_state\enforcement\telemetry_recorder.py:1:"""TelemetryRecorder — Durable L4 telemetry and outcome logging.
agentic_core\L4_state\enforcement\telemetry_recorder.py:3:Phase 1 Wave 1.3 implementation. Replaces stub with full telemetry
agentic_core\L4_state\enforcement\telemetry_recorder.py:47:"""Durable L4 telemetry recorder with metrics and reconciliation.
agentic_core\L4_state\enforcement\telemetry_recorder.py:49:- record(): Store telemetry events with timestamps
agentic_core\L4_state\enforcement\telemetry_recorder.py:60:"""Record a telemetry event.
agentic_core\L4_state\enforcement\telemetry_recorder.py:63:event_type: Type of telemetry event
agentic_core\L4_state\enforcement\telemetry_recorder.py:85:self.logger.info(f"Telemetry recorded: {event_type} (id: {event_id[:8]})")
agentic_core\L4_state\enforcement\telemetry_recorder.py:149:"""Retrieve telemetry events.
agentic_core\L4_state\enforcement\telemetry_recorder.py:156:List of telemetry events
agentic_core\L4_state\enforcement\telemetry_recorder.py:164:"""Clear all telemetry data (tests only)."""
agentic_core\L4_state\enforcement\telemetry_recorder_enforcer.py:31:logging.info(f"Telemetry: [{event.data['type']}] - {event.data['span_id']}")
agentic_core\L4_state\enforcement\violation_event_store.py:5:- store_violation_event(event) -> event_hash  (idempotent by hash)
agentic_core\L4_state\enforcement\violation_event_store.py:17:from agentic_core.L4_state.types.violation_event_types import ViolationEvent
agentic_core\L4_state\enforcement\violation_event_store.py:31:def store_violation_event(self, event: ViolationEvent) -> str:
agentic_core\L4_state\enforcement\violation_event_store.py:38:f"ViolationEventStore.store_violation_event: "
agentic_core\L4_state\engines\replay_bundle_emitter.py:4:emit_replay_bundle() is called after successful execution to produce and
agentic_core\L4_state\engines\replay_bundle_emitter.py:16:def emit_replay_bundle(
agentic_core\L4_state\engines\replay_bundle_emitter.py:27:prior_violation_event_hashes: list[str] | None = None,
agentic_core\L4_state\engines\replay_bundle_emitter.py:46:prior_violation_event_hashes=prior_violation_event_hashes,
agentic_core\L4_state\reasoning\CachedStateLedgerAgent.py:65:self._successful_traces: list[dict] = []  # NEW: Required by GeminiSpy telemetry
agentic_core\L4_state\reasoning\CachedStateLedgerAgent.py:88:# [L4 TELEMETRY] Record successful cache operation for GeminiSpy
agentic_core\L4_state\reasoning\CachedStateLedgerAgent.py:99:# [L4 TELEMETRY] Record successful retrieval
agentic_core\L4_state\reasoning\CachedStateLedgerAgent.py:138:"""Public accessor required by ValidationContext and GeminiSpy telemetry"""
agentic_core\L4_state\reasoning\RedisSovereignAgent.py:34:[PHASE 2 MIGRATION] Absorbed Auditing and Telemetry:
agentic_core\L4_state\types\replay_bundle.py:43:prior_violation_event_hashes: list  — sorted list of ViolationEvent.event_hash strings
agentic_core\L4_state\types\replay_bundle.py:58:prior_violation_event_hashes: list[str]
agentic_core\L4_state\types\replay_bundle.py:85:if not isinstance(self.prior_violation_event_hashes, list):
agentic_core\L4_state\types\replay_bundle.py:86:raise TypeError("ReplayBundle: prior_violation_event_hashes must be a list")
agentic_core\L4_state\types\replay_bundle.py:92:self.prior_violation_event_hashes = sorted(self.prior_violation_event_hashes)
agentic_core\L4_state\types\replay_bundle.py:114:"prior_violation_event_hashes": sorted(self.prior_violation_event_hashes),
agentic_core\L4_state\types\replay_bundle.py:133:"prior_violation_event_hashes": list(self.prior_violation_event_hashes),
agentic_core\L4_state\types\replay_bundle.py:150:prior_violation_event_hashes: list[str] | None = None,
agentic_core\L4_state\types\replay_bundle.py:165:prior_violation_event_hashes=prior_violation_event_hashes or [],
agentic_core\L4_state\types\violation_event.py:115:def emit_violation_event(
agentic_core\L4_state\utils\sanitize_telemetry_util.py:2:Telemetry Sanitizer - Anti-Observer Effect Protection.
agentic_core\L5_safety\enforcement\audit_healing_strategy.py:63:"action": "emit_corrective_event",
agentic_core\L5_safety\enforcement\audit_healing_strategy.py:146:result: Any = await self._emit_corrective_event(event_data)
agentic_core\L5_safety\enforcement\audit_healing_strategy.py:160:async def _emit_corrective_event(self, event_data: dict) -> bool:
agentic_core\L5_safety\enforcement\human_review_queue.py:241:self._emit_policy_update_proposal(request, HILOutcome.APPROVED)
agentic_core\L5_safety\enforcement\human_review_queue.py:270:self._emit_policy_update_proposal(request, HILOutcome.REJECTED)
agentic_core\L5_safety\enforcement\human_review_queue.py:348:def _emit_policy_update_proposal(
agentic_core\L5_safety\enforcement\human_review_queue.py:374:from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter
agentic_core\L5_safety\enforcement\human_review_queue.py:376:emitter = TelemetryEmitter()
agentic_core\L5_safety\enforcement\human_review_queue.py:377:emitter.emit_typed_artifact("POLICY_UPDATE_PROPOSAL", proposal)
agentic_core\L5_safety\enforcement\human_review_queue_enforcer.py:241:self._emit_policy_update_proposal(request, HILOutcome.APPROVED)
agentic_core\L5_safety\enforcement\human_review_queue_enforcer.py:270:self._emit_policy_update_proposal(request, HILOutcome.REJECTED)
agentic_core\L5_safety\enforcement\human_review_queue_enforcer.py:348:def _emit_policy_update_proposal(
agentic_core\L5_safety\enforcement\human_review_queue_enforcer.py:374:from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter
agentic_core\L5_safety\enforcement\human_review_queue_enforcer.py:376:emitter = TelemetryEmitter()
agentic_core\L5_safety\enforcement\human_review_queue_enforcer.py:377:emitter.emit_typed_artifact("POLICY_UPDATE_PROPOSAL", proposal)
agentic_core\L5_safety\enforcement\mission_utils.py:100:if any(x in content_lower for x in ["Metric", "telemetry", "trace", "observ"]):
agentic_core\L5_safety\enforcement\mission_utils.py:145:if any(x in name_lower for x in ["observ", "Metric", "telemetry"]):
agentic_core\L5_safety\enforcement\mission_utils_enforcer.py:100:if any(x in content_lower for x in ["Metric", "telemetry", "trace", "observ"]):
agentic_core\L5_safety\enforcement\mission_utils_enforcer.py:145:if any(x in name_lower for x in ["observ", "Metric", "telemetry"]):
agentic_core\L5_safety\governance\lazy_seam_classifier.py:22:"D4_OBSERVABILITY_INTEGRATION": "Telemetry/probes integration",
agentic_core\L5_safety\governance\lazy_seam_classifier.py:91:# D4_OBSERVABILITY_INTEGRATION: Telemetry and monitoring
agentic_core\L5_safety\governance\lazy_seam_classifier.py:93:"telemetry",
agentic_core\L5_safety\governance\lazy_seam_classifier.py:106:return ("D4_OBSERVABILITY_INTEGRATION", "Observability/telemetry integration point")
agentic_core\L5_safety\reasoning\CodeFormatterAgent.py:36:- SovereignBaseAgent: Provides sovereign infrastructure (config, healing, telemetry)
agentic_core\L5_safety\reasoning\DDDAlignmentAgent.py:88:"role": "Truth: Telemetry, Logging, and Audit Trails",
agentic_core\L5_safety\reasoning\DuplicateCodeDetectorAgent.py:78:MCPHardenedMixin: Provides MCP hardening and telemetry.
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:2443:"L6_observability": ("dashboard", "metric", "telemetry", "monitor"),
agentic_core\L5_safety\reasoning\FileClassificationAgent.py:3724:3. Has record_*/emit_*/publish_*/get_metrics methods (telemetry API)
agentic_core\L5_safety\reasoning\RegressionOracleAgent.py:93:self._emit_regression_check_pass,
agentic_core\L5_safety\reasoning\RegressionOracleAgent.py:150:def _emit_regression_check_pass(self, file_path: str, method_name: str) -> Any:
agentic_core\L5_safety\reasoning\UnusedCleanupAgent.py:37:- SovereignBaseAgent: Provides sovereign infrastructure (config, healing, telemetry)
agentic_core\L5_safety\types\heal_llm_seam.py:6:Phase 5: Added telemetry + budget caps.
agentic_core\L5_safety\types\heal_llm_seam.py:131:# PHASE 5: Telemetry + Budget Caps
agentic_core\L5_safety\types\heal_llm_seam.py:219:"""Deterministic telemetry record for heal runs (no timestamps/UUIDs).
agentic_core\L5_safety\types\heal_llm_seam.py:251:"""Compute deterministic hash of telemetry record for filenames."""
agentic_core\L5_safety\types\heal_llm_seam.py:256:def emit_heal_telemetry(
agentic_core\L5_safety\types\heal_llm_seam.py:260:"""Emit a deterministic telemetry artifact.
agentic_core\L5_safety\types\heal_llm_seam.py:263:record: The telemetry record to emit.
agentic_core\L5_safety\types\heal_llm_seam.py:291:f"Telemetry artifact conflict: {filepath} exists with different content. "
agentic_core\L5_safety\utils\agent_categorizer_util.py:86:r"Telemetry|Trace|Tracing",
agentic_core\L5_safety\utils\canonical_truth_util.py:208:"L6": r"observability|logging|telemetry|metrics",
agentic_core\L5_safety\utils\guard_observability_footprint_util.py:27:without leaving a trace in the L6 observability layer (logging, telemetry).
agentic_core\L5_safety\config\structure_blueprint\artifacts.py:294:"docs/reports/telemetry": {
agentic_core\L5_safety\config\structure_blueprint\artifacts.py:295:"description": "System telemetry, performance metrics, and observability data.",
agentic_core\L5_safety\config\structure_blueprint\artifacts.py:298:"keywords": ["telemetry", "metrics", "performance", "observability"],
agentic_core\L5_safety\config\structure_blueprint\artifacts.py:301:re.compile(r".*telemetry.*"),
agentic_core\L5_safety\config\structure_blueprint\artifacts.py:617:"keywords": ["report", "coverage", "telemetry", "audit", "plan", "implementation"],
agentic_core\L5_safety\config\structure_blueprint\derived.py:145:"telemetry": ["telemetry_agents", "metrics_agents"],
agentic_core\L5_safety\config\structure_blueprint\semantics.py:152:"telemetry",
agentic_core\L5_safety\config\structure_blueprint\semantics.py:353:"primary": frozenset({"metric", "trace", "telemetry", "log", "compliance"}),
agentic_core\L5_safety\config\structure_blueprint\semantics.py:742:"keyword_signals": ["Metric", "counter", "gauge", "measure", "telemetry"],
agentic_core\L5_safety\config\structure_blueprint\semantics.py:1200:"file": "agentic_core/observability/telemetry/TelemetryAgent.py",
agentic_core\L5_safety\config\structure_blueprint\semantics.py:1866:"telemetry": {
agentic_core\L5_safety\config\structure_blueprint\semantics.py:1867:"purpose": "Distributed telemetry, event emission, and structured observability events",
agentic_core\L5_safety\config\structure_blueprint\semantics.py:1869:"keywords": ["telemetry", "event", "emit", "signal", "observe"],
agentic_core\L5_safety\config\structure_blueprint\_constants.py:431:"notes": "LCD+ canonical skeleton + dashboards/ nuance. metrics/logs/tracing/telemetry/reports/agents/engine DISSOLVED.",
agentic_core\L5_safety\config\structure_blueprint\_constants.py:470:"purpose": "Observability engines and telemetry processors.",
agentic_core\L5_safety\config\structure_blueprint\_constants.py:1121:"telemetry": {"purpose": "System telemetry, performance metrics, and observability data"},
agentic_core\L5_safety\config\structure_blueprint\_verify.py:920:emit_report_json,
agentic_core\L5_safety\config\structure_blueprint\_verify.py:995:report_json = emit_report_json(report)
agentic_core\L5_safety\config\structure_blueprint\enforcement\types.py:102:def emit_report_json(report: EnforcementReport) -> dict[str, Any]:
agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py:342:"""Get telemetry schema summary for Phase 5 report.
agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py:375:"""Get telemetry aggregates from synthetic artifacts (fixed set).
agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py:379:# Pre-computed aggregates from synthetic telemetry artifacts
agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py:538:# Phase 5: Telemetry Schema Summary section
agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py:542:"## Telemetry Schema Summary",
agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py:571:# Phase 5: Telemetry Aggregates section
agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py:575:"## Telemetry Aggregates (Synthetic)",
agentic_core\L5_safety\enforcement\governance\agent_heal_audit.py:577:"Aggregates computed from fixed set of synthetic telemetry artifacts:",
agentic_core\L5_safety\utils\evidence\phase11_l1_telemetry_emitter_evidence.py:2:Phase 11 L1 Telemetry Emitter Evidence Generator
agentic_core\L5_safety\utils\evidence\phase11_l1_telemetry_emitter_evidence.py:3:Python-only evidence capture for L1 cognition telemetry emission.
agentic_core\L5_safety\utils\evidence\phase11_l1_telemetry_emitter_evidence.py:49:"""Generate Phase 11 L1 Telemetry Emitter evidence bundle."""
agentic_core\L5_safety\utils\evidence\phase11_l1_telemetry_emitter_evidence.py:75:# 3) pytest - telemetry emitter tests
agentic_core\L5_safety\utils\evidence\phase11_l1_telemetry_emitter_evidence.py:76:print("Running telemetry emitter tests...")
agentic_core\L5_safety\utils\evidence\phase11_l1_telemetry_emitter_evidence.py:77:sections.append("# Telemetry Emitter Tests\n")
agentic_core\L5_safety\utils\evidence\phase11_l1_telemetry_emitter_evidence.py:108:emitter_file = repo_root / "agentic_core" / "L1_cognition" / "telemetry" / "telemetry_emitter.py"
agentic_core\L5_safety\utils\evidence\phase11_l1_telemetry_emitter_evidence.py:163:print("Phase 11 L1 Telemetry Emitter evidence generation complete!")
agentic_core\L6_observability\dashboards\dashboard_generator.py:231:elif "/telemetry" in path or "Telemetry" in class_name:
agentic_core\L6_observability\enforcement\rag_telemetry_collector.py:4:RAG Telemetry Collector - L6 observability
agentic_core\L6_observability\enforcement\rag_telemetry_collector.py:46:Collects RAG telemetry for L6 observability dashboard.
agentic_core\L6_observability\enforcement\rag_telemetry_collector_enforcer.py:4:RAG Telemetry Collector - L6 observability
agentic_core\L6_observability\enforcement\rag_telemetry_collector_enforcer.py:46:Collects RAG telemetry for L6 observability dashboard.
agentic_core\L6_observability\engines\detection_signal_emitter.py:13:def emit_detection_signal(
agentic_core\L6_observability\engines\detection_signal_emitter.py:40:def emit_signal_from_gateway_result(
agentic_core\L6_observability\engines\PerformanceAnalystAgentSimple.py:74:Logger.info("[PerformanceAnalyst] L6 observability - ready for telemetry")
agentic_core\L6_observability\engines\TieredVigilanceEmitter.py:70:def emit_vigilance_event(
agentic_core\L6_observability\engines\TieredVigilanceEmitter.py:99:"emit_vigilance_event",
agentic_core\L6_observability\utils\system_telemetry_util.py:1:"""Telemetry utilities.
agentic_core\L6_observability\utils\system_telemetry_util.py:4:Category: UTILITY (Telemetry collector)
agentic_core\L6_observability\utils\system_telemetry_util.py:6:Provides system telemetry functionality.
agentic_core\L6_observability\utils\system_telemetry_util.py:11:"""System telemetry collector."""
agentic_core\L6_observability\utils\system_telemetry_util.py:14:"""Initialize telemetry."""
agentic_core\L6_observability\utils\system_telemetry_util.py:39:"""Get telemetry instance.
agentic_core\L6_observability\utils\system_telemetry_util.py:45:Telemetry instance
agentic_core\L6_observability\dashboards\core\experiencein_config.py:5:Created: 2026-01-13 | Version: 2.0.0 (Phase 2 - Enhanced Telemetry)
agentic_core\L6_observability\dashboards\core\experiencein_config.py:47:# Initialize telemetry-enabled clients
agentic_core\L6_observability\dashboards\core\experiencein_config.py:130:# Phase 2 Endpoints - Enhanced Telemetry for Dashboard Live Runtime
agentic_core\prompt_governance\contracts\context_contracts.py:32:"""Shape contract for telemetry envelope fields."""
agentic_core\runtime\config\contextual_router_config.py:81:def emit_signal(self, signal_type: str, data: dict[str, Any]) -> None:
agentic_core\runtime\config\contextual_router_config.py:108:def emit_signal(
agentic_core\runtime\config\detection_config.py:87:def emit_signal(self, result: DetectionResult) -> str:
agentic_core\runtime\types\sovereign_events_types.py:52:def emit_event(
agentic_core\runtime\types\sovereign_events_types.py:170:self.emit_event(f"{event_prefix}.started", {"args": str(args)})
agentic_core\runtime\types\sovereign_events_types.py:176:self.emit_event(
agentic_core\runtime\types\sovereign_events_types.py:182:self.emit_event(
agentic_core\runtime\utils\runtime_bootstrapper_util.py:51:telemetry=self._get_tool("telemetry", lambda: TelemetryRecorder(self.config)),
agentic_core\runtime\utils\sovereign_dependency_error_util.py:9:from runtime.core.telemetry import TraceEvent
agentic_core\runtime\utils\sovereign_dependency_error_util.py:54:telemetry: Any | None = None,
agentic_core\runtime\utils\sovereign_dependency_error_util.py:73:telemetry: TelemetryRecorder instance (injected)
agentic_core\runtime\utils\sovereign_dependency_error_util.py:150:if telemetry is None:
agentic_core\runtime\utils\sovereign_dependency_error_util.py:152:"SubatomicHop requires 'telemetry' (TelemetryRecorder) to be injected.",
agentic_core\runtime\utils\sovereign_dependency_error_util.py:154:self.telemetry = telemetry
agentic_core\runtime\utils\sovereign_dependency_error_util.py:171:self.telemetry.record(
agentic_core\runtime\utils\sovereign_dependency_error_util.py:204:self.telemetry.record(
agentic_core\runtime\utils\sovereign_dependency_error_util.py:227:self.telemetry.record(
agentic_core\runtime\utils\sovereign_dependency_error_util.py:263:self.telemetry.record(
agentic_core\runtime\utils\sovereign_dependency_error_util.py:279:self.telemetry.record(
agentic_core\runtime\utils\sovereign_dependency_error_util.py:302:"""Check telemetry for past failures on similar tasks."""
agentic_core\runtime\utils\sovereign_dependency_error_util.py:328:self.telemetry.record(
agentic_core\runtime\utils\sovereign_dependency_error_util.py:339:self.telemetry.record(
agentic_core\runtime\utils\sovereign_dependency_error_util.py:374:self.telemetry.record(
agentic_core\runtime\utils\sovereign_dependency_error_util.py:399:self.telemetry.record(
agentic_core\runtime\utils\sovereign_dependency_error_util.py:413:self.telemetry.record(
agentic_core\runtime\utils\sovereign_dependency_error_util.py:429:self.telemetry.record(
agentic_core\runtime\utils\sovereign_dependency_error_util.py:443:self.telemetry.record(
agentic_core\runtime\utils\subatomic_hop_util.py:11:from agentic_core.runtime.core.telemetry import TraceEvent
agentic_core\runtime\utils\subatomic_hop_util.py:51:telemetry: Any | None = None,
agentic_core\runtime\utils\subatomic_hop_util.py:70:telemetry: TelemetryRecorder instance (injected)
agentic_core\runtime\utils\subatomic_hop_util.py:92:self.telemetry = self._ensure_dep(telemetry, "TelemetryRecorder")
agentic_core\runtime\utils\subatomic_hop_util.py:129:self.telemetry.record(
agentic_core\runtime\utils\subatomic_hop_util.py:155:self.telemetry.record(
agentic_core\runtime\utils\subatomic_hop_util.py:174:self.telemetry.record(
agentic_core\runtime\utils\subatomic_hop_util.py:208:self.telemetry.record(
agentic_core\runtime\utils\subatomic_hop_util.py:224:self.telemetry.record(
agentic_core\runtime\utils\subatomic_hop_util.py:250:"""Check telemetry for past failures on similar tasks."""
agentic_core\runtime\utils\subatomic_hop_util.py:282:self.telemetry.record(
agentic_core\runtime\utils\subatomic_hop_util.py:294:self.telemetry.record(
agentic_core\runtime\utils\subatomic_hop_util.py:321:self.telemetry.record(
agentic_core\runtime\utils\subatomic_hop_util.py:348:self.telemetry.record(
agentic_core\runtime\utils\subatomic_hop_util.py:361:"""Handle execution errors with unified telemetry."""
agentic_core\runtime\utils\subatomic_hop_util.py:364:self.telemetry.record(
agentic_core\runtime\utils\subatomic_hop_util.py:378:self.telemetry.record(
apps_lic\reasoning\GovernanceShieldAgent.py:75:"leveraged anonymized telemetry for model fine-tuning",
apps_lic\reasoning\LicHealingOrchestrator.py:51:def assess_system_health(self, telemetry: dict[str, Any]) -> dict[str, str]:
apps_lic\reasoning\LicHealingOrchestrator.py:56:if telemetry.get("error_rate", 0) > 0.05:
apps_lic\reasoning\LicHealingOrchestrator.py:185:telemetry: dict[str, Any],
apps_lic\reasoning\LicHealingOrchestrator.py:192:telemetry: Current system telemetry
apps_lic\reasoning\QAConductorAgent.py:434:#     """Placeholder MCP agent for telemetry-aligned meta learning."""
apps_lic\reasoning\QAConductorAgent.py:437:#         self.log_info("MetaLearningLoop invoked - emitting telemetry only.")
apps_lic\reasoning\TwoPhaseDeduplicationAgent.py:517:#         # CRITICAL: Chain up to HealerMixin for telemetry and safety guards
apps_lic\validators\PersonaPlannerValidator.py:275:"""Record telemetry data (best-effort)."""
apps_lic\validators\PersonaPlannerValidator.py:289:Logger.debug(f"Failed to record telemetry: {e}")
apps_lic\validators\PersonaPlannerValidator.py:292:"""Get a summary of the persona plan for debugging/telemetry."""
apps_rg\enforcement\HardenedanthropicexecutorStrategy.py:7:- Structured telemetry logging
apps_rg\enforcement\HardenedanthropicexecutorStrategy.py:66:token validation, and structured telemetry.
apps_rg\enforcement\HardenedanthropicexecutorStrategy.py:72:telemetry: SystemTelemetry | None = None,
apps_rg\enforcement\HardenedanthropicexecutorStrategy.py:78:telemetry: Optional telemetry instance
apps_rg\enforcement\HardenedanthropicexecutorStrategy.py:88:telemetry=telemetry,
apps_rg\engines\service_invoker_engine.py:34:# Here we mock it but ensure the Telemetry is real.
apps_rg\engines\service_invoker_engine.py:44:# Telemetry
apps_rg\reasoning\HardenedopenaiexecutorStrategy.py:7:- Structured telemetry logging
apps_rg\reasoning\HardenedopenaiexecutorStrategy.py:73:token validation, and structured telemetry.
apps_rg\reasoning\HardenedopenaiexecutorStrategy.py:79:telemetry: SystemTelemetry | None = None,
apps_rg\reasoning\HardenedopenaiexecutorStrategy.py:85:telemetry: Optional telemetry instance
apps_rg\reasoning\HardenedopenaiexecutorStrategy.py:95:telemetry=telemetry,
apps_rg\scripts\generate_final_report.py:97:print("✅ Signal Propagation: Standardized telemetry")
apps_rg\scripts\rg_live_fire.py:118:# 5. Telemetry Audit
apps_rg\scripts\rg_live_fire.py:121:f"📊 TELEMETRY: {summary['total_spans']} Spans Recorded. Failures: {summary['failures']}",
apps_rg\scripts\test_engine.py:133:# Test 8: Base Engine Telemetry Wrapper (async)
apps_rg\scripts\test_run_grand_unification_tests.py:111:assert summary["total_spans"] >= 6, f"Telemetry gap detected. Only found {summary['total_spans']} spans."
apps_rg\types\AllProvidersDownError.py:48:telemetry: SystemTelemetry | None = None,
apps_rg\types\AllProvidersDownError.py:54:telemetry: Optional telemetry instance
apps_rg\types\AllProvidersDownError.py:57:# Telemetry is optional - use provided or None
apps_rg\types\AllProvidersDownError.py:58:self.telemetry = telemetry
apps_rg\types\AllProvidersDownError.py:147:self.telemetry.log_metric(
apps_rg\types\resume_analysis_plan_types.py:174:# 10. Record telemetry (best-effort)
apps_rg\types\resume_analysis_plan_types.py:428:"""Record telemetry data (best-effort)."""
apps_rg\types\resume_analysis_plan_types.py:440:Logger.debug(f"Failed to record telemetry: {e}")
apps_rg\types\resume_analysis_plan_types.py:443:"""Get a summary of the planning execution for debugging/telemetry."""
apps_rg\types\trace_registry_types.py:49:Centralized Telemetry Aggregator.
apps_shared\reasoning\PilotOrchestrator.py:33:self.emit_event("goal.received", {"goal": goal})
apps_shared\reasoning\restore_all_archived_agents.py:70:if any(x in name_lower for x in ["telemetry", "metrics", "tracing", "monitor", "observ"]):
apps_shared\scripts\meta_learning_bridge.py:31:def emit_app_signal_event(
apps_shared\scripts\meta_learning_bridge.py:143:def emit_app_signal_aggregate(
apps_shared\types\hardened_gemini_executor_types.py:85:"""Telemetry data for interaction logging."""
apps_shared\types\hardened_gemini_executor_types.py:191:"""Telemetry data for interaction logging."""
apps_shared\types\hardened_gemini_executor_types.py:417:async def log_interaction_telemetry(self, telemetry: InteractionTelemetry):
apps_shared\types\hardened_gemini_executor_types.py:418:"""Log structured telemetry for observability.
apps_shared\types\hardened_gemini_executor_types.py:421:telemetry: Telemetry data to log
apps_shared\types\hardened_gemini_executor_types.py:425:"interaction_id": telemetry.interaction_id,
apps_shared\types\hardened_gemini_executor_types.py:426:"model": telemetry.model,
apps_shared\types\hardened_gemini_executor_types.py:427:"input_tokens": telemetry.input_tokens,
apps_shared\types\hardened_gemini_executor_types.py:428:"output_tokens": telemetry.output_tokens,
apps_shared\types\hardened_gemini_executor_types.py:429:"total_tokens": telemetry.total_tokens,
apps_shared\types\hardened_gemini_executor_types.py:430:"latency_ms": telemetry.latency_ms,
apps_shared\types\hardened_gemini_executor_types.py:431:"timestamp": telemetry.timestamp,
apps_shared\types\hardened_gemini_executor_types.py:434:if telemetry.error:
apps_shared\types\hardened_gemini_executor_types.py:435:log_data["error"] = telemetry.error
apps_shared\types\hardened_gemini_executor_types.py:493:# 6. Calculate telemetry
apps_shared\types\hardened_gemini_executor_types.py:504:# 7. Log telemetry
apps_shared\types\hardened_gemini_executor_types.py:505:telemetry = InteractionTelemetry(
apps_shared\types\hardened_gemini_executor_types.py:514:await self.log_interaction_telemetry(telemetry)
apps_shared\types\hardened_gemini_executor_types.py:519:# Log error telemetry
apps_shared\types\hardened_gemini_executor_types.py:521:telemetry = InteractionTelemetry(
apps_shared\types\hardened_gemini_executor_types.py:531:await self.log_interaction_telemetry(telemetry)
apps_shared\types\sovereign_severity_types.py:3151:Sovereign event telemetry with Builder pattern support.
apps_shared\types\sovereign_severity_types.py:3154:- Fluent telemetry emission
apps_shared\types\sovereign_severity_types.py:3197:- Fluent, immutable telemetry emission
apps_shared\types\sovereign_severity_types.py:3254:raise ValueError("Sovereignty Telemetry Error: source is required.")
apps_shared\utils\app_base_util.py:127:Get application metadata for telemetry and monitoring.
apps_shared\utils\runtime_observability_collectors_util.py:1:# from archives.legacy_root_folders.core.models.models import TelemetryEvent  # DEPRECATED: Archive import removed to protect archives from validation edits
apps_shared\utils\runtime_observability_collectors_util.py:4:_telemetry_buffer: list[TelemetryEvent] = []
apps_shared\utils\runtime_observability_collectors_util.py:8:def append_event(evt: TelemetryEvent) -> None:
apps_shared\utils\runtime_observability_collectors_util.py:9:"""Append a telemetry event to the in-memory buffer."""
apps_shared\utils\runtime_observability_collectors_util.py:14:def get_events() -> list[TelemetryEvent]:
apps_shared\utils\runtime_observability_collectors_util.py:15:"""Return a shallow copy of the telemetry buffer."""
apps_shared\utils\runtime_observability_collectors_util.py:21:"""Clear all telemetry events and open spans (primarily for tests)."""
apps_shared\utils\runtime_observability_spans_util.py:4:# from archives.legacy_root_folders.core.models.models import TelemetryEvent  # DEPRECATED: Archive import removed to protect archives from validation edits
apps_shared\utils\runtime_observability_spans_util.py:25:TelemetryEvent(
apps_shared\utils\runtime_observability_spans_util.py:53:TelemetryEvent(
apps_shared\utils\state_persistence_error_util.py:39:telemetry: SystemTelemetry | None = None,
apps_shared\utils\state_persistence_error_util.py:46:telemetry: Optional telemetry instance
apps_shared\utils\state_persistence_error_util.py:49:self.telemetry = telemetry or get_telemetry()
apps_shared\utils\state_persistence_error_util.py:121:self.telemetry.log_success(
apps_shared\utils\state_persistence_error_util.py:165:self.telemetry.log_failure(
artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__RuntimeTelemetryAgent.py:10:RUNTIME TELEMETRY AGENT
artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__RuntimeTelemetryAgent.py:129:print(" SOVEREIGN RUNTIME TELEMETRY REPORT")
artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__RuntimeTelemetryAgent.py:145:telemetry = RuntimeTelemetryAgent()
artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__RuntimeTelemetryAgent.py:146:_, duration = telemetry.benchmark_startup(MockSovereignAgent)
artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__RuntimeTelemetryAgent.py:149:report = telemetry.audit_security_overhead(0.03, duration)
artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__RuntimeTelemetryAgent.py:151:telemetry.report_performance()
artifacts\consolidation\backups\agentic_core__L6_observability__reasoning__StrategicObservationAgent.py:36:raw_data: The input telemetry or log data from lower layers.
ops_scripts\general\architecture_gap_analyzer.py:259:key_patterns=["metrics", "dashboard", "success_rate", "mttr", "tracking", "telemetry"],
ops_scripts\general\ast_import_audit.py:1005:parser.add_argument("--emit-tag", dest="emit_tag", help="Tag for this scan (e.g., runtime, dev, sdks)")
ops_scripts\general\ast_import_audit.py:1071:elif args.roots and args.emit_tag:
ops_scripts\general\ast_import_audit.py:1073:print(f"Scanning: roots={args.roots} tag={args.emit_tag} exclude-subdir={args.exclude_subdir}")
ops_scripts\general\ast_import_audit.py:1076:tag=args.emit_tag,
ops_scripts\general\ast_import_audit.py:1080:inv_path = out_dir / f"dependency_audit_scan_{args.emit_tag}.json"
ops_scripts\general\benchmark_batch_optimization.py:174:print("📁 LocationAgent telemetry now uses efficient batching")
ops_scripts\general\mission_telemetry_dashboard.py:3:MISSION TELEMETRY DASHBOARD
ops_scripts\general\mission_telemetry_dashboard.py:47:print(f"📡 SOVEREIGN MISSION TELEMETRY [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
ops_scripts\general\sovereign_healing_mission.py:74:# Validate file location (this triggers telemetry internally)
ops_scripts\general\sovereign_healing_mission.py:96:# 6. Report Telemetry
ops_scripts\maintenance\territory_ssot_definitions_config.py:79:TERRITORY_OBSERVABILITY_TELEMETRY = "L6_Observability/Telemetry"
ops_scripts\maintenance\territory_ssot_definitions_config.py:183:elif "telemetry" in path_str:
ops_scripts\maintenance\territory_ssot_definitions_config.py:341:"telemetry",
ops_scripts\maintenance\verification.py:393:signal_bus.emit_signal(
ops_scripts\dev_tools\l0_scripts\dashboard_qa_deep_audit_util.py:56:if "/telemetry" in path or "/agents" in path:
ops_scripts\dev_tools\l0_scripts\dashboard_qa_deep_audit_util.py:57:return "L6_Observability/Telemetry"
ops_scripts\dev_tools\l0_scripts\dashboard_qa_deep_audit_util.py:62:return "L6_Observability/Telemetry"  # Default L6
ops_scripts\dev_tools\l0_scripts\regenerate_dashboard_full_util.py:85:"L6_Observability/Telemetry": "L6 observability/Infrastructure",
ops_scripts\dev_tools\l0_scripts\simulate_sovereign_workflow_util.py:54:# 5. Verify Telemetry
ops_scripts\dev_tools\l0_scripts\start_runtime_api_util.py:5:This script starts the FastAPI server that provides real-time telemetry
tests\agentic_core\test_phase3_detection_signal.py:10:emit_detection_signal,
tests\agentic_core\test_phase3_detection_signal.py:11:emit_signal_from_gateway_result,
tests\agentic_core\test_phase3_detection_signal.py:156:def test_emit_detection_signal_returns_valid_signal(self):
tests\agentic_core\test_phase3_detection_signal.py:157:sig = emit_detection_signal(
tests\agentic_core\test_phase3_detection_signal.py:181:sig = emit_signal_from_gateway_result(
tests\agentic_core\test_phase3_detection_signal.py:191:def test_emit_from_failed_result_raises_anomaly_score(self):
tests\agentic_core\test_phase3_detection_signal.py:196:sig = emit_signal_from_gateway_result(
tests\agentic_core\test_phase3_detection_signal.py:203:def test_emit_from_success_result_has_zero_anomaly(self):
tests\agentic_core\test_phase3_detection_signal.py:208:sig = emit_signal_from_gateway_result(
tests\agentic_core\test_phase3_l4_persistence.py:9:from agentic_core.L4_state.types.detection_signal_store_types import (
tests\agentic_core\test_phase3_timeshift_routing.py:15:from agentic_core.L4_state.types.detection_signal_store_types import DetectionSignalStore
tests\agentic_core\test_phase5_l4_violation_persistence.py:9:from agentic_core.L4_state.enforcement.violation_event_store import ViolationEventStore
tests\agentic_core\test_phase5_l4_violation_persistence.py:10:from agentic_core.L4_state.types.violation_event_types import ViolationEvent, emit_violation_event
tests\agentic_core\test_phase5_l4_violation_persistence.py:18:return emit_violation_event(
tests\agentic_core\test_phase5_l4_violation_persistence.py:32:h = store.store_violation_event(e)
tests\agentic_core\test_phase5_l4_violation_persistence.py:40:store.store_violation_event(e)
tests\agentic_core\test_phase5_l4_violation_persistence.py:41:store.store_violation_event(e)
tests\agentic_core\test_phase5_l4_violation_persistence.py:47:store.store_violation_event({"not": "an event"})  # type: ignore[arg-type]
tests\agentic_core\test_phase5_l4_violation_persistence.py:58:store.store_violation_event(e3)
tests\agentic_core\test_phase5_l4_violation_persistence.py:59:store.store_violation_event(e5)
tests\agentic_core\test_phase5_l4_violation_persistence.py:60:store.store_violation_event(e7)
tests\agentic_core\test_phase5_l4_violation_persistence.py:69:store.store_violation_event(_make_event(commit_tick=tick))
tests\agentic_core\test_phase5_l4_violation_persistence.py:78:store.store_violation_event(e)
tests\agentic_core\test_phase5_l4_violation_persistence.py:96:store.store_violation_event(e_same)
tests\agentic_core\test_phase5_l4_violation_persistence.py:106:store.store_violation_event(e_same)
tests\agentic_core\test_phase5_l4_violation_persistence.py:107:store.store_violation_event(e_prior)
tests\agentic_core\test_phase5_l4_violation_persistence.py:121:store.store_violation_event(e)
tests\agentic_core\test_phase5_l4_violation_persistence.py:138:store.store_violation_event(e)
tests\agentic_core\test_phase5_l4_violation_persistence.py:149:store.store_violation_event(_make_event(commit_tick=t))
tests\agentic_core\test_phase5_l4_violation_persistence.py:157:store.store_violation_event(_make_event(commit_tick=1))
tests\agentic_core\test_phase5_l4_violation_persistence.py:169:store.store_violation_event(_make_event(commit_tick=9))
tests\agentic_core\test_phase5_l4_violation_persistence.py:176:store.store_violation_event(_make_event(commit_tick=t))
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:19:from agentic_core.L4_state.enforcement.violation_event_store import ViolationEventStore
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:20:from agentic_core.L4_state.types.violation_event_types import emit_violation_event
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:34:e = emit_violation_event(
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:42:store.store_violation_event(e)
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:61:prior = emit_violation_event(
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:69:store.store_violation_event(prior)
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:72:same_cycle = emit_violation_event(
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:80:store.store_violation_event(same_cycle)
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:102:same_cycle = emit_violation_event(
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:110:store.store_violation_event(same_cycle)
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:194:e = emit_violation_event(
tests\agentic_core\test_phase5_timeshift_escalation_routing.py:202:store.store_violation_event(e)
tests\agentic_core\test_phase5_violation_event.py:9:from agentic_core.L4_state.types.violation_event_types import (
tests\agentic_core\test_phase5_violation_event.py:11:emit_violation_event,
tests\agentic_core\test_phase5_violation_event.py:34:def test_violation_event_hash_stable(self):
tests\agentic_core\test_phase5_violation_event.py:73:def test_violation_event_codes_sorted_in_canonical_bytes(self):
tests\agentic_core\test_phase5_violation_event.py:143:def test_emit_returns_violation_event(self):
tests\agentic_core\test_phase5_violation_event.py:144:e = emit_violation_event(
tests\agentic_core\test_phase5_violation_event.py:155:def test_emit_appends_to_registry(self):
tests\agentic_core\test_phase5_violation_event.py:157:emit_violation_event(
tests\agentic_core\test_phase5_violation_event.py:166:emit_violation_event(
tests\agentic_core\test_phase5_violation_event.py:177:def test_emit_does_not_alter_decision(self):
tests\agentic_core\test_phase5_violation_event.py:179:e = emit_violation_event(
tests\agentic_core\test_phase7_end_to_end_gateway_tool_isolation.py:96:def test_full_gateway_path_l1_emit_l2_execute(self):
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:18:from agentic_core.L4_state.engines.replay_bundle_emitter import emit_replay_bundle
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:45:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:59:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:72:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:88:b1 = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:96:b2 = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:108:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:126:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:141:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:161:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:175:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:183:prior_violation_event_hashes=["vh1", "vh2"],
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:187:assert "vh1" in bundle.prior_violation_event_hashes
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:193:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:203:prior_violation_event_hashes=["vh1"],
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:230:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:246:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:253:prior_violation_event_hashes=["vh1"],
tests\agentic_core\test_phase9_end_to_end_gateway_replay.py:262:bundle = emit_replay_bundle(
tests\agentic_core\test_phase9_replay_bundle_model.py:31:"prior_violation_event_hashes": [],
tests\agentic_core\test_phase9_replay_bundle_model.py:68:b1 = _make_bundle(prior_violation_event_hashes=["vh-A"])
tests\agentic_core\test_phase9_replay_bundle_model.py:69:b2 = _make_bundle(prior_violation_event_hashes=["vh-B"])
tests\agentic_core\test_phase9_replay_bundle_model.py:97:prior_violation_event_hashes=["vh-Z", "vh-A", "vh-M"],
tests\agentic_core\test_phase9_replay_bundle_model.py:102:prior_violation_event_hashes=["vh-A", "vh-M", "vh-Z"],
tests\agentic_core\test_phase9_replay_bundle_model.py:109:b = _make_bundle(prior_violation_event_hashes=["vh-Z", "vh-A", "vh-M"])
tests\agentic_core\test_phase9_replay_bundle_model.py:110:assert b.prior_violation_event_hashes == sorted(b.prior_violation_event_hashes)
tests\agentic_core\test_phase9_replay_bundle_model.py:130:prior_violation_event_hashes=[],
tests\agentic_core\test_phase9_replay_bundle_model.py:134:assert b.prior_violation_event_hashes == []
tests\agentic_core\test_phase9_replay_bundle_model.py:179:with pytest.raises(TypeError, match="prior_violation_event_hashes"):
tests\agentic_core\test_phase9_replay_bundle_model.py:180:_make_bundle(prior_violation_event_hashes="not-a-list")  # type: ignore[arg-type]
tests\agentic_core\test_phase9_replay_bundle_model.py:219:"prior_violation_event_hashes",
tests\agentic_core\test_phase9_replay_verifier.py:91:b = _make_bundle(prior_violation_event_hashes=["vh-secret"])
tests\agentic_core\test_phase9_replay_verifier.py:116:prior_violation_event_hashes=["vh1"],
tests\agentic_core\test_phase9_replay_verifier.py:209:prior_violation_event_hashes=["vh1"],
tests\agentic_core\test_phase9_replay_verifier.py:220:prior_violation_event_hashes=["vh1"],
tests\apps_rg\test_engine.py:133:# Test 8: Base Engine Telemetry Wrapper (async)
tests\apps_rg\test_run_grand_unification_tests.py:111:assert summary["total_spans"] >= 6, f"Telemetry gap detected. Only found {summary['total_spans']} spans."
tests\contracts\test_agent_artifact_emission.py:5:- self.emit_artifact(...)
tests\contracts\_discover_debt.py:40:def emit_frozenset(name, paths):
tests\contracts\_discover_debt.py:79:emit_frozenset("KNOWN_DEBT_P1", p1)
tests\contracts\_discover_debt.py:100:emit_frozenset("KNOWN_DEBT_P2", p2)
tests\contracts\_discover_debt.py:127:emit_frozenset("KNOWN_DEBT_P3", p3)
tests\contracts\_discover_debt.py:156:emit_frozenset("KNOWN_DEBT_P4", p4)
tests\contracts\_discover_debt.py:192:emit_frozenset("KNOWN_DEBT_P5", p5)
tests\contracts\_discover_debt.py:249:emit_frozenset("KNOWN_DEBT_P6", p6)
tests\contracts\_discover_debt.py:272:emit_frozenset("KNOWN_DEBT_P7", p7)
tests\contracts\_scanner.py:43:"emit_artifact",
tests\contracts\_scanner.py:45:"emit_result",
tests\contracts\_scanner.py:272:- bare calls: emit_artifact(...)
tests\contracts\_scanner.py:273:- attribute calls: self.emit_artifact(...)
tests\governance\test_heal_telemetry_and_budgets.py:2:Phase 5 tests for heal telemetry and budget caps.
tests\governance\test_heal_telemetry_and_budgets.py:4:Tests deterministic telemetry emission and budget enforcement.
tests\governance\test_heal_telemetry_and_budgets.py:52:"""Telemetry hash is deterministic for same inputs."""
tests\governance\test_heal_telemetry_and_budgets.py:85:"""Telemetry record can be serialized to deterministic JSON."""
tests\governance\test_heal_telemetry_and_budgets.py:107:"""Tests for deterministic telemetry artifact emission."""
tests\governance\test_heal_telemetry_and_budgets.py:109:def test_emit_creates_artifact(self, tmp_path):
tests\governance\test_heal_telemetry_and_budgets.py:110:"""emit_heal_telemetry creates artifact file."""
tests\governance\test_heal_telemetry_and_budgets.py:113:emit_heal_telemetry,
tests\governance\test_heal_telemetry_and_budgets.py:129:filepath = emit_heal_telemetry(record, artifacts_root=tmp_path)
tests\governance\test_heal_telemetry_and_budgets.py:139:def test_emit_idempotent_same_content(self, tmp_path):
tests\governance\test_heal_telemetry_and_budgets.py:140:"""emit_heal_telemetry is idempotent for same content."""
tests\governance\test_heal_telemetry_and_budgets.py:143:emit_heal_telemetry,
tests\governance\test_heal_telemetry_and_budgets.py:159:filepath1 = emit_heal_telemetry(record, artifacts_root=tmp_path)
tests\governance\test_heal_telemetry_and_budgets.py:160:filepath2 = emit_heal_telemetry(record, artifacts_root=tmp_path)
tests\governance\test_heal_telemetry_and_budgets.py:165:def test_emit_fails_on_conflict(self, tmp_path):
tests\governance\test_heal_telemetry_and_budgets.py:166:"""emit_heal_telemetry fails if file exists with different content."""
tests\governance\test_heal_telemetry_and_budgets.py:169:emit_heal_telemetry,
tests\governance\test_heal_telemetry_and_budgets.py:186:emit_heal_telemetry(record1, artifacts_root=tmp_path)
tests\governance\test_heal_telemetry_and_budgets.py:202:with pytest.raises(ValueError, match="Telemetry artifact conflict"):
tests\governance\test_heal_telemetry_and_budgets.py:203:emit_heal_telemetry(record2, artifacts_root=tmp_path)
tests\governance\test_seam_dynamic_enforcement.py:380:test_file.write_text("mod = __import__('agentic_core.L6_observability.telemetry')\n")
tests\governance\test_upward_import_enforcement.py:653:test_file.write_text("import agentic_core.L6_observability.telemetry\n")
tests\guardian\test_artifact_class_enum_ratchet.py:22:"_emit_contract_json_schema",  # Schema helper
tests\guardian\test_artifact_emission_prohibition.py:198:def test_assert_layer_may_emit_allows_non_forbidden_combo(self):
tests\guardian\test_mece_naming_compliance.py:319:def test_emit_compliance_artifact(self, project_root, tmp_path):
tests\guardian\test_v15_p1_compliance.py:47:TelemetryEmitter,
tests\guardian\test_v15_p1_compliance.py:538:# P1-M-17 (§15.6): INCIDENT and RESULT telemetry emission
tests\guardian\test_v15_p1_compliance.py:543:"""P1-M-17: TelemetryEmitter emits events for INCIDENT and RESULT."""
tests\guardian\test_v15_p1_compliance.py:545:def test_emit_incident(self):
tests\guardian\test_v15_p1_compliance.py:546:emitter = TelemetryEmitter()
tests\guardian\test_v15_p1_compliance.py:554:emitter.emit_incident(incident)
tests\guardian\test_v15_p1_compliance.py:558:def test_emit_result(self):
tests\guardian\test_v15_p1_compliance.py:559:emitter = TelemetryEmitter()
tests\guardian\test_v15_p1_compliance.py:566:emitter.emit_result(result)
tests\guardian\test_v15_p3_compliance.py:26:emit_policy_exception,
tests\guardian\test_v15_p3_compliance.py:177:art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
tests\guardian\test_v15_p3_compliance.py:239:"""§3.7 — emit_policy_exception contract function."""
tests\guardian\test_v15_p3_compliance.py:242:art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
tests\guardian\test_v15_p3_compliance.py:248:art = emit_policy_exception(**VALID_EXCEPTION_KWARGS, nonce="custom-nonce")
tests\guardian\test_v15_p3_compliance.py:253:emit_policy_exception(**{**VALID_EXCEPTION_KWARGS, "trace_id": ""})
tests\guardian\test_v15_p3_compliance.py:257:art = emit_policy_exception(**{**VALID_EXCEPTION_KWARGS, "exception_scope": scope})
tests\guardian\test_v15_p3_compliance.py:261:art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
tests\guardian\test_v15_p3_compliance.py:265:art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
tests\guardian\test_v15_p3_compliance.py:270:art = emit_policy_exception(**VALID_EXCEPTION_KWARGS)
tests\agentic_core\interfaces\test_detection_protocol.py:179:def emit_signal(self, result: DetectionResult) -> str:
tests\agentic_core\interfaces\test_detection_protocol.py:205:def test_mock_emit_signal(self):
tests\agentic_core\interfaces\test_detection_protocol.py:215:signal_id = emitter.emit_signal(result)
tests\agentic_core\interfaces\test_detection_protocol.py:228:emitter.emit_signal(result)
tests\agentic_core\interfaces\test_detection_protocol.py:236:emitter.emit_signal(
tests\agentic_core\interfaces\test_detection_protocol.py:245:emitter.emit_signal(
tests\agentic_core\interfaces\test_detection_protocol.py:261:emitter.emit_signal(
tests\agentic_core\interfaces\test_detection_protocol.py:270:emitter.emit_signal(
tests\agentic_core\mixins\test_feature_flagged_agent_mixin.py:192:def test_emit_detection_signal_disabled(self):
tests\agentic_core\mixins\test_feature_flagged_agent_mixin.py:197:result = agent.emit_detection_signal(
tests\agentic_core\mixins\test_feature_flagged_agent_mixin.py:205:def test_emit_detection_signal_enabled_no_implementation(self):
tests\agentic_core\mixins\test_feature_flagged_agent_mixin.py:211:result = agent.emit_detection_signal(
tests\agentic_core\L1_cognition\core\test_cognitive_endurance.py:5:- Telemetry Pruner (sanitize_tool_output)
tests\agentic_core\L1_cognition\core\test_cognitive_endurance.py:23:"""Test the telemetry pruner (anti-token overload)."""
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:21:emit_self_healing_trigger,
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:42:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:58:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:70:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:82:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:108:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:180:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:192:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:204:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:215:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:226:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:237:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:248:trigger = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:299:emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:317:return emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:336:return emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:353:t1 = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:361:t2 = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:373:t1 = emit_self_healing_trigger(
tests\agentic_core\L2_execution\types\test_self_healing_trigger.py:381:t2 = emit_self_healing_trigger(
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:240:original_emit = queue._emit_policy_update_proposal
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:246:queue._emit_policy_update_proposal = capture_emit
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:261:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter",
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:264:mock_instance.emit_typed_artifact = mock_emit
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:284:original_emit = queue._emit_policy_update_proposal
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:290:queue._emit_policy_update_proposal = capture_emit
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:305:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter",
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:308:mock_instance.emit_typed_artifact = mock_emit
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:334:original_emit = queue._emit_policy_update_proposal
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:340:queue._emit_policy_update_proposal = capture_emit
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:362:original_emit = queue._emit_policy_update_proposal
tests\agentic_core\L3_orchestration\reasoning\test_hil_policy_proposal_emission.py:368:queue._emit_policy_update_proposal = capture_emit
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:326:"""Assert TelemetryEmitter.emit_route_decision is called as durable sink."""
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:328:def test_emit_route_decision_called_once_with_all_keys(self):
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:329:"""emit_route_decision called exactly once; payload has all artifact keys."""
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:350:seam.TelemetryEmitter,
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:351:"emit_route_decision",
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:361:def test_emit_route_decision_called_on_blocked_path(self):
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:383:seam.TelemetryEmitter,
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:384:"emit_route_decision",
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:396:"""Assert TelemetryEmitter.flush_to_artifacts_dir persists events to disk."""
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:402:from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:414:emitter = TelemetryEmitter()
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:415:emitter.emit_route_decision(artifact)
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:431:from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter
tests\agentic_core\L3_orchestration\reasoning\test_route_decision_artifact_contract.py:433:emitter = TelemetryEmitter()
tests\agentic_core\L3_orchestration\reasoning\test_token_budget_enforcement.py:238:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter.emit_typed_artifact",
tests\agentic_core\L3_orchestration\reasoning\test_token_budget_enforcement.py:307:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter.emit_typed_artifact",
tests\agentic_core\L3_orchestration\reasoning\test_token_budget_enforcement.py:373:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter.emit_typed_artifact",
tests\agentic_core\L3_orchestration\reasoning\test_token_budget_enforcement.py:441:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter.emit_typed_artifact",
tests\agentic_core\L3_orchestration\reasoning\test_token_budget_enforcement.py:516:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter.emit_typed_artifact",
tests\agentic_core\L3_orchestration\reasoning\test_tool_enforcement_gate.py:190:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter.emit_typed_artifact",
tests\agentic_core\L3_orchestration\reasoning\test_tool_enforcement_gate.py:218:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter.emit_typed_artifact",
tests\agentic_core\L3_orchestration\reasoning\test_tool_enforcement_gate.py:283:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter.emit_typed_artifact",
tests\agentic_core\L3_orchestration\reasoning\test_tool_enforcement_gate.py:354:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter.emit_typed_artifact",
tests\agentic_core\L3_orchestration\reasoning\test_tool_enforcement_gate.py:403:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter.emit_typed_artifact",
tests\agentic_core\L3_orchestration\reasoning\test_tool_enforcement_gate.py:423:"agentic_core.L0_routing.types.routing_contracts_types.TelemetryEmitter.emit_typed_artifact",
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:22:emit_cognitive_diff_bundle,
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:66:bundle = emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:78:bundle = emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:87:bundle = emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:104:bundle = emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:157:emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:177:return emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:194:a = emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:199:b = emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:209:a = emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:214:b = emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:222:bundle = emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:262:bundle = emit_cognitive_diff_bundle(
tests\agentic_core\L3_orchestration\types\test_cognitive_diff_bundle.py:288:bundle = emit_cognitive_diff_bundle(
tests\agentic_core\L5_safety\reasoning\test_lcd_migration_remediation.py:1007:"""A file with monitor/telemetry/report keywords should score highest for L6."""
tests\agentic_core\L5_safety\reasoning\test_lcd_migration_remediation.py:1012:Persists health metrics for monitoring and telemetry.
tests\agentic_core\L5_safety\reasoning\test_service_classification_hardening.py:138:def emit_event(self, event):
tests\agentic_core\L5_safety\utils\test_fca_safety_gates.py:350:p.write_text("import json\nclass Telemetry: pass\n")
tests\agentic_core\L6_observability\agents\test_telemetry_agent.py:5:Autonomous telemetry emission agent.
tests\agentic_core\L6_observability\agents\test_telemetry_agent.py:52:def test_has_emit_method(self, agent_class):
tests\agentic_core\L6_observability\reasoning\test_dashboard_agent.py:25:"""Tests for telemetry functionality."""
tests\agentic_core\L6_observability\reasoning\test_dashboard_agent.py:28:"""Telemetry types should be defined in types/."""
tests\agentic_core\L6_observability\reasoning\test_dashboard_agent.py:94:"telemetry",
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:23:emit_vigilance_event,
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:69:event = emit_vigilance_event(
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:76:event = emit_vigilance_event(
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:144:event = emit_vigilance_event(signals=["info_metric"], semantic_clock=clock)
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:149:event = emit_vigilance_event(
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:168:event = emit_vigilance_event(signals=["info_metric"], semantic_clock=clock)
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:182:event = emit_vigilance_event(signals=["info_metric"], semantic_clock=clock)
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:186:event = emit_vigilance_event(signals=["guardian_fail"], semantic_clock=clock)
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:190:event = emit_vigilance_event(signals=["budget_overflow"], semantic_clock=clock)
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:194:event = emit_vigilance_event(
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:209:return emit_vigilance_event(
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:220:a = emit_vigilance_event(signals=["guardian_fail"], semantic_clock=clock)
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:221:b = emit_vigilance_event(signals=["guardian_fail"], semantic_clock=clock)
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:225:a = emit_vigilance_event(
tests\agentic_core\L6_observability\types\test_tiered_vigilance_monitor.py:229:b = emit_vigilance_event(
tests\apps_rg\scripts\test_engine.py:133:# Test 8: Base Engine Telemetry Wrapper (async)
tests\apps_rg\scripts\test_run_grand_unification_tests.py:111:assert summary["total_spans"] >= 6, f"Telemetry gap detected. Only found {summary['total_spans']} spans."
tests\apps_shared\scripts\test_meta_learning_bridge.py:20:emit_app_signal_aggregate,
tests\apps_shared\scripts\test_meta_learning_bridge.py:21:emit_app_signal_event,
tests\apps_shared\scripts\test_meta_learning_bridge.py:48:e1 = emit_app_signal_event(**kwargs)
tests\apps_shared\scripts\test_meta_learning_bridge.py:49:e2 = emit_app_signal_event(**kwargs)
tests\apps_shared\scripts\test_meta_learning_bridge.py:60:inspect.getfile(emit_app_signal_event),
tests\apps_shared\scripts\test_meta_learning_bridge.py:210:agg1 = emit_app_signal_aggregate(
tests\apps_shared\scripts\test_meta_learning_bridge.py:220:agg2 = emit_app_signal_aggregate(
tests\apps_shared\scripts\test_meta_learning_bridge.py:238:bridge_path = Path(inspect.getfile(emit_app_signal_event))
tests\e2e\agentic_core\L0_maintenance\misc\test_ssot_e2e_reporting.py:29:Integration Suite: Verifies full lifecycles, state persistence, and final telemetry reports.
tests\e2e\agentic_core\L0_maintenance\misc\test_ssot_e2e_reporting.py:238:# CASE 7: Large Scale Telemetry Serialization
tests\e2e\agentic_core\L0_maintenance\misc\test_ssot_e2e_reporting.py:317:# CASE 10: Telemetry Severity Filtering
tests\e2e\ops_scripts\misc\test_complete_mission_workflow.py:3:Shows the mission control capabilities including telemetry, batch optimization, and healing.
tests\e2e\ops_scripts\misc\test_complete_mission_workflow.py:17:Demonstrate the complete mission workflow with telemetry and batch optimization.
tests\e2e\ops_scripts\misc\test_complete_mission_workflow.py:36:# 2. Pre-Mission Telemetry Check
tests\e2e\ops_scripts\misc\test_complete_mission_workflow.py:37:print("\n📊 2. PRE-MISSION TELEMETRY...")
tests\e2e\ops_scripts\misc\test_complete_mission_workflow.py:59:# Use batch context for telemetry optimization
tests\e2e\ops_scripts\misc\test_complete_mission_workflow.py:69:# This triggers optimized telemetry (batched)
tests\e2e\ops_scripts\misc\test_complete_mission_workflow.py:96:print(f"   📊 Telemetry efficiency: {efficiency:.1f} files per scan increment")
tests\e2e\ops_scripts\misc\test_complete_mission_workflow.py:140:print("   📊 Telemetry integrity: ✅")
tests\e2e\ops_scripts\misc\test_complete_mission_workflow.py:159:print("   📊 Telemetry Intelligence: ✅")
tests\e2e\ops_scripts\misc\test_location_agent_telemetry.py:2:Quick integration test to verify LocationAgent telemetry works with batch optimization.
tests\e2e\ops_scripts\misc\test_location_agent_telemetry.py:25:# Import RuntimeStateGuard directly to test telemetry
tests\e2e\ops_scripts\misc\test_location_agent_telemetry.py:59:print("LocationAgent telemetry integration verified! ✅")
tests\e2e\ops_scripts\misc\test_mission_dry_run.py:141:print("   ✅ Telemetry and batching working")
tests\support\l3_orchestration\SubatomicHopAgent.py:23:from agentic_core.runtime.core.telemetry import TraceEvent
tests\support\l3_orchestration\SubatomicHopAgent.py:65:telemetry: Any | None = None,
tests\support\l3_orchestration\SubatomicHopAgent.py:84:telemetry: TelemetryRecorder instance (injected)
tests\support\l3_orchestration\SubatomicHopAgent.py:104:self.telemetry = self._ensure_dep(telemetry, "TelemetryRecorder")
tests\support\l3_orchestration\SubatomicHopAgent.py:223:self.telemetry.record(
tests\support\l3_orchestration\SubatomicHopAgent.py:247:self.telemetry.record(
tests\support\l3_orchestration\SubatomicHopAgent.py:266:self.telemetry.record(
tests\support\l3_orchestration\SubatomicHopAgent.py:298:self.telemetry.record(
tests\support\l3_orchestration\SubatomicHopAgent.py:314:self.telemetry.record(
tests\support\l3_orchestration\SubatomicHopAgent.py:338:"""Check telemetry for past failures on similar tasks."""
tests\support\l3_orchestration\SubatomicHopAgent.py:365:self.telemetry.record(
tests\support\l3_orchestration\SubatomicHopAgent.py:376:self.telemetry.record(
tests\support\l3_orchestration\SubatomicHopAgent.py:401:self.telemetry.record(
tests\support\l3_orchestration\SubatomicHopAgent.py:426:self.telemetry.record(
tests\support\l3_orchestration\SubatomicHopAgent.py:439:"""Handle execution errors with unified telemetry."""
tests\support\l3_orchestration\SubatomicHopAgent.py:441:self.telemetry.record(
tests\support\l3_orchestration\SubatomicHopAgent.py:455:self.telemetry.record(
tests\support\l6_observability\SovereignObservabilityAgent.py:138:self.emit_event(
tests\support\l6_observability\SovereignObservabilityAgent.py:152:Check if current telemetry should be sampled (for INFO level).
tests\support\l6_observability\SovereignObservabilityAgent.py:155:True if telemetry should be recorded, False to skip
tests\support\l6_observability\SovereignObservabilityAgent.py:161:[SKEPTICAL CHALLENGE RESPONSE] Rate limit ERROR telemetry.
tests\support\l6_observability\SovereignObservabilityAgent.py:188:- Keeping 100% of ERROR level telemetry (but rate-limited to 100/sec)
tests\support\l6_observability\SovereignObservabilityAgent.py:199:telemetry_batch: List of telemetry records to ingest
tests\support\l6_observability\SovereignObservabilityAgent.py:244:for telemetry in filtered_batch:
tests\support\l6_observability\SovereignObservabilityAgent.py:246:self.emit_event(
tests\support\l6_observability\SovereignObservabilityAgent.py:249:"trace_id": telemetry.get("trace_id"),
tests\support\l6_observability\SovereignObservabilityAgent.py:250:"service_name": telemetry.get("service_name"),
tests\support\l6_observability\SovereignObservabilityAgent.py:251:"level": telemetry.get("level"),
tests\support\l6_observability\SovereignObservabilityAgent.py:252:"operation": telemetry.get("operation_name"),
tests\support\l6_observability\TelemetryAgent.py:14:Emits structured telemetry events for observability and auditing.
tests\support\l6_observability\TelemetryAgent.py:26:Placed in observability/telemetry per SSOT semantic registry:
tests\support\l6_observability\TelemetryAgent.py:27:"Distributed telemetry, event emission, and structured observability events"
tests\support\l6_observability\TelemetryAgent.py:29:Depth: agentic_core/observability/telemetry/telemetry_agent.py
tests\support\l6_observability\TelemetryAgent.py:51:Autonomous telemetry emission agent.
tests\support\l6_observability\TelemetryAgent.py:65:Initialize telemetry buffer.
tests\support\l6_observability\TelemetryAgent.py:81:event_type="telemetry.agent_started",
tests\support\l6_observability\TelemetryAgent.py:94:Emit a structured telemetry event.
tests\support\l6_observability\TelemetryAgent.py:189:def emit_compliance_scan_started(self, file_count: int) -> None:
tests\support\l6_observability\TelemetryAgent.py:198:def emit_compliance_scan_completed(self, violation_count: int, duration_seconds: float) -> None:
tests\support\l6_observability\TelemetryAgent.py:211:def emit_violation_detected(self, file_path: str, ViolationType: str, message: str, agent: str) -> None:
tests\support\l6_observability\TelemetryAgent.py:220:def emit_agent_action(
tests\unit\L1_cognition\test_telemetry_emitter.py:2:Unit tests for L1 Cognition Telemetry Emitter - write-only, ZERO-decision component.
tests\unit\L1_cognition\test_telemetry_emitter.py:7:from agentic_core.L1_cognition.telemetry.telemetry_emitter import (
tests\unit\L1_cognition\test_telemetry_emitter.py:8:TelemetryEmitter,
tests\unit\L1_cognition\test_telemetry_emitter.py:9:TelemetryEvent,
tests\unit\L1_cognition\test_telemetry_emitter.py:49:class TestTelemetryEvent:
tests\unit\L1_cognition\test_telemetry_emitter.py:50:"""Test TelemetryEvent immutable dataclass."""
tests\unit\L1_cognition\test_telemetry_emitter.py:56:event = TelemetryEvent.create(
tests\unit\L1_cognition\test_telemetry_emitter.py:72:event1 = TelemetryEvent.create(
tests\unit\L1_cognition\test_telemetry_emitter.py:76:event2 = TelemetryEvent.create(
tests\unit\L1_cognition\test_telemetry_emitter.py:87:event1 = TelemetryEvent.create(
tests\unit\L1_cognition\test_telemetry_emitter.py:91:event2 = TelemetryEvent.create(
tests\unit\L1_cognition\test_telemetry_emitter.py:101:event = TelemetryEvent.create(
tests\unit\L1_cognition\test_telemetry_emitter.py:118:event = TelemetryEvent.create(
tests\unit\L1_cognition\test_telemetry_emitter.py:143:class TestTelemetryEmitter:
tests\unit\L1_cognition\test_telemetry_emitter.py:144:"""Test TelemetryEmitter write-only behavior."""
tests\unit\L1_cognition\test_telemetry_emitter.py:146:def test_emit_calls_injected_record_fn_exactly_once(self):
tests\unit\L1_cognition\test_telemetry_emitter.py:148:emitter = TelemetryEmitter()
tests\unit\L1_cognition\test_telemetry_emitter.py:151:event = TelemetryEvent.create(
tests\unit\L1_cognition\test_telemetry_emitter.py:167:def test_emit_performs_no_mutation(self):
tests\unit\L1_cognition\test_telemetry_emitter.py:169:emitter = TelemetryEmitter()
tests\unit\L1_cognition\test_telemetry_emitter.py:172:event = TelemetryEvent.create(
tests\unit\L1_cognition\test_telemetry_emitter.py:191:def test_emit_no_branching_logic(self):
tests\unit\L1_cognition\test_telemetry_emitter.py:193:emitter = TelemetryEmitter()
tests\unit\L1_cognition\test_telemetry_emitter.py:197:TelemetryEvent.create("trace1", "stage1", "kind1", 1, {"a": 1}),
tests\unit\L1_cognition\test_telemetry_emitter.py:198:TelemetryEvent.create("trace2", "stage2", "kind2", 2, {"b": 2}),
tests\unit\L1_cognition\test_telemetry_emitter.py:199:TelemetryEvent.create("trace3", "stage3", "kind3", 3, {"c": 3}),
tests\unit\L1_cognition\test_telemetry_emitter.py:216:emitter = TelemetryEmitter()
tests\unit\L1_cognition\test_telemetry_emitter.py:236:# Verify it's a proper TelemetryEvent
tests\unit\L1_cognition\test_telemetry_emitter.py:237:assert isinstance(event, TelemetryEvent)
tests\unit\L1_cognition\test_telemetry_emitter.py:240:"""Test build_event produces same result as direct TelemetryEvent.create."""
tests\unit\L1_cognition\test_telemetry_emitter.py:241:emitter = TelemetryEmitter()
tests\unit\L1_cognition\test_telemetry_emitter.py:251:event2 = TelemetryEvent.create(
tests\unit\L4_state\test_telemetry_recorder.py:3:Phase 1 Wave 1.3 test suite. Verifies durable telemetry,
tests\_quarantine\integration\apps_lic_dir\test_lic_hop_pipeline_integration.py:165:"""Verify pipeline emits telemetry at each stage."""
tests\_quarantine\integration\apps_lic_dir\test_lic_hop_pipeline_integration.py:166:pytest.skip("Implementation pending - verify telemetry")
tests\_quarantine\integration\apps_shared_dir\test_shared_infrastructure_integration.py:8:- Observability and telemetry
tests\_quarantine\integration\apps_shared_dir\test_shared_infrastructure_integration.py:15:- Observability: Telemetry and metrics collection integration
tests\_quarantine\integration\apps_shared_dir\test_shared_infrastructure_integration.py:32:"telemetry": MagicMock(),
tests\_quarantine\integration\apps_shared_dir\test_shared_infrastructure_integration.py:103:"""MECE Category: Telemetry and metrics collection integration."""
tests\_quarantine\integration\apps_shared_dir\test_shared_infrastructure_integration.py:106:"""Verify telemetry captures LIC agent execution spans."""
tests\_quarantine\integration\apps_shared_dir\test_shared_infrastructure_integration.py:107:telemetry = mock_infrastructure["telemetry"]
tests\_quarantine\integration\apps_shared_dir\test_shared_infrastructure_integration.py:108:telemetry.start_span.return_value = MagicMock()
tests\_quarantine\integration\apps_shared_dir\test_shared_infrastructure_integration.py:113:"""Verify telemetry captures RG engine execution spans."""
tests\_quarantine\integration\agentic_core\core_dashboard\test_integration.py:29:"""Verify telemetry update functions exist."""
tests\_quarantine\integration\agentic_core\core_dashboard\test_integration.py:30:# Placeholder for actual telemetry function test
tests\_quarantine\integration\agentic_core\core_dashboard\test_telemetry.py:2:Dashboard Telemetry Tests (Phase 1-2)
tests\_quarantine\integration\agentic_core\core_dashboard\test_telemetry.py:5:Tests for dashboard live runtime meta-learning and telemetry.
tests\_quarantine\integration\agentic_core\core_dashboard\test_telemetry.py:61:"""Test telemetry callback functionality."""
tests\_quarantine\integration\agentic_core\core_dashboard\test_telemetry.py:64:"""Verify telemetry callbacks can be registered."""
tests\_quarantine\integration\agentic_core\core_dashboard\test_telemetry.py:69:"""Verify telemetry callbacks are invoked on state changes."""
tests\_quarantine\integration\agentic_core\L0_maintenance_dir\test_execute_ssot_comprehensive.py:3:Description: Comprehensive 10-case test suite for enhanced SSOT execution, covering safety, LLM logic, and telemetry.
tests\_quarantine\integration\agentic_core\L0_maintenance_dir\test_execute_ssot_comprehensive.py:205:# CASE 9: Telemetry Report Accuracy
```

### Exception Handling References
```
agentic_core\L0_routing\scripts\execute_ssot.py:52:try:
agentic_core\L0_routing\scripts\execute_ssot.py:55:raise RuntimeError("CRITICAL: _legacy_main not found in execute_ssot module")
agentic_core\L0_routing\scripts\execute_ssot.py:59:raise RuntimeError("CRITICAL: _legacy_main attribute is not callable")
agentic_core\L0_routing\scripts\execute_ssot.py:61:raise RuntimeError(
agentic_core\L0_routing\scripts\execute_ssot.py:70:imported, re-raise so the caller sees a hard failure instead of a silent
agentic_core\L0_routing\scripts\execute_ssot.py:73:try:
agentic_core\L0_routing\scripts\execute_ssot.py:78:except Exception:
agentic_core\L0_routing\scripts\execute_ssot.py:93:try:
agentic_core\L0_routing\scripts\execute_ssot.py:97:except ImportError:
agentic_core\L0_routing\scripts\execute_ssot.py:103:try:
agentic_core\L0_routing\scripts\execute_ssot.py:105:except ImportError:
agentic_core\L0_routing\scripts\execute_ssot.py:112:try:
agentic_core\L0_routing\scripts\execute_ssot.py:114:except ImportError:
agentic_core\L0_routing\scripts\execute_ssot.py:141:raise RuntimeError(f"Unable to resolve repo root from: {cur}")
agentic_core\L0_routing\scripts\execute_ssot.py:155:level = logging.WARNING
agentic_core\L0_routing\scripts\execute_ssot.py:157:level = logging.DEBUG
agentic_core\L0_routing\scripts\execute_ssot.py:159:level = logging.INFO
agentic_core\L0_routing\scripts\execute_ssot.py:160:logging.basicConfig(
agentic_core\L0_routing\scripts\execute_ssot.py:170:try:
agentic_core\L0_routing\scripts\execute_ssot.py:172:except FileNotFoundError:
agentic_core\L0_routing\scripts\execute_ssot.py:174:try:
agentic_core\L0_routing\scripts\execute_ssot.py:177:except Exception:
agentic_core\L0_routing\scripts\execute_ssot.py:179:try:
agentic_core\L0_routing\scripts\execute_ssot.py:182:except Exception:
agentic_core\L0_routing\scripts\execute_ssot.py:189:for handler in logging.getLogger().handlers + logging.getLogger("").handlers:
agentic_core\L0_routing\scripts\execute_ssot.py:200:try:
agentic_core\L0_routing\scripts\execute_ssot.py:203:except Exception:
agentic_core\L0_routing\scripts\execute_ssot.py:218:try:
agentic_core\L0_routing\scripts\execute_ssot.py:251:except Exception:
agentic_core\L0_routing\scripts\execute_ssot.py:261:try:
agentic_core\L0_routing\scripts\execute_ssot.py:280:except Exception as exc:
agentic_core\L0_routing\scripts\execute_ssot.py:281:logging.getLogger(__name__).warning("[V15] SSOT gateway audit failed (LOG_ONLY): %s", exc)
agentic_core\L0_routing\scripts\execute_ssot.py:422:try:
agentic_core\L0_routing\scripts\execute_ssot.py:614:logger.warning(
agentic_core\L0_routing\scripts\execute_ssot.py:664:try:
agentic_core\L0_routing\scripts\execute_ssot.py:691:except ImportError:
agentic_core\L0_routing\scripts\execute_ssot.py:692:logger.warning("CognitiveDispositionAgent not available, using default confidence")
agentic_core\L0_routing\scripts\execute_ssot.py:695:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:696:logger.error(f"Cognitive analysis failed: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:725:logging.warning(f"Sovereignty DENIED for {agent_name}: Atomic lock active")
agentic_core\L0_routing\scripts\execute_ssot.py:729:logging.critical(
agentic_core\L0_routing\scripts\execute_ssot.py:737:logging.warning(f"Sovereignty DENIED for {agent_name}: Cycle detected {op_signature}")
agentic_core\L0_routing\scripts\execute_ssot.py:757:logging.warning(f"Sovereignty released with FAILURE status for {agent_name}")
agentic_core\L0_routing\scripts\execute_ssot.py:780:try:
agentic_core\L0_routing\scripts\execute_ssot.py:790:logging.warning(
agentic_core\L0_routing\scripts\execute_ssot.py:794:logging.warning(
agentic_core\L0_routing\scripts\execute_ssot.py:800:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:801:logging.warning(f"Could not verify Windows LongPathsEnabled: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:810:try:
agentic_core\L0_routing\scripts\execute_ssot.py:814:except OSError:
agentic_core\L0_routing\scripts\execute_ssot.py:826:try:
agentic_core\L0_routing\scripts\execute_ssot.py:830:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:889:logger.warning(
agentic_core\L0_routing\scripts\execute_ssot.py:895:logger.critical("Infinite prompt loop detected - killing process capability")
agentic_core\L0_routing\scripts\execute_ssot.py:896:raise RecursionError("Interactive prompt limit exceeded (Infinite Loop Protection)")
agentic_core\L0_routing\scripts\execute_ssot.py:898:raise RuntimeError(f"Interactive prompt blocked in autonomous mode: {prompt}")
agentic_core\L0_routing\scripts\execute_ssot.py:913:try:
agentic_core\L0_routing\scripts\execute_ssot.py:916:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:920:raise e
agentic_core\L0_routing\scripts\execute_ssot.py:922:raise e
agentic_core\L0_routing\scripts\execute_ssot.py:925:logger.warning(
agentic_core\L0_routing\scripts\execute_ssot.py:929:logger.error(f"All retries failed for {func.__name__}")
agentic_core\L0_routing\scripts\execute_ssot.py:930:raise last_exception
agentic_core\L0_routing\scripts\execute_ssot.py:963:logging.info("Phase 2: No violations to reconcile.")
agentic_core\L0_routing\scripts\execute_ssot.py:974:logging.info(f"Phase 2: Attempting to reconcile {len(plan['violations_found'])} violations...")
agentic_core\L0_routing\scripts\execute_ssot.py:989:logging.warning(f"Skipping fix for {file_path}: {reason}")
agentic_core\L0_routing\scripts\execute_ssot.py:1003:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1006:raise ValueError(f"Agent {agent_name} not found")
agentic_core\L0_routing\scripts\execute_ssot.py:1018:raise RuntimeError(f"Agent reported failure: {fix_result.get('error', 'Unknown')}")
agentic_core\L0_routing\scripts\execute_ssot.py:1024:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:1025:logging.error(f"Fix failed for {agent_name} on {file_path}: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:1092:logger = logging.getLogger("UnifiedSovereign")
agentic_core\L0_routing\scripts\execute_ssot.py:1166:logger.error(message)
agentic_core\L0_routing\scripts\execute_ssot.py:1168:logger.warning(message)
agentic_core\L0_routing\scripts\execute_ssot.py:1171:logger.info(message)
agentic_core\L0_routing\scripts\execute_ssot.py:1187:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1196:except Exception:
agentic_core\L0_routing\scripts\execute_ssot.py:1199:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1218:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:1219:logger.error(f"Failed to save runtime state (Atomic Write Failed): {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:1220:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1264:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1269:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1282:logger.warning(f"Skipping agent with invalid path parts: {raw_path}")
agentic_core\L0_routing\scripts\execute_ssot.py:1292:logger.warning(f"Blocking unauthorized module load attempt: {module_path}")
agentic_core\L0_routing\scripts\execute_ssot.py:1297:except Exception as p_err:
agentic_core\L0_routing\scripts\execute_ssot.py:1299:logger.warning(f"Skipping malformed agent path '{raw_path}': {p_err}")
agentic_core\L0_routing\scripts\execute_ssot.py:1301:logger.info(f"Loaded {len(agents)} agents from cache")
agentic_core\L0_routing\scripts\execute_ssot.py:1303:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:1304:logger.warning(f"Cache load failed: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:1308:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1311:logger.info("Running live agent discovery...")
agentic_core\L0_routing\scripts\execute_ssot.py:1316:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1329:logger.warning(f"Skipping agent with invalid path parts: {raw_path}")
agentic_core\L0_routing\scripts\execute_ssot.py:1339:logger.warning(f"Blocking unauthorized module load attempt: {module_path}")
agentic_core\L0_routing\scripts\execute_ssot.py:1344:except Exception as p_err:
agentic_core\L0_routing\scripts\execute_ssot.py:1346:logger.warning(f"Skipping malformed agent path '{raw_path}': {p_err}")
agentic_core\L0_routing\scripts\execute_ssot.py:1349:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1362:logger.info(f"Discovered {len(agents)} agents (cached)")
agentic_core\L0_routing\scripts\execute_ssot.py:1364:except Exception as cache_err:
agentic_core\L0_routing\scripts\execute_ssot.py:1365:logger.warning(f"Failed to cache agent discovery: {cache_err}")
agentic_core\L0_routing\scripts\execute_ssot.py:1370:except ImportError:
agentic_core\L0_routing\scripts\execute_ssot.py:1371:logger.warning("Live discovery unavailable - Full_Agent_discovery not found")
agentic_core\L0_routing\scripts\execute_ssot.py:1373:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:1374:logger.error(f"Live discovery failed: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:1466:logger.info(f"=== PHASE 1: DISCOVERY - {territory} ===")
agentic_core\L0_routing\scripts\execute_ssot.py:1488:logger.critical(f"SECURITY ALERT: Path traversal attempt detected for territory '{territory}'")
agentic_core\L0_routing\scripts\execute_ssot.py:1505:logger.warning(f"Territory path does not exist: {territory_path}")
agentic_core\L0_routing\scripts\execute_ssot.py:1509:logger.info("🧠 Using CognitiveDispositionAgent for enhanced violation analysis...")
agentic_core\L0_routing\scripts\execute_ssot.py:1514:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1516:except RuntimeError:
agentic_core\L0_routing\scripts\execute_ssot.py:1529:logger.info(f"🧠 Enhanced confidence with cognitive analysis: {confidence.value:.2f}")
agentic_core\L0_routing\scripts\execute_ssot.py:1548:logger.info(f"Location Decision: {reason}")
agentic_core\L0_routing\scripts\execute_ssot.py:1551:logger.info(f"🔧 Triggering LocationAgent auto-heal for {len(violations)} violations")
agentic_core\L0_routing\scripts\execute_ssot.py:1562:logger.warning(
agentic_core\L0_routing\scripts\execute_ssot.py:1583:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1616:logger.info(f"📋 FileClassificationAgent early detection: {classification_count} issues found")
agentic_core\L0_routing\scripts\execute_ssot.py:1619:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:1620:logger.warning(f"FileClassificationAgent early detection failed: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:1644:logger.info(f"=== PHASE 2: ALIGNMENT - {territory} ===")
agentic_core\L0_routing\scripts\execute_ssot.py:1662:logger.info(f"Decision: {reason}")
agentic_core\L0_routing\scripts\execute_ssot.py:1695:logger.info(f"=== PHASE 3: VALIDATION - {territory} ===")
agentic_core\L0_routing\scripts\execute_ssot.py:1716:try:
agentic_core\L0_routing\scripts\execute_ssot.py:1717:logger.info("🔍 Detecting gravity violations (layer inversions)...")
agentic_core\L0_routing\scripts\execute_ssot.py:1750:logger.info(f"🔧 Gravity violations processed: {gravity_violations} found, {gravity_fixed} fixed")
agentic_core\L0_routing\scripts\execute_ssot.py:1753:logger.info("✅ No gravity violations detected")
agentic_core\L0_routing\scripts\execute_ssot.py:1756:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:1757:logger.error(f"Gravity violation detection failed: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:1802:logger.warning("Skipping healing: No governance report available.")
agentic_core\L0_routing\scripts\execute_ssot.py:1826:logger.info(f"=== PHASE 4: HEALING - {territory} ===")
agentic_core\L0_routing\scripts\execute_ssot.py:1829:logger.warning("No governance report - skipping healing")
agentic_core\L0_routing\scripts\execute_ssot.py:1836:logger.warning("No healing plan generated")
agentic_core\L0_routing\scripts\execute_ssot.py:1845:logger.info(f"Decision: {reason}")
agentic_core\L0_routing\scripts\execute_ssot.py:1869:logger.info(f"=== PHASE 5: CERTIFICATION - {territory} ===")
agentic_core\L0_routing\scripts\execute_ssot.py:2232:logger.info(f"📜 CERTIFICATE ISSUED: {territory}")
agentic_core\L0_routing\scripts\execute_ssot.py:2248:try:
agentic_core\L0_routing\scripts\execute_ssot.py:2273:logger.info("📁 Final compliance reports saved:")
agentic_core\L0_routing\scripts\execute_ssot.py:2274:logger.info(f"   JSON: {json_path.relative_to(project_root)}")
agentic_core\L0_routing\scripts\execute_ssot.py:2275:logger.info(f"   Markdown: {md_path.relative_to(project_root)}")
agentic_core\L0_routing\scripts\execute_ssot.py:2278:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:2279:logger.error(f"Failed to save comprehensive reports: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:2293:try:
agentic_core\L0_routing\scripts\execute_ssot.py:2299:logger.info("🧠 L3 ORCHESTRATOR SUMMONED (via subprocess): Delegating command.")
agentic_core\L0_routing\scripts\execute_ssot.py:2312:logger.warning("L3 Orchestrator not found. Falling back to L5 iteration.")
agentic_core\L0_routing\scripts\execute_ssot.py:2315:logger.error(f"L3 Orchestration failed: {result.get('error')}. Falling back.")
agentic_core\L0_routing\scripts\execute_ssot.py:2319:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:2320:logger.error(f"L3 Orchestration failed: {e}. Falling back to L5 iteration.")
agentic_core\L0_routing\scripts\execute_ssot.py:2491:raise ValueError(f"Unknown agent key(s): {sorted(unknown)}. Valid: {sorted(CANONICAL_ROSTER_KEYS)}")
agentic_core\L0_routing\scripts\execute_ssot.py:2550:try:
agentic_core\L0_routing\scripts\execute_ssot.py:2552:except SystemExit as exc:
agentic_core\L0_routing\scripts\execute_ssot.py:2651:try:
agentic_core\L0_routing\scripts\execute_ssot.py:2653:logger.info(f"Agent subset resolved: {requested_agent_keys}")
agentic_core\L0_routing\scripts\execute_ssot.py:2654:except ValueError as ve:
agentic_core\L0_routing\scripts\execute_ssot.py:2655:parser.error(str(ve))
agentic_core\L0_routing\scripts\execute_ssot.py:2667:logger.critical("🛑 PRE-FLIGHT CHECK FAILED:")
agentic_core\L0_routing\scripts\execute_ssot.py:2669:logger.error(f"  - {err}")
agentic_core\L0_routing\scripts\execute_ssot.py:2675:parser.error("Invalid territory name: only alphanumeric and underscores allowed.")
agentic_core\L0_routing\scripts\execute_ssot.py:2679:logger.info("DISCOVERABLE AGENTS:")
agentic_core\L0_routing\scripts\execute_ssot.py:2689:try:
agentic_core\L0_routing\scripts\execute_ssot.py:2700:logger.error(f"Baseline capture failed: {result.get('error')}")
agentic_core\L0_routing\scripts\execute_ssot.py:2703:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:2704:logger.error(f"Baseline capture failed: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:2709:logger.info(f"DIRECT AGENT EXECUTION: {args.agent}")
agentic_core\L0_routing\scripts\execute_ssot.py:2710:try:
agentic_core\L0_routing\scripts\execute_ssot.py:2713:logger.error(f"Agent {args.agent} not found.")
agentic_core\L0_routing\scripts\execute_ssot.py:2714:logger.info("Use --list-agents to see available agents")
agentic_core\L0_routing\scripts\execute_ssot.py:2718:logger.info(f"Found: {name} at {path}")
agentic_core\L0_routing\scripts\execute_ssot.py:2730:logger.error(f"Could not instantiate {name}")
agentic_core\L0_routing\scripts\execute_ssot.py:2733:logger.info(f"Running {name}...")
agentic_core\L0_routing\scripts\execute_ssot.py:2745:logger.info(f"Result: {result}")
agentic_core\L0_routing\scripts\execute_ssot.py:2748:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:2749:logger.error(f"Failed to run agent: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:2773:logger.info("🏛️ UNIFIED SOVEREIGN PROTOCOL STARTED")
agentic_core\L0_routing\scripts\execute_ssot.py:2774:logger.info(f"  Mode: {'AUTONOMOUS' if not args.manual else 'MANUAL'}")
agentic_core\L0_routing\scripts\execute_ssot.py:2775:logger.info(f"  LLM: {'ENABLED' if enable_llm else 'DISABLED'}")
agentic_core\L0_routing\scripts\execute_ssot.py:2776:logger.info(f"  CDA: {'ENABLED' if enable_cda else 'DISABLED'}")
agentic_core\L0_routing\scripts\execute_ssot.py:2777:logger.info(f"  HEALING: {'ACTIVE' if not dry_run else 'DRY-RUN'}")
agentic_core\L0_routing\scripts\execute_ssot.py:2778:logger.info(f"  APPROVAL: {'AUTO' if auto_approve else 'INTERACTIVE'}")
agentic_core\L0_routing\scripts\execute_ssot.py:2781:try:
agentic_core\L0_routing\scripts\execute_ssot.py:2789:logger.info("Total Awareness: Mandatory agent roster registered.")
agentic_core\L0_routing\scripts\execute_ssot.py:2790:logger.info(f"  Agents validated: {', '.join(roster_result.get('agents_validated', []))}")
agentic_core\L0_routing\scripts\execute_ssot.py:2794:logger.critical("🛑 SOVEREIGN CONTRACT BREACH - AGENT INTEGRITY FAILED:")
agentic_core\L0_routing\scripts\execute_ssot.py:2796:logger.error(f"  - {err}")
agentic_core\L0_routing\scripts\execute_ssot.py:2801:logger.critical(f"🛑 FATAL: Mandatory agent or dependency missing: {error_msg}")
agentic_core\L0_routing\scripts\execute_ssot.py:2805:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:2806:logger.critical(f"🛑 FATAL: Agent roster validation failed: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:2884:try:
agentic_core\L0_routing\scripts\execute_ssot.py:2891:logger.info(f"🔍 [PHASE 8] Running integrity check (Scope: {targets})...")
agentic_core\L0_routing\scripts\execute_ssot.py:2892:try:
agentic_core\L0_routing\scripts\execute_ssot.py:2908:logger.warning(
agentic_core\L0_routing\scripts\execute_ssot.py:2913:logger.error(
agentic_core\L0_routing\scripts\execute_ssot.py:2920:logger.warning("⚠️  Proceeding with caution (Heal mode active)...")
agentic_core\L0_routing\scripts\execute_ssot.py:2922:logger.warning(f"Integrity check failed: {result.get('error')}")
agentic_core\L0_routing\scripts\execute_ssot.py:2924:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:2925:logger.warning(f"Integrity check failed, continuing: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:2935:logger.info("🎉 L3 MISSION COMPLETED")
agentic_core\L0_routing\scripts\execute_ssot.py:2941:logger.info(f"\n{'=' * 60}")
agentic_core\L0_routing\scripts\execute_ssot.py:2942:logger.info(f"🚀 PROCESSING TERRITORY: {territory}")
agentic_core\L0_routing\scripts\execute_ssot.py:2943:logger.info(f"{'=' * 60}")
agentic_core\L0_routing\scripts\execute_ssot.py:2950:try:
agentic_core\L0_routing\scripts\execute_ssot.py:2980:logger.info(f"✅ Phase 2: {len(raw['modifications'])} fixes applied")
agentic_core\L0_routing\scripts\execute_ssot.py:2982:logger.warning(f"⚠️ Phase 2: {len(raw['failures'])} fixes failed")
agentic_core\L0_routing\scripts\execute_ssot.py:2994:logger.info("✅ Phase 3: All files pass validation")
agentic_core\L0_routing\scripts\execute_ssot.py:2997:logger.warning(f"⚠️ Phase 3: {remaining_count} issues detected")
agentic_core\L0_routing\scripts\execute_ssot.py:3029:logger.info(f"Sovereignty Decision: {pascal_reason}")
agentic_core\L0_routing\scripts\execute_ssot.py:3032:logger.info(f"🛡️ Triggering Sovereignty Purge: {territory}")
agentic_core\L0_routing\scripts\execute_ssot.py:3076:logger.info(f"=== PHASE 4.5: ADDITIONAL AGENTS - {territory} ===")
agentic_core\L0_routing\scripts\execute_ssot.py:3079:logger.info(f"🤖 Triggering Debate Synthesis: {territory}")
agentic_core\L0_routing\scripts\execute_ssot.py:3081:try:
agentic_core\L0_routing\scripts\execute_ssot.py:3104:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:3105:logger.warning(f"DebateSynthesisAgent failed: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:3109:try:
agentic_core\L0_routing\scripts\execute_ssot.py:3133:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:3134:logger.warning(f"RootHygieneAgent failed: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:3141:logger.error(f"Phase 1 failed for {territory} - skipping")
agentic_core\L0_routing\scripts\execute_ssot.py:3144:except RuntimeError as runtime_err:
agentic_core\L0_routing\scripts\execute_ssot.py:3147:logger.critical(f"🛑 BLOCKED INTERACTIVE PROMPT in {territory}: {runtime_err}")
agentic_core\L0_routing\scripts\execute_ssot.py:3150:raise runtime_err
agentic_core\L0_routing\scripts\execute_ssot.py:3152:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:3153:logger.error(f"❌ Protocol crashed on {territory}: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:3166:logger.info(f"\n{'=' * 60}")
agentic_core\L0_routing\scripts\execute_ssot.py:3167:logger.info("🎉 UNIFIED PROTOCOL COMPLETED")
agentic_core\L0_routing\scripts\execute_ssot.py:3168:logger.info(f"{'=' * 60}")
agentic_core\L0_routing\scripts\execute_ssot.py:3169:logger.info(f"Territories processed: {len(results)}/{len(targets)}")
agentic_core\L0_routing\scripts\execute_ssot.py:3170:logger.info(f"Decisions made: {len(decision_engine.decisions_made)}")
agentic_core\L0_routing\scripts\execute_ssot.py:3176:logger.info(f"  High confidence: {high_conf}, Medium: {med_conf}, Low: {low_conf}")
agentic_core\L0_routing\scripts\execute_ssot.py:3181:except Exception as fatal_e:
agentic_core\L0_routing\scripts\execute_ssot.py:3183:logger.critical(f"🔥 FATAL PROTOCOL ERROR: {fatal_e}")
agentic_core\L0_routing\scripts\execute_ssot.py:3206:logging.info("Starting dynamic agent discovery...")
agentic_core\L0_routing\scripts\execute_ssot.py:3227:try:
agentic_core\L0_routing\scripts\execute_ssot.py:3235:except Exception:
agentic_core\L0_routing\scripts\execute_ssot.py:3239:try:
agentic_core\L0_routing\scripts\execute_ssot.py:3262:try:
agentic_core\L0_routing\scripts\execute_ssot.py:3268:logging.debug(f"Loaded Standard Agent: {name}")
agentic_core\L0_routing\scripts\execute_ssot.py:3273:logging.debug(f"Loaded Duck-Typed Agent: {name}")
agentic_core\L0_routing\scripts\execute_ssot.py:3277:logging.info(f"Wrapping Legacy Agent: {name}")
agentic_core\L0_routing\scripts\execute_ssot.py:3281:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:3282:logging.warning(f"Failed to instantiate {name}: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:3285:except Exception as e:
agentic_core\L0_routing\scripts\execute_ssot.py:3286:logging.debug(f"Skipping module {file_path}: {e}")
agentic_core\L0_routing\scripts\execute_ssot.py:3288:logging.info(f"Discovery complete. Loaded {len(discovered_agents)} agents (including adapters).")
agentic_core\L0_routing\scripts\execute_ssot.py:3307:logging.critical("Force quitting on second signal...")
agentic_core\L0_routing\scripts\execute_ssot.py:3310:logging.warning("\n[!] Shutdown signal received. Finishing current agent operation...")
agentic_core\L0_routing\scripts\execute_ssot.py:3328:raise SystemExit(2)
agentic_core\L2_execution\tools\write_gateway.py:22:Logger: Any = logging.getLogger("L2.WriteGateway")
agentic_core\L2_execution\tools\write_gateway.py:69:try:
agentic_core\L2_execution\tools\write_gateway.py:72:except ValueError:
agentic_core\L2_execution\tools\write_gateway.py:79:raise RuntimeError(
agentic_core\L2_execution\tools\write_gateway.py:246:try:
agentic_core\L2_execution\tools\write_gateway.py:253:except BaseException:
agentic_core\L2_execution\tools\write_gateway.py:254:try:
agentic_core\L2_execution\tools\write_gateway.py:256:except OSError:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:22:logger = logging.getLogger(__name__)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:67:try:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:69:except Exception:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:75:try:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:77:raise SourceMutationBlocked(
agentic_core\L0_routing\enforcement\mutation_prohibition.py:81:except AttributeError:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:83:try:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:85:raise SourceMutationBlocked(
agentic_core\L0_routing\enforcement\mutation_prohibition.py:89:except ValueError:
agentic_core\L0_routing\enforcement\mutation_prohibition.py:135:logger.error("MUTATION_PROHIBITION DENY: %s", msg)
agentic_core\L0_routing\enforcement\mutation_prohibition.py:136:raise PermissionError(msg)
```

## Wave 2 — Block Event Emission

**Commit hash:** 2a588dbd6

**Files changed:**
- agentic_core/L0_routing/enforcement/mutation_prohibition.py
- tests/unit_min_deps/test_ssot_mutation_fence.py

## Wave 3 — Verification

### Unit Tests (SSOT Mutation Fence)
```
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 14 items

tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_agentic_core [32mPASSED[0m[32m [  7%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_allows_outside [32mPASSED[0m[32m [ 14%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_override_allows [32mPASSED[0m[32m [ 21%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_tests [32mPASSED[0m[32m [ 28%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_enforce_protected_root_blocks_github [32mPASSED[0m[32m [ 35%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_agentic_core [32mPASSED[0m[32m [ 42%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_tests [32mPASSED[0m[32m [ 50%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestProtectedRootEnforcement::test_exception_includes_matched_root_github [32mPASSED[0m[32m [ 57%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_blocks_protected_root [32mPASSED[0m[32m [ 64%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_gateway_allows_outside_protected_root [32mPASSED[0m[32m [ 71%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestWriteGatewayIntegration::test_write_bytes_blocks_protected_root [32mPASSED[0m[32m [ 78%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_block_emits_jsonl_event [32mPASSED[0m[32m [ 85%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_logging_failure_does_not_mask_exception [32mPASSED[0m[32m [ 92%][0m
tests/unit_min_deps/test_ssot_mutation_fence.py::TestBlockEventEmission::test_exception_message_still_includes_diagnostics [32mPASSED[0m[32m [100%][0m

============================ slowest 10 durations =============================

(10 durations < 0.005s hidden.  Use -vv to show these durations.)
[32m============================= [32m[1m14 passed[0m[32m in 0.04s[0m[32m ==============================[0m


```

### Full Pytest Suite
```
❌ agent_discovery_full.json not found
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
testpaths: C:\Git\Agentic-Workflow\tests\enforcement
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 4215 items / 46 errors
INTERNALERROR> Traceback (most recent call last):
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 318, in wrap_session
INTERNALERROR>     session.exitstatus = doit(config, session) or 0
INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 371, in _main
INTERNALERROR>     config.hook.pytest_collection(session=session)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
INTERNALERROR>     raise exception
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\logging.py", line 788, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\warnings.py", line 98, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\config\__init__.py", line 1403, in pytest_collection
INTERNALERROR>     return (yield)
INTERNALERROR>             ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 382, in pytest_collection
INTERNALERROR>     session.perform_collect()
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 857, in perform_collect
INTERNALERROR>     self.items.extend(self.genitems(node))
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1023, in genitems
INTERNALERROR>     yield from self.genitems(subnode)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 1020, in genitems
INTERNALERROR>     rep, duplicate = self._collect_one_node(node, handle_dupes)
INTERNALERROR>                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\main.py", line 883, in _collect_one_node
INTERNALERROR>     rep = collect_one_node(node)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 576, in collect_one_node
INTERNALERROR>     rep: CollectReport = ihook.pytest_make_collect_report(collector=collector)
INTERNALERROR>                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_hooks.py", line 512, in __call__
INTERNALERROR>     return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
INTERNALERROR>     return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 167, in _multicall
INTERNALERROR>     raise exception
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
INTERNALERROR>     teardown.throw(exception)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\capture.py", line 880, in pytest_make_collect_report
INTERNALERROR>     rep = yield
INTERNALERROR>           ^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\pluggy\_callers.py", line 121, in _multicall
INTERNALERROR>     res = hook_impl.function(*args)
INTERNALERROR>           ^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 400, in pytest_make_collect_report
INTERNALERROR>     call = CallInfo.from_call(
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 353, in from_call
INTERNALERROR>     result: TResult | None = func()
INTERNALERROR>                              ^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\runner.py", line 398, in collect
INTERNALERROR>     return list(collector.collect())
INTERNALERROR>                 ^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 563, in collect
INTERNALERROR>     self._register_setup_module_fixture()
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 576, in _register_setup_module_fixture
INTERNALERROR>     self.obj, ("setUpModule", "setup_module")
INTERNALERROR>     ^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 289, in obj
INTERNALERROR>     self._obj = obj = self._getobj()
INTERNALERROR>                       ^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 560, in _getobj
INTERNALERROR>     return importtestmodule(self.path, self.config)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\python.py", line 507, in importtestmodule
INTERNALERROR>     mod = import_path(
INTERNALERROR>           ^^^^^^^^^^^^
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\pathlib.py", line 587, in import_path
INTERNALERROR>     importlib.import_module(module_name)
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
INTERNALERROR>     return _bootstrap._gcd_import(name[level:], package, level)
INTERNALERROR>            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
INTERNALERROR>   File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
INTERNALERROR>   File "C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\site-packages\_pytest\assertion\rewrite.py", line 197, in exec_module
INTERNALERROR>     exec(co, module.__dict__)
INTERNALERROR>   File "c:\Git\Agentic-Workflow\tests\agentic_core\L5_safety\enforcement\test_data.py", line 9, in <module>
INTERNALERROR>     import agentic_core.L5_safety.enforcement.data_enforcer
INTERNALERROR>   File "C:\Git\Agentic-Workflow\agentic_core\L5_safety\enforcement\data.py", line 34, in <module>
INTERNALERROR>     sys.exit(1)
INTERNALERROR> SystemExit: 1

[31m======================= [33m3 warnings[0m, [31m[1m46 errors[0m[31m in 3.67s[0m[31m ========================[0m

mainloop: caught unexpected SystemExit!

```

### Repro Run Output
```
ARGV=['python', '-m', 'agentic_core.L0_routing.scripts.execute_ssot', '--domains', 'L0_routing,L2_execution,L3_orchestration,L5_safety']



STDERR:
ERROR: Direct invocation of execute_ssot.py is not supported.
Use the entrypoint instead:
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy


```

### Protected Root Mutation Proof
#### Before
```
 M agentic_core/L4_state/config/vllm_routing_predicates.py
?? agentic_core/L5_safety/utils/canonical_hash.py
?? agentic_core/L5_safety/utils/evidence/
?? agentic_core/L5_safety/utils/rag_reranker_shim.py
?? agentic_core/L5_safety/utils/vllm_boundary_client.py

```

#### After
```
 M agentic_core/L4_state/config/vllm_routing_predicates.py
?? agentic_core/L5_safety/utils/canonical_hash.py
?? agentic_core/L5_safety/utils/evidence/
?? agentic_core/L5_safety/utils/rag_reranker_shim.py
?? agentic_core/L5_safety/utils/vllm_boundary_client.py

```

## RCA Delta (<=10 lines)

**Event Emission Design:** Added ProtectedRootBlockEvent dataclass with 4 fields: ts_utc (ISO8601), target (normalized path), matched_root (name), caller (module:function). Events emitted only on block, never on allow path.

**Determinism:** JSONL format with sorted keys ensures stable, parseable output. Each block produces exactly one newline-terminated JSON line in logs/ssot_protected_root_blocks.jsonl.

**Non-Masking Behavior:** _emit_block_event wraps all logging in try/except with pass on failure. Logging failures never prevent SourceMutationBlocked from being raised. Tests verify this via monkeypatching open() to raise PermissionError.

**Safety:** No mutation authority added. Log destination (logs/) is outside IMMUTABLE_ROOTS. No new dependencies beyond stdlib (dataclasses, datetime, json).

## Follow-ons (out-of-scope)

1. Add log rotation policy for logs/ssot_protected_root_blocks.jsonl to prevent unbounded growth
2. Create dashboard aggregating block events by matched_root and target patterns
3. Add optional caller stack trace capture (configurable via env var) for deeper debugging
