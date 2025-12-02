#!/usr/bin/env python3

def fix_domain_tokens_filenames():
    """Fix remaining domain tokens in filenames"""
    
    print("=== FIXING DOMAIN TOKENS IN FILENAMES ===")
    
    # Read the file as text
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Domain token patterns in filenames that need to be fixed
    filename_replacements = [
        # Config domain filenames
        ('execute_config_action.py', 'execute_action.py'),
        ('invoke_config_service.py', 'invoke_service.py'),
        ('process_config_response.py', 'process_response.py'),
        ('aggregate_config_state.py', 'aggregate_state.py'),
        ('merge_config_contexts.py', 'merge_contexts.py'),
        ('consolidate_config_updates.py', 'consolidate_updates.py'),
        ('prepare_config_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_config_state.py', 'serialize_state.py'),
        ('format_config_payload.py', 'format_payload.py'),
        ('validate_config_schema.py', 'validate_schema.py'),
        ('check_config_compliance.py', 'check_compliance.py'),
        ('enforce_config_contracts.py', 'enforce_contracts.py'),
        ('apply_config_safety.py', 'apply_safety.py'),
        ('enforce_config_policy.py', 'enforce_policy.py'),
        ('validate_config_ethics.py', 'validate_ethics.py'),
        ('prepare_config_payload.py', 'prepare_payload.py'),
        ('format_config_request.py', 'format_request.py'),
        ('serialize_config_params.py', 'serialize_params.py'),
        
        # Data domain filenames
        ('execute_data_action.py', 'execute_action.py'),
        ('invoke_data_service.py', 'invoke_service.py'),
        ('process_data_response.py', 'process_response.py'),
        ('aggregate_data_state.py', 'aggregate_state.py'),
        ('merge_data_contexts.py', 'merge_contexts.py'),
        ('consolidate_data_updates.py', 'consolidate_updates.py'),
        ('prepare_data_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_data_state.py', 'serialize_state.py'),
        ('format_data_payload.py', 'format_payload.py'),
        ('validate_data_schema.py', 'validate_schema.py'),
        ('check_data_compliance.py', 'check_compliance.py'),
        ('enforce_data_contracts.py', 'enforce_contracts.py'),
        ('apply_data_safety.py', 'apply_safety.py'),
        ('enforce_data_policy.py', 'enforce_policy.py'),
        ('validate_data_ethics.py', 'validate_ethics.py'),
        ('prepare_data_payload.py', 'prepare_payload.py'),
        ('format_data_request.py', 'format_request.py'),
        ('serialize_data_params.py', 'serialize_params.py'),
        
        # Observability domain filenames
        ('execute_observability_action.py', 'execute_action.py'),
        ('invoke_observability_service.py', 'invoke_service.py'),
        ('process_observability_response.py', 'process_response.py'),
        ('aggregate_observability_state.py', 'aggregate_state.py'),
        ('merge_observability_contexts.py', 'merge_contexts.py'),
        ('consolidate_observability_updates.py', 'consolidate_updates.py'),
        ('prepare_observability_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_observability_state.py', 'serialize_state.py'),
        ('format_observability_payload.py', 'format_payload.py'),
        ('validate_observability_schema.py', 'validate_schema.py'),
        ('check_observability_compliance.py', 'check_compliance.py'),
        ('enforce_observability_contracts.py', 'enforce_contracts.py'),
        ('apply_observability_safety.py', 'apply_safety.py'),
        ('enforce_observability_policy.py', 'enforce_policy.py'),
        ('validate_observability_ethics.py', 'validate_ethics.py'),
        ('prepare_observability_payload.py', 'prepare_payload.py'),
        ('format_observability_request.py', 'format_request.py'),
        ('serialize_observability_params.py', 'serialize_params.py'),
        
        # Runtime domain filenames
        ('execute_runtime_action.py', 'execute_action.py'),
        ('invoke_runtime_service.py', 'invoke_service.py'),
        ('process_runtime_response.py', 'process_response.py'),
        ('aggregate_runtime_state.py', 'aggregate_state.py'),
        ('merge_runtime_contexts.py', 'merge_contexts.py'),
        ('consolidate_runtime_updates.py', 'consolidate_updates.py'),
        ('prepare_runtime_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_runtime_state.py', 'serialize_state.py'),
        ('format_runtime_payload.py', 'format_payload.py'),
        ('validate_runtime_schema.py', 'validate_schema.py'),
        ('check_runtime_compliance.py', 'check_compliance.py'),
        ('enforce_runtime_contracts.py', 'enforce_contracts.py'),
        ('apply_runtime_safety.py', 'apply_safety.py'),
        ('enforce_runtime_policy.py', 'enforce_policy.py'),
        ('validate_runtime_ethics.py', 'validate_ethics.py'),
        ('prepare_runtime_payload.py', 'prepare_payload.py'),
        ('format_runtime_request.py', 'format_request.py'),
        ('serialize_runtime_params.py', 'serialize_params.py'),
        
        # Scripts domain filenames
        ('execute_scripts_action.py', 'execute_action.py'),
        ('invoke_scripts_service.py', 'invoke_service.py'),
        ('process_scripts_response.py', 'process_response.py'),
        ('aggregate_scripts_state.py', 'aggregate_state.py'),
        ('merge_scripts_contexts.py', 'merge_contexts.py'),
        ('consolidate_scripts_updates.py', 'consolidate_updates.py'),
        ('prepare_scripts_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_scripts_state.py', 'serialize_state.py'),
        ('format_scripts_payload.py', 'format_payload.py'),
        ('validate_scripts_schema.py', 'validate_schema.py'),
        ('check_scripts_compliance.py', 'check_compliance.py'),
        ('enforce_scripts_contracts.py', 'enforce_contracts.py'),
        ('apply_scripts_safety.py', 'apply_safety.py'),
        ('enforce_scripts_policy.py', 'enforce_policy.py'),
        ('validate_scripts_ethics.py', 'validate_ethics.py'),
        ('prepare_scripts_payload.py', 'prepare_payload.py'),
        ('format_scripts_request.py', 'format_request.py'),
        ('serialize_scripts_params.py', 'serialize_params.py'),
        
        # Tests domain filenames
        ('execute_tests_action.py', 'execute_action.py'),
        ('invoke_tests_service.py', 'invoke_service.py'),
        ('process_tests_response.py', 'process_response.py'),
        ('aggregate_tests_state.py', 'aggregate_state.py'),
        ('merge_tests_contexts.py', 'merge_contexts.py'),
        ('consolidate_tests_updates.py', 'consolidate_updates.py'),
        ('prepare_tests_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_tests_state.py', 'serialize_state.py'),
        ('format_tests_payload.py', 'format_payload.py'),
        ('validate_tests_schema.py', 'validate_schema.py'),
        ('check_tests_compliance.py', 'check_compliance.py'),
        ('enforce_tests_contracts.py', 'enforce_contracts.py'),
        ('apply_tests_safety.py', 'apply_safety.py'),
        ('enforce_tests_policy.py', 'enforce_policy.py'),
        ('validate_tests_ethics.py', 'validate_ethics.py'),
        ('prepare_tests_payload.py', 'prepare_payload.py'),
        ('format_tests_request.py', 'format_request.py'),
        ('serialize_tests_params.py', 'serialize_params.py'),
        
        # Schema domain filenames
        ('execute_schema_action.py', 'execute_action.py'),
        ('invoke_schema_service.py', 'invoke_service.py'),
        ('process_schema_response.py', 'process_response.py'),
        ('aggregate_schema_state.py', 'aggregate_state.py'),
        ('merge_schema_contexts.py', 'merge_contexts.py'),
        ('consolidate_schema_updates.py', 'consolidate_updates.py'),
        ('prepare_schema_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_schema_state.py', 'serialize_state.py'),
        ('format_schema_payload.py', 'format_payload.py'),
        ('validate_schema_schema.py', 'validate_schema.py'),
        ('check_schema_compliance.py', 'check_compliance.py'),
        ('enforce_schema_contracts.py', 'enforce_contracts.py'),
        ('apply_schema_safety.py', 'apply_safety.py'),
        ('enforce_schema_policy.py', 'enforce_policy.py'),
        ('validate_schema_ethics.py', 'validate_ethics.py'),
        ('prepare_schema_payload.py', 'prepare_payload.py'),
        ('format_schema_request.py', 'format_request.py'),
        ('serialize_schema_params.py', 'serialize_params.py'),
        
        # Prompt governance domain filenames
        ('execute_prompt_action.py', 'execute_action.py'),
        ('invoke_prompt_service.py', 'invoke_service.py'),
        ('process_prompt_response.py', 'process_response.py'),
        ('aggregate_prompt_state.py', 'aggregate_state.py'),
        ('merge_prompt_contexts.py', 'merge_contexts.py'),
        ('consolidate_prompt_updates.py', 'consolidate_updates.py'),
        ('prepare_prompt_snapshot.py', 'prepare_snapshot.py'),
        ('serialize_prompt_state.py', 'serialize_state.py'),
        ('format_prompt_payload.py', 'format_payload.py'),
        ('validate_prompt_schema.py', 'validate_schema.py'),
        ('check_prompt_compliance.py', 'check_compliance.py'),
        ('enforce_prompt_contracts.py', 'enforce_contracts.py'),
        ('apply_prompt_safety.py', 'apply_safety.py'),
        ('enforce_prompt_policy.py', 'enforce_policy.py'),
        ('validate_prompt_ethics.py', 'validate_ethics.py'),
        ('prepare_prompt_payload.py', 'prepare_payload.py'),
        ('format_prompt_request.py', 'format_request.py'),
        ('serialize_prompt_params.py', 'serialize_params.py'),
    ]
    
    # Apply replacements
    changes_made = 0
    for old, new in filename_replacements:
        if old in content:
            count = content.count(old)
            content = content.replace(old, new)
            changes_made += count
            if count > 0:
                print(f"  Replaced {count}: {old} → {new}")
    
    print(f"\nTotal filename changes: {changes_made}")
    
    # Write back
    with open('unified_structure_subatomic.yaml', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Domain token filename fixes completed")

if __name__ == '__main__':
    fix_domain_tokens_filenames()
