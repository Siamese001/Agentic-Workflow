"""Fix remaining unit test files with eager imports."""

import re
from pathlib import Path

REPO_ROOT = Path("c:/Git/Agentic-Workflow")

# Unit test files with eager imports (from grep scan)
UNIT_FILES = [
    "tests/unit/agentic_core/prompt_governance/contracts/test_lifecycle_contracts.py",
    "tests/unit/agentic_core/L0_routing/engines/test_phase3_advanced_features.py",
    "tests/unit/agentic_core/L0_routing/engines/test_phase2_multi_model_integration.py",
    "tests/unit/agentic_core/L0_routing/scripts/test_path_setup.py",
    "tests/unit/agentic_core/L5_safety/reasoning/test_FileClassificationAgent_e2e/conftest.py",
    "tests/unit/agentic_core/L5_safety/test_hollow_file_detector.py",
    "tests/unit/agentic_core/L5_safety/validators/test_anti_pattern_scanner_validator_enhanced.py",
    "tests/unit/agentic_core/L0_routing/types/test_guardian_contract_types.py",
    "tests/unit/agentic_core/L4_state/enforcement/test_graph_memory_bridge_concurrency.py",
    "tests/unit/agentic_core/L4_state/enforcement/test_graph_memory_bridge_isolation.py",
    "tests/unit/agentic_core/L4_state/memory/test_faiss_store.py",
    "tests/unit/agentic_core/L4_state/memory/test_l1_exact_cache.py",
    "tests/unit/agentic_core/L5_safety/validators/test_anti_pattern_scanner_validator_adg.py",
    "tests/unit/agentic_core/adg/extraction/test_static_scanner.py",
]


def fix_file(filepath: Path) -> int:
    """Convert eager imports to lazy fixtures."""
    content = filepath.read_text(encoding="utf-8")
    original = content

    # Pattern to find agentic_core imports (single and multi-line)
    import_pattern = r"^(from agentic_core[^\n]+(?:\n[^\n\S]+[^\n]+)*)"
    imports = re.findall(import_pattern, content, re.MULTILINE)

    if not imports:
        return 0

    # Build fixtures
    fixtures = ["# Lazy import fixtures - avoid collection-time errors"]
    for i, imp in enumerate(imports):
        lines = imp.strip().split("\n")
        if len(lines) == 1:
            match = re.match(r"from\s+(\S+)\s+import\s+(.+)", imp.strip())
            if match:
                module = match.group(1)
                names = [n.strip() for n in match.group(2).split(",")]
            else:
                continue
        else:
            first_line = lines[0].strip()
            module_match = re.match(r"from\s+(\S+)\s+import", first_line)
            if not module_match:
                continue
            module = module_match.group(1)
            names = []
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("("):
                    line = line[1:]
                if ")" in line:
                    line = line[: line.index(")")]
                names.extend([n.strip() for n in line.split(",") if n.strip()])

        fixture_name = f"_lazy_{module.replace('.', '_')}_{i}"
        names_str = ", ".join(names)
        attrs = ", ".join(f'"{n}": {n}' for n in names)

        fixture = f"""@pytest.fixture(scope="session")
def {fixture_name}():
    from {module} import {names_str}
    return type('_Import', (), {{{attrs}}})"""
        fixtures.append(fixture)

    fixtures_code = "\n\n".join(fixtures)

    # Remove old imports
    new_content = re.sub(import_pattern, "", content, flags=re.MULTILINE)

    # Insert fixtures after pytest import
    if "import pytest" in new_content:
        new_content = new_content.replace(
            "import pytest",
            f"import pytest\n\n{fixtures_code}",
        )
    else:
        new_content = f"import pytest\n\n{fixtures_code}\n\n{new_content}"

    # Clean up blank lines
    new_content = re.sub(r"\n{4,}", "\n\n\n", new_content)

    if new_content != original:
        filepath.write_text(new_content, encoding="utf-8")
        return len(imports)
    return 0


def main():
    total = 0
    for file_path in UNIT_FILES:
        full_path = REPO_ROOT / file_path
        if full_path.exists():
            fixes = fix_file(full_path)
            if fixes:
                print(f"✅ {file_path}: fixed {fixes} import(s)")
                total += fixes
            else:
                print(f"ℹ️  {file_path}: no agentic_core imports found (or already fixed)")
        else:
            print(f"⚠️  {file_path}: file not found")

    print(f"\n{'=' * 50}")
    print(f"Unit test files: {total} eager imports converted")


if __name__ == "__main__":
    main()
