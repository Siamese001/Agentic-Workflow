"""Spine Wiring Verification for apps_lic Multi-Touch Infrastructure.

Wave 6, Phase 3 of apps-lic-infra-prerequisites-unblock-p2p3

This module provides spine initialization and wiring verification,
completing the infrastructure by ensuring all components are properly
connected.

App: apps_lic
Layer: Integration (apps_lic/)

Dependencies:
    - All W1-W5 infrastructure components
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime, timezone

# Wiring probes intentionally degrade to WiringStatus — narrow catches for ADG P2 hygiene.
_WIRING_VERIFY_EXCEPTIONS = (
    ImportError,
    ModuleNotFoundError,
    AttributeError,
    TypeError,
    ValueError,
    KeyError,
    RuntimeError,
    OSError,
    AssertionError,
)


# -----------------------------------------------------------------------------
# Wiring Status
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class WiringStatus:
    """Status of a wiring connection."""
    
    component: str
    connected: bool
    details: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass(frozen=True)
class SpineWiringReport:
    """Complete spine wiring verification report."""
    
    all_connected: bool
    components: list[WiringStatus]
    verified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def get_failures(self) -> list[WiringStatus]:
        """Get list of failed connections."""
        return [c for c in self.components if not c.connected]


# -----------------------------------------------------------------------------
# Wiring Verifier
# -----------------------------------------------------------------------------

class SpineWiringVerifier:
    """Verifier for apps_lic spine wiring.
    
    This class checks that all infrastructure components are properly
    wired together and ready for operation.
    """
    
    COMPONENTS = [
        "touch_state_schema",
        "touch_state_uwg",
        "coordination_fabric",
        "touch_scheduler",
        "hitl_policy",
        "hitl_evaluator",
        "fec_producer",
        "identity_service",
        "carry_forward_bridge",
        "p2_templates",  # W1.P3: P2 template activation
        "p2_rubric_dims",  # W1.P3: P2 rubric dimensions
        "sequence_definitions",  # W2.P1: 3-touch sequence definitions
        "touch_propagation",  # W2.P2: N→N+1 context propagation
        "sequence_state_machine",  # W2.P3: Sequence state machine
        "signal_types",  # W3.P1: Signal type definitions
        "signal_detector",  # W3.P1: Signal detection integration
        "trigger_wake_mapper",  # W3.P2: Trigger→wake mapping
        "research_bridge",  # W4.P1: apps_research → apps_lic flow
        "c0_retrieval_wiring",  # W4.P2: C0 retrieval → FEC producer
    ]
    
    def verify_all(self) -> SpineWiringReport:
        """Verify all spine wiring connections.
        
        Returns
        -------
        SpineWiringReport
            Complete wiring verification report
        """
        components = []
        
        for component in self.COMPONENTS:
            status = self._verify_component(component)
            components.append(status)
        
        all_connected = all(c.connected for c in components)
        
        return SpineWiringReport(
            all_connected=all_connected,
            components=components,
        )
    
    def _verify_component(self, component: str) -> WiringStatus:
        """Verify a single component connection."""
        verifiers = {
            "touch_state_schema": self._verify_touch_state_schema,
            "touch_state_uwg": self._verify_touch_state_uwg,
            "coordination_fabric": self._verify_coordination_fabric,
            "touch_scheduler": self._verify_touch_scheduler,
            "hitl_policy": self._verify_hitl_policy,
            "hitl_evaluator": self._verify_hitl_evaluator,
            "fec_producer": self._verify_fec_producer,
            "identity_service": self._verify_identity_service,
            "carry_forward_bridge": self._verify_carry_forward_bridge,
            "p2_templates": self._verify_p2_templates,
            "p2_rubric_dims": self._verify_p2_rubric_dims,
            "sequence_definitions": self._verify_sequence_definitions,
            "touch_propagation": self._verify_touch_propagation,
            "sequence_state_machine": self._verify_sequence_state_machine,
            "signal_types": self._verify_signal_types,
            "signal_detector": self._verify_signal_detector,
            "trigger_wake_mapper": self._verify_trigger_wake_mapper,
            "research_bridge": self._verify_research_bridge,
            "c0_retrieval_wiring": self._verify_c0_retrieval_wiring,
        }
        
        verifier = verifiers.get(component)
        if verifier:
            return verifier()
        
        return WiringStatus(
            component=component,
            connected=False,
            error="Unknown component",
        )
    
    def _verify_touch_state_schema(self) -> WiringStatus:
        """Verify touch state schema exists."""
        from pathlib import Path
        
        schema_path = Path("agentic_core/L4_state/schemas/apps_lic_touch_state.sql")
        
        if schema_path.exists():
            return WiringStatus(
                component="touch_state_schema",
                connected=True,
                details={"schema_path": str(schema_path)},
            )
        
        return WiringStatus(
            component="touch_state_schema",
            connected=False,
            error=f"Schema file not found: {schema_path}",
        )
    
    def _verify_touch_state_uwg(self) -> WiringStatus:
        """Verify touch state UWG adapter."""
        try:
            from agentic_core.L4_state.uwg.touch_state_writer import (
                TouchStateUWGAdapter,
                TOUCH_STATE_WRITE_CLASS,
            )
            
            return WiringStatus(
                component="touch_state_uwg",
                connected=True,
                details={
                    "write_class": TOUCH_STATE_WRITE_CLASS,
                    "adapter": TouchStateUWGAdapter.__name__,
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="touch_state_uwg",
                connected=False,
                error=str(e),
            )
    
    def _verify_coordination_fabric(self) -> WiringStatus:
        """Verify coordination fabric."""
        try:
            from agentic_core.cache.core.redis_coordination_fabric import get_fabric
            fabric = get_fabric()
            
            return WiringStatus(
                component="coordination_fabric",
                connected=True,
                details={"fabric": type(fabric).__name__},
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="coordination_fabric",
                connected=False,
                error=str(e),
            )
    
    def _verify_touch_scheduler(self) -> WiringStatus:
        """Verify touch scheduler."""
        try:
            from apps_lic.coordination.touch_scheduler import (
                get_touch_scheduler,
                DEFAULT_WAKE_QUEUE_KEY,
            )
            
            scheduler = get_touch_scheduler()
            
            return WiringStatus(
                component="touch_scheduler",
                connected=True,
                details={
                    "queue_key": DEFAULT_WAKE_QUEUE_KEY,
                    "scheduler": type(scheduler).__name__,
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="touch_scheduler",
                connected=False,
                error=str(e),
            )
    
    def _verify_hitl_policy(self) -> WiringStatus:
        """Verify HITL policy."""
        try:
            from agentic_core.L5_safety.policy.apps_lic_reengagement import (
                ReengagementHITLPolicy,
                HITLPolicyRegistry,
            )
            
            policy = HITLPolicyRegistry.get_or_default("apps_lic.reengagement")
            
            return WiringStatus(
                component="hitl_policy",
                connected=True,
                details={
                    "policy_id": policy.policy_id,
                    "version": policy.version,
                    "rules_count": len(policy.rules),
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="hitl_policy",
                connected=False,
                error=str(e),
            )
    
    def _verify_hitl_evaluator(self) -> WiringStatus:
        """Verify HITL evaluator."""
        try:
            from agentic_core.L5_safety.evaluators.apps_lic_reengagement import (
                ReengagementPolicyEvaluator,
            )
            
            evaluator = ReengagementPolicyEvaluator()
            
            return WiringStatus(
                component="hitl_evaluator",
                connected=True,
                details={"evaluator": type(evaluator).__name__},
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="hitl_evaluator",
                connected=False,
                error=str(e),
            )
    
    def _verify_fec_producer(self) -> WiringStatus:
        """Verify FEC producer."""
        try:
            from apps_lic.cert.fec_producer import (
                produce_fec,
                PRODUCER_ID,
                FEC_SCHEMA_VERSION,
            )
            
            return WiringStatus(
                component="fec_producer",
                connected=True,
                details={
                    "producer_id": PRODUCER_ID,
                    "schema_version": FEC_SCHEMA_VERSION,
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="fec_producer",
                connected=False,
                error=str(e),
            )
    
    def _verify_identity_service(self) -> WiringStatus:
        """Verify identity service."""
        try:
            from apps_lic.identity.propagation import (
                get_identity_propagation_service,
                IdentityPropagationService,
            )
            
            service = get_identity_propagation_service()
            
            return WiringStatus(
                component="identity_service",
                connected=True,
                details={"service": type(service).__name__},
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="identity_service",
                connected=False,
                error=str(e),
            )
    
    def _verify_carry_forward_bridge(self) -> WiringStatus:
        """Verify carry-forward bridge."""
        try:
            from apps_lic.identity.carry_forward import ContextCarryForwardBridge
            from apps_lic.identity.propagation import get_identity_propagation_service
            from agentic_core.L4_state.uwg.durable_write_gateway import get_gateway
            from agentic_core.L4_state.uwg.touch_state_writer import TouchStateUWGAdapter
            
            identity_service = get_identity_propagation_service()
            gateway = get_gateway()
            state_adapter = TouchStateUWGAdapter(gateway)
            
            bridge = ContextCarryForwardBridge(
                identity_service=identity_service,
                state_adapter=state_adapter,
            )
            
            return WiringStatus(
                component="carry_forward_bridge",
                connected=True,
                details={"bridge": type(bridge).__name__},
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="carry_forward_bridge",
                connected=False,
                error=str(e),
            )
    
    def _verify_p2_templates(self) -> WiringStatus:
        """Verify P2 templates with context slots."""
        from pathlib import Path
        
        templates_dir = Path("apps_lic/prompt_assembly/templates")
        required_templates = [
            "outreach_draft_v1.yaml",
            "outreach_draft_v2.yaml",
            "compact_recruiter_arc.yaml",
            "exec_positioning.yaml",
        ]
        
        found = []
        missing = []
        
        for template in required_templates:
            template_path = templates_dir / template
            if template_path.exists():
                # Check for P2 slots
                content = template_path.read_text()
                has_p2_slots = all(slot in content for slot in ["N0", "A0", "L0"])
                found.append((template, has_p2_slots))
            else:
                missing.append(template)
        
        if missing:
            return WiringStatus(
                component="p2_templates",
                connected=False,
                error=f"Missing templates: {missing}",
            )
        
        # Check if all have P2 slots
        without_p2 = [t for t, has_p2 in found if not has_p2]
        if without_p2:
            return WiringStatus(
                component="p2_templates",
                connected=False,
                error=f"Templates missing P2 slots: {without_p2}",
            )
        
        return WiringStatus(
            component="p2_templates",
            connected=True,
            details={
                "templates": [t for t, _ in found],
                "p2_slots": ["N0", "A0", "L0"],
            },
        )
    
    def _verify_p2_rubric_dims(self) -> WiringStatus:
        """Verify P2 rubric dimensions registered."""
        try:
            from apps_lic.config.domain_contract.eval_rubrics import get_eval_rubric
            
            rubric = get_eval_rubric("aer::apps_lic::outreach_message::v1")
            dim_ids = [d.dimension_id for d in rubric.score_dimensions]
            
            p2_dims = ["narrative_coherence", "tone_register_fit", "differentiator_grounded"]
            found_dims = [d for d in p2_dims if d in dim_ids]
            missing_dims = [d for d in p2_dims if d not in dim_ids]
            
            if missing_dims:
                return WiringStatus(
                    component="p2_rubric_dims",
                    connected=False,
                    error=f"Missing P2 dimensions: {missing_dims}",
                )
            
            return WiringStatus(
                component="p2_rubric_dims",
                connected=True,
                details={
                    "p2_dimensions": found_dims,
                    "total_dimensions": len(dim_ids),
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="p2_rubric_dims",
                connected=False,
                error=str(e),
            )
    
    def _verify_sequence_definitions(self) -> WiringStatus:
        """Verify W2.P1: 3-touch sequence definitions."""
        from pathlib import Path
        
        try:
            from apps_lic.sequences.touch_sequence_definitions import (
                SEQUENCE_REGISTRY,
                SequenceType,
                get_sequence_definition,
            )
            
            # Check all 3 sequence types are defined
            required_types = [
                SequenceType.STANDARD_3_TOUCH,
                SequenceType.EXECUTIVE_3_TOUCH,
                SequenceType.RECRUITER_COMPACT,
            ]
            
            found = []
            for seq_type in required_types:
                try:
                    seq_def = get_sequence_definition(seq_type)
                    found.append((seq_type.value, len(seq_def.touches)))
                except ValueError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
                    pass
            
            if len(found) != 3:
                missing = [t.value for t in required_types if t not in SEQUENCE_REGISTRY]
                return WiringStatus(
                    component="sequence_definitions",
                    connected=False,
                    error=f"Missing sequence types: {missing}",
                )
            
            return WiringStatus(
                component="sequence_definitions",
                connected=True,
                details={
                    "sequences": found,
                    "registry_size": len(SEQUENCE_REGISTRY),
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="sequence_definitions",
                connected=False,
                error=str(e),
            )
    
    def _verify_touch_propagation(self) -> WiringStatus:
        """Verify W2.P2: Touch N→N+1 propagation."""
        try:
            from apps_lic.sequences.touch_propagation import (
                TouchContextPropagator,
                TouchContext,
                create_touch_context_from_result,
            )
            from apps_lic.sequences.touch_sequence_definitions import SequenceType
            
            # Test propagation works
            propagator = TouchContextPropagator()
            
            # Create mock source context
            source = TouchContext(
                touch_id="test:touch:1",
                touch_number=1,
                sequence_type=SequenceType.STANDARD_3_TOUCH,
                campaign_id="test-campaign",
                recipient_hash="abc123",
                sent_at=None,
                message_body_hash="hash123",
                response_received=False,
                context_data={"hook_used": "test-hook"},
            )
            
            # Try propagation to touch 2
            result = propagator.propagate(source, 2)
            
            if not result.success:
                return WiringStatus(
                    component="touch_propagation",
                    connected=False,
                    error=f"Propagation test failed: {result.error}",
                )
            
            return WiringStatus(
                component="touch_propagation",
                connected=True,
                details={
                    "propagation_keys": list(result.propagated_context.keys()),
                    "p2_slots_bound": list(result.p2_slots_bound.keys()),
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="touch_propagation",
                connected=False,
                error=str(e),
            )
    
    def _verify_sequence_state_machine(self) -> WiringStatus:
        """Verify W2.P3: Sequence state machine."""
        try:
            from apps_lic.state.sequence_state_machine import (
                SequenceStateMachine,
                SequenceState,
                SequenceStateRecord,
                TouchState,
                TouchStatus,
            )
            from apps_lic.sequences.touch_sequence_definitions import SequenceType
            
            # Test state machine operations
            machine = SequenceStateMachine()
            
            # Create a test sequence
            record = machine.create_sequence(
                sequence_id="test-seq-001",
                campaign_id="test-campaign",
                recipient_hash="recipient123",
                sequence_type=SequenceType.STANDARD_3_TOUCH,
            )
            
            # Add a touch
            touch = machine.add_touch_state(record, "touch-001", 1)
            machine.update_touch_status(record, "touch-001", TouchStatus.SCHEDULED)
            
            # Test transition
            record = machine.transition(record, "touch_scheduled")
            
            if record.current_state != SequenceState.SCHEDULED:
                return WiringStatus(
                    component="sequence_state_machine",
                    connected=False,
                    error=f"State transition failed: expected SCHEDULED, got {record.current_state}",
                )
            
            return WiringStatus(
                component="sequence_state_machine",
                connected=True,
                details={
                    "initial_state": SequenceState.PENDING,
                    "transitions_working": True,
                    "active_sequences": len(machine.get_active_sequences()),
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="sequence_state_machine",
                connected=False,
                error=str(e),
            )
    
    def _verify_signal_types(self) -> WiringStatus:
        """Verify W3.P1: Signal type definitions."""
        try:
            from apps_lic.signals.types import (
                SignalType,
                SignalStrength,
                SignalSource,
                ResurfacingSignal,
                SignalDetectionResult,
                SIGNAL_PRIORITY,
            )
            
            # Verify all signal types exist
            signal_types = [
                SignalType.HIRING_SURGE,
                SignalType.EXEC_ROLE_OPEN,
                SignalType.FUNDING_ROUND,
                SignalType.COMPETITOR_LAUNCH,
                SignalType.PROFILE_VIEW,
            ]
            
            # Verify signal priority mapping
            priorities = [SIGNAL_PRIORITY.get(st) for st in signal_types]
            
            if None in priorities:
                missing = [st for st in signal_types if SIGNAL_PRIORITY.get(st) is None]
                return WiringStatus(
                    component="signal_types",
                    connected=False,
                    error=f"Missing signal priorities: {missing}",
                )
            
            # Test signal creation
            test_signal = ResurfacingSignal(
                signal_id="test-sig-001",
                signal_type=SignalType.FUNDING_ROUND,
                strength=SignalStrength.STRONG,
                source=SignalSource.CRUNCHBASE,
                detected_at=datetime.now(timezone.utc),
                company_id="test-company",
            )
            
            confidence = test_signal._strength_to_confidence()
            
            return WiringStatus(
                component="signal_types",
                connected=True,
                details={
                    "signal_types_count": len(SignalType),
                    "test_confidence": confidence,
                    "signal_sources": len(SignalSource),
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="signal_types",
                connected=False,
                error=str(e),
            )
    
    def _verify_signal_detector(self) -> WiringStatus:
        """Verify W3.P1: Signal detection integration."""
        try:
            from apps_lic.signals.detector import (
                SignalDetector,
                SignalDetectorConfig,
            )
            from apps_lic.signals.types import SignalSource
            
            # Create detector
            config = SignalDetectorConfig(
                enabled_sources=[SignalSource.RESEARCH, SignalSource.MANUAL],
            )
            detector = SignalDetector(config)
            
            # Test detection (should work even with RESURFACING_ENABLED off)
            result = detector.detect_signals(company_id="test-company")
            
            return WiringStatus(
                component="signal_detector",
                connected=True,
                details={
                    "config_loaded": True,
                    "sources_configured": len(config.enabled_sources),
                    "detection_result": "initialized" if result.error else "ready",
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="signal_detector",
                connected=False,
                error=str(e),
            )
    
    def _verify_trigger_wake_mapper(self) -> WiringStatus:
        """Verify W3.P2: Trigger→wake mapping."""
        try:
            from apps_lic.signals.trigger_wake_mapper import (
                TriggerWakeMapper,
                WakeMappingDecision,
            )
            from apps_lic.signals.types import (
                ResurfacingSignal,
                SignalType,
                SignalStrength,
                SignalSource,
            )
            from datetime import datetime, timezone
            
            # Create mapper
            mapper = TriggerWakeMapper()
            
            # Create test signal
            signal = ResurfacingSignal(
                signal_id="test-sig-001",
                signal_type=SignalType.FUNDING_ROUND,
                strength=SignalStrength.STRONG,
                source=SignalSource.CRUNCHBASE,
                detected_at=datetime.now(timezone.utc),
            )
            
            # Test mapping
            decision = mapper.map_signal_to_wake(
                signal=signal,
                touch_sequence=2,
            )
            
            if not decision.should_wake:
                return WiringStatus(
                    component="trigger_wake_mapper",
                    connected=False,
                    error="Signal should trigger wake but decision was negative",
                )
            
            return WiringStatus(
                component="trigger_wake_mapper",
                connected=True,
                details={
                    "mapping_works": True,
                    "priority": decision.priority,
                    "cadence_boost_hours": decision.cadence_boost_hours,
                    "confidence": decision.trigger_confidence,
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="trigger_wake_mapper",
                connected=False,
                error=str(e),
            )
    
    def _verify_research_bridge(self) -> WiringStatus:
        """Verify W4.P1: apps_research → apps_lic bridge."""
        try:
            from apps_lic.integrations.apps_research_bridge import (
                AppsResearchBridge,
                ResearchResult,
                EvidenceItem,
            )
            
            # Test bridge instantiation
            bridge = AppsResearchBridge(capability_ref="apps_research.v1")
            
            # Verify bridge has required methods
            assert hasattr(bridge, 'fetch')
            assert hasattr(bridge, '_invoke_apps_research')
            assert hasattr(bridge, '_translate')
            
            return WiringStatus(
                component="research_bridge",
                connected=True,
                details={
                    "bridge_instantiated": True,
                    "supported_capabilities": len(bridge.SUPPORTED_CAPABILITIES),
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="research_bridge",
                connected=False,
                error=str(e),
            )
    
    def _verify_c0_retrieval_wiring(self) -> WiringStatus:
        """Verify W4.P2: C0 retrieval → FEC producer wiring."""
        try:
            from apps_lic.cert.fec_producer import (
                produce_fec,
                PRODUCER_ID,
                FEC_SCHEMA_VERSION,
            )
            
            # Test FEC producer with mock C0 context
            test_context = {
                "research_snippets": [
                    {"source": "linkedin", "content": "Company raised Series B", "confidence": 0.9},
                ],
                "company_brief": {"funding_stage": "Series B"},
                "competitive_signals": [{"type": "hiring", "confidence": 0.85}],
            }
            
            fec = produce_fec(test_context)
            
            # Verify FEC structure
            assert fec["producer"] == PRODUCER_ID
            assert fec["_schema_version"] == FEC_SCHEMA_VERSION
            assert "retrieval_sources" in fec
            assert "grounded" in fec
            
            # Test with C0 retrieval populated (forward-compatible path)
            test_context_with_c0 = {
                **test_context,
                "c0_retrieval_sources": {
                    "retrieval_id": "c0-test-001",
                    "query": "Company funding news",
                    "results": [{"chunk": "test"}],
                    "confidence": 0.92,
                },
            }
            
            fec_with_c0 = produce_fec(test_context_with_c0)
            assert fec_with_c0["grounded"] is True
            assert fec_with_c0["evidence_sufficiency"] == "grounded"
            
            return WiringStatus(
                component="c0_retrieval_wiring",
                connected=True,
                details={
                    "fec_producer_id": PRODUCER_ID,
                    "schema_version": FEC_SCHEMA_VERSION,
                    "template_path_works": True,
                    "c0_path_works": True,
                },
            )
        except _WIRING_VERIFY_EXCEPTIONS as e:
            return WiringStatus(
                component="c0_retrieval_wiring",
                connected=False,
                error=str(e),
            )


# -----------------------------------------------------------------------------
# Spine Initialization
# -----------------------------------------------------------------------------

class SpineInitializer:
    """Initializer for apps_lic spine with full infrastructure."""
    
    @staticmethod
    def initialize_all() -> dict[str, Any]:
        """Initialize all spine components in order.
        
        Initialization order:
        1. Touch state registration (L4)
        2. Coordination-touch integration
        3. HITL policy registration
        4. FEC producer registration
        5. Identity integration
        
        Returns
        -------
        dict[str, Any]
            {
                "status": "success|partial|error",
                "results": dict,
                "report": SpineWiringReport,
            }
        """
        results = {}
        
        # Step 1: Touch state registration
        try:
            from apps_lic.state.touch_state_registration import initialize_touch_state
            results["touch_state"] = initialize_touch_state()
        except _WIRING_VERIFY_EXCEPTIONS as e:
            results["touch_state"] = f"error: {e}"
        
        # Step 2: Coordination-touch integration
        try:
            from apps_lic.coordination.touch_state_integration import (
                initialize_coordination_touch_integration,
            )
            results["coordination"] = initialize_coordination_touch_integration()
        except _WIRING_VERIFY_EXCEPTIONS as e:
            results["coordination"] = f"error: {e}"
        
        # Step 3: HITL policy
        try:
            from agentic_core.L5_safety.policy.apps_lic_reengagement import (
                ReengagementHITLPolicy,
                HITLPolicyRegistry,
            )
            policy = ReengagementHITLPolicy()
            HITLPolicyRegistry.register(policy)
            results["hitl_policy"] = True
        except _WIRING_VERIFY_EXCEPTIONS as e:
            results["hitl_policy"] = f"error: {e}"
        
        # Step 4: FEC producer (import triggers registration)
        try:
            import apps_lic.cert  # noqa: F401
            results["fec_producer"] = True
        except _WIRING_VERIFY_EXCEPTIONS as e:
            results["fec_producer"] = f"error: {e}"
        
        # Step 5: Identity integration
        try:
            from apps_lic.identity.integration import initialize_identity_integration
            results["identity"] = initialize_identity_integration()
        except _WIRING_VERIFY_EXCEPTIONS as e:
            results["identity"] = f"error: {e}"
        
        # Verify wiring
        verifier = SpineWiringVerifier()
        report = verifier.verify_all()
        
        # Determine overall status
        if report.all_connected:
            status = "success"
        elif any(results.values()):
            status = "partial"
        else:
            status = "error"
        
        return {
            "status": status,
            "results": results,
            "report": report,
        }


# -----------------------------------------------------------------------------
# CLI / Diagnostic
# -----------------------------------------------------------------------------

def print_wiring_report(report: SpineWiringReport) -> None:
    """Print wiring report in human-readable format."""
    print("=" * 60)
    print("apps_lic Spine Wiring Verification Report")
    print("=" * 60)
    print(f"Verified at: {report.verified_at}")
    print(f"Overall status: {'✅ ALL CONNECTED' if report.all_connected else '⚠️ PARTIAL/FAILURES'}")
    print()
    
    print("Component Status:")
    print("-" * 60)
    for component in report.components:
        symbol = "✅" if component.connected else "❌"
        print(f"  {symbol} {component.component}")
        
        if component.details:
            for key, value in component.details.items():
                print(f"      {key}: {value}")
        
        if component.error:
            print(f"      ERROR: {component.error}")
    
    print()
    
    failures = report.get_failures()
    if failures:
        print(f"⚠️  {len(failures)} component(s) need attention")
    else:
        print("✅ All components properly wired and ready")
    
    print("=" * 60)


def main() -> int:
    """CLI entrypoint for wiring verification."""
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="spine_wiring_verify",
        description="Verify apps_lic spine wiring",
    )
    parser.add_argument(
        "--initialize",
        action="store_true",
        help="Initialize all components before verifying",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    args = parser.parse_args()
    
    if args.initialize:
        result = SpineInitializer.initialize_all()
        report = result["report"]
    else:
        verifier = SpineWiringVerifier()
        report = verifier.verify_all()
    
    if args.json:
        import json
        print(json.dumps({
            "all_connected": report.all_connected,
            "verified_at": report.verified_at,
            "components": [
                {
                    "component": c.component,
                    "connected": c.connected,
                    "details": c.details,
                    "error": c.error,
                }
                for c in report.components
            ],
        }, indent=2))
    else:
        print_wiring_report(report)
    
    return 0 if report.all_connected else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
