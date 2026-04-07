#!/usr/bin/env python3
"""
Fix imports for L0 routing enforcement module - Version 4.
Only export classes that can be successfully imported.
"""

import pathlib


def test_import(module_name, class_name):
    """Test if a specific import works."""
    try:
        __import__(module_name, fromlist=[class_name])
        return True
    except Exception as e:
        print(f"  Cannot import {class_name} from {module_name}: {e}")
        return False

def fix_init_file_minimal(init_path):
    """Fix __init__.py with only working imports."""
    try:
        enforcement_dir = init_path.parent

        # Test imports for each module
        working_imports = []

        modules_to_test = [
            ('execution_gateway', ['ExecutionGatewayError', 'UnregisteredAgentError', 'GatewayResult', 'V15ExecutionGateway']),
            ('boundary_contracts', ['BoundarySchemaError', 'ContextRetrievalError', 'MetaInvariantError', 'SSOTBindingError']),
            ('crypto_trust_contracts', ['SigningError', 'VerificationError', 'ReplayDetectedError', 'EscalationRequiredError']),
            ('mutation_prohibition', ['SourceMutationBlocked', 'ProtectedRootBlockEvent']),
            ('routing_contract', ['UngovernnedRouteError', 'StaleRoutingContractError', 'RoutingContractValidationError']),
            ('traceability_contracts', ['TraceIDFormatError', 'ErrorSignatureError', 'PolicyConfigPinError']),
        ]

        for module_name, class_names in modules_to_test:
            print(f"Testing {module_name}:")
            for class_name in class_names:
                full_module = f"agentic_core.L0_routing.enforcement.{module_name}"
                if test_import(full_module, class_name):
                    working_imports.append(f"from .{module_name} import {class_name}")
                    print(f"  ✓ {class_name}")

        # Create minimal __init__.py content
        lines = [
            "from agentic_core.runtime.contracts.lifecycle_trace_contract import (",
            "    _emit_agent_executes_agent,",
            "    _emit_applies_guardrail,  # noqa: E402",
            "    _emit_authorize_and_execute,",
            "    _emit_blocks_direct_write,",
            "    _emit_captures_evaluation_metric,",
            "    _emit_captures_execution_output,",
            "    _emit_captures_pattern,",
            "    _emit_captures_runtime_anomaly,",
            "    _emit_checks_agent_registry,",
            "    _emit_coordinates_agents,",
            "    _emit_dispatches_agent,",
            "    _emit_dispatches_execution_plan,",
            "    _emit_dispatches_healing_run,  # noqa: E402",
            "    _emit_emits_metric_event,",
            "    _emit_escalates_failure,",
            "    _emit_escalates_to_human,  # noqa: E402",
            "    _emit_execution_terminates_at_uwg,",
            "    _emit_feeds_meta_learning,",
            "    _emit_gated_by_confidence,",
            "    _emit_hard_fails_untranscripted,",
            "    _emit_improves_agent_policy,",
            "    _emit_invokes_eval,",
            "    _emit_invokes_evaluation,",
            "    _emit_links_execution_to_snapshot,",
            "    _emit_links_incident_trace,",
            "    _emit_observes_runtime_state,",
            "    _emit_orchestrates_workflow,",
            "    _emit_proposal_commits_routing,",
            "    _emit_pulls_context,",
            "    _emit_reads_environ,",
            "    _emit_reads_policy_state,  # noqa: E402",
            "    _emit_reads_runtime_state,",
            "    _emit_records_execution_trace,  # noqa: E402",
            "    _emit_records_healing_outcome,",
            "    _emit_records_incident_event,",
            "    _emit_records_learning_event,",
            "    _emit_records_telemetry_event,",
            "    _emit_records_tool_invocation,",
            "    _emit_records_workflow_lineage,",
            "    _emit_routes_through,  # noqa: E402",
            "    _emit_routes_to_agent,",
            "    _emit_routes_to_capability,",
            "    _emit_signs_execution_trace,  # noqa: E402",
            "    _emit_snapshots_state,  # noqa: E402",
            "    _emit_stores_embedding,",
            "    _emit_stores_learning_state,",
            "    _emit_transcripts_response,",
            "    _emit_triggers_alert,",
            "    _emit_updates_meta_learning_state,",
            "    _emit_updates_monitoring_state,",
            "    _emit_updates_routing_strategy,",
            "    _emit_validated_by_safety_plane,",
            "    _emit_validates_agent_capability,",
            "    _emit_validates_capability,",
            "    _emit_verifies_boundary,",
            "    _emit_verifies_policy,",
            "    _emit_writes_learning_snapshot,",
            "    _emit_writes_observability_log,",
            "    _emit_writes_through,",
            "    _emit_writes_via_uwg,",
            "    emit_determinism_digest,  # noqa: E402",
            "    emit_replay_key,  # noqa: E402",
            ")",
            "",
        ]

        # Add only working imports
        lines.extend(working_imports)
        lines.append("")

        # Add minimal lifecycle trace calls
        lines.extend([
            "emit_replay_key(\"p0\", \"__init__\")",
            "emit_determinism_digest(\"p0\", \"__init__\")",
        ])

        # Write back
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"Created minimal {init_path} with {len(working_imports)} working imports")
        return True
    except Exception as e:
        print(f"Error fixing {init_path}: {e}")
        return False

def main():
    """Main function to fix L0 routing enforcement imports."""
    enforcement_dir = pathlib.Path('agentic_core/L0_routing/enforcement')
    init_path = enforcement_dir / '__init__.py'

    if not init_path.exists():
        print(f"__init__.py not found at {init_path}")
        return

    if fix_init_file_minimal(init_path):
        print("Successfully created minimal L0 routing enforcement __init__.py")
    else:
        print("Failed to fix __init__.py")

if __name__ == '__main__':
    main()
