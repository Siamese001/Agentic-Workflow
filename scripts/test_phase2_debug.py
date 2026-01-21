"""Debug script for Phase 2 test categorization"""

import shutil
import tempfile
from pathlib import Path

from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

# Create test structure
tmp = tempfile.mkdtemp()
tmp_path = Path(tmp)

try:
    # Setup tests violation
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_login_e2e.py").write_text("# E2E test")
    (tests_dir / "test_math_unit.py").write_text("# Unit test")

    # Setup apps_shared
    (tmp_path / "apps_shared").mkdir()

    # Test with auto_approve
    agent = HierarchyAgent(tmp_path, healing_enabled=True, auto_approve=True)
    print(f"Agent auto_approve: {agent._auto_approve}")
    print(f"Gatekeeper require_approval: {agent.gatekeeper._require_approval}")

    # Debug: Check what files are found
    from agentic_core.utils.ssot_discovery import get_python_files

    print("\nFiles found by get_python_files in tests/:")
    for f in get_python_files(tests_dir):
        print(f"  {f.relative_to(tmp_path)}")

    results = agent.relocate_misplaced_files()
    print("\nResults:")
    print(f"  violations_found: {results['violations_found']}")
    print(f"  files_relocated: {results['files_relocated']}")
    print(f"  roots_processed: {results['roots_processed']}")

    print("\nFile locations:")
    print(f"  E2E categorized: {(tests_dir / 'e2e' / 'test_login_e2e.py').exists()}")
    print(f"  Unit categorized: {(tests_dir / 'unit' / 'test_math_unit.py').exists()}")
    print(f"  Original e2e exists: {(tests_dir / 'test_login_e2e.py').exists()}")
    print(f"  Original unit exists: {(tests_dir / 'test_math_unit.py').exists()}")

finally:
    shutil.rmtree(tmp)
