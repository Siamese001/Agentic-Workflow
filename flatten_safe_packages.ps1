# Flatten single-file packages (safe ones only)
$errorActionPreference = "Stop"

if (Test-Path "apps_shared\api\__init__.py") {
    Write-Host "Flattening apps_shared\api"
    git mv "apps_shared\api/__init__.py" "apps_shared\api.py"
    Remove-Item "apps_shared\api" -Force
}

if (Test-Path "apps_shared\safety\__init__.py") {
    Write-Host "Flattening apps_shared\safety"
    git mv "apps_shared\safety/__init__.py" "apps_shared\safety.py"
    Remove-Item "apps_shared\safety" -Force
}

if (Test-Path "apps_shared\shared_utilities\__init__.py") {
    Write-Host "Flattening apps_shared\shared_utilities"
    git mv "apps_shared\shared_utilities/__init__.py" "apps_shared\shared_utilities.py"
    Remove-Item "apps_shared\shared_utilities" -Force
}

if (Test-Path "runtime\validation\__init__.py") {
    Write-Host "Flattening runtime\validation"
    git mv "runtime\validation/__init__.py" "runtime\validation.py"
    Remove-Item "runtime\validation" -Force
}

if (Test-Path "scripts\runtime\guardrails\__init__.py") {
    Write-Host "Flattening scripts\runtime\guardrails"
    git mv "scripts\runtime\guardrails/__init__.py" "scripts\runtime\guardrails.py"
    Remove-Item "scripts\runtime\guardrails" -Force
}

if (Test-Path "scripts\runtime\validation\__init__.py") {
    Write-Host "Flattening scripts\runtime\validation"
    git mv "scripts\runtime\validation/__init__.py" "scripts\runtime\validation.py"
    Remove-Item "scripts\runtime\validation" -Force
}

if (Test-Path "scripts\security\guardrails\check_rules\__init__.py") {
    Write-Host "Flattening scripts\security\guardrails\check_rules"
    git mv "scripts\security\guardrails\check_rules/__init__.py" "scripts\security\guardrails\check_rules.py"
    Remove-Item "scripts\security\guardrails\check_rules" -Force
}

if (Test-Path "scripts\runtime\synthesis\use_tools\__init__.py") {
    Write-Host "Flattening scripts\runtime\synthesis\use_tools"
    git mv "scripts\runtime\synthesis\use_tools/__init__.py" "scripts\runtime\synthesis\use_tools.py"
    Remove-Item "scripts\runtime\synthesis\use_tools" -Force
}

if (Test-Path "scripts\pipeline\data_access\get_info\__init__.py") {
    Write-Host "Flattening scripts\pipeline\data_access\get_info"
    git mv "scripts\pipeline\data_access\get_info/__init__.py" "scripts\pipeline\data_access\get_info.py"
    Remove-Item "scripts\pipeline\data_access\get_info" -Force
}

if (Test-Path "scripts\pipeline\guardrails\check_rules\__init__.py") {
    Write-Host "Flattening scripts\pipeline\guardrails\check_rules"
    git mv "scripts\pipeline\guardrails\check_rules/__init__.py" "scripts\pipeline\guardrails\check_rules.py"
    Remove-Item "scripts\pipeline\guardrails\check_rules" -Force
}

if (Test-Path "scripts\pipeline\synthesis\use_tools\__init__.py") {
    Write-Host "Flattening scripts\pipeline\synthesis\use_tools"
    git mv "scripts\pipeline\synthesis\use_tools/__init__.py" "scripts\pipeline\synthesis\use_tools.py"
    Remove-Item "scripts\pipeline\synthesis\use_tools" -Force
}

if (Test-Path "scripts\logic\data_access\check_rules\__init__.py") {
    Write-Host "Flattening scripts\logic\data_access\check_rules"
    git mv "scripts\logic\data_access\check_rules/__init__.py" "scripts\logic\data_access\check_rules.py"
    Remove-Item "scripts\logic\data_access\check_rules" -Force
}

if (Test-Path "scripts\logic\data_access\get_info\__init__.py") {
    Write-Host "Flattening scripts\logic\data_access\get_info"
    git mv "scripts\logic\data_access\get_info/__init__.py" "scripts\logic\data_access\get_info.py"
    Remove-Item "scripts\logic\data_access\get_info" -Force
}

if (Test-Path "scripts\logic\guardrails\check_rules\__init__.py") {
    Write-Host "Flattening scripts\logic\guardrails\check_rules"
    git mv "scripts\logic\guardrails\check_rules/__init__.py" "scripts\logic\guardrails\check_rules.py"
    Remove-Item "scripts\logic\guardrails\check_rules" -Force
}

if (Test-Path "scripts\logic\guardrails\manage_costs\__init__.py") {
    Write-Host "Flattening scripts\logic\guardrails\manage_costs"
    git mv "scripts\logic\guardrails\manage_costs/__init__.py" "scripts\logic\guardrails\manage_costs.py"
    Remove-Item "scripts\logic\guardrails\manage_costs" -Force
}

if (Test-Path "scripts\logic\synthesis\pick_best_result\__init__.py") {
    Write-Host "Flattening scripts\logic\synthesis\pick_best_result"
    git mv "scripts\logic\synthesis\pick_best_result/__init__.py" "scripts\logic\synthesis\pick_best_result.py"
    Remove-Item "scripts\logic\synthesis\pick_best_result" -Force
}

if (Test-Path "scripts\logic\synthesis\use_tools\__init__.py") {
    Write-Host "Flattening scripts\logic\synthesis\use_tools"
    git mv "scripts\logic\synthesis\use_tools/__init__.py" "scripts\logic\synthesis\use_tools.py"
    Remove-Item "scripts\logic\synthesis\use_tools" -Force
}

if (Test-Path "scripts\logic\validation\check_structure\__init__.py") {
    Write-Host "Flattening scripts\logic\validation\check_structure"
    git mv "scripts\logic\validation\check_structure/__init__.py" "scripts\logic\validation\check_structure.py"
    Remove-Item "scripts\logic\validation\check_structure" -Force
}

if (Test-Path "scripts\logic\validation\convert_content\__init__.py") {
    Write-Host "Flattening scripts\logic\validation\convert_content"
    git mv "scripts\logic\validation\convert_content/__init__.py" "scripts\logic\validation\convert_content.py"
    Remove-Item "scripts\logic\validation\convert_content" -Force
}

if (Test-Path "scripts\cache\data_access\get_info\__init__.py") {
    Write-Host "Flattening scripts\cache\data_access\get_info"
    git mv "scripts\cache\data_access\get_info/__init__.py" "scripts\cache\data_access\get_info.py"
    Remove-Item "scripts\cache\data_access\get_info" -Force
}

if (Test-Path "scripts\cache\guardrails\check_rules\__init__.py") {
    Write-Host "Flattening scripts\cache\guardrails\check_rules"
    git mv "scripts\cache\guardrails\check_rules/__init__.py" "scripts\cache\guardrails\check_rules.py"
    Remove-Item "scripts\cache\guardrails\check_rules" -Force
}

if (Test-Path "schemas\templates\injection_patterns\__init__.py") {
    Write-Host "Flattening schemas\templates\injection_patterns"
    git mv "schemas\templates\injection_patterns/__init__.py" "schemas\templates\injection_patterns.py"
    Remove-Item "schemas\templates\injection_patterns" -Force
}

if (Test-Path "schemas\security_controls\guardrails\check_schema_rules\__init__.py") {
    Write-Host "Flattening schemas\security_controls\guardrails\check_schema_rules"
    git mv "schemas\security_controls\guardrails\check_schema_rules/__init__.py" "schemas\security_controls\guardrails\check_schema_rules.py"
    Remove-Item "schemas\security_controls\guardrails\check_schema_rules" -Force
}

if (Test-Path "schemas\runtime\guardrails\check_schema_rules\__init__.py") {
    Write-Host "Flattening schemas\runtime\guardrails\check_schema_rules"
    git mv "schemas\runtime\guardrails\check_schema_rules/__init__.py" "schemas\runtime\guardrails\check_schema_rules.py"
    Remove-Item "schemas\runtime\guardrails\check_schema_rules" -Force
}

if (Test-Path "schemas\runtime\guardrails\check_schema_safety\__init__.py") {
    Write-Host "Flattening schemas\runtime\guardrails\check_schema_safety"
    git mv "schemas\runtime\guardrails\check_schema_safety/__init__.py" "schemas\runtime\guardrails\check_schema_safety.py"
    Remove-Item "schemas\runtime\guardrails\check_schema_safety" -Force
}

if (Test-Path "schemas\runtime\synthesis\use_schema_tools\__init__.py") {
    Write-Host "Flattening schemas\runtime\synthesis\use_schema_tools"
    git mv "schemas\runtime\synthesis\use_schema_tools/__init__.py" "schemas\runtime\synthesis\use_schema_tools.py"
    Remove-Item "schemas\runtime\synthesis\use_schema_tools" -Force
}

if (Test-Path "schemas\runtime\synthesis\use_schema_utility\__init__.py") {
    Write-Host "Flattening schemas\runtime\synthesis\use_schema_utility"
    git mv "schemas\runtime\synthesis\use_schema_utility/__init__.py" "schemas\runtime\synthesis\use_schema_utility.py"
    Remove-Item "schemas\runtime\synthesis\use_schema_utility" -Force
}

if (Test-Path "schemas\runtime\validation\check_schema_safety\__init__.py") {
    Write-Host "Flattening schemas\runtime\validation\check_schema_safety"
    git mv "schemas\runtime\validation\check_schema_safety/__init__.py" "schemas\runtime\validation\check_schema_safety.py"
    Remove-Item "schemas\runtime\validation\check_schema_safety" -Force
}

if (Test-Path "schemas\runtime\validation\check_schema_structure\__init__.py") {
    Write-Host "Flattening schemas\runtime\validation\check_schema_structure"
    git mv "schemas\runtime\validation\check_schema_structure/__init__.py" "schemas\runtime\validation\check_schema_structure.py"
    Remove-Item "schemas\runtime\validation\check_schema_structure" -Force
}

if (Test-Path "schemas\pipeline\data_access\get_schema_info\__init__.py") {
    Write-Host "Flattening schemas\pipeline\data_access\get_schema_info"
    git mv "schemas\pipeline\data_access\get_schema_info/__init__.py" "schemas\pipeline\data_access\get_schema_info.py"
    Remove-Item "schemas\pipeline\data_access\get_schema_info" -Force
}

if (Test-Path "schemas\pipeline\guardrails\check_schema_rules\__init__.py") {
    Write-Host "Flattening schemas\pipeline\guardrails\check_schema_rules"
    git mv "schemas\pipeline\guardrails\check_schema_rules/__init__.py" "schemas\pipeline\guardrails\check_schema_rules.py"
    Remove-Item "schemas\pipeline\guardrails\check_schema_rules" -Force
}

if (Test-Path "schemas\pipeline\synthesis\use_schema_tools\__init__.py") {
    Write-Host "Flattening schemas\pipeline\synthesis\use_schema_tools"
    git mv "schemas\pipeline\synthesis\use_schema_tools/__init__.py" "schemas\pipeline\synthesis\use_schema_tools.py"
    Remove-Item "schemas\pipeline\synthesis\use_schema_tools" -Force
}

if (Test-Path "schemas\logic\data_access\check_schema_rules\__init__.py") {
    Write-Host "Flattening schemas\logic\data_access\check_schema_rules"
    git mv "schemas\logic\data_access\check_schema_rules/__init__.py" "schemas\logic\data_access\check_schema_rules.py"
    Remove-Item "schemas\logic\data_access\check_schema_rules" -Force
}

if (Test-Path "schemas\logic\data_access\get_schema_info\__init__.py") {
    Write-Host "Flattening schemas\logic\data_access\get_schema_info"
    git mv "schemas\logic\data_access\get_schema_info/__init__.py" "schemas\logic\data_access\get_schema_info.py"
    Remove-Item "schemas\logic\data_access\get_schema_info" -Force
}

if (Test-Path "schemas\logic\guardrails\check_schema_rules\__init__.py") {
    Write-Host "Flattening schemas\logic\guardrails\check_schema_rules"
    git mv "schemas\logic\guardrails\check_schema_rules/__init__.py" "schemas\logic\guardrails\check_schema_rules.py"
    Remove-Item "schemas\logic\guardrails\check_schema_rules" -Force
}

if (Test-Path "schemas\logic\guardrails\manage_schema_costs\__init__.py") {
    Write-Host "Flattening schemas\logic\guardrails\manage_schema_costs"
    git mv "schemas\logic\guardrails\manage_schema_costs/__init__.py" "schemas\logic\guardrails\manage_schema_costs.py"
    Remove-Item "schemas\logic\guardrails\manage_schema_costs" -Force
}

if (Test-Path "schemas\logic\synthesis\pick_best_result\__init__.py") {
    Write-Host "Flattening schemas\logic\synthesis\pick_best_result"
    git mv "schemas\logic\synthesis\pick_best_result/__init__.py" "schemas\logic\synthesis\pick_best_result.py"
    Remove-Item "schemas\logic\synthesis\pick_best_result" -Force
}

if (Test-Path "schemas\logic\synthesis\state_update\__init__.py") {
    Write-Host "Flattening schemas\logic\synthesis\state_update"
    git mv "schemas\logic\synthesis\state_update/__init__.py" "schemas\logic\synthesis\state_update.py"
    Remove-Item "schemas\logic\synthesis\state_update" -Force
}

if (Test-Path "schemas\logic\synthesis\use_schema_retry\__init__.py") {
    Write-Host "Flattening schemas\logic\synthesis\use_schema_retry"
    git mv "schemas\logic\synthesis\use_schema_retry/__init__.py" "schemas\logic\synthesis\use_schema_retry.py"
    Remove-Item "schemas\logic\synthesis\use_schema_retry" -Force
}

if (Test-Path "schemas\logic\synthesis\use_schema_tools\__init__.py") {
    Write-Host "Flattening schemas\logic\synthesis\use_schema_tools"
    git mv "schemas\logic\synthesis\use_schema_tools/__init__.py" "schemas\logic\synthesis\use_schema_tools.py"
    Remove-Item "schemas\logic\synthesis\use_schema_tools" -Force
}

if (Test-Path "schemas\logic\validation\check_schema_structure\__init__.py") {
    Write-Host "Flattening schemas\logic\validation\check_schema_structure"
    git mv "schemas\logic\validation\check_schema_structure/__init__.py" "schemas\logic\validation\check_schema_structure.py"
    Remove-Item "schemas\logic\validation\check_schema_structure" -Force
}

if (Test-Path "schemas\logic\validation\convert_schema_content\__init__.py") {
    Write-Host "Flattening schemas\logic\validation\convert_schema_content"
    git mv "schemas\logic\validation\convert_schema_content/__init__.py" "schemas\logic\validation\convert_schema_content.py"
    Remove-Item "schemas\logic\validation\convert_schema_content" -Force
}

if (Test-Path "schemas\logic\validation\find_schema_diagnostics\__init__.py") {
    Write-Host "Flattening schemas\logic\validation\find_schema_diagnostics"
    git mv "schemas\logic\validation\find_schema_diagnostics/__init__.py" "schemas\logic\validation\find_schema_diagnostics.py"
    Remove-Item "schemas\logic\validation\find_schema_diagnostics" -Force
}

if (Test-Path "schemas\logic\validation\find_schema_problems\__init__.py") {
    Write-Host "Flattening schemas\logic\validation\find_schema_problems"
    git mv "schemas\logic\validation\find_schema_problems/__init__.py" "schemas\logic\validation\find_schema_problems.py"
    Remove-Item "schemas\logic\validation\find_schema_problems" -Force
}

if (Test-Path "schemas\cache\data_access\get_schema_info\__init__.py") {
    Write-Host "Flattening schemas\cache\data_access\get_schema_info"
    git mv "schemas\cache\data_access\get_schema_info/__init__.py" "schemas\cache\data_access\get_schema_info.py"
    Remove-Item "schemas\cache\data_access\get_schema_info" -Force
}

if (Test-Path "schemas\cache\guardrails\check_schema_rules\__init__.py") {
    Write-Host "Flattening schemas\cache\guardrails\check_schema_rules"
    git mv "schemas\cache\guardrails\check_schema_rules/__init__.py" "schemas\cache\guardrails\check_schema_rules.py"
    Remove-Item "schemas\cache\guardrails\check_schema_rules" -Force
}

if (Test-Path "runtime\guardrails\check_rules\policy_check_safety\__init__.py") {
    Write-Host "Flattening runtime\guardrails\check_rules\policy_check_safety"
    git mv "runtime\guardrails\check_rules\policy_check_safety/__init__.py" "runtime\guardrails\check_rules\policy_check_safety.py"
    Remove-Item "runtime\guardrails\check_rules\policy_check_safety" -Force
}

if (Test-Path "prompt_governance\templates\budget-manager-layer\refine-phase-group\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\budget-manager-layer\refine-phase-group"
    git mv "prompt_governance\templates\budget-manager-layer\refine-phase-group/__init__.py" "prompt_governance\templates\budget-manager-layer\refine-phase-group.py"
    Remove-Item "prompt_governance\templates\budget-manager-layer\refine-phase-group" -Force
}

if (Test-Path "prompt_governance\templates\budget-manager-layer\refine-phase-group_constraint-check-ops\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\budget-manager-layer\refine-phase-group_constraint-check-ops"
    git mv "prompt_governance\templates\budget-manager-layer\refine-phase-group_constraint-check-ops/__init__.py" "prompt_governance\templates\budget-manager-layer\refine-phase-group_constraint-check-ops.py"
    Remove-Item "prompt_governance\templates\budget-manager-layer\refine-phase-group_constraint-check-ops" -Force
}

if (Test-Path "prompt_governance\templates\resume\executor-microagent-layer\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\resume\executor-microagent-layer"
    git mv "prompt_governance\templates\resume\executor-microagent-layer/__init__.py" "prompt_governance\templates\resume\executor-microagent-layer.py"
    Remove-Item "prompt_governance\templates\resume\executor-microagent-layer" -Force
}

if (Test-Path "prompt_governance\templates\resume\executor-microagent-layer_retry-phase-group\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\resume\executor-microagent-layer_retry-phase-group"
    git mv "prompt_governance\templates\resume\executor-microagent-layer_retry-phase-group/__init__.py" "prompt_governance\templates\resume\executor-microagent-layer_retry-phase-group.py"
    Remove-Item "prompt_governance\templates\resume\executor-microagent-layer_retry-phase-group" -Force
}

if (Test-Path "prompt_governance\templates\resume\observer-microagent-layer\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\resume\observer-microagent-layer"
    git mv "prompt_governance\templates\resume\observer-microagent-layer/__init__.py" "prompt_governance\templates\resume\observer-microagent-layer.py"
    Remove-Item "prompt_governance\templates\resume\observer-microagent-layer" -Force
}

if (Test-Path "prompt_governance\templates\resume\observer-microagent-layer_inspect-phase-group\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\resume\observer-microagent-layer_inspect-phase-group"
    git mv "prompt_governance\templates\resume\observer-microagent-layer_inspect-phase-group/__init__.py" "prompt_governance\templates\resume\observer-microagent-layer_inspect-phase-group.py"
    Remove-Item "prompt_governance\templates\resume\observer-microagent-layer_inspect-phase-group" -Force
}

if (Test-Path "prompt_governance\templates\resume\planner-microagent-layer\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\resume\planner-microagent-layer"
    git mv "prompt_governance\templates\resume\planner-microagent-layer/__init__.py" "prompt_governance\templates\resume\planner-microagent-layer.py"
    Remove-Item "prompt_governance\templates\resume\planner-microagent-layer" -Force
}

if (Test-Path "prompt_governance\templates\resume\planner-microagent-layer_act-phase-group\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\resume\planner-microagent-layer_act-phase-group"
    git mv "prompt_governance\templates\resume\planner-microagent-layer_act-phase-group/__init__.py" "prompt_governance\templates\resume\planner-microagent-layer_act-phase-group.py"
    Remove-Item "prompt_governance\templates\resume\planner-microagent-layer_act-phase-group" -Force
}

if (Test-Path "prompt_governance\templates\router-microagent-layer\expand-phase-group\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\router-microagent-layer\expand-phase-group"
    git mv "prompt_governance\templates\router-microagent-layer\expand-phase-group/__init__.py" "prompt_governance\templates\router-microagent-layer\expand-phase-group.py"
    Remove-Item "prompt_governance\templates\router-microagent-layer\expand-phase-group" -Force
}

if (Test-Path "prompt_governance\templates\router-microagent-layer\expand-phase-group_vectorization-ops\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\router-microagent-layer\expand-phase-group_vectorization-ops"
    git mv "prompt_governance\templates\router-microagent-layer\expand-phase-group_vectorization-ops/__init__.py" "prompt_governance\templates\router-microagent-layer\expand-phase-group_vectorization-ops.py"
    Remove-Item "prompt_governance\templates\router-microagent-layer\expand-phase-group_vectorization-ops" -Force
}

if (Test-Path "prompt_governance\templates\safety-guard-layer\validate-phase-group\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\safety-guard-layer\validate-phase-group"
    git mv "prompt_governance\templates\safety-guard-layer\validate-phase-group/__init__.py" "prompt_governance\templates\safety-guard-layer\validate-phase-group.py"
    Remove-Item "prompt_governance\templates\safety-guard-layer\validate-phase-group" -Force
}

if (Test-Path "prompt_governance\templates\safety-guard-layer\validate-phase-group_retrieval-ops\__init__.py") {
    Write-Host "Flattening prompt_governance\templates\safety-guard-layer\validate-phase-group_retrieval-ops"
    git mv "prompt_governance\templates\safety-guard-layer\validate-phase-group_retrieval-ops/__init__.py" "prompt_governance\templates\safety-guard-layer\validate-phase-group_retrieval-ops.py"
    Remove-Item "prompt_governance\templates\safety-guard-layer\validate-phase-group_retrieval-ops" -Force
}

if (Test-Path "prompt_governance\security_controls\guardrails\check_prompt_rules\__init__.py") {
    Write-Host "Flattening prompt_governance\security_controls\guardrails\check_prompt_rules"
    git mv "prompt_governance\security_controls\guardrails\check_prompt_rules/__init__.py" "prompt_governance\security_controls\guardrails\check_prompt_rules.py"
    Remove-Item "prompt_governance\security_controls\guardrails\check_prompt_rules" -Force
}

if (Test-Path "prompt_governance\security_controls\guardrails\check_prompt_rules_manage_costs_state_update\__init__.py") {
    Write-Host "Flattening prompt_governance\security_controls\guardrails\check_prompt_rules_manage_costs_state_update"
    git mv "prompt_governance\security_controls\guardrails\check_prompt_rules_manage_costs_state_update/__init__.py" "prompt_governance\security_controls\guardrails\check_prompt_rules_manage_costs_state_update.py"
    Remove-Item "prompt_governance\security_controls\guardrails\check_prompt_rules_manage_costs_state_update" -Force
}

if (Test-Path "prompt_governance\security_controls\guardrails\check_prompt_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening prompt_governance\security_controls\guardrails\check_prompt_rules_policy_check_safety"
    git mv "prompt_governance\security_controls\guardrails\check_prompt_rules_policy_check_safety/__init__.py" "prompt_governance\security_controls\guardrails\check_prompt_rules_policy_check_safety.py"
    Remove-Item "prompt_governance\security_controls\guardrails\check_prompt_rules_policy_check_safety" -Force
}

if (Test-Path "prompt_governance\runtime\guardrails\check_prompt_rules\__init__.py") {
    Write-Host "Flattening prompt_governance\runtime\guardrails\check_prompt_rules"
    git mv "prompt_governance\runtime\guardrails\check_prompt_rules/__init__.py" "prompt_governance\runtime\guardrails\check_prompt_rules.py"
    Remove-Item "prompt_governance\runtime\guardrails\check_prompt_rules" -Force
}

if (Test-Path "prompt_governance\runtime\synthesis\use_prompt_tools\__init__.py") {
    Write-Host "Flattening prompt_governance\runtime\synthesis\use_prompt_tools"
    git mv "prompt_governance\runtime\synthesis\use_prompt_tools/__init__.py" "prompt_governance\runtime\synthesis\use_prompt_tools.py"
    Remove-Item "prompt_governance\runtime\synthesis\use_prompt_tools" -Force
}

if (Test-Path "prompt_governance\runtime\synthesis\use_prompt_tools_utility_prepare_information\__init__.py") {
    Write-Host "Flattening prompt_governance\runtime\synthesis\use_prompt_tools_utility_prepare_information"
    git mv "prompt_governance\runtime\synthesis\use_prompt_tools_utility_prepare_information/__init__.py" "prompt_governance\runtime\synthesis\use_prompt_tools_utility_prepare_information.py"
    Remove-Item "prompt_governance\runtime\synthesis\use_prompt_tools_utility_prepare_information" -Force
}

if (Test-Path "prompt_governance\runtime\validation\check_prompt_structure\__init__.py") {
    Write-Host "Flattening prompt_governance\runtime\validation\check_prompt_structure"
    git mv "prompt_governance\runtime\validation\check_prompt_structure/__init__.py" "prompt_governance\runtime\validation\check_prompt_structure.py"
    Remove-Item "prompt_governance\runtime\validation\check_prompt_structure" -Force
}

if (Test-Path "prompt_governance\pipeline\data_access\get_prompt_info\__init__.py") {
    Write-Host "Flattening prompt_governance\pipeline\data_access\get_prompt_info"
    git mv "prompt_governance\pipeline\data_access\get_prompt_info/__init__.py" "prompt_governance\pipeline\data_access\get_prompt_info.py"
    Remove-Item "prompt_governance\pipeline\data_access\get_prompt_info" -Force
}

if (Test-Path "prompt_governance\pipeline\guardrails\check_prompt_rules\__init__.py") {
    Write-Host "Flattening prompt_governance\pipeline\guardrails\check_prompt_rules"
    git mv "prompt_governance\pipeline\guardrails\check_prompt_rules/__init__.py" "prompt_governance\pipeline\guardrails\check_prompt_rules.py"
    Remove-Item "prompt_governance\pipeline\guardrails\check_prompt_rules" -Force
}

if (Test-Path "prompt_governance\pipeline\synthesis\use_prompt_tools\__init__.py") {
    Write-Host "Flattening prompt_governance\pipeline\synthesis\use_prompt_tools"
    git mv "prompt_governance\pipeline\synthesis\use_prompt_tools/__init__.py" "prompt_governance\pipeline\synthesis\use_prompt_tools.py"
    Remove-Item "prompt_governance\pipeline\synthesis\use_prompt_tools" -Force
}

if (Test-Path "prompt_governance\pipeline\synthesis\use_prompt_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening prompt_governance\pipeline\synthesis\use_prompt_tools_use_a_tool"
    git mv "prompt_governance\pipeline\synthesis\use_prompt_tools_use_a_tool/__init__.py" "prompt_governance\pipeline\synthesis\use_prompt_tools_use_a_tool.py"
    Remove-Item "prompt_governance\pipeline\synthesis\use_prompt_tools_use_a_tool" -Force
}

if (Test-Path "prompt_governance\logic\data_access\check_prompt_rules\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\data_access\check_prompt_rules"
    git mv "prompt_governance\logic\data_access\check_prompt_rules/__init__.py" "prompt_governance\logic\data_access\check_prompt_rules.py"
    Remove-Item "prompt_governance\logic\data_access\check_prompt_rules" -Force
}

if (Test-Path "prompt_governance\logic\data_access\get_prompt_info\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\data_access\get_prompt_info"
    git mv "prompt_governance\logic\data_access\get_prompt_info/__init__.py" "prompt_governance\logic\data_access\get_prompt_info.py"
    Remove-Item "prompt_governance\logic\data_access\get_prompt_info" -Force
}

if (Test-Path "prompt_governance\logic\data_access\get_prompt_info_understand_request\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\data_access\get_prompt_info_understand_request"
    git mv "prompt_governance\logic\data_access\get_prompt_info_understand_request/__init__.py" "prompt_governance\logic\data_access\get_prompt_info_understand_request.py"
    Remove-Item "prompt_governance\logic\data_access\get_prompt_info_understand_request" -Force
}

if (Test-Path "prompt_governance\logic\data_access\get_prompt_info_utility_prepare_information\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\data_access\get_prompt_info_utility_prepare_information"
    git mv "prompt_governance\logic\data_access\get_prompt_info_utility_prepare_information/__init__.py" "prompt_governance\logic\data_access\get_prompt_info_utility_prepare_information.py"
    Remove-Item "prompt_governance\logic\data_access\get_prompt_info_utility_prepare_information" -Force
}

if (Test-Path "prompt_governance\logic\guardrails\check_prompt_rules\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\guardrails\check_prompt_rules"
    git mv "prompt_governance\logic\guardrails\check_prompt_rules/__init__.py" "prompt_governance\logic\guardrails\check_prompt_rules.py"
    Remove-Item "prompt_governance\logic\guardrails\check_prompt_rules" -Force
}

if (Test-Path "prompt_governance\logic\guardrails\manage_prompt_costs\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\guardrails\manage_prompt_costs"
    git mv "prompt_governance\logic\guardrails\manage_prompt_costs/__init__.py" "prompt_governance\logic\guardrails\manage_prompt_costs.py"
    Remove-Item "prompt_governance\logic\guardrails\manage_prompt_costs" -Force
}

if (Test-Path "prompt_governance\logic\synthesis\pick_best_result\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\synthesis\pick_best_result"
    git mv "prompt_governance\logic\synthesis\pick_best_result/__init__.py" "prompt_governance\logic\synthesis\pick_best_result.py"
    Remove-Item "prompt_governance\logic\synthesis\pick_best_result" -Force
}

if (Test-Path "prompt_governance\logic\synthesis\pick_best_result_understand_request\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\synthesis\pick_best_result_understand_request"
    git mv "prompt_governance\logic\synthesis\pick_best_result_understand_request/__init__.py" "prompt_governance\logic\synthesis\pick_best_result_understand_request.py"
    Remove-Item "prompt_governance\logic\synthesis\pick_best_result_understand_request" -Force
}

if (Test-Path "prompt_governance\logic\synthesis\state_update\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\synthesis\state_update"
    git mv "prompt_governance\logic\synthesis\state_update/__init__.py" "prompt_governance\logic\synthesis\state_update.py"
    Remove-Item "prompt_governance\logic\synthesis\state_update" -Force
}

if (Test-Path "prompt_governance\logic\synthesis\use_prompt_tools\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\synthesis\use_prompt_tools"
    git mv "prompt_governance\logic\synthesis\use_prompt_tools/__init__.py" "prompt_governance\logic\synthesis\use_prompt_tools.py"
    Remove-Item "prompt_governance\logic\synthesis\use_prompt_tools" -Force
}

if (Test-Path "prompt_governance\logic\synthesis\use_prompt_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\synthesis\use_prompt_tools_use_a_tool"
    git mv "prompt_governance\logic\synthesis\use_prompt_tools_use_a_tool/__init__.py" "prompt_governance\logic\synthesis\use_prompt_tools_use_a_tool.py"
    Remove-Item "prompt_governance\logic\synthesis\use_prompt_tools_use_a_tool" -Force
}

if (Test-Path "prompt_governance\logic\validation\check_prompt_structure\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\validation\check_prompt_structure"
    git mv "prompt_governance\logic\validation\check_prompt_structure/__init__.py" "prompt_governance\logic\validation\check_prompt_structure.py"
    Remove-Item "prompt_governance\logic\validation\check_prompt_structure" -Force
}

if (Test-Path "prompt_governance\logic\validation\convert_prompt_content\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\validation\convert_prompt_content"
    git mv "prompt_governance\logic\validation\convert_prompt_content/__init__.py" "prompt_governance\logic\validation\convert_prompt_content.py"
    Remove-Item "prompt_governance\logic\validation\convert_prompt_content" -Force
}

if (Test-Path "prompt_governance\logic\validation\find_prompt_problems\__init__.py") {
    Write-Host "Flattening prompt_governance\logic\validation\find_prompt_problems"
    git mv "prompt_governance\logic\validation\find_prompt_problems/__init__.py" "prompt_governance\logic\validation\find_prompt_problems.py"
    Remove-Item "prompt_governance\logic\validation\find_prompt_problems" -Force
}

if (Test-Path "prompt_governance\config\logic\data_access_check_rules\__init__.py") {
    Write-Host "Flattening prompt_governance\config\logic\data_access_check_rules"
    git mv "prompt_governance\config\logic\data_access_check_rules/__init__.py" "prompt_governance\config\logic\data_access_check_rules.py"
    Remove-Item "prompt_governance\config\logic\data_access_check_rules" -Force
}

if (Test-Path "prompt_governance\config\logic\data_access_get_info\__init__.py") {
    Write-Host "Flattening prompt_governance\config\logic\data_access_get_info"
    git mv "prompt_governance\config\logic\data_access_get_info/__init__.py" "prompt_governance\config\logic\data_access_get_info.py"
    Remove-Item "prompt_governance\config\logic\data_access_get_info" -Force
}

if (Test-Path "prompt_governance\config\logic\guardrails\__init__.py") {
    Write-Host "Flattening prompt_governance\config\logic\guardrails"
    git mv "prompt_governance\config\logic\guardrails/__init__.py" "prompt_governance\config\logic\guardrails.py"
    Remove-Item "prompt_governance\config\logic\guardrails" -Force
}

if (Test-Path "prompt_governance\config\logic\settings\__init__.py") {
    Write-Host "Flattening prompt_governance\config\logic\settings"
    git mv "prompt_governance\config\logic\settings/__init__.py" "prompt_governance\config\logic\settings.py"
    Remove-Item "prompt_governance\config\logic\settings" -Force
}

if (Test-Path "prompt_governance\config\logic\synthesis\__init__.py") {
    Write-Host "Flattening prompt_governance\config\logic\synthesis"
    git mv "prompt_governance\config\logic\synthesis/__init__.py" "prompt_governance\config\logic\synthesis.py"
    Remove-Item "prompt_governance\config\logic\synthesis" -Force
}

if (Test-Path "prompt_governance\config\logic\validation\__init__.py") {
    Write-Host "Flattening prompt_governance\config\logic\validation"
    git mv "prompt_governance\config\logic\validation/__init__.py" "prompt_governance\config\logic\validation.py"
    Remove-Item "prompt_governance\config\logic\validation" -Force
}

if (Test-Path "prompt_governance\config\pipeline\data_access_get_info\__init__.py") {
    Write-Host "Flattening prompt_governance\config\pipeline\data_access_get_info"
    git mv "prompt_governance\config\pipeline\data_access_get_info/__init__.py" "prompt_governance\config\pipeline\data_access_get_info.py"
    Remove-Item "prompt_governance\config\pipeline\data_access_get_info" -Force
}

if (Test-Path "prompt_governance\config\pipeline\guardrails\__init__.py") {
    Write-Host "Flattening prompt_governance\config\pipeline\guardrails"
    git mv "prompt_governance\config\pipeline\guardrails/__init__.py" "prompt_governance\config\pipeline\guardrails.py"
    Remove-Item "prompt_governance\config\pipeline\guardrails" -Force
}

if (Test-Path "prompt_governance\config\pipeline\synthesis\__init__.py") {
    Write-Host "Flattening prompt_governance\config\pipeline\synthesis"
    git mv "prompt_governance\config\pipeline\synthesis/__init__.py" "prompt_governance\config\pipeline\synthesis.py"
    Remove-Item "prompt_governance\config\pipeline\synthesis" -Force
}

if (Test-Path "prompt_governance\config\runtime\synthesis\__init__.py") {
    Write-Host "Flattening prompt_governance\config\runtime\synthesis"
    git mv "prompt_governance\config\runtime\synthesis/__init__.py" "prompt_governance\config\runtime\synthesis.py"
    Remove-Item "prompt_governance\config\runtime\synthesis" -Force
}

if (Test-Path "prompt_governance\config\security_controls\guardrails\__init__.py") {
    Write-Host "Flattening prompt_governance\config\security_controls\guardrails"
    git mv "prompt_governance\config\security_controls\guardrails/__init__.py" "prompt_governance\config\security_controls\guardrails.py"
    Remove-Item "prompt_governance\config\security_controls\guardrails" -Force
}

if (Test-Path "prompt_governance\cache\data_access\get_prompt_info\__init__.py") {
    Write-Host "Flattening prompt_governance\cache\data_access\get_prompt_info"
    git mv "prompt_governance\cache\data_access\get_prompt_info/__init__.py" "prompt_governance\cache\data_access\get_prompt_info.py"
    Remove-Item "prompt_governance\cache\data_access\get_prompt_info" -Force
}

if (Test-Path "prompt_governance\cache\data_access\get_prompt_info_understand_request\__init__.py") {
    Write-Host "Flattening prompt_governance\cache\data_access\get_prompt_info_understand_request"
    git mv "prompt_governance\cache\data_access\get_prompt_info_understand_request/__init__.py" "prompt_governance\cache\data_access\get_prompt_info_understand_request.py"
    Remove-Item "prompt_governance\cache\data_access\get_prompt_info_understand_request" -Force
}

if (Test-Path "prompt_governance\cache\guardrails\check_prompt_rules\__init__.py") {
    Write-Host "Flattening prompt_governance\cache\guardrails\check_prompt_rules"
    git mv "prompt_governance\cache\guardrails\check_prompt_rules/__init__.py" "prompt_governance\cache\guardrails\check_prompt_rules.py"
    Remove-Item "prompt_governance\cache\guardrails\check_prompt_rules" -Force
}

if (Test-Path "observability\runtime\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening observability\runtime\guardrails\check_rules_policy_check_safety"
    git mv "observability\runtime\guardrails\check_rules_policy_check_safety/__init__.py" "observability\runtime\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "observability\runtime\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "observability\runtime\synthesis\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening observability\runtime\synthesis\use_tools_use_a_tool"
    git mv "observability\runtime\synthesis\use_tools_use_a_tool/__init__.py" "observability\runtime\synthesis\use_tools_use_a_tool.py"
    Remove-Item "observability\runtime\synthesis\use_tools_use_a_tool" -Force
}

if (Test-Path "observability\runtime\synthesis\use_tools_utility_prepare_information\__init__.py") {
    Write-Host "Flattening observability\runtime\synthesis\use_tools_utility_prepare_information"
    git mv "observability\runtime\synthesis\use_tools_utility_prepare_information/__init__.py" "observability\runtime\synthesis\use_tools_utility_prepare_information.py"
    Remove-Item "observability\runtime\synthesis\use_tools_utility_prepare_information" -Force
}

if (Test-Path "observability\runtime\validation\check_structure_policy_check_safety\__init__.py") {
    Write-Host "Flattening observability\runtime\validation\check_structure_policy_check_safety"
    git mv "observability\runtime\validation\check_structure_policy_check_safety/__init__.py" "observability\runtime\validation\check_structure_policy_check_safety.py"
    Remove-Item "observability\runtime\validation\check_structure_policy_check_safety" -Force
}

if (Test-Path "observability\pipeline\data_access\get_info_understand_request\__init__.py") {
    Write-Host "Flattening observability\pipeline\data_access\get_info_understand_request"
    git mv "observability\pipeline\data_access\get_info_understand_request/__init__.py" "observability\pipeline\data_access\get_info_understand_request.py"
    Remove-Item "observability\pipeline\data_access\get_info_understand_request" -Force
}

if (Test-Path "observability\pipeline\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening observability\pipeline\guardrails\check_rules_policy_check_safety"
    git mv "observability\pipeline\guardrails\check_rules_policy_check_safety/__init__.py" "observability\pipeline\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "observability\pipeline\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "observability\pipeline\synthesis\use_tools_routing_retry_task\__init__.py") {
    Write-Host "Flattening observability\pipeline\synthesis\use_tools_routing_retry_task"
    git mv "observability\pipeline\synthesis\use_tools_routing_retry_task/__init__.py" "observability\pipeline\synthesis\use_tools_routing_retry_task.py"
    Remove-Item "observability\pipeline\synthesis\use_tools_routing_retry_task" -Force
}

if (Test-Path "observability\pipeline\synthesis\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening observability\pipeline\synthesis\use_tools_use_a_tool"
    git mv "observability\pipeline\synthesis\use_tools_use_a_tool/__init__.py" "observability\pipeline\synthesis\use_tools_use_a_tool.py"
    Remove-Item "observability\pipeline\synthesis\use_tools_use_a_tool" -Force
}

if (Test-Path "observability\logic\data_access\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening observability\logic\data_access\check_rules_policy_check_safety"
    git mv "observability\logic\data_access\check_rules_policy_check_safety/__init__.py" "observability\logic\data_access\check_rules_policy_check_safety.py"
    Remove-Item "observability\logic\data_access\check_rules_policy_check_safety" -Force
}

if (Test-Path "observability\logic\data_access\get_info_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening observability\logic\data_access\get_info_embedding_compare_meaning"
    git mv "observability\logic\data_access\get_info_embedding_compare_meaning/__init__.py" "observability\logic\data_access\get_info_embedding_compare_meaning.py"
    Remove-Item "observability\logic\data_access\get_info_embedding_compare_meaning" -Force
}

if (Test-Path "observability\logic\data_access\get_info_understand_request\__init__.py") {
    Write-Host "Flattening observability\logic\data_access\get_info_understand_request"
    git mv "observability\logic\data_access\get_info_understand_request/__init__.py" "observability\logic\data_access\get_info_understand_request.py"
    Remove-Item "observability\logic\data_access\get_info_understand_request" -Force
}

if (Test-Path "observability\logic\data_access\get_info_utility_prepare_information\__init__.py") {
    Write-Host "Flattening observability\logic\data_access\get_info_utility_prepare_information"
    git mv "observability\logic\data_access\get_info_utility_prepare_information/__init__.py" "observability\logic\data_access\get_info_utility_prepare_information.py"
    Remove-Item "observability\logic\data_access\get_info_utility_prepare_information" -Force
}

if (Test-Path "observability\logic\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening observability\logic\guardrails\check_rules_policy_check_safety"
    git mv "observability\logic\guardrails\check_rules_policy_check_safety/__init__.py" "observability\logic\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "observability\logic\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "observability\logic\guardrails\manage_costs_state_update\__init__.py") {
    Write-Host "Flattening observability\logic\guardrails\manage_costs_state_update"
    git mv "observability\logic\guardrails\manage_costs_state_update/__init__.py" "observability\logic\guardrails\manage_costs_state_update.py"
    Remove-Item "observability\logic\guardrails\manage_costs_state_update" -Force
}

if (Test-Path "observability\logic\synthesis\pick_best_result\__init__.py") {
    Write-Host "Flattening observability\logic\synthesis\pick_best_result"
    git mv "observability\logic\synthesis\pick_best_result/__init__.py" "observability\logic\synthesis\pick_best_result.py"
    Remove-Item "observability\logic\synthesis\pick_best_result" -Force
}

if (Test-Path "observability\logic\synthesis\pick_best_result_understand_request\__init__.py") {
    Write-Host "Flattening observability\logic\synthesis\pick_best_result_understand_request"
    git mv "observability\logic\synthesis\pick_best_result_understand_request/__init__.py" "observability\logic\synthesis\pick_best_result_understand_request.py"
    Remove-Item "observability\logic\synthesis\pick_best_result_understand_request" -Force
}

if (Test-Path "observability\logic\synthesis\state_update\__init__.py") {
    Write-Host "Flattening observability\logic\synthesis\state_update"
    git mv "observability\logic\synthesis\state_update/__init__.py" "observability\logic\synthesis\state_update.py"
    Remove-Item "observability\logic\synthesis\state_update" -Force
}

if (Test-Path "observability\logic\synthesis\use_tools_routing_retry_task\__init__.py") {
    Write-Host "Flattening observability\logic\synthesis\use_tools_routing_retry_task"
    git mv "observability\logic\synthesis\use_tools_routing_retry_task/__init__.py" "observability\logic\synthesis\use_tools_routing_retry_task.py"
    Remove-Item "observability\logic\synthesis\use_tools_routing_retry_task" -Force
}

if (Test-Path "observability\logic\synthesis\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening observability\logic\synthesis\use_tools_use_a_tool"
    git mv "observability\logic\synthesis\use_tools_use_a_tool/__init__.py" "observability\logic\synthesis\use_tools_use_a_tool.py"
    Remove-Item "observability\logic\synthesis\use_tools_use_a_tool" -Force
}

if (Test-Path "observability\logic\validation\check_structure_policy_check_safety\__init__.py") {
    Write-Host "Flattening observability\logic\validation\check_structure_policy_check_safety"
    git mv "observability\logic\validation\check_structure_policy_check_safety/__init__.py" "observability\logic\validation\check_structure_policy_check_safety.py"
    Remove-Item "observability\logic\validation\check_structure_policy_check_safety" -Force
}

if (Test-Path "observability\logic\validation\convert_content_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening observability\logic\validation\convert_content_embedding_compare_meaning"
    git mv "observability\logic\validation\convert_content_embedding_compare_meaning/__init__.py" "observability\logic\validation\convert_content_embedding_compare_meaning.py"
    Remove-Item "observability\logic\validation\convert_content_embedding_compare_meaning" -Force
}

if (Test-Path "observability\logic\validation\find_problems\__init__.py") {
    Write-Host "Flattening observability\logic\validation\find_problems"
    git mv "observability\logic\validation\find_problems/__init__.py" "observability\logic\validation\find_problems.py"
    Remove-Item "observability\logic\validation\find_problems" -Force
}

if (Test-Path "observability\logic\validation\find_problems_diagnostics\__init__.py") {
    Write-Host "Flattening observability\logic\validation\find_problems_diagnostics"
    git mv "observability\logic\validation\find_problems_diagnostics/__init__.py" "observability\logic\validation\find_problems_diagnostics.py"
    Remove-Item "observability\logic\validation\find_problems_diagnostics" -Force
}

if (Test-Path "observability\cache\data_access\get_info_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening observability\cache\data_access\get_info_embedding_compare_meaning"
    git mv "observability\cache\data_access\get_info_embedding_compare_meaning/__init__.py" "observability\cache\data_access\get_info_embedding_compare_meaning.py"
    Remove-Item "observability\cache\data_access\get_info_embedding_compare_meaning" -Force
}

if (Test-Path "observability\cache\data_access\get_info_understand_request\__init__.py") {
    Write-Host "Flattening observability\cache\data_access\get_info_understand_request"
    git mv "observability\cache\data_access\get_info_understand_request/__init__.py" "observability\cache\data_access\get_info_understand_request.py"
    Remove-Item "observability\cache\data_access\get_info_understand_request" -Force
}

if (Test-Path "observability\cache\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening observability\cache\guardrails\check_rules_policy_check_safety"
    git mv "observability\cache\guardrails\check_rules_policy_check_safety/__init__.py" "observability\cache\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "observability\cache\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "config\logic\settings\__init__.py") {
    Write-Host "Flattening config\logic\settings"
    git mv "config\logic\settings/__init__.py" "config\logic\settings.py"
    Remove-Item "config\logic\settings" -Force
}

if (Test-Path "config\pipeline\data_access\get_info_understand_request\__init__.py") {
    Write-Host "Flattening config\pipeline\data_access\get_info_understand_request"
    git mv "config\pipeline\data_access\get_info_understand_request/__init__.py" "config\pipeline\data_access\get_info_understand_request.py"
    Remove-Item "config\pipeline\data_access\get_info_understand_request" -Force
}

if (Test-Path "config\pipeline\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening config\pipeline\guardrails\check_rules_policy_check_safety"
    git mv "config\pipeline\guardrails\check_rules_policy_check_safety/__init__.py" "config\pipeline\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "config\pipeline\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "config\pipeline\synthesis\use_tools_routing_retry_task\__init__.py") {
    Write-Host "Flattening config\pipeline\synthesis\use_tools_routing_retry_task"
    git mv "config\pipeline\synthesis\use_tools_routing_retry_task/__init__.py" "config\pipeline\synthesis\use_tools_routing_retry_task.py"
    Remove-Item "config\pipeline\synthesis\use_tools_routing_retry_task" -Force
}

if (Test-Path "config\pipeline\synthesis\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening config\pipeline\synthesis\use_tools_use_a_tool"
    git mv "config\pipeline\synthesis\use_tools_use_a_tool/__init__.py" "config\pipeline\synthesis\use_tools_use_a_tool.py"
    Remove-Item "config\pipeline\synthesis\use_tools_use_a_tool" -Force
}

if (Test-Path "config\logic\data_access\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening config\logic\data_access\check_rules_policy_check_safety"
    git mv "config\logic\data_access\check_rules_policy_check_safety/__init__.py" "config\logic\data_access\check_rules_policy_check_safety.py"
    Remove-Item "config\logic\data_access\check_rules_policy_check_safety" -Force
}

if (Test-Path "config\logic\data_access\get_info_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening config\logic\data_access\get_info_embedding_compare_meaning"
    git mv "config\logic\data_access\get_info_embedding_compare_meaning/__init__.py" "config\logic\data_access\get_info_embedding_compare_meaning.py"
    Remove-Item "config\logic\data_access\get_info_embedding_compare_meaning" -Force
}

if (Test-Path "config\logic\data_access\get_info_understand_request\__init__.py") {
    Write-Host "Flattening config\logic\data_access\get_info_understand_request"
    git mv "config\logic\data_access\get_info_understand_request/__init__.py" "config\logic\data_access\get_info_understand_request.py"
    Remove-Item "config\logic\data_access\get_info_understand_request" -Force
}

if (Test-Path "config\logic\data_access\get_info_utility_prepare_information\__init__.py") {
    Write-Host "Flattening config\logic\data_access\get_info_utility_prepare_information"
    git mv "config\logic\data_access\get_info_utility_prepare_information/__init__.py" "config\logic\data_access\get_info_utility_prepare_information.py"
    Remove-Item "config\logic\data_access\get_info_utility_prepare_information" -Force
}

if (Test-Path "config\logic\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening config\logic\guardrails\check_rules_policy_check_safety"
    git mv "config\logic\guardrails\check_rules_policy_check_safety/__init__.py" "config\logic\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "config\logic\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "config\logic\guardrails\manage_costs_state_update\__init__.py") {
    Write-Host "Flattening config\logic\guardrails\manage_costs_state_update"
    git mv "config\logic\guardrails\manage_costs_state_update/__init__.py" "config\logic\guardrails\manage_costs_state_update.py"
    Remove-Item "config\logic\guardrails\manage_costs_state_update" -Force
}

if (Test-Path "config\logic\synthesis\pick_best_result\__init__.py") {
    Write-Host "Flattening config\logic\synthesis\pick_best_result"
    git mv "config\logic\synthesis\pick_best_result/__init__.py" "config\logic\synthesis\pick_best_result.py"
    Remove-Item "config\logic\synthesis\pick_best_result" -Force
}

if (Test-Path "config\logic\synthesis\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening config\logic\synthesis\use_tools_use_a_tool"
    git mv "config\logic\synthesis\use_tools_use_a_tool/__init__.py" "config\logic\synthesis\use_tools_use_a_tool.py"
    Remove-Item "config\logic\synthesis\use_tools_use_a_tool" -Force
}

if (Test-Path "config\logic\validation\check_structure_policy_check_safety\__init__.py") {
    Write-Host "Flattening config\logic\validation\check_structure_policy_check_safety"
    git mv "config\logic\validation\check_structure_policy_check_safety/__init__.py" "config\logic\validation\check_structure_policy_check_safety.py"
    Remove-Item "config\logic\validation\check_structure_policy_check_safety" -Force
}

if (Test-Path "config\logic\validation\convert_content_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening config\logic\validation\convert_content_embedding_compare_meaning"
    git mv "config\logic\validation\convert_content_embedding_compare_meaning/__init__.py" "config\logic\validation\convert_content_embedding_compare_meaning.py"
    Remove-Item "config\logic\validation\convert_content_embedding_compare_meaning" -Force
}

if (Test-Path "config\cache\data_access\get_info_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening config\cache\data_access\get_info_embedding_compare_meaning"
    git mv "config\cache\data_access\get_info_embedding_compare_meaning/__init__.py" "config\cache\data_access\get_info_embedding_compare_meaning.py"
    Remove-Item "config\cache\data_access\get_info_embedding_compare_meaning" -Force
}

if (Test-Path "config\cache\data_access\get_info_understand_request\__init__.py") {
    Write-Host "Flattening config\cache\data_access\get_info_understand_request"
    git mv "config\cache\data_access\get_info_understand_request/__init__.py" "config\cache\data_access\get_info_understand_request.py"
    Remove-Item "config\cache\data_access\get_info_understand_request" -Force
}

if (Test-Path "config\cache\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening config\cache\guardrails\check_rules_policy_check_safety"
    git mv "config\cache\guardrails\check_rules_policy_check_safety/__init__.py" "config\cache\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "config\cache\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "archives\legacy_root_folders\orchestration\control_plane\__init__.py") {
    Write-Host "Flattening archives\legacy_root_folders\orchestration\control_plane"
    git mv "archives\legacy_root_folders\orchestration\control_plane/__init__.py" "archives\legacy_root_folders\orchestration\control_plane.py"
    Remove-Item "archives\legacy_root_folders\orchestration\control_plane" -Force
}

if (Test-Path "archives\legacy_root_folders\orchestration\dag_engine\__init__.py") {
    Write-Host "Flattening archives\legacy_root_folders\orchestration\dag_engine"
    git mv "archives\legacy_root_folders\orchestration\dag_engine/__init__.py" "archives\legacy_root_folders\orchestration\dag_engine.py"
    Remove-Item "archives\legacy_root_folders\orchestration\dag_engine" -Force
}

if (Test-Path "archives\legacy_root_folders\orchestration\model_routing\__init__.py") {
    Write-Host "Flattening archives\legacy_root_folders\orchestration\model_routing"
    git mv "archives\legacy_root_folders\orchestration\model_routing/__init__.py" "archives\legacy_root_folders\orchestration\model_routing.py"
    Remove-Item "archives\legacy_root_folders\orchestration\model_routing" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agents\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agents"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agents/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agents.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agents" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\config\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\config"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\config/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\config.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\config" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\mcp\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\mcp"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\mcp/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\mcp.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\mcp" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\pydantic\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\pydantic"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\pydantic/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\pydantic.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\pydantic" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\pydantic_stub\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\pydantic_stub"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\pydantic_stub/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\pydantic_stub.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\pydantic_stub" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\schema\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\schema"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\schema/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\schema.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\schema" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.6\openai\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.6\openai"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.6\openai/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.6\openai.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.6\openai" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\agents\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\agents"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\agents/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\agents.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\agents" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\anthropic\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\anthropic"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\anthropic/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\anthropic.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\anthropic" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\config\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\config"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\config/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\config.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\config" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\mcp\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\mcp"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\mcp/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\mcp.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\mcp" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\openai\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\openai"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\openai/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\openai.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\openai" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\pytest_benchmark\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\pytest_benchmark"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\pytest_benchmark/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\pytest_benchmark.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\pytest_benchmark" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\schema\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\schema"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\schema/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\schema.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\schema" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\agents\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\agents"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\agents/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\agents.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\agents" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\anthropic\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\anthropic"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\anthropic/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\anthropic.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\anthropic" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\config\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\config"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\config/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\config.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\config" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\mcp\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\mcp"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\mcp/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\mcp.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\mcp" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\openai\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\openai"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\openai/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\openai.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\openai" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\pytest_benchmark\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\pytest_benchmark"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\pytest_benchmark/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\pytest_benchmark.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\pytest_benchmark" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\schema\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\schema"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\schema/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\schema.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\schema" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\chromadb\utils\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\chromadb\utils"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\chromadb\utils/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\chromadb\utils.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\chromadb\utils" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\google\generativeai\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\google\generativeai"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\google\generativeai/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\google\generativeai.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\google\generativeai" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\vendor\langchain\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\vendor\langchain"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\vendor\langchain/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\vendor\langchain.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\vendor\langchain" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\chromadb\utils\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\chromadb\utils"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\chromadb\utils/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\chromadb\utils.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\chromadb\utils" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\google\generativeai\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\google\generativeai"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\google\generativeai/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\google\generativeai.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\google\generativeai" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\vendor\langchain\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\vendor\langchain"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\vendor\langchain/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\vendor\langchain.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.7\Agentic-Workflow\vendor\langchain" -Force
}

if (Test-Path "archives\legacy_resume_gen\Older Microservices Models\v10.6\chromadb\utils\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Older Microservices Models\v10.6\chromadb\utils"
    git mv "archives\legacy_resume_gen\Older Microservices Models\v10.6\chromadb\utils/__init__.py" "archives\legacy_resume_gen\Older Microservices Models\v10.6\chromadb\utils.py"
    Remove-Item "archives\legacy_resume_gen\Older Microservices Models\v10.6\chromadb\utils" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\control_plane\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\control_plane"
    git mv "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\control_plane/__init__.py" "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\control_plane.py"
    Remove-Item "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\control_plane" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\dag_engine\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\dag_engine"
    git mv "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\dag_engine/__init__.py" "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\dag_engine.py"
    Remove-Item "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\dag_engine" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\model_routing\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\model_routing"
    git mv "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\model_routing/__init__.py" "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\model_routing.py"
    Remove-Item "archives\legacy_resume_gen\Agentic_Workflow-10_10\orchestration\model_routing" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic_Workflow-10_10\tests\vector\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic_Workflow-10_10\tests\vector"
    git mv "archives\legacy_resume_gen\Agentic_Workflow-10_10\tests\vector/__init__.py" "archives\legacy_resume_gen\Agentic_Workflow-10_10\tests\vector.py"
    Remove-Item "archives\legacy_resume_gen\Agentic_Workflow-10_10\tests\vector" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agentic_workflow\workflow_v10_7\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agentic_workflow\workflow_v10_7"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agentic_workflow\workflow_v10_7/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agentic_workflow\workflow_v10_7.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agentic_workflow\workflow_v10_7" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agent_stacks_v10_8\components\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agent_stacks_v10_8\components"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agent_stacks_v10_8\components/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agent_stacks_v10_8\components.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\agent_stacks_v10_8\components" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\chromadb\utils\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\chromadb\utils"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\chromadb\utils/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\chromadb\utils.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\chromadb\utils" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\simulations\engines\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\simulations\engines"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\simulations\engines/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\simulations\engines.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\simulations\engines" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\simulations\models\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\simulations\models"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\simulations\models/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\simulations\models.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\simulations\models" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\anthropic_stub\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\anthropic_stub"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\anthropic_stub/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\anthropic_stub.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\anthropic_stub" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\chromadb_stub\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\chromadb_stub"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\chromadb_stub/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\chromadb_stub.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\chromadb_stub" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\google_generativeai_stub\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\google_generativeai_stub"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\google_generativeai_stub/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\google_generativeai_stub.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\google_generativeai_stub" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\langchain\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\langchain"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\langchain/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\langchain.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\langchain" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\openai_stub\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\openai_stub"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\openai_stub/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\openai_stub.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\openai_stub" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\pydantic\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\pydantic"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\pydantic/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\pydantic.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\pydantic" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\pytest_benchmark\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\pytest_benchmark"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\pytest_benchmark/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\pytest_benchmark.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\pytest_benchmark" -Force
}

if (Test-Path "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\redis_stub\__init__.py") {
    Write-Host "Flattening archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\redis_stub"
    git mv "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\redis_stub/__init__.py" "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\redis_stub.py"
    Remove-Item "archives\legacy_resume_gen\Agentic-Workflow-10_7_main\vendor\redis_stub" -Force
}

if (Test-Path "apps_shared\security\guardrails\check_rules_manage_costs\__init__.py") {
    Write-Host "Flattening apps_shared\security\guardrails\check_rules_manage_costs"
    git mv "apps_shared\security\guardrails\check_rules_manage_costs/__init__.py" "apps_shared\security\guardrails\check_rules_manage_costs.py"
    Remove-Item "apps_shared\security\guardrails\check_rules_manage_costs" -Force
}

if (Test-Path "apps_shared\security\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening apps_shared\security\guardrails\check_rules_policy_check_safety"
    git mv "apps_shared\security\guardrails\check_rules_policy_check_safety/__init__.py" "apps_shared\security\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "apps_shared\security\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "apps_shared\runtime\data_access\get_info_understand_request\__init__.py") {
    Write-Host "Flattening apps_shared\runtime\data_access\get_info_understand_request"
    git mv "apps_shared\runtime\data_access\get_info_understand_request/__init__.py" "apps_shared\runtime\data_access\get_info_understand_request.py"
    Remove-Item "apps_shared\runtime\data_access\get_info_understand_request" -Force
}

if (Test-Path "apps_shared\runtime\synthesis\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening apps_shared\runtime\synthesis\use_tools_use_a_tool"
    git mv "apps_shared\runtime\synthesis\use_tools_use_a_tool/__init__.py" "apps_shared\runtime\synthesis\use_tools_use_a_tool.py"
    Remove-Item "apps_shared\runtime\synthesis\use_tools_use_a_tool" -Force
}

if (Test-Path "apps_shared\runtime\synthesis\use_tools_utility_prepare_information\__init__.py") {
    Write-Host "Flattening apps_shared\runtime\synthesis\use_tools_utility_prepare_information"
    git mv "apps_shared\runtime\synthesis\use_tools_utility_prepare_information/__init__.py" "apps_shared\runtime\synthesis\use_tools_utility_prepare_information.py"
    Remove-Item "apps_shared\runtime\synthesis\use_tools_utility_prepare_information" -Force
}

if (Test-Path "apps_shared\runtime\validation\check_format_policy_check_safety\__init__.py") {
    Write-Host "Flattening apps_shared\runtime\validation\check_format_policy_check_safety"
    git mv "apps_shared\runtime\validation\check_format_policy_check_safety/__init__.py" "apps_shared\runtime\validation\check_format_policy_check_safety.py"
    Remove-Item "apps_shared\runtime\validation\check_format_policy_check_safety" -Force
}

if (Test-Path "apps_shared\rag\hardening\content\__init__.py") {
    Write-Host "Flattening apps_shared\rag\hardening\content"
    git mv "apps_shared\rag\hardening\content/__init__.py" "apps_shared\rag\hardening\content.py"
    Remove-Item "apps_shared\rag\hardening\content" -Force
}

if (Test-Path "apps_shared\rag\hardening\diagnostics\__init__.py") {
    Write-Host "Flattening apps_shared\rag\hardening\diagnostics"
    git mv "apps_shared\rag\hardening\diagnostics/__init__.py" "apps_shared\rag\hardening\diagnostics.py"
    Remove-Item "apps_shared\rag\hardening\diagnostics" -Force
}

if (Test-Path "apps_shared\rag\hardening\diagnostics_diagnostics\__init__.py") {
    Write-Host "Flattening apps_shared\rag\hardening\diagnostics_diagnostics"
    git mv "apps_shared\rag\hardening\diagnostics_diagnostics/__init__.py" "apps_shared\rag\hardening\diagnostics_diagnostics.py"
    Remove-Item "apps_shared\rag\hardening\diagnostics_diagnostics" -Force
}

if (Test-Path "apps_shared\rag\hardening\guardrails\__init__.py") {
    Write-Host "Flattening apps_shared\rag\hardening\guardrails"
    git mv "apps_shared\rag\hardening\guardrails/__init__.py" "apps_shared\rag\hardening\guardrails.py"
    Remove-Item "apps_shared\rag\hardening\guardrails" -Force
}

if (Test-Path "apps_shared\rag\hardening\guardrails_check_rules\__init__.py") {
    Write-Host "Flattening apps_shared\rag\hardening\guardrails_check_rules"
    git mv "apps_shared\rag\hardening\guardrails_check_rules/__init__.py" "apps_shared\rag\hardening\guardrails_check_rules.py"
    Remove-Item "apps_shared\rag\hardening\guardrails_check_rules" -Force
}

if (Test-Path "apps_shared\rag\hardening\structure\__init__.py") {
    Write-Host "Flattening apps_shared\rag\hardening\structure"
    git mv "apps_shared\rag\hardening\structure/__init__.py" "apps_shared\rag\hardening\structure.py"
    Remove-Item "apps_shared\rag\hardening\structure" -Force
}

if (Test-Path "apps_shared\rag\hardening\validation\__init__.py") {
    Write-Host "Flattening apps_shared\rag\hardening\validation"
    git mv "apps_shared\rag\hardening\validation/__init__.py" "apps_shared\rag\hardening\validation.py"
    Remove-Item "apps_shared\rag\hardening\validation" -Force
}

if (Test-Path "apps_shared\rag\retrieval\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening apps_shared\rag\retrieval\check_rules_policy_check_safety"
    git mv "apps_shared\rag\retrieval\check_rules_policy_check_safety/__init__.py" "apps_shared\rag\retrieval\check_rules_policy_check_safety.py"
    Remove-Item "apps_shared\rag\retrieval\check_rules_policy_check_safety" -Force
}

if (Test-Path "apps_shared\rag\retrieval\get_info_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening apps_shared\rag\retrieval\get_info_embedding_compare_meaning"
    git mv "apps_shared\rag\retrieval\get_info_embedding_compare_meaning/__init__.py" "apps_shared\rag\retrieval\get_info_embedding_compare_meaning.py"
    Remove-Item "apps_shared\rag\retrieval\get_info_embedding_compare_meaning" -Force
}

if (Test-Path "apps_shared\rag\retrieval\get_info_understand_request\__init__.py") {
    Write-Host "Flattening apps_shared\rag\retrieval\get_info_understand_request"
    git mv "apps_shared\rag\retrieval\get_info_understand_request/__init__.py" "apps_shared\rag\retrieval\get_info_understand_request.py"
    Remove-Item "apps_shared\rag\retrieval\get_info_understand_request" -Force
}

if (Test-Path "apps_shared\rag\retrieval\get_info_utility_prepare_information\__init__.py") {
    Write-Host "Flattening apps_shared\rag\retrieval\get_info_utility_prepare_information"
    git mv "apps_shared\rag\retrieval\get_info_utility_prepare_information/__init__.py" "apps_shared\rag\retrieval\get_info_utility_prepare_information.py"
    Remove-Item "apps_shared\rag\retrieval\get_info_utility_prepare_information" -Force
}

if (Test-Path "apps_shared\pipeline\data_access\get_info_understand_request\__init__.py") {
    Write-Host "Flattening apps_shared\pipeline\data_access\get_info_understand_request"
    git mv "apps_shared\pipeline\data_access\get_info_understand_request/__init__.py" "apps_shared\pipeline\data_access\get_info_understand_request.py"
    Remove-Item "apps_shared\pipeline\data_access\get_info_understand_request" -Force
}

if (Test-Path "apps_shared\pipeline\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening apps_shared\pipeline\guardrails\check_rules_policy_check_safety"
    git mv "apps_shared\pipeline\guardrails\check_rules_policy_check_safety/__init__.py" "apps_shared\pipeline\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "apps_shared\pipeline\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "apps_shared\pipeline\synthesis\use_tools_routing_retry_task\__init__.py") {
    Write-Host "Flattening apps_shared\pipeline\synthesis\use_tools_routing_retry_task"
    git mv "apps_shared\pipeline\synthesis\use_tools_routing_retry_task/__init__.py" "apps_shared\pipeline\synthesis\use_tools_routing_retry_task.py"
    Remove-Item "apps_shared\pipeline\synthesis\use_tools_routing_retry_task" -Force
}

if (Test-Path "apps_shared\pipeline\synthesis\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening apps_shared\pipeline\synthesis\use_tools_use_a_tool"
    git mv "apps_shared\pipeline\synthesis\use_tools_use_a_tool/__init__.py" "apps_shared\pipeline\synthesis\use_tools_use_a_tool.py"
    Remove-Item "apps_shared\pipeline\synthesis\use_tools_use_a_tool" -Force
}

if (Test-Path "apps_shared\logic\data_access\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening apps_shared\logic\data_access\check_rules_policy_check_safety"
    git mv "apps_shared\logic\data_access\check_rules_policy_check_safety/__init__.py" "apps_shared\logic\data_access\check_rules_policy_check_safety.py"
    Remove-Item "apps_shared\logic\data_access\check_rules_policy_check_safety" -Force
}

if (Test-Path "apps_shared\logic\data_access\get_info_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening apps_shared\logic\data_access\get_info_embedding_compare_meaning"
    git mv "apps_shared\logic\data_access\get_info_embedding_compare_meaning/__init__.py" "apps_shared\logic\data_access\get_info_embedding_compare_meaning.py"
    Remove-Item "apps_shared\logic\data_access\get_info_embedding_compare_meaning" -Force
}

if (Test-Path "apps_shared\logic\data_access\get_info_understand_request\__init__.py") {
    Write-Host "Flattening apps_shared\logic\data_access\get_info_understand_request"
    git mv "apps_shared\logic\data_access\get_info_understand_request/__init__.py" "apps_shared\logic\data_access\get_info_understand_request.py"
    Remove-Item "apps_shared\logic\data_access\get_info_understand_request" -Force
}

if (Test-Path "apps_shared\logic\data_access\get_info_utility_prepare_information\__init__.py") {
    Write-Host "Flattening apps_shared\logic\data_access\get_info_utility_prepare_information"
    git mv "apps_shared\logic\data_access\get_info_utility_prepare_information/__init__.py" "apps_shared\logic\data_access\get_info_utility_prepare_information.py"
    Remove-Item "apps_shared\logic\data_access\get_info_utility_prepare_information" -Force
}

if (Test-Path "apps_shared\logic\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening apps_shared\logic\guardrails\check_rules_policy_check_safety"
    git mv "apps_shared\logic\guardrails\check_rules_policy_check_safety/__init__.py" "apps_shared\logic\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "apps_shared\logic\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "apps_shared\logic\guardrails\manage_costs_state_update\__init__.py") {
    Write-Host "Flattening apps_shared\logic\guardrails\manage_costs_state_update"
    git mv "apps_shared\logic\guardrails\manage_costs_state_update/__init__.py" "apps_shared\logic\guardrails\manage_costs_state_update.py"
    Remove-Item "apps_shared\logic\guardrails\manage_costs_state_update" -Force
}

if (Test-Path "apps_shared\logic\synthesis\check_format_policy_check_safety\__init__.py") {
    Write-Host "Flattening apps_shared\logic\synthesis\check_format_policy_check_safety"
    git mv "apps_shared\logic\synthesis\check_format_policy_check_safety/__init__.py" "apps_shared\logic\synthesis\check_format_policy_check_safety.py"
    Remove-Item "apps_shared\logic\synthesis\check_format_policy_check_safety" -Force
}

if (Test-Path "apps_shared\logic\synthesis\pick_best_result\__init__.py") {
    Write-Host "Flattening apps_shared\logic\synthesis\pick_best_result"
    git mv "apps_shared\logic\synthesis\pick_best_result/__init__.py" "apps_shared\logic\synthesis\pick_best_result.py"
    Remove-Item "apps_shared\logic\synthesis\pick_best_result" -Force
}

if (Test-Path "apps_shared\logic\synthesis\use_tools_routing_retry_task\__init__.py") {
    Write-Host "Flattening apps_shared\logic\synthesis\use_tools_routing_retry_task"
    git mv "apps_shared\logic\synthesis\use_tools_routing_retry_task/__init__.py" "apps_shared\logic\synthesis\use_tools_routing_retry_task.py"
    Remove-Item "apps_shared\logic\synthesis\use_tools_routing_retry_task" -Force
}

if (Test-Path "apps_shared\logic\synthesis\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening apps_shared\logic\synthesis\use_tools_use_a_tool"
    git mv "apps_shared\logic\synthesis\use_tools_use_a_tool/__init__.py" "apps_shared\logic\synthesis\use_tools_use_a_tool.py"
    Remove-Item "apps_shared\logic\synthesis\use_tools_use_a_tool" -Force
}

if (Test-Path "apps_shared\logic\validation\check_format_policy_check_safety\__init__.py") {
    Write-Host "Flattening apps_shared\logic\validation\check_format_policy_check_safety"
    git mv "apps_shared\logic\validation\check_format_policy_check_safety/__init__.py" "apps_shared\logic\validation\check_format_policy_check_safety.py"
    Remove-Item "apps_shared\logic\validation\check_format_policy_check_safety" -Force
}

if (Test-Path "apps_shared\logic\validation\convert\__init__.py") {
    Write-Host "Flattening apps_shared\logic\validation\convert"
    git mv "apps_shared\logic\validation\convert/__init__.py" "apps_shared\logic\validation\convert.py"
    Remove-Item "apps_shared\logic\validation\convert" -Force
}

if (Test-Path "apps_shared\logic\validation\find_problems\__init__.py") {
    Write-Host "Flattening apps_shared\logic\validation\find_problems"
    git mv "apps_shared\logic\validation\find_problems/__init__.py" "apps_shared\logic\validation\find_problems.py"
    Remove-Item "apps_shared\logic\validation\find_problems" -Force
}

if (Test-Path "apps_shared\logic\validation\pick_best_result\__init__.py") {
    Write-Host "Flattening apps_shared\logic\validation\pick_best_result"
    git mv "apps_shared\logic\validation\pick_best_result/__init__.py" "apps_shared\logic\validation\pick_best_result.py"
    Remove-Item "apps_shared\logic\validation\pick_best_result" -Force
}

if (Test-Path "apps_shared\cache\data_access\get_info_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening apps_shared\cache\data_access\get_info_embedding_compare_meaning"
    git mv "apps_shared\cache\data_access\get_info_embedding_compare_meaning/__init__.py" "apps_shared\cache\data_access\get_info_embedding_compare_meaning.py"
    Remove-Item "apps_shared\cache\data_access\get_info_embedding_compare_meaning" -Force
}

if (Test-Path "apps_shared\cache\data_access\get_info_understand_request\__init__.py") {
    Write-Host "Flattening apps_shared\cache\data_access\get_info_understand_request"
    git mv "apps_shared\cache\data_access\get_info_understand_request/__init__.py" "apps_shared\cache\data_access\get_info_understand_request.py"
    Remove-Item "apps_shared\cache\data_access\get_info_understand_request" -Force
}

if (Test-Path "apps_shared\cache\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening apps_shared\cache\guardrails\check_rules_policy_check_safety"
    git mv "apps_shared\cache\guardrails\check_rules_policy_check_safety/__init__.py" "apps_shared\cache\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "apps_shared\cache\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "apps_rg\L1_cognition\P1_retrieve\check_resume_rules\__init__.py") {
    Write-Host "Flattening apps_rg\L1_cognition\P1_retrieve\check_resume_rules"
    git mv "apps_rg\L1_cognition\P1_retrieve\check_resume_rules/__init__.py" "apps_rg\L1_cognition\P1_retrieve\check_resume_rules.py"
    Remove-Item "apps_rg\L1_cognition\P1_retrieve\check_resume_rules" -Force
}

if (Test-Path "apps_rg\L1_cognition\P3_aggregate\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening apps_rg\L1_cognition\P3_aggregate\use_tools_use_a_tool"
    git mv "apps_rg\L1_cognition\P3_aggregate\use_tools_use_a_tool/__init__.py" "apps_rg\L1_cognition\P3_aggregate\use_tools_use_a_tool.py"
    Remove-Item "apps_rg\L1_cognition\P3_aggregate\use_tools_use_a_tool" -Force
}

if (Test-Path "apps_rg\L1_cognition\P4_safety\check_resume_rules\__init__.py") {
    Write-Host "Flattening apps_rg\L1_cognition\P4_safety\check_resume_rules"
    git mv "apps_rg\L1_cognition\P4_safety\check_resume_rules/__init__.py" "apps_rg\L1_cognition\P4_safety\check_resume_rules.py"
    Remove-Item "apps_rg\L1_cognition\P4_safety\check_resume_rules" -Force
}

if (Test-Path "apps_lic\L1_cognition\P1_retrieve\check_outreach_rules\__init__.py") {
    Write-Host "Flattening apps_lic\L1_cognition\P1_retrieve\check_outreach_rules"
    git mv "apps_lic\L1_cognition\P1_retrieve\check_outreach_rules/__init__.py" "apps_lic\L1_cognition\P1_retrieve\check_outreach_rules.py"
    Remove-Item "apps_lic\L1_cognition\P1_retrieve\check_outreach_rules" -Force
}

if (Test-Path "apps_lic\L1_cognition\P1_retrieve\get_info_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening apps_lic\L1_cognition\P1_retrieve\get_info_embedding_compare_meaning"
    git mv "apps_lic\L1_cognition\P1_retrieve\get_info_embedding_compare_meaning/__init__.py" "apps_lic\L1_cognition\P1_retrieve\get_info_embedding_compare_meaning.py"
    Remove-Item "apps_lic\L1_cognition\P1_retrieve\get_info_embedding_compare_meaning" -Force
}

if (Test-Path "apps_lic\L1_cognition\P1_retrieve\get_info_understand_request\__init__.py") {
    Write-Host "Flattening apps_lic\L1_cognition\P1_retrieve\get_info_understand_request"
    git mv "apps_lic\L1_cognition\P1_retrieve\get_info_understand_request/__init__.py" "apps_lic\L1_cognition\P1_retrieve\get_info_understand_request.py"
    Remove-Item "apps_lic\L1_cognition\P1_retrieve\get_info_understand_request" -Force
}

if (Test-Path "apps_lic\L1_cognition\P1_retrieve\get_info_utility_prepare_information\__init__.py") {
    Write-Host "Flattening apps_lic\L1_cognition\P1_retrieve\get_info_utility_prepare_information"
    git mv "apps_lic\L1_cognition\P1_retrieve\get_info_utility_prepare_information/__init__.py" "apps_lic\L1_cognition\P1_retrieve\get_info_utility_prepare_information.py"
    Remove-Item "apps_lic\L1_cognition\P1_retrieve\get_info_utility_prepare_information" -Force
}

if (Test-Path "apps_lic\L1_cognition\P3_aggregate\pick_message_refinement_adjust_scores\__init__.py") {
    Write-Host "Flattening apps_lic\L1_cognition\P3_aggregate\pick_message_refinement_adjust_scores"
    git mv "apps_lic\L1_cognition\P3_aggregate\pick_message_refinement_adjust_scores/__init__.py" "apps_lic\L1_cognition\P3_aggregate\pick_message_refinement_adjust_scores.py"
    Remove-Item "apps_lic\L1_cognition\P3_aggregate\pick_message_refinement_adjust_scores" -Force
}

if (Test-Path "apps_lic\L1_cognition\P3_aggregate\use_tools_routing_retry_task\__init__.py") {
    Write-Host "Flattening apps_lic\L1_cognition\P3_aggregate\use_tools_routing_retry_task"
    git mv "apps_lic\L1_cognition\P3_aggregate\use_tools_routing_retry_task/__init__.py" "apps_lic\L1_cognition\P3_aggregate\use_tools_routing_retry_task.py"
    Remove-Item "apps_lic\L1_cognition\P3_aggregate\use_tools_routing_retry_task" -Force
}

if (Test-Path "apps_lic\L1_cognition\P3_aggregate\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening apps_lic\L1_cognition\P3_aggregate\use_tools_use_a_tool"
    git mv "apps_lic\L1_cognition\P3_aggregate\use_tools_use_a_tool/__init__.py" "apps_lic\L1_cognition\P3_aggregate\use_tools_use_a_tool.py"
    Remove-Item "apps_lic\L1_cognition\P3_aggregate\use_tools_use_a_tool" -Force
}

if (Test-Path "apps_lic\L1_cognition\P4_safety\check_outreach_rules\__init__.py") {
    Write-Host "Flattening apps_lic\L1_cognition\P4_safety\check_outreach_rules"
    git mv "apps_lic\L1_cognition\P4_safety\check_outreach_rules/__init__.py" "apps_lic\L1_cognition\P4_safety\check_outreach_rules.py"
    Remove-Item "apps_lic\L1_cognition\P4_safety\check_outreach_rules" -Force
}

if (Test-Path "agentic_core\L3_orchestration\data_access\get_info_understand_request\__init__.py") {
    Write-Host "Flattening agentic_core\L3_orchestration\data_access\get_info_understand_request"
    git mv "agentic_core\L3_orchestration\data_access\get_info_understand_request/__init__.py" "agentic_core\L3_orchestration\data_access\get_info_understand_request.py"
    Remove-Item "agentic_core\L3_orchestration\data_access\get_info_understand_request" -Force
}

if (Test-Path "agentic_core\L3_orchestration\guardrails\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening agentic_core\L3_orchestration\guardrails\check_rules_policy_check_safety"
    git mv "agentic_core\L3_orchestration\guardrails\check_rules_policy_check_safety/__init__.py" "agentic_core\L3_orchestration\guardrails\check_rules_policy_check_safety.py"
    Remove-Item "agentic_core\L3_orchestration\guardrails\check_rules_policy_check_safety" -Force
}

if (Test-Path "agentic_core\L3_orchestration\synthesis\use_tools_routing_retry_task\__init__.py") {
    Write-Host "Flattening agentic_core\L3_orchestration\synthesis\use_tools_routing_retry_task"
    git mv "agentic_core\L3_orchestration\synthesis\use_tools_routing_retry_task/__init__.py" "agentic_core\L3_orchestration\synthesis\use_tools_routing_retry_task.py"
    Remove-Item "agentic_core\L3_orchestration\synthesis\use_tools_routing_retry_task" -Force
}

if (Test-Path "agentic_core\L3_orchestration\synthesis\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening agentic_core\L3_orchestration\synthesis\use_tools_use_a_tool"
    git mv "agentic_core\L3_orchestration\synthesis\use_tools_use_a_tool/__init__.py" "agentic_core\L3_orchestration\synthesis\use_tools_use_a_tool.py"
    Remove-Item "agentic_core\L3_orchestration\synthesis\use_tools_use_a_tool" -Force
}

if (Test-Path "agentic_core\L2_execution\tools\routing_retry_task\__init__.py") {
    Write-Host "Flattening agentic_core\L2_execution\tools\routing_retry_task"
    git mv "agentic_core\L2_execution\tools\routing_retry_task/__init__.py" "agentic_core\L2_execution\tools\routing_retry_task.py"
    Remove-Item "agentic_core\L2_execution\tools\routing_retry_task" -Force
}

if (Test-Path "agentic_core\L1_cognition\P1_retrieve\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P1_retrieve\check_rules_policy_check_safety"
    git mv "agentic_core\L1_cognition\P1_retrieve\check_rules_policy_check_safety/__init__.py" "agentic_core\L1_cognition\P1_retrieve\check_rules_policy_check_safety.py"
    Remove-Item "agentic_core\L1_cognition\P1_retrieve\check_rules_policy_check_safety" -Force
}

if (Test-Path "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P1_retrieve\gather_context_inputs"
    git mv "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs/__init__.py" "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs.py"
    Remove-Item "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs" -Force
}

if (Test-Path "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_embedding_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_embedding_embedding_compare_meaning"
    git mv "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_embedding_embedding_compare_meaning/__init__.py" "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_embedding_embedding_compare_meaning.py"
    Remove-Item "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_embedding_embedding_compare_meaning" -Force
}

if (Test-Path "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_integrate_source_signals\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_integrate_source_signals"
    git mv "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_integrate_source_signals/__init__.py" "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_integrate_source_signals.py"
    Remove-Item "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_integrate_source_signals" -Force
}

if (Test-Path "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_integrate_source_signals_understand_request\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_integrate_source_signals_understand_request"
    git mv "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_integrate_source_signals_understand_request/__init__.py" "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_integrate_source_signals_understand_request.py"
    Remove-Item "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_integrate_source_signals_understand_request" -Force
}

if (Test-Path "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_understand\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_understand"
    git mv "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_understand/__init__.py" "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_understand.py"
    Remove-Item "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_understand" -Force
}

if (Test-Path "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_utility\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_utility"
    git mv "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_utility/__init__.py" "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_utility.py"
    Remove-Item "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_utility" -Force
}

if (Test-Path "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_utility_utility_prepare_information\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_utility_utility_prepare_information"
    git mv "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_utility_utility_prepare_information/__init__.py" "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_utility_utility_prepare_information.py"
    Remove-Item "agentic_core\L1_cognition\P1_retrieve\gather_context_inputs_utility_utility_prepare_information" -Force
}

if (Test-Path "agentic_core\L1_cognition\P1_retrieve\get_info_understand_request\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P1_retrieve\get_info_understand_request"
    git mv "agentic_core\L1_cognition\P1_retrieve\get_info_understand_request/__init__.py" "agentic_core\L1_cognition\P1_retrieve\get_info_understand_request.py"
    Remove-Item "agentic_core\L1_cognition\P1_retrieve\get_info_understand_request" -Force
}

if (Test-Path "agentic_core\L1_cognition\P2_inspect\check_structure_policy\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P2_inspect\check_structure_policy"
    git mv "agentic_core\L1_cognition\P2_inspect\check_structure_policy/__init__.py" "agentic_core\L1_cognition\P2_inspect\check_structure_policy.py"
    Remove-Item "agentic_core\L1_cognition\P2_inspect\check_structure_policy" -Force
}

if (Test-Path "agentic_core\L1_cognition\P2_inspect\check_structure_policy_check_safety\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P2_inspect\check_structure_policy_check_safety"
    git mv "agentic_core\L1_cognition\P2_inspect\check_structure_policy_check_safety/__init__.py" "agentic_core\L1_cognition\P2_inspect\check_structure_policy_check_safety.py"
    Remove-Item "agentic_core\L1_cognition\P2_inspect\check_structure_policy_check_safety" -Force
}

if (Test-Path "agentic_core\L1_cognition\P2_inspect\check_structure_semantic_semantic_adjust_scores\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P2_inspect\check_structure_semantic_semantic_adjust_scores"
    git mv "agentic_core\L1_cognition\P2_inspect\check_structure_semantic_semantic_adjust_scores/__init__.py" "agentic_core\L1_cognition\P2_inspect\check_structure_semantic_semantic_adjust_scores.py"
    Remove-Item "agentic_core\L1_cognition\P2_inspect\check_structure_semantic_semantic_adjust_scores" -Force
}

if (Test-Path "agentic_core\L1_cognition\P2_inspect\convert_content\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P2_inspect\convert_content"
    git mv "agentic_core\L1_cognition\P2_inspect\convert_content/__init__.py" "agentic_core\L1_cognition\P2_inspect\convert_content.py"
    Remove-Item "agentic_core\L1_cognition\P2_inspect\convert_content" -Force
}

if (Test-Path "agentic_core\L1_cognition\P2_inspect\convert_core_content\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P2_inspect\convert_core_content"
    git mv "agentic_core\L1_cognition\P2_inspect\convert_core_content/__init__.py" "agentic_core\L1_cognition\P2_inspect\convert_core_content.py"
    Remove-Item "agentic_core\L1_cognition\P2_inspect\convert_core_content" -Force
}

if (Test-Path "agentic_core\L1_cognition\P2_inspect\convert_core_content_embedding_embedding_compare_meaning\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P2_inspect\convert_core_content_embedding_embedding_compare_meaning"
    git mv "agentic_core\L1_cognition\P2_inspect\convert_core_content_embedding_embedding_compare_meaning/__init__.py" "agentic_core\L1_cognition\P2_inspect\convert_core_content_embedding_embedding_compare_meaning.py"
    Remove-Item "agentic_core\L1_cognition\P2_inspect\convert_core_content_embedding_embedding_compare_meaning" -Force
}

if (Test-Path "agentic_core\L1_cognition\P2_inspect\convert_core_content_semantic\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P2_inspect\convert_core_content_semantic"
    git mv "agentic_core\L1_cognition\P2_inspect\convert_core_content_semantic/__init__.py" "agentic_core\L1_cognition\P2_inspect\convert_core_content_semantic.py"
    Remove-Item "agentic_core\L1_cognition\P2_inspect\convert_core_content_semantic" -Force
}

if (Test-Path "agentic_core\L1_cognition\P2_inspect\convert_core_content_semantic_semantic_adjust_scores\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P2_inspect\convert_core_content_semantic_semantic_adjust_scores"
    git mv "agentic_core\L1_cognition\P2_inspect\convert_core_content_semantic_semantic_adjust_scores/__init__.py" "agentic_core\L1_cognition\P2_inspect\convert_core_content_semantic_semantic_adjust_scores.py"
    Remove-Item "agentic_core\L1_cognition\P2_inspect\convert_core_content_semantic_semantic_adjust_scores" -Force
}

if (Test-Path "agentic_core\L1_cognition\P2_inspect\detect_anomalies_analyze_symptoms\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P2_inspect\detect_anomalies_analyze_symptoms"
    git mv "agentic_core\L1_cognition\P2_inspect\detect_anomalies_analyze_symptoms/__init__.py" "agentic_core\L1_cognition\P2_inspect\detect_anomalies_analyze_symptoms.py"
    Remove-Item "agentic_core\L1_cognition\P2_inspect\detect_anomalies_analyze_symptoms" -Force
}

if (Test-Path "agentic_core\L1_cognition\P2_inspect\detect_anomalies_analyze_symptoms_update_memory\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P2_inspect\detect_anomalies_analyze_symptoms_update_memory"
    git mv "agentic_core\L1_cognition\P2_inspect\detect_anomalies_analyze_symptoms_update_memory/__init__.py" "agentic_core\L1_cognition\P2_inspect\detect_anomalies_analyze_symptoms_update_memory.py"
    Remove-Item "agentic_core\L1_cognition\P2_inspect\detect_anomalies_analyze_symptoms_update_memory" -Force
}

if (Test-Path "agentic_core\L1_cognition\P3_aggregate\pick_best_result\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P3_aggregate\pick_best_result"
    git mv "agentic_core\L1_cognition\P3_aggregate\pick_best_result/__init__.py" "agentic_core\L1_cognition\P3_aggregate\pick_best_result.py"
    Remove-Item "agentic_core\L1_cognition\P3_aggregate\pick_best_result" -Force
}

if (Test-Path "agentic_core\L1_cognition\P3_aggregate\pick_best_result_understand_request\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P3_aggregate\pick_best_result_understand_request"
    git mv "agentic_core\L1_cognition\P3_aggregate\pick_best_result_understand_request/__init__.py" "agentic_core\L1_cognition\P3_aggregate\pick_best_result_understand_request.py"
    Remove-Item "agentic_core\L1_cognition\P3_aggregate\pick_best_result_understand_request" -Force
}

if (Test-Path "agentic_core\L1_cognition\P3_aggregate\select_optimal_evaluate_options\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P3_aggregate\select_optimal_evaluate_options"
    git mv "agentic_core\L1_cognition\P3_aggregate\select_optimal_evaluate_options/__init__.py" "agentic_core\L1_cognition\P3_aggregate\select_optimal_evaluate_options.py"
    Remove-Item "agentic_core\L1_cognition\P3_aggregate\select_optimal_evaluate_options" -Force
}

if (Test-Path "agentic_core\L1_cognition\P3_aggregate\select_optimal_evaluate_options_understand_request\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P3_aggregate\select_optimal_evaluate_options_understand_request"
    git mv "agentic_core\L1_cognition\P3_aggregate\select_optimal_evaluate_options_understand_request/__init__.py" "agentic_core\L1_cognition\P3_aggregate\select_optimal_evaluate_options_understand_request.py"
    Remove-Item "agentic_core\L1_cognition\P3_aggregate\select_optimal_evaluate_options_understand_request" -Force
}

if (Test-Path "agentic_core\L1_cognition\P3_aggregate\select_optimal_refinement_semantic_adjust_scores\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P3_aggregate\select_optimal_refinement_semantic_adjust_scores"
    git mv "agentic_core\L1_cognition\P3_aggregate\select_optimal_refinement_semantic_adjust_scores/__init__.py" "agentic_core\L1_cognition\P3_aggregate\select_optimal_refinement_semantic_adjust_scores.py"
    Remove-Item "agentic_core\L1_cognition\P3_aggregate\select_optimal_refinement_semantic_adjust_scores" -Force
}

if (Test-Path "agentic_core\L1_cognition\P3_aggregate\sync_status_update_memory\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P3_aggregate\sync_status_update_memory"
    git mv "agentic_core\L1_cognition\P3_aggregate\sync_status_update_memory/__init__.py" "agentic_core\L1_cognition\P3_aggregate\sync_status_update_memory.py"
    Remove-Item "agentic_core\L1_cognition\P3_aggregate\sync_status_update_memory" -Force
}

if (Test-Path "agentic_core\L1_cognition\P3_aggregate\sync_status_update_memory_update_memory\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P3_aggregate\sync_status_update_memory_update_memory"
    git mv "agentic_core\L1_cognition\P3_aggregate\sync_status_update_memory_update_memory/__init__.py" "agentic_core\L1_cognition\P3_aggregate\sync_status_update_memory_update_memory.py"
    Remove-Item "agentic_core\L1_cognition\P3_aggregate\sync_status_update_memory_update_memory" -Force
}

if (Test-Path "agentic_core\L1_cognition\P3_aggregate\sync_status_utility\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P3_aggregate\sync_status_utility"
    git mv "agentic_core\L1_cognition\P3_aggregate\sync_status_utility/__init__.py" "agentic_core\L1_cognition\P3_aggregate\sync_status_utility.py"
    Remove-Item "agentic_core\L1_cognition\P3_aggregate\sync_status_utility" -Force
}

if (Test-Path "agentic_core\L1_cognition\P3_aggregate\sync_status_utility_utility_prepare_information\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P3_aggregate\sync_status_utility_utility_prepare_information"
    git mv "agentic_core\L1_cognition\P3_aggregate\sync_status_utility_utility_prepare_information/__init__.py" "agentic_core\L1_cognition\P3_aggregate\sync_status_utility_utility_prepare_information.py"
    Remove-Item "agentic_core\L1_cognition\P3_aggregate\sync_status_utility_utility_prepare_information" -Force
}

if (Test-Path "agentic_core\L1_cognition\P3_aggregate\use_tools_routing_retry_task\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P3_aggregate\use_tools_routing_retry_task"
    git mv "agentic_core\L1_cognition\P3_aggregate\use_tools_routing_retry_task/__init__.py" "agentic_core\L1_cognition\P3_aggregate\use_tools_routing_retry_task.py"
    Remove-Item "agentic_core\L1_cognition\P3_aggregate\use_tools_routing_retry_task" -Force
}

if (Test-Path "agentic_core\L1_cognition\P3_aggregate\use_tools_use_a_tool\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P3_aggregate\use_tools_use_a_tool"
    git mv "agentic_core\L1_cognition\P3_aggregate\use_tools_use_a_tool/__init__.py" "agentic_core\L1_cognition\P3_aggregate\use_tools_use_a_tool.py"
    Remove-Item "agentic_core\L1_cognition\P3_aggregate\use_tools_use_a_tool" -Force
}

if (Test-Path "agentic_core\L1_cognition\P4_safety\check_rules_policy_check_safety\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P4_safety\check_rules_policy_check_safety"
    git mv "agentic_core\L1_cognition\P4_safety\check_rules_policy_check_safety/__init__.py" "agentic_core\L1_cognition\P4_safety\check_rules_policy_check_safety.py"
    Remove-Item "agentic_core\L1_cognition\P4_safety\check_rules_policy_check_safety" -Force
}

if (Test-Path "agentic_core\L1_cognition\P4_safety\control_resources_track_usage\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P4_safety\control_resources_track_usage"
    git mv "agentic_core\L1_cognition\P4_safety\control_resources_track_usage/__init__.py" "agentic_core\L1_cognition\P4_safety\control_resources_track_usage.py"
    Remove-Item "agentic_core\L1_cognition\P4_safety\control_resources_track_usage" -Force
}

if (Test-Path "agentic_core\L1_cognition\P4_safety\control_resources_track_usage_update_memory\__init__.py") {
    Write-Host "Flattening agentic_core\L1_cognition\P4_safety\control_resources_track_usage_update_memory"
    git mv "agentic_core\L1_cognition\P4_safety\control_resources_track_usage_update_memory/__init__.py" "agentic_core\L1_cognition\P4_safety\control_resources_track_usage_update_memory.py"
    Remove-Item "agentic_core\L1_cognition\P4_safety\control_resources_track_usage_update_memory" -Force
}

