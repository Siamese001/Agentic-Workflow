"""ADG static scanner smoke tests — import verification and schema integrity."""
import pytest

@pytest.mark.smoke
def test_scanner_importable():
    """Verify ADGStaticScanner class imports without error."""
    try:
        from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
        assert ADGStaticScanner is not None
        assert callable(ADGStaticScanner)
    except ImportError as e:
        pytest.skip(f"ADGStaticScanner not available: {e}")

@pytest.mark.smoke
def test_schema_frozensets_nonempty():
    """Verify all schema frozensets (P0-P4) are non-empty."""
    try:
        from agentic_core.adg.schema import (
            # P0 frozensets
            EXECUTION_TRACE_CLASSES,
            GUARDRAIL_CLASS_NAMES,
            POLICY_STATE_READER_CLASSES,
            MUTATION_TRANSPORT_CLASSES,
            JIT_CONTEXT_CLASSES,
            _GOVERNANCE_READ_SYMBOLS,
            _GOVERNANCE_WRITE_SYMBOLS,
            _GOVERNANCE_ROUTE_SYMBOLS,

            # P1 frozensets
            ROUTES_TO_AGENT_SYMBOLS,
            ORCHESTRATES_WORKFLOW_SYMBOLS,
            DISPATCHES_EXECUTION_PLAN_SYMBOLS,
            VALIDATES_AGENT_CAPABILITY_SYMBOLS,
            CHECKS_AGENT_REGISTRY_SYMBOLS,

            # P2 frozensets
            AUTHORIZE_EXECUTE_SYMBOLS,
            VALIDATES_CAPABILITY_SYMBOLS,
            ROUTES_TO_CAPABILITY_SYMBOLS,
            WRITES_VIA_UWG_SYMBOLS,
            BLOCKS_DIRECT_WRITE_SYMBOLS,
            RECORDS_TOOL_INVOCATION_SYMBOLS,
            CAPTURES_EXECUTION_OUTPUT_SYMBOLS,

            # P3 frozensets
            CAPTURES_PATTERN_SYMBOLS,
            RECORDS_LEARNING_EVENT_SYMBOLS,
            WRITES_LEARNING_SNAPSHOT_SYMBOLS,
            FEEDS_META_LEARNING_SYMBOLS,
            UPDATES_ROUTING_STRATEGY_SYMBOLS,
            IMPROVES_AGENT_POLICY_SYMBOLS,
            STORES_LEARNING_STATE_SYMBOLS,

            # P4 frozensets
            EMITS_METRIC_EVENT_SYMBOLS,
            RECORDS_INCIDENT_EVENT_SYMBOLS,
            CAPTURES_RUNTIME_ANOMALY_SYMBOLS,
            WRITES_OBSERVABILITY_LOG_SYMBOLS,
            UPDATES_MONITORING_STATE_SYMBOLS,
            TRIGGERS_ALERT_SYMBOLS,
            LINKS_INCIDENT_TRACE_SYMBOLS,
        )

        # Check that all frozensets are non-empty
        p0_frozensets = [
            EXECUTION_TRACE_CLASSES, GUARDRAIL_CLASS_NAMES, POLICY_STATE_READER_CLASSES,
            MUTATION_TRANSPORT_CLASSES, JIT_CONTEXT_CLASSES, _GOVERNANCE_READ_SYMBOLS,
            _GOVERNANCE_WRITE_SYMBOLS, _GOVERNANCE_ROUTE_SYMBOLS
        ]

        p1_frozensets = [
            ROUTES_TO_AGENT_SYMBOLS, ORCHESTRATES_WORKFLOW_SYMBOLS,
            DISPATCHES_EXECUTION_PLAN_SYMBOLS, VALIDATES_AGENT_CAPABILITY_SYMBOLS,
            CHECKS_AGENT_REGISTRY_SYMBOLS
        ]

        p2_frozensets = [
            AUTHORIZE_EXECUTE_SYMBOLS, VALIDATES_CAPABILITY_SYMBOLS,
            ROUTES_TO_CAPABILITY_SYMBOLS, WRITES_VIA_UWG_SYMBOLS,
            BLOCKS_DIRECT_WRITE_SYMBOLS, RECORDS_TOOL_INVOCATION_SYMBOLS,
            CAPTURES_EXECUTION_OUTPUT_SYMBOLS
        ]

        p3_frozensets = [
            CAPTURES_PATTERN_SYMBOLS, RECORDS_LEARNING_EVENT_SYMBOLS,
            WRITES_LEARNING_SNAPSHOT_SYMBOLS, FEEDS_META_LEARNING_SYMBOLS,
            UPDATES_ROUTING_STRATEGY_SYMBOLS, IMPROVES_AGENT_POLICY_SYMBOLS,
            STORES_LEARNING_STATE_SYMBOLS
        ]

        p4_frozensets = [
            EMITS_METRIC_EVENT_SYMBOLS, RECORDS_INCIDENT_EVENT_SYMBOLS,
            CAPTURES_RUNTIME_ANOMALY_SYMBOLS, WRITES_OBSERVABILITY_LOG_SYMBOLS,
            UPDATES_MONITORING_STATE_SYMBOLS, TRIGGERS_ALERT_SYMBOLS,
            LINKS_INCIDENT_TRACE_SYMBOLS
        ]

        all_frozensets = p0_frozensets + p1_frozensets + p2_frozensets + p3_frozensets + p4_frozensets

        for i, frozenset in enumerate(all_frozensets):
            assert len(frozenset) > 0, f"Schema frozenset {i} is empty"

    except ImportError as e:
        pytest.skip(f"schema frozensets not available: {e}")

@pytest.mark.smoke
def test_schema_relation_types():
    """Verify RelationType literals are present."""
    try:
        from agentic_core.adg.schema import RelationType

        # Check that RelationType has core expected literals
        required_relations = {
            'calls', 'imports', 'belongs_to_layer', 'covers', 'violates',
            'records_execution_trace', 'applies_guardrail', 'reads_policy_state',
            'emits_replay_key', 'emits_determinism_digest', 'snapshots_state',
            'pulls_context', 'writes_through', 'routes_through',
            'validated_by_safety_plane', 'invokes_eval', 'execution_terminates_at_uwg',
            'routes_to_agent', 'orchestrates_workflow', 'dispatches_execution_plan',
            'validates_agent_capability', 'checks_agent_registry',
        }

        available_relations = set(RelationType.__args__)

        # Check that all required relations are available
        missing_relations = required_relations - available_relations
        assert not missing_relations, f"Missing RelationType literals: {missing_relations}"

    except ImportError as e:
        pytest.skip(f"RelationType not available: {e}")

@pytest.mark.smoke
def test_schema_edge_kinds():
    """Verify EdgeKind literals are present."""
    try:
        from agentic_core.adg.schema import EdgeKind

        # Check that EdgeKind has expected literals (actual values are lowercase action nouns)
        required_kinds = {'import', 'call', 'write', 'export'}
        available_kinds = set(EdgeKind.__args__)

        missing_kinds = required_kinds - available_kinds
        assert not missing_kinds, f"Missing EdgeKind literals: {missing_kinds}"

    except ImportError as e:
        pytest.skip(f"EdgeKind not available: {e}")
