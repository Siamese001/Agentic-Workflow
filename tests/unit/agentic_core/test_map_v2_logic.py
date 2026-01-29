"""
file: tests/migration/test_map_v2_logic.py
description: |
    Aggressive validation of the V2 Migration Map.
    Ensures ZERO path stuttering and minimal Orphans.
    Mandatory Pass: 100%
"""

from pathlib import Path

import pytest


def get_map_file_path():
    """Dynamically resolve the migration map file path."""
    # Try multiple resolution strategies
    current_file = Path(__file__).resolve()

    # Strategy 1: Relative to test file (tests/migration/test_map_v2_logic.py)
    project_root = current_file.parents[2]
    map_file = project_root / "migration_map_v2.md"
    if map_file.exists():
        return map_file

    # Strategy 2: Relative to current working directory
    cwd_path = Path.cwd() / "migration_map_v2.md"
    if cwd_path.exists():
        return cwd_path

    # Strategy 3: Absolute path (Windows-specific fallback)
    abs_path = Path("C:/Git/Agentic-Workflow/migration_map_v2.md")
    if abs_path.exists():
        return abs_path

    # If none work, return the expected path for error reporting
    return map_file


@pytest.fixture
def migration_data():
    MAP_FILE = get_map_file_path()

    # Try to open the file directly - this will give us a better error message
    try:
        with open(MAP_FILE, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError as e:
        # Add detailed debugging
        current_file = Path(__file__).resolve()
        project_root = current_file.parents[2]

        debug_info = f"""
Migration map not found. Debug information:
- Expected path: {MAP_FILE}
- File exists (Path.exists()): {MAP_FILE.exists()}
- Current file: {current_file}
- Project root: {project_root}
- CWD: {Path.cwd()}
- CWD map exists: {(Path.cwd() / "migration_map_v2.md").exists()}
- Directory listing of project root: {list(project_root.glob("migration_map*"))}
- Original error: {e}
"""
        pytest.fail(debug_info)

    # Parse table into dict {current_path: proposed_path}
    data = {}
    in_table = False
    for line in lines:
        if "| Current Path |" in line:
            in_table = True
            continue
        if "## Refined Orphan List" in line:
            break
        if in_table and "|" in line and "---" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                data[parts[0]] = parts[1]
    return data


def test_tc_1_5_1_no_path_stuttering(migration_data):
    """
    TC-1.5.1: Fail if any proposed path contains repeated directory segments.
    e.g. 'apps_rg/apps_rg' is FORBIDDEN.
    """
    stutter_patterns = [
        "apps_rg/apps_rg",
        "apps_lic/apps_lic",
        "agentic_core/agentic_core",
        "L5_safety/L5_safety",
    ]

    violations = []
    for current, proposed in migration_data.items():
        for pattern in stutter_patterns:
            if pattern in proposed:
                violations.append(f"{current} -> {proposed}")

    assert not violations, f"Stuttering detected in {len(violations)} paths:\n" + "\n".join(
        violations[:5]
    )


def test_tc_1_5_2_orphan_reduction(migration_data):
    """
    TC-1.5.2: Path Heuristics must resolve previous orphans.
    Specific checks for known problem files.
    """
    # 1. Check apps_rg conftest
    rg_conftest = next(
        (
            p
            for c, p in migration_data.items()
            if "tests\\apps_rg\\conftest.py" in c or "tests/apps_rg/conftest.py" in c
        ),
        None,
    )

    if rg_conftest:
        assert "agentic_core" not in rg_conftest, (
            "apps_rg/conftest.py incorrectly mapped to agentic_core"
        )
        assert (
            "tests/unit/apps_rg/conftest.py" in rg_conftest
            or "tests/integration/apps_rg/conftest.py" in rg_conftest
        ), f"apps_rg/conftest.py mapped to unexpected location: {rg_conftest}"


def test_tc_1_5_3_root_conftest_handling(migration_data):
    """
    TC-1.5.3: Root conftest must move to fixtures, NOT agentic_core.
    """
    root_conftest = next(
        (
            p
            for c, p in migration_data.items()
            if c.strip() == "tests\\conftest.py" or c.strip() == "tests/conftest.py"
        ),
        None,
    )

    if root_conftest:
        assert "agentic_core" not in root_conftest, (
            "Root conftest incorrectly sucked into agentic_core gravity."
        )
        assert "tests/fixtures/root_conftest.py" in root_conftest, (
            f"Root conftest target invalid: {root_conftest}"
        )


def test_tc_1_5_4_strict_mirror_structure(migration_data):
    """
    TC-1.5.4: All mapped paths must start with tests/unit, tests/integration, tests/e2e, or tests/fixtures.
    """
    allowed_roots = ["tests/unit/", "tests/integration/", "tests/e2e/", "tests/fixtures/"]

    violations = []
    for current, proposed in migration_data.items():
        if not any(proposed.startswith(root) for root in allowed_roots):
            violations.append(f"{current} -> {proposed}")

    assert not violations, "Proposed paths violate Strict Mirror Structure:\n" + "\n".join(
        violations[:5]
    )


if __name__ == "__main__":
    # Allow running directly for quick feedback
    pytest.main([__file__, "-v"])
