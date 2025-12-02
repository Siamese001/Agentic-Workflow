#!/usr/bin/env python3

import re

def fix_domain_tokens_text_based():
    """Fix domain tokens using safe text-based replacement"""
    
    print("=== SAFE TEXT-BASED DOMAIN TOKEN FIX ===")
    
    # Read the file as text
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Original file length: {len(content)} characters")
    
    # Domain token patterns to fix in filenames and keys
    replacements = [
        # Config domain
        ('load_config_planning.py', 'load_planning.py'),
        ('parse_config_settings.py', 'parse_settings.py'),
        ('extract_config_parameters.py', 'extract_parameters.py'),
        ('retrieve_config_context.py', 'retrieve_context.py'),
        ('query_config_store.py', 'query_store.py'),
        ('fetch_config_history.py', 'fetch_history.py'),
        ('inspect_config_state.py', 'inspect_state.py'),
        ('capture_config_diagnostics.py', 'capture_diagnostics.py'),
        ('log_config_inspection.py', 'log_inspection.py'),
        ('rank_config_components.py', 'rank_components.py'),
        ('apply_config_algorithm.py', 'apply_algorithm.py'),
        ('sort_config_results.py', 'sort_results.py'),
        ('validate_config_schema.py', 'validate_schema.py'),
        ('check_config_compliance.py', 'check_compliance.py'),
        ('enforce_config_contracts.py', 'enforce_contracts.py'),
        ('apply_config_safety.py', 'apply_safety.py'),
        ('enforce_config_policy.py', 'enforce_policy.py'),
        ('validate_config_ethics.py', 'validate_ethics.py'),
        ('prepare_config_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_config_state.py', 'serialize_state.py'),
        ('format_config_payload.py', 'format_payload.py'),
        ('prepare_config_payload.py', 'prepare_payload.py'),
        ('format_config_request.py', 'format_request.py'),
        ('serialize_config_params.py', 'serialize_params.py'),
        ('manage_config_costs.py', 'manage_costs.py'),
        
        # Data domain
        ('load_data_planning.py', 'load_planning.py'),
        ('parse_data_settings.py', 'parse_settings.py'),
        ('extract_data_parameters.py', 'extract_parameters.py'),
        ('retrieve_data_context.py', 'retrieve_context.py'),
        ('query_data_store.py', 'query_store.py'),
        ('fetch_data_history.py', 'fetch_history.py'),
        ('inspect_data_state.py', 'inspect_state.py'),
        ('capture_data_diagnostics.py', 'capture_diagnostics.py'),
        ('log_data_inspection.py', 'log_inspection.py'),
        ('rank_data_components.py', 'rank_components.py'),
        ('apply_data_algorithm.py', 'apply_algorithm.py'),
        ('sort_data_results.py', 'sort_results.py'),
        ('validate_data_schema.py', 'validate_schema.py'),
        ('check_data_compliance.py', 'check_compliance.py'),
        ('enforce_data_contracts.py', 'enforce_contracts.py'),
        ('apply_data_safety.py', 'apply_safety.py'),
        ('enforce_data_policy.py', 'enforce_policy.py'),
        ('validate_data_ethics.py', 'validate_ethics.py'),
        ('prepare_data_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_data_state.py', 'serialize_state.py'),
        ('format_data_payload.py', 'format_payload.py'),
        ('format_data_request.py', 'format_request.py'),
        ('serialize_data_params.py', 'serialize_params.py'),
        ('prepare_data_payload.py', 'prepare_payload.py'),
        ('manage_data_costs.py', 'manage_costs.py'),
        ('check_data_format', 'check_format'),
        
        # Observability domain
        ('load_observability_planning.py', 'load_planning.py'),
        ('parse_observability_settings.py', 'parse_settings.py'),
        ('extract_observability_parameters.py', 'extract_parameters.py'),
        ('retrieve_observability_context.py', 'retrieve_context.py'),
        ('query_observability_store.py', 'query_store.py'),
        ('fetch_observability_history.py', 'fetch_history.py'),
        ('inspect_observability_state.py', 'inspect_state.py'),
        ('capture_observability_diagnostics.py', 'capture_diagnostics.py'),
        ('log_observability_inspection.py', 'log_inspection.py'),
        ('rank_observability_components.py', 'rank_components.py'),
        ('apply_observability_algorithm.py', 'apply_algorithm.py'),
        ('sort_observability_results.py', 'sort_results.py'),
        ('validate_observability_schema.py', 'validate_schema.py'),
        ('check_observability_compliance.py', 'check_compliance.py'),
        ('enforce_observability_contracts.py', 'enforce_contracts.py'),
        ('apply_observability_safety.py', 'apply_safety.py'),
        ('enforce_observability_policy.py', 'enforce_policy.py'),
        ('validate_observability_ethics.py', 'validate_ethics.py'),
        ('prepare_observability_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_observability_state.py', 'serialize_state.py'),
        ('format_observability_payload.py', 'format_payload.py'),
        ('manage_observability_costs.py', 'manage_costs.py'),
        
        # Runtime domain
        ('load_runtime_planning.py', 'load_planning.py'),
        ('parse_runtime_settings.py', 'parse_settings.py'),
        ('extract_runtime_parameters.py', 'extract_parameters.py'),
        ('retrieve_runtime_context.py', 'retrieve_context.py'),
        ('query_runtime_store.py', 'query_store.py'),
        ('fetch_runtime_history.py', 'fetch_history.py'),
        ('inspect_runtime_state.py', 'inspect_state.py'),
        ('capture_runtime_diagnostics.py', 'capture_diagnostics.py'),
        ('log_runtime_inspection.py', 'log_inspection.py'),
        ('rank_runtime_components.py', 'rank_components.py'),
        ('apply_runtime_algorithm.py', 'apply_algorithm.py'),
        ('sort_runtime_results.py', 'sort_results.py'),
        ('validate_runtime_schema.py', 'validate_schema.py'),
        ('check_runtime_compliance.py', 'check_compliance.py'),
        ('enforce_runtime_contracts.py', 'enforce_contracts.py'),
        ('apply_runtime_safety.py', 'apply_safety.py'),
        ('enforce_runtime_policy.py', 'enforce_policy.py'),
        ('validate_runtime_ethics.py', 'validate_ethics.py'),
        ('prepare_runtime_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_runtime_state.py', 'serialize_state.py'),
        ('format_runtime_payload.py', 'format_payload.py'),
        ('format_runtime_request.py', 'format_request.py'),
        ('serialize_runtime_params.py', 'serialize_params.py'),
        ('manage_runtime_costs.py', 'manage_costs.py'),
        
        # Scripts domain
        ('load_scripts_planning.py', 'load_planning.py'),
        ('parse_scripts_settings.py', 'parse_settings.py'),
        ('extract_scripts_parameters.py', 'extract_parameters.py'),
        ('retrieve_scripts_context.py', 'retrieve_context.py'),
        ('query_scripts_store.py', 'query_store.py'),
        ('fetch_scripts_history.py', 'fetch_history.py'),
        ('inspect_scripts_state.py', 'inspect_state.py'),
        ('capture_scripts_diagnostics.py', 'capture_diagnostics.py'),
        ('log_scripts_inspection.py', 'log_inspection.py'),
        ('rank_scripts_components.py', 'rank_components.py'),
        ('apply_scripts_algorithm.py', 'apply_algorithm.py'),
        ('sort_scripts_results.py', 'sort_results.py'),
        ('validate_scripts_schema.py', 'validate_schema.py'),
        ('check_scripts_compliance.py', 'check_compliance.py'),
        ('enforce_scripts_contracts.py', 'enforce_contracts.py'),
        ('apply_scripts_safety.py', 'apply_safety.py'),
        ('enforce_scripts_policy.py', 'enforce_policy.py'),
        ('validate_scripts_ethics.py', 'validate_ethics.py'),
        ('prepare_scripts_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_scripts_state.py', 'serialize_state.py'),
        ('format_scripts_payload.py', 'format_payload.py'),
        ('format_scripts_request.py', 'format_request.py'),
        ('serialize_scripts_params.py', 'serialize_params.py'),
        ('manage_scripts_costs.py', 'manage_costs.py'),
        
        # Tests domain
        ('load_tests_planning.py', 'load_planning.py'),
        ('parse_tests_settings.py', 'parse_settings.py'),
        ('extract_tests_parameters.py', 'extract_parameters.py'),
        ('retrieve_tests_context.py', 'retrieve_context.py'),
        ('query_tests_store.py', 'query_store.py'),
        ('fetch_tests_history.py', 'fetch_history.py'),
        ('inspect_tests_state.py', 'inspect_state.py'),
        ('capture_tests_diagnostics.py', 'capture_diagnostics.py'),
        ('log_tests_inspection.py', 'log_inspection.py'),
        ('rank_tests_components.py', 'rank_components.py'),
        ('apply_tests_algorithm.py', 'apply_algorithm.py'),
        ('sort_tests_results.py', 'sort_results.py'),
        ('validate_tests_schema.py', 'validate_schema.py'),
        ('check_tests_compliance.py', 'check_compliance.py'),
        ('enforce_tests_contracts.py', 'enforce_contracts.py'),
        ('apply_tests_safety.py', 'apply_safety.py'),
        ('enforce_tests_policy.py', 'enforce_policy.py'),
        ('validate_tests_ethics.py', 'validate_ethics.py'),
        ('prepare_tests_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_tests_state.py', 'serialize_state.py'),
        ('format_tests_payload.py', 'format_payload.py'),
        ('format_tests_request.py', 'format_request.py'),
        ('serialize_tests_params.py', 'serialize_params.py'),
        ('manage_tests_costs.py', 'manage_costs.py'),
        
        # Apps domain specific
        ('format_job_metadata.py', 'format_metadata.py'),
        ('format_recipient_metadata.py', 'format_metadata.py'),
        ('format_interaction_data.py', 'format_data.py'),
        ('format_state_data.py', 'format_data.py'),
        ('serialize_resume_data.py', 'serialize_data.py'),
        ('serialize_outreach_data.py', 'serialize_data.py'),
        ('format_universal_data.py', 'format_data.py'),
        ('format_common_metadata.py', 'format_metadata.py'),
        ('check_data_format', 'check_format'),
        ('get_resume_info', 'get_info'),
        ('get_recipient_info', 'get_info'),
        ('update_resume_state', 'update_state'),
        ('update_outreach_state', 'update_state'),
        ('use_resume_tools', 'use_tools'),
        ('use_message_tools', 'use_tools'),
    ]
    
    # Apply replacements
    changes_made = 0
    for old, new in replacements:
        if old in content:
            count = content.count(old)
            content = content.replace(old, new)
            changes_made += count
            print(f"  Replaced {count} occurrences: {old} → {new}")
    
    print(f"\nTotal changes made: {changes_made}")
    
    # Write back the fixed content
    with open('unified_structure_subatomic.yaml', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed file length: {len(content)} characters")
    print("✅ Safe domain token fix completed")

if __name__ == '__main__':
    fix_domain_tokens_text_based()
