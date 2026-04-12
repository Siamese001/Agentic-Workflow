"""Aggressive cleanup of corrupted test files - fix all remaining patterns."""

import os
import re


def aggressive_clean(filepath):
    """Remove all stray code patterns from test files."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    cleaned = []
    in_class = False
    in_function = False
    indent_level = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Track class/function state
        if stripped.startswith("class "):
            in_class = True
            in_function = False
            cleaned.append(line)
            i += 1
            continue

        if stripped.startswith("def test_"):
            in_function = True
            indent_level = len(line) - len(line.lstrip())
            cleaned.append(line)
            i += 1
            continue

        # Check for stray code at module level after class ends
        if in_class and not in_function:
            # If we see # Arrange, # Act, result = None, assert at module level, skip it
            if any(
                stripped.startswith(x)
                for x in [
                    "# Arrange",
                    "# Act",
                    "# Assert",
                    "result = None",
                    "assert ",
                    "input_data = ",
                    "runtime_context = ",
                ]
            ):
                # Skip this line and keep skipping related lines
                i += 1
                continue

        # If we're in a function and see a bare string followed by # Arrange at wrong indent, skip
        if in_function and stripped.startswith('"""') and "runtime behavior" in stripped:
            # Check if next lines are stray code
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith("# Arrange") or next_line.startswith("# Act"):
                    # Skip the docstring and all stray code until we hit proper indentation or end of file
                    i += 1
                    while i < len(lines):
                        curr_indent = len(lines[i]) - len(lines[i].lstrip())
                        if lines[i].strip() == "" or curr_indent <= indent_level:
                            if lines[i].strip() not in ["", "pass"] and not lines[i].strip().startswith("#"):
                                if curr_indent <= indent_level and (
                                    lines[i].strip().startswith("def ")
                                    or lines[i].strip().startswith("class ")
                                ):
                                    break
                        i += 1
                    continue

        # Remove pytest.main calls at module level
        if stripped.startswith("pytest.main"):
            i += 1
            continue

        cleaned.append(line)
        i += 1

    # Join and clean up multiple blank lines
    content = "".join(cleaned)
    content = re.sub(r"\n{4,}", "\n\n\n", content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# Fix remaining problematic test files
files_to_fix = [
    r"tests\unit\test_campaign_planner_agent.py",
    r"tests\unit\test_content_quality_agent.py",
    r"tests\unit\test_content_strategy_agent.py",
    r"tests\unit\test_dispatch_resume_tools_agent.py",
    r"tests\unit\test_fact_check_agent.py",
    r"tests\unit\test_gap_closure_architect_agent.py",
    r"tests\unit\test_phase23_basic_v2.py",
    r"tests\unit\test_proactive_agent.py",
    r"tests\unit\test_rg_healing_orchestrator.py",
    r"tests\unit\test_rg_reflection_agent.py",
    r"tests\unit\test_rg_resume_orchestrator.py",
    r"tests\unit\test_rg_strategic_planner_agent.py",
    r"tests\unit\test_rg_template_optimizer_agent.py",
    r"tests\unit\test_section_balance_agent.py",
    r"tests\unit\apps_shared\config\test_apps_shared_config_init_adg.py",
    r"tests\unit\apps_shared\enforcement\test_HardenedeventbusStrategy.py",
    r"tests\unit\apps_shared\enforcement\test_ProvenancetrackerStrategy.py",
    r"tests\unit\apps_shared\reasoning\test_InfrastructureOrchestrator.py",
    r"tests\unit\apps_shared\utils\test_security_config_util.py",
    r"tests\unit\apps_lic\reasoning\test_hop_pipeline_executor_adg.py",
    r"tests\unit\apps_lic\utils\test_PIISanitizerSpecialistAgent_util.py",
    r"tests\unit\apps_lic\utils\test_lic_engine_validation_capability_util_adg.py",
    r"tests\unit\apps_rg\engines\utils\test_brand_compliance_agent.py",
    r"tests\unit\apps_rg\engines\utils\test_campaign_planner_agent.py",
    r"tests\unit\apps_rg\engines\utils\test_content_quality_agent.py",
    r"tests\unit\apps_rg\engines\utils\test_fact_check_agent.py",
    r"tests\unit\apps_rg\engines\utils\test_rg_reflection_agent.py",
    r"tests\unit\apps_rg\engines\utils\test_rg_resume_orchestrator.py",
    r"tests\unit\apps_rg\types\test_gap_closure_architect_agent_types_adg.py",
    r"tests\unit\apps_rg\utils\test_authenticity_patterns_util.py",
    r"tests\unit\apps_rg\validators\test_regeneration_validator.py",
]

count = 0
for filepath in files_to_fix:
    if os.path.exists(filepath):
        aggressive_clean(filepath)
        print(f"Fixed: {filepath}")
        count += 1
    else:
        print(f"Not found: {filepath}")

print(f"Fixed {count} files")
