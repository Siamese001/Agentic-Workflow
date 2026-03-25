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

