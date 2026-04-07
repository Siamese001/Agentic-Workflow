#!/usr/bin/env python3
"""Fix hardcoded C:\Git\Agentic-Workflow paths in Python files.

Replaces hardcoded absolute paths with dynamic resolution using
Path(__file__).resolve().parents[X] patterns.
"""

from pathlib import Path

# Patterns to replace
REPO_ROOT = Path(__file__).resolve().parents[2]

# Files to fix (from grep results)
FILES_TO_FIX = {
    "tools/testing/test_mcp_comprehensive.py": {
        "C:\\\\Git\\\\Agentic-Workflow\\.windsurf\\mcp_config.json": "REPO_ROOT / '.windsurf' / 'mcp_config.json'",
        "C:\\\\Git\\\\Agentic-Workflow": "str(REPO_ROOT)",
        "C:\\\\Git\\\\Agentic-Workflow\\mcp_test_results.json": "REPO_ROOT / 'mcp_test_results.json'",
    },
    "tools/testing/test_all_mcp_servers.py": {
        "C:\\\\Git\\\\Agentic-Workflow\\.windsurf\\mcp_config.json": "REPO_ROOT / '.windsurf' / 'mcp_config.json'",
    },
    "tools/fix/fix_import_tests.py": {
        "'c:\\\\Git\\\\Agentic-Workflow'": "str(REPO_ROOT)",
    },
    "tools/debug/debug_filesystem_mcp.py": {
        "C:\\\\Git\\\\Agentic-Workflow\\.windsurf\\mcp_config.json": "REPO_ROOT / '.windsurf' / 'mcp_config.json'",
        "'C:\\\\Git\\\\Agentic-Workflow'": "str(REPO_ROOT)",
        '"C:\\\\Git\\\\Agentic-Workflow"': "str(REPO_ROOT)",
        "C:\\\\Git\\\\Agentic-Workflow\\filesystem_debug_results.json": "REPO_ROOT / 'filesystem_debug_results.json'",
    },
    "tools/analysis/extract_skipped_tests.py": {
        '"C:\\\\Git\\\\Agentic-Workflow"': "str(REPO_ROOT)",
    },
    "tools/analysis/_compare_adg_format.py": {
        "'C:\\\\Git\\\\Agentic-WorkFlow\\artifacts\\adg\\adg_file_graph_20260311T171158Z.zip'": "str(REPO_ROOT / 'artifacts' / 'adg' / 'adg_file_graph_20260311T171158Z.zip')",
        "'C:\\\\Git\\\\Agentic-Workflow\\artifacts\\adg'": "str(REPO_ROOT / 'artifacts' / 'adg')",
        "'C:\\\\Git\\\\Agentic-Workflow\\artifacts\\adg\\_prior_format'": "str(REPO_ROOT / 'artifacts' / 'adg' / '_prior_format')",
    },
    "tools/adg/_adg_heal_subgraph.py": {
        "'C:\\\\Git\\\\Agentic-Workflow\\artifacts\\adg'": "str(REPO_ROOT / 'artifacts' / 'adg')",
    },
    "tools/adg/_adg_inspect_nodes.py": {
        "'C:\\\\Git\\\\Agentic-Workflow\\artifacts\\adg'": "str(REPO_ROOT / 'artifacts' / 'adg')",
    },
    "tools/analysis/analyze_missing_imports.py": {
        '"C:\\\\Git\\\\Agentic-Workflow"': "str(REPO_ROOT)",
    },
    "ops_scripts/ci/generate_mcp_configs.py": {
        '"C:\\\\Git\\\\Agentic-Workflow\\tools\\adg\\adg_mcp_server.py"': "str(REPO_ROOT / 'tools' / 'adg' / 'adg_mcp_server.py')",
        '"C:\\\\Git\\\\Agentic-Workflow"': "str(REPO_ROOT)",
        '"C:\\\\Git\\\\Agentic-Workflow\\artifacts\\adg"': "str(REPO_ROOT / 'artifacts' / 'adg')",
        '"C:\\\\Git\\\\Agentic-Workflow\\tools\\memory\\adg_memory_server.py"': "str(REPO_ROOT / 'tools' / 'memory' / 'adg_memory_server.py')",
        '"C:\\\\Git\\\\Agentic-Workflow\\artifacts\\memory\\knowledge_graph.sqlite"': "str(REPO_ROOT / 'artifacts' / 'memory' / 'knowledge_graph.sqlite')",
    },
    "ops_scripts/ci/_run_heal_with_mutation.py": {
        "'c:\\\\Git\\\\Agentic-Workflow'": "str(REPO_ROOT)",
    },
    "ops_scripts/ci/_trace_inject.py": {
        "'c:\\\\Git\\\\Agentic-Workflow'": "str(REPO_ROOT)",
    },
    "tests/unit/agentic_core/L0_routing/utils/test_path_util.py": {
        '"C:\\\\Git\\\\Agentic-Workflow"': "str(REPO_ROOT)",
    },
    "ops_scripts/general/architectural_guard.py": {
        "'C:\\\\Git\\\\Agentic-Workflow\\apps_shared\\common_utils'": "str(REPO_ROOT / 'apps_shared' / 'common_utils')",
    },
    "ops_scripts/general/file_disposition.py": {
        "'C:\\\\Git\\\\Agentic-Workflow\\apps_shared\\common_utils'": "str(REPO_ROOT / 'apps_shared' / 'common_utils')",
        "'C:\\\\Git\\\\Agentic-Workflow'": "str(REPO_ROOT)",
    },
    "ops_scripts/general/fix_test_headers.py": {
        "'Source: C\\\\Git\\\\Agentic-Workflow'": "'Source: ' + str(REPO_ROOT)",
    },
    "ops_scripts/general/verify_global_imports.py": {
        "'C:\\\\Git\\\\Agentic-Workflow'": "str(REPO_ROOT)",
    },
    "ops_scripts/general/logic_signature.py": {
        "'C:\\\\Git\\\\Agentic-Workflow\\archives\\Reachout Engine Archive'": "str(REPO_ROOT / 'archives' / 'Reachout Engine Archive')",
        "'C:\\\\Git\\\\Agentic-Workflow\\archives\\resume_gen_json'": "str(REPO_ROOT / 'archives' / 'resume_gen_json')",
        '"C:\\\\Git\\\\Agentic-Workflow\\apps_rg"': "str(REPO_ROOT / 'apps_rg')",
    },
    "apps_shared/scripts/fix_all_dataclass_underscores.py": {
        '"c:\\\\Git\\\\Agentic-Workflow\\agentic_core\\schemas\\models\\core_contracts_types.py"': "str(REPO_ROOT / 'agentic_core' / 'schemas' / 'models' / 'core_contracts_types.py')",
    },
    "apps_rg/scripts/rg_json_miner.py": {
        '"C:\\\\Git\\\\Agentic-Workflow\\archives\\resume_gen_json"': "str(REPO_ROOT / 'archives' / 'resume_gen_json')",
        '"C:\\\\Git\\\\Agentic-Workflow\\apps_rg\\RG_JSON_KNOWLEDGE_MAP.md"': "str(REPO_ROOT / 'apps_rg' / 'RG_JSON_KNOWLEDGE_MAP.md')",
    },
    "agentic_core/L5_safety/enforcement/agent_info_enforcer.py": {
        '"C:\\\\Git\\\\Agentic-WorkFlow\\\\"': "str(REPO_ROOT / '')",
        '"C:\\\\Git\\\\Agentic-Workflow\\agentic_core"': "str(REPO_ROOT / 'agentic_core')",
        '"C:\\\\Git\\\\Agentic-Workflow\\ast_redundancy_report.json"': "str(REPO_ROOT / 'ast_redundancy_report.json')",
    },
}


def fix_file(file_path: Path, replacements: dict[str, str]) -> int:
    """Apply replacements to a file."""
    content = file_path.read_text(encoding="utf-8")
    original = content

    for old, new in replacements.items():
        content = content.replace(old, new)

    # Add import for Path if needed
    if "REPO_ROOT" in content and "from pathlib import Path" not in content:
        # Find the first import and add after it
        lines = content.split("\n")
        import_idx = -1
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                import_idx = i
            elif not line.startswith("import ") and not line.startswith("from ") and import_idx >= 0:
                # Add import after last import
                lines.insert(import_idx + 1, "from pathlib import Path")
                lines.insert(import_idx + 2, "")
                content = "\n".join(lines)
                break

    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return 1
    return 0


def main():
    """Fix all hardcoded paths."""
    fixed_count = 0
    for rel_path, replacements in FILES_TO_FIX.items():
        file_path = REPO_ROOT / rel_path
        if file_path.exists():
            fixed = fix_file(file_path, replacements)
            if fixed:
                print(f"Fixed: {rel_path}")
                fixed_count += fixed
        else:
            print(f"Not found: {rel_path}")

    print(f"\nTotal files fixed: {fixed_count}")


if __name__ == "__main__":
    main()
