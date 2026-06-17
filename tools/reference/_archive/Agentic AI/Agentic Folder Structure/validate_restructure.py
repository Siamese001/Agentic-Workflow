#!/usr/bin/env python3
"""
Validation script for the restructured YAML to ensure all 14 legacy editor completion criteria are met
"""

import yaml


def validate_yaml_structure():
    """Validate the restructured YAML against all completion criteria"""

    # Load YAML
    try:
        with open("unified_structure_restructured.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        print("✅ YAML parses correctly")
    except Exception as e:
        print(f"❌ YAML parsing error: {e}")
        return False

    # Track validation results
    results = {}

    # CRITERION 1: No "-ops" anywhere
    def check_no_ops(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if "-ops" in key:
                    return False, f"Found '-ops' in: {path}/{key}"
                result = check_no_ops(value, f"{path}/{key}")
                if not result[0]:
                    return result
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                result = check_no_ops(item, f"{path}[{i}]")
                if not result[0]:
                    return result
        return True, ""

    no_ops_result = check_no_ops(data)
    results["NO_OPS_ANYWHERE"] = no_ops_result[0]
    print(f"✅ No '-ops' anywhere: {no_ops_result[0]}")
    if not no_ops_result[0]:
        print(f"   ❌ {no_ops_result[1]}")

    # CRITERION 2: Engine names are shortened
    expected_engines = ["rg", "lic", "shared"]
    actual_engines = list(data.get("agentic-directory", {}).get("apps", {}).keys())
    engines_correct = set(actual_engines) == set(expected_engines)
    results["ENGINE_NAMES_SHORTENED"] = engines_correct
    print(f"✅ Engine names shortened: {engines_correct}")
    if not engines_correct:
        print(f"   Expected: {expected_engines}, Actual: {actual_engines}")

    # CRITERION 3: Layer names shortened
    expected_layers = ["plan-layer", "orc-layer", "exec-layer", "mem-layer", "safe-layer"]

    def check_layers(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in expected_layers:
                    continue
                # Check if this looks like a layer (has phase groups)
                if isinstance(value, dict) and any("phase" in k for k in value.keys()):
                    return False, f"Unexpected layer name: {key}"
                result = check_layers(value)
                if not result[0]:
                    return result
        return True, ""

    layers_result = check_layers(data)
    results["LAYER_NAMES_SHORTENED"] = layers_result[0]
    print(f"✅ Layer names shortened: {layers_result[0]}")
    if not layers_result[0]:
        print(f"   ❌ {layers_result[1]}")

    # CRITERION 4: L4 domains are engine-specific
    rg_domains = [
        "get-resume-info",
        "score-job-fit",
        "pick-best-resume-content",
        "check-resume-rules",
        "check-resume-structure",
        "use-resume-tools",
        "update-resume-state",
        "find-resume-problems",
        "improve-resume-output",
        "manage-resume-costs",
        "understand-resume-meaning",
        "convert-resume-to-vectors",
    ]

    lic_domains = [
        "get-recipient-info",
        "score-personalization",
        "pick-best-message",
        "check-outreach-rules",
        "check-message-structure",
        "use-message-tools",
        "update-outreach-state",
        "find-message-problems",
        "improve-message-output",
        "manage-outreach-costs",
        "understand-message-meaning",
        "convert-message-to-vectors",
    ]

    shared_domains = [
        "get-shared-info",
        "convert-shared-content",
        "pick-best-result",
        "combine-scores",
        "check-data-structure",
        "check-shared-rules",
        "use-shared-tools",
        "update-shared-state",
        "find-shared-problems",
        "improve-shared-output",
        "manage-shared-costs",
        "understand-shared-meaning",
    ]

    def check_engine_domains(obj, engine_name, expected_domains, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if engine_name in path and key in expected_domains:
                    continue
                elif (
                    engine_name in path and key not in expected_domains and "-" in key and "phase" not in key
                ):
                    return False, f"Unexpected domain in {engine_name}: {key}"
                result = check_engine_domains(value, engine_name, expected_domains, f"{path}/{key}")
                if not result[0]:
                    return result
        return True, ""

    rg_domains_result = check_engine_domains(data, "rg", rg_domains)
    lic_domains_result = check_engine_domains(data, "lic", lic_domains)
    shared_domains_result = check_engine_domains(data, "shared", shared_domains)

    domains_correct = rg_domains_result[0] and lic_domains_result[0] and shared_domains_result[0]
    results["ENGINE_SPECIFIC_DOMAINS"] = domains_correct
    print(f"✅ Engine-specific L4 domains: {domains_correct}")
    if not domains_correct:
        for result in [rg_domains_result, lic_domains_result, shared_domains_result]:
            if not result[0]:
                print(f"   ❌ {result[1]}")

    # CRITERION 5: L5 names are short (≤10 chars)
    expected_l5 = ["general", "utility", "policy", "semantic", "routing", "embedding", "refinement"]

    def check_l5_names(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in expected_l5:
                    continue
                # Check if this looks like L5 (has L6 children)
                if isinstance(value, dict) and len(key) <= 10 and "-" not in key:
                    return False, f"Unexpected L5 name: {key}"
                result = check_l5_names(value, f"{path}/{key}")
                if not result[0]:
                    return result
        return True, ""

    l5_result = check_l5_names(data)
    results["L5_NAMES_SHORT"] = l5_result[0]
    print(f"✅ L5 names are short (≤10 chars): {l5_result[0]}")
    if not l5_result[0]:
        print(f"   ❌ {l5_result[1]}")

    # CRITERION 6: L6 names are layman-friendly
    expected_l6 = [
        "understand-request",
        "prepare-information",
        "compare-meaning",
        "adjust-scores",
        "retry-task",
        "update-memory",
        "use-a-tool",
        "check-safety",
    ]

    def check_l6_names(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in expected_l6:
                    continue
                # Check if this looks like L6 (has L7 files)
                if isinstance(value, dict) and any(
                    str(k).endswith(".py") or str(k) == "null" for k in value.values()
                ):
                    return False, f"Unexpected L6 name: {key}"
                result = check_l6_names(value, f"{path}/{key}")
                if not result[0]:
                    return result
        return True, ""

    l6_result = check_l6_names(data)
    results["L6_NAMES_LAYMAN"] = l6_result[0]
    print(f"✅ L6 names are layman-friendly: {l6_result[0]}")
    if not l6_result[0]:
        print(f"   ❌ {l6_result[1]}")

    # CRITERION 7: All paths under 160 characters
    def check_path_lengths(obj, current_path="", max_length=160):
        violations = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{current_path}/{key}" if current_path else key
                if len(new_path) > max_length:
                    violations.append(f"Path too long ({len(new_path)} chars): {new_path}")
                violations.extend(check_path_lengths(value, new_path, max_length))
        return violations

    path_violations = check_path_lengths(data)
    results["PATHS_UNDER_160"] = len(path_violations) == 0
    print(f"✅ All paths under 160 chars: {len(path_violations) == 0}")
    if path_violations:
        for violation in path_violations[:5]:  # Show first 5 violations
            print(f"   ❌ {violation}")
        if len(path_violations) > 5:
            print(f"   ... and {len(path_violations) - 5} more")

    # CRITERION 8: Exact 7-level structure
    def check_depth(obj, current_depth=1, target_depth=7):
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Check if we've reached a file (L7)
                if isinstance(value, dict) and any(
                    str(k).endswith(".py") or str(k) == "null" for k in value.values()
                ):
                    if current_depth != target_depth:
                        return False, f"File at wrong depth: {key} at depth {current_depth}"
                else:
                    result = check_depth(value, current_depth + 1, target_depth)
                    if not result[0]:
                        return result
        return True, ""

    depth_result = check_depth(data)
    results["EXACT_7_LEVELS"] = depth_result[0]
    print(f"✅ Exact 7-level structure: {depth_result[0]}")
    if not depth_result[0]:
        print(f"   ❌ {depth_result[1]}")

    # CRITERION 9: L7 filenames have semantic signal
    def check_l7_filenames(obj, path=""):
        violations = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict) and any(str(k).endswith(".py") for k in value.keys()):
                    for filename in value.keys():
                        if str(filename).endswith(".py") and len(str(filename)) < 10:
                            violations.append(f"Short filename: {path}/{key}/{filename}")
                violations.extend(check_l7_filenames(value, f"{path}/{key}"))
        return violations

    filename_violations = check_l7_filenames(data)
    results["L7_SEMANTIC_FILENAMES"] = len(filename_violations) == 0
    print(f"✅ L7 filenames have semantic signal: {len(filename_violations) == 0}")
    if filename_violations:
        for violation in filename_violations[:3]:
            print(f"   ❌ {violation}")

    # CRITERION 10: No empty directories
    def check_no_empty_dirs(obj, path=""):
        violations = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict) and len(value) == 0:
                    violations.append(f"Empty directory: {path}/{key}")
                elif isinstance(value, dict):
                    violations.extend(check_no_empty_dirs(value, f"{path}/{key}"))
        return violations

    empty_violations = check_no_empty_dirs(data)
    results["NO_EMPTY_DIRS"] = len(empty_violations) == 0
    print(f"✅ No empty directories: {len(empty_violations) == 0}")
    if empty_violations:
        for violation in empty_violations[:3]:
            print(f"   ❌ {violation}")

    # CRITERION 11: No legacy ops domains remain
    legacy_domains = [
        "retrieval-ops",
        "vectorization-ops",
        "ranking-ops",
        "cost-budget-ops",
        "state-management-ops",
        "constraint-check-ops",
        "diagnostics-ops",
        "schema-validation-ops",
        "tool-adapter-ops",
        "semantic-evaluators",
        "embedding-operations",
        "response-refinement",
    ]

    def check_no_legacy(obj, path=""):
        for key in obj.keys() if isinstance(obj, dict) else []:
            if key in legacy_domains:
                return False, f"Found legacy domain: {path}/{key}"
            if isinstance(obj[key], dict):
                result = check_no_legacy(obj[key], f"{path}/{key}")
                if not result[0]:
                    return result
        return True, ""

    legacy_result = check_no_legacy(data)
    results["NO_LEGACY_DOMAINS"] = legacy_result[0]
    print(f"✅ No legacy ops domains: {legacy_result[0]}")
    if not legacy_result[0]:
        print(f"   ❌ {legacy_result[1]}")

    # CRITERION 12: All L2-L6 names ≤20 characters
    def check_name_lengths(obj, path=""):
        violations = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Check L2-L6 names (not L1 root, not L7 files)
                if len(key) > 20 and not key.endswith(".py") and path != "":
                    violations.append(f"Name too long ({len(key)} chars): {path}/{key}")
                if isinstance(value, dict):
                    violations.extend(check_name_lengths(value, f"{path}/{key}"))
        return violations

    length_violations = check_name_lengths(data)
    results["NAMES_UNDER_20"] = len(length_violations) == 0
    print(f"✅ All L2-L6 names ≤20 chars: {len(length_violations) == 0}")
    if length_violations:
        for violation in length_violations[:3]:
            print(f"   ❌ {violation}")

    # CRITERION 13: YAML is fully valid
    results["YAML_FULLY_VALID"] = True  # Already checked at start

    # CRITERION 14: All completion criteria true
    all_true = all(results.values())
    results["ALL_CRITERIA_TRUE"] = all_true

    print("📊 VALIDATION SUMMARY:")
    passed = sum(results.values())
    total = len(results)
    print(f"   Passed: {passed}/{total} criteria")

    if all_true:
        print("   🎉 ALL CRITERIA MET - Ready to replace original!")
    else:
        print("   ❌ Some criteria failed - review before replacing")
        failed_criteria = [k for k, v in results.items() if not v]
        print(f"   Failed: {failed_criteria}")

    return all_true


if __name__ == "__main__":
    validate_yaml_structure()
