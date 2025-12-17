#!/usr/bin/env python
"""
Strip BOM and fix leading whitespace issues in test files.
"""

import os
from pathlib import Path

def fix_file(file_path: Path):
    """Fix BOM and leading whitespace in a file"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        # Remove BOM if present
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]

        # Convert to string and fix leading whitespace
        text = content.decode('utf-8')
        lines = text.split('\n')

        # Fix first line if it has unexpected indent
        if lines:
            first_line = lines[0]
            if first_line.strip() and (first_line.startswith(' ') or first_line.startswith('\t')):
                # Remove leading spaces/tabs from first line
                lines[0] = first_line.lstrip()

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return True
    except Exception as e:
pass
# print(f"Error fixing {file_path}: {e}")  # [Security Fix]
        return False

# Fix all remaining failed files
failed_files = [
    "tests/test_agentic_behaviors.py",
    "tests/test_agentic_canon.py",
    "tests/test_canon_validator_governance.py",
    "tests/test_canon_validator_integration.py",
    "tests/test_canon_validator_security.py",
    "tests/test_edge_cases_hardened.py",
    "tests/test_input_sanitizer.py",
    "tests/test_l5_integration.py",
    "tests/test_lead_agent.py",
    "tests/test_mcp_e2e.py",
    "tests/test_mcp_installation.py",
    "tests/test_mcp_without_reddit.py",
    "tests/test_precision_layer.py",
    "tests/test_prompt_injection_loader.py",
    "tests/test_reasoning_layer.py",
    "tests/test_reflection_engine.py",
    "tests/test_sdks.py",
    "tests/test_sequential_thinking.py",
    "tests/test_sota_layer.py",
    "tests/test_subatomic_hop.py",
    "tests/test_tavily_integration.py",
    "tests/test_titanium_integration.py",
    "tests/test_titanium_pipeline.py",
    "tests/test_uber_signal_agents.py",
    "tests/test_whitelist_bypass.py",
    "tests/test_whitelist_debug.py",
    "tests/test_zlm.py",
    "tests/test_outreach_zse.py",
    "tests/master_integration_suite_fixed.py",
    "tests/integration/test_end_to_end_workflow.py",
    "tests/integration/test_hardened_orchestrator_comprehensive.py",
    "tests/integration/test_hardened_orchestrator_simple.py",
    "tests/integration/test_kx_nodes.py",
    "tests/integration/test_mcp_agent_integration.py",
    "tests/integration/test_resume_logic.py",
    "tests/unit/test_hardening_infrastructure.py",
    "tests/unit/test_l2_neo4j_integration.py",
    "tests/unit/test_thermostatic_passport.py",
    "tests/unit/test_validation_chain.py",
    "tests/unit/agentic_core/test_fallback_paths.py",
    "tests/unit/apps_lic/test_lic_outreach_dag.py",
    "tests/unit/apps_rg/test_resume_integrity.py",
    "tests/unit/apps_rg/test_resume_integrity_simple.py",
    "tests/unit/apps_rg/test_resume_logic_mock.py",
    "tests/unit/apps_shared/test_rag_logic.py",
    "tests/unit/apps_shared/test_sdk_registry.py",
    "tests/unit/config/test_config.py",
    "tests/unit/engine/test_embedding_ops.py",
    "tests/unit/engine/test_tool_ops.py",
    "tests/unit/observability/test_observability.py",
    "tests/unit/prompt_governance/test_constitutional_logic.py",
    "tests/unit/prompt_governance/test_prompt_governance.py",
    "tests/unit/runtime/test_cache.py",
    "tests/unit/runtime/test_cache_regression.py",
    "tests/unit/runtime/test_dynamic_dag.py",
    "tests/unit/runtime/test_instructional_injections.py",
    "tests/unit/runtime/test_mcp_tools.py",
    "tests/unit/runtime/test_multi_provider_clients.py",
    "tests/unit/runtime/test_node_negotiation.py",
    "tests/unit/schemas/test_memory_schema_validation.py",
    "tests/unit/schemas/test_models.py",
    "tests/unit/schemas/test_planning_schema_validation.py",
    "tests/unit/scripts/test_scripts.py",
    "tests/unit/shared/test_pipeline_ops.py",
    "tests/unit/shared/test_security_controls.py",
    "tests/perf/throughput/test_cache_throughput.py",
    "tests/load/soak/test_soak.py",
    "tests/integration/api/test_api_integration.py",
    "tests/integration/api/test_provider_routing.py",
    "tests/integration/core_plus_runtime/test_core_runtime_integration.py",
    "tests/integration/core_plus_runtime/test_rag_pipeline_integration.py",
    "tests/integration/cross_domain/test_cross_domain_integration.py",
    "tests/integration/cross_domain/test_schema_compatibility.py",
    "tests/integration/full_pipeline/test_e2e_safety.py",
    "tests/integration/full_pipeline/test_full_pipeline_integration.py",
    "tests/integration/lic_plus_data/test_lic_data_integration.py",
    "tests/integration/lic_plus_data/test_lic_research_integration.py",
    "tests/integration/rg_plus_data/test_rg_data_integration.py",
    "tests/integration/workflow/test_full_agentic_loop.py",
    "tests/integration/workflow/test_workflow_state_integration.py",
    "tests/golden/safety/test_llm_guardrails.py",
    "tests/golden/safety/test_safety_properties.py",
    "tests/e2e/admin_flows/test_admin_system_management.py",
    "tests/e2e/outreach_flows/test_outreach_campaign_lifecycle.py",
    "tests/e2e/outreach_flows/test_outreach_flows.py",
    "tests/e2e/outreach_flows/test_outreach_research_e2e.py",
    "tests/e2e/resume_flows/test_resume_flows.py",
    "tests/e2e/resume_flows/test_resume_generation_lifecycle.py",
    "tests/apps_cv/adversarial_hardening/test_cv_a003.py",
    "tests/apps_cv/adversarial_hardening/test_cv_a004.py",
    "tests/apps_cv/adversarial_hardening/test_cv_a005.py",
    "tests/apps_cv/emergency_protocol/test_ebp_001.py",
    "tests/apps_cv/emergency_protocol/test_ebp_002.py",
    "tests/apps_cv/emergency_protocol/test_ebp_003.py",
    "tests/apps_cv/integration_logic/test_cv_i001.py",
    "tests/apps_cv/integration_logic/test_cv_i003.py",
    "tests/apps_cv/integration_logic/test_cv_i004.py",
    "tests/apps_cv/unit_mocks/test_cv_u002.py",
    "tests/debug_resume_test.py",
    "tests/simple_test.py"
]

# print("🔧 Stripping BOM and fixing leading whitespace...")  # [Security Fix]
fixed = 0
for file_path in failed_files:
    path = Path(file_path)
    if path.exists():
        if fix_file(path):
            fixed += 1
            # print(f"✅ Fixed: {file_path}")  # [Security Fix]
        else:
            # print(f"❌ Failed: {file_path}")  # [Security Fix]

# print(f"\n✅ Fixed {fixed} files")  # [Security Fix]

