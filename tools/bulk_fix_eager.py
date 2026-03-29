"""
Mechanical eager import fixer - converts module-level agentic_core imports
to lazy fixtures using a simple find-and-replace pattern.
"""

import re
from pathlib import Path

REPO_ROOT = Path("c:/Git/Agentic-Workflow")

# Files to process (from the violation scan)
FILES = [
    "tests/architecture/test_wave2_phase2_3_prompt_taxonomy.py",
    "tests/e2e/test_ptc_full_lifecycle_e2e.py",
    "tests/e2e/test_ptc_aggressive_hardening.py",
    "tests/e2e/test_hitl_lifecycle_e2e.py",
    "tests/e2e/test_graphrag_hardened.py",
    "tests/e2e/test_graphrag_e2e.py",
    "tests/e2e/test_prompt_lifecycle_edge_cases_e2e.py",
    "tests/e2e/test_mcp_drift_e2e.py",
    "tests/e2e/test_code_validation_gates_e2e.py",
    "tests/e2e/test_cross_layer_integration_e2e.py",
    "tests/e2e/test_opentelemetry_integration_e2e.py",
    "tests/e2e/test_runtime_adg_l6_observability_e2e.py",
    "tests/integration/test_ptc_full_integration.py",
    "tests/integration/test_depth_violation_no_archive_invariant.py",
    "tests/integration/test_ci_adg_migration.py",
    "tests/integration/test_prompt_lifecycle_pipeline.py",
    "tests/integration/agentic_core/test_redis_l1_retrieval_gate_e2e.py",
    "tests/integration/test_wave4_simple_integration.py",
]


def simple_fix(filepath: Path) -> int:
    """Apply simple eager-to-lazy import conversion.

    Strategy: Replace module-level 'from agentic_core' with fixture-based lazy loading.
    Returns number of fixes applied.
    """
    content = filepath.read_text(encoding="utf-8")
    original = content

    # Find all agentic_core imports (both single and multi-line)
    import_pattern = r'^(from agentic_core[^\n]+(?:\n[^\n\S]+[^\n]+)*)'
    imports = re.findall(import_pattern, content, re.MULTILINE)

    if not imports:
        return 0

    # Build fixture replacement
    fixtures = ["# Lazy import fixtures - avoid collection-time errors"]
    for i, imp in enumerate(imports):
        lines = imp.strip().split('\n')
        if len(lines) == 1:
            # Single line import: from X import A, B, C
            match = re.match(r'from\s+(\S+)\s+import\s+(.+)', imp.strip())
            if match:
                module = match.group(1)
                names = [n.strip() for n in match.group(2).split(',')]
            else:
                continue
        else:
            # Multi-line import with parentheses
            first_line = lines[0].strip()
            module_match = re.match(r'from\s+(\S+)\s+import', first_line)
            if not module_match:
                continue
            module = module_match.group(1)
            # Extract names from subsequent lines
            names = []
            for line in lines[1:]:
                line = line.strip()
                if line.startswith('('):
                    line = line[1:]
                if ')' in line:
                    line = line[:line.index(')')]
                names.extend([n.strip() for n in line.split(',') if n.strip()])

        fixture_name = f"_lazy_{module.replace('.', '_')}_{i}"
        names_str = ", ".join(names)
        attrs = ", ".join(f'"{n}": {n}' for n in names)

        fixture = f'''@pytest.fixture(scope="session")
def {fixture_name}():
    from {module} import {names_str}
    return type('_Import', (), {{{attrs}}})'''
        fixtures.append(fixture)

    fixtures_code = "\n\n".join(fixtures)

    # Replace imports with fixtures in content
    new_content = re.sub(import_pattern, '', content, flags=re.MULTILINE)

    # Insert fixtures after 'import pytest' line
    if 'import pytest' in new_content:
        new_content = new_content.replace(
            'import pytest',
            f'import pytest\n\n{fixtures_code}'
        )
    else:
        # Add pytest import at top
        new_content = f'import pytest\n\n{fixtures_code}\n\n{new_content}'

    # Clean up multiple blank lines
    new_content = re.sub(r'\n{4,}', '\n\n\n', new_content)

    if new_content != original:
        filepath.write_text(new_content, encoding="utf-8")
        return len(imports)
    return 0


def main():
    total = 0
    for file_path in FILES:
        full_path = REPO_ROOT / file_path
        if full_path.exists():
            fixes = simple_fix(full_path)
            if fixes:
                print(f"✅ {file_path}: fixed {fixes} import(s)")
                total += fixes
            else:
                print(f"ℹ️  {file_path}: no agentic_core imports found")
        else:
            print(f"⚠️  {file_path}: file not found")

    print(f"\n{'='*50}")
    print(f"Total: {total} eager imports converted to lazy fixtures")


if __name__ == "__main__":
    main()
