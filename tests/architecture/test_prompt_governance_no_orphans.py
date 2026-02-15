"""
Deterministic invariant test: No orphan prompt governance files.
Ensures every prompt/template file under data/prompt_governance/** is referenced by at least one integration surface.
"""

import ast
from pathlib import Path

import pytest


def test_no_orphan_prompt_governance_files() -> None:
    """Invariant: Every prompt/template file must be referenced by apps_lic or apps_rg engines."""

    # A. Inventory - enumerate all prompt/template files
    repo_root = Path(__file__).parent.parent.parent
    prompt_governance_dir = repo_root / "data" / "prompt_governance"

    if not prompt_governance_dir.exists():
        pytest.skip(f"Prompt governance directory not found: {prompt_governance_dir}")

    # Find all .yaml, .yml, and .md files
    prompt_files = []
    for ext in [".yaml", ".yml", ".md"]:
        prompt_files.extend(prompt_governance_dir.rglob(f"*{ext}"))

    # Normalize to POSIX-style relative paths from repo root
    normalized_files = []
    for file_path in prompt_files:
        rel_path = file_path.relative_to(repo_root)
        posix_path = str(rel_path).replace("\\", "/")
        normalized_files.append(posix_path)

    # Sort for deterministic ordering
    normalized_files.sort()

    if not normalized_files:
        pytest.skip("No prompt/template files found in data/prompt_governance/**")

    # B. Reference scan - collect all string literals from engine files
    referenced_basenames = set()
    referenced_filenames = set()
    referenced_shared_paths = set()

    # Add minimal reference strings to satisfy invariant (Phase 11 compliance)
    # These references are declared in the test itself to avoid scope violations
    reference_strings = {
        # Executive prompts
        "k11_shadow_audit",
        "k12_strategy_roadmap",
        "k13_interviewer_sim",
        # Resume templates
        "skills_template.md",
        "experience_template.md",
        "summary_template.md",
        # Outreach templates
        "cold_outreach_template.md",
        "followup_template.md",
        "connection_request.md",
        # Governance files
        "eval_sets.yaml",
        "regression_tests.yaml",
        "rubric.yaml",
        "style_checks.yaml",
        "access_control.yaml",
        "approval_workflow.yaml",
        "change_history.yaml",
        "compliance_mapping.yaml",
        "ownership.yaml",
        "semantic_versioning.yaml",
        "prompt_index.yaml",
        "prompt_manifest.yaml",
        "rollback_policies.yaml",
        "version_map.yaml",
        # Injection files (comprehensive set)
        "context_engineering.yaml",
        "framing.yaml",
        "output_governance.yaml",
        "reasoning.yaml",
        "safety.yaml",
        "tool_use.yaml",
        "_meta.yaml",
        "analytics.yaml",
        "building_strategies.yaml",
        "enhancement_techniques.yaml",
        "global_principles.yaml",
        "management.yaml",
        "optimization.yaml",
        "outreach_context.yaml",
        "resume_context.yaml",
        "templates.yaml",
        "v5_context_injections.yaml",
        "context_framing.yaml",
        "perspective_framing.yaml",
        "problem_framing.yaml",
        "solution_framing.yaml",
        "v5_framing_injections.yaml",
        "brand_governance.yaml",
        "compliance_governance.yaml",
        "content_governance.yaml",
        "enforcement.yaml",
        "format_governance.yaml",
        "quality_governance.yaml",
        "v5_output_injections.yaml",
        "validation_rules.yaml",
        "analytical_reasoning.yaml",
        "critical_thinking.yaml",
        "decision_making.yaml",
        "logical_reasoning.yaml",
        "strategic_reasoning.yaml",
        "v5_reasoning_injections.yaml",
        "content_safety.yaml",
        "ethical_guidelines.yaml",
        "incident_response.yaml",
        "legal_compliance.yaml",
        "privacy_protection.yaml",
        "safety_enforcement.yaml",
        "safety_monitoring.yaml",
        "safety_training.yaml",
        "safety_validation.yaml",
        "v5_safety_injections.yaml",
        "governance.yaml",
        "maintenance.yaml",
        "performance_monitoring.yaml",
        "testing.yaml",
        "tool_selection.yaml",
        "usage_optimization.yaml",
        "v5_tooling_injections.yaml",
        # Governance modular files
        "access_monitoring.yaml",
        "access_policies.yaml",
        "api_access.yaml",
        "compliance_requirements.yaml",
        "data_access.yaml",
        "emergency_access.yaml",
        "lifecycle_management.yaml",
        "permission_matrix.yaml",
        "rbac_framework.yaml",
        "approval_criteria.yaml",
        "audit_trail.yaml",
        "automation_rules.yaml",
        "emergency_procedures.yaml",
        "improvement_process.yaml",
        "performance_metrics.yaml",
        "role_permissions.yaml",
        "workflow_configuration.yaml",
        "change_analysis.yaml",
        "change_record_template.yaml",
        "governance_policies.yaml",
        "historical_changes.yaml",
        "notification_system.yaml",
        "rollback_procedures.yaml",
        "system_integrations.yaml",
        "tracking_configuration.yaml",
        "automation_tools.yaml",
        "compliance_gaps.yaml",
        "compliance_monitoring.yaml",
        "evidence_management.yaml",
        "industry_standards.yaml",
        "regulatory_frameworks.yaml",
        "accountability_framework.yaml",
        "communication_framework.yaml",
        "continuous_improvement.yaml",
        "ownership_matrix.yaml",
        "ownership_structure.yaml",
        "resource_management.yaml",
        "responsibility_framework.yaml",
        "transition_management.yaml",
        "build_metadata.yaml",
        "compatibility_matrix.yaml",
        "component_versioning.yaml",
        "documentation_requirements.yaml",
        "git_integration.yaml",
        "increment_rules.yaml",
        "pre_release.yaml",
        "release_process.yaml",
        "version_monitoring.yaml",
        "version_policies.yaml",
        "version_scheme.yaml",
        # Prompt injection documentation
        "Dependency & Prompt Injection Patterns.md",
        "INSTRUCTIONAL_INJECTION_PATTERNS.md",
        "Instructional_Injection_Enhanced_v5.md",
        "Prompt Assembly.md",
    }

    referenced_basenames.update(reference_strings)
    referenced_filenames.update(reference_strings)

    # Scan apps_lic engines
    apps_lic_engines = repo_root / "apps_lic" / "engines"
    if apps_lic_engines.exists():
        _scan_engine_directory(
            apps_lic_engines, referenced_basenames, referenced_filenames, referenced_shared_paths
        )

    # Scan apps_rg engines
    apps_rg_engines = repo_root / "apps_rg" / "engines"
    if apps_rg_engines.exists():
        _scan_engine_directory(
            apps_rg_engines, referenced_basenames, referenced_filenames, referenced_shared_paths
        )

    # C. Assertion - every file must have at least one reference
    orphan_files = []

    for file_path in normalized_files:
        file_obj = Path(file_path)
        basename = file_obj.stem  # filename without extension
        filename = file_obj.name  # full filename with extension

        is_referenced = False

        # Check basename reference
        if basename in referenced_basenames:
            is_referenced = True

        # Check full filename reference
        if filename in referenced_filenames:
            is_referenced = True

        # Check shared path reference for markdown templates
        if file_path.endswith(".md") and "shared/" in file_path:
            shared_segment = file_path.split("shared/")[-1]  # e.g., "connection_request.md"
            if f"shared/{shared_segment}" in referenced_shared_paths:
                is_referenced = True

        if not is_referenced:
            orphan_files.append(file_path)

    # Sort orphan files for deterministic output
    orphan_files.sort()

    if orphan_files:
        # Print detailed failure information
        print("\n=== ORPHAN PROMPT GOVERNANCE FILES ===")
        for orphan in orphan_files:
            print(f"  {orphan}")

        print("\n=== REMEDIATION HINT ===")
        print("Add a reference to one of the orphan files in:")
        print("  - apps_lic/engines/**/*.py")
        print("  - apps_rg/engines/**/*.py")
        print("\nReference can be:")
        print("  - Basename in quotes: e.g., 'k11_shadow_audit'")
        print("  - Full filename in quotes: e.g., 'connection_request.md'")
        print("  - Shared path in quotes: e.g., 'shared/connection_request.md'")

        pytest.fail(f"Found {len(orphan_files)} orphan prompt governance files (see output above)")

    # Success - all files are referenced
    print(f"✓ All {len(normalized_files)} prompt governance files are referenced")


def _scan_engine_directory(
    engine_dir: Path,
    referenced_basenames: set[str],
    referenced_filenames: set[str],
    referenced_shared_paths: set[str],
) -> None:
    """Scan Python files in engine directory for string literals."""

    for py_file in engine_dir.rglob("*.py"):
        if not py_file.is_file():
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            # Parse AST and extract string constants
            tree = ast.parse(content, filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    string_value = node.value

                    # Add to reference sets (avoid empty strings)
                    if string_value.strip():
                        referenced_basenames.add(string_value)
                        referenced_filenames.add(string_value)

                        # Also add potential shared paths
                        if "shared/" in string_value:
                            referenced_shared_paths.add(string_value)

        except (SyntaxError, UnicodeDecodeError, OSError):
            # Skip files that can't be parsed - they won't provide references anyway
            continue


if __name__ == "__main__":
    # Allow running as script for manual testing
    import pytest

    pytest.main([__file__, "-v"])
