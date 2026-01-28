"""
file: tests/migration/test_import_reality.py
description: |
    Validates that 'agentic_core' is the REAL production package.
    Fails if the module has no __file__ attribute (often true for mocks)
    or if it doesn't point to the expected physical location.
"""
import pytest
import sys
import os
from pathlib import Path

# Robust project root detection - find directory containing agentic_core
_file_path = Path(__file__).resolve()
PROJECT_ROOT = _file_path.parent
while PROJECT_ROOT != PROJECT_ROOT.parent:
    if (PROJECT_ROOT / "agentic_core").is_dir():
        break
    PROJECT_ROOT = PROJECT_ROOT.parent


def test_agentic_core_is_real():
    """
    Verifies agentic_core is not a stub.
    """
    # 1. Force import
    try:
        import agentic_core
    except ImportError:
        pytest.fail("CRITICAL: agentic_core cannot be imported.")

    # 2. Check for Reality
    if not hasattr(agentic_core, "__file__"):
        pytest.fail(
            f"SOVEREIGNTY VIOLATION: agentic_core has no __file__. "
            f"It is likely a Namespace Stub or Mock.\n"
            f"Sys Modules: {sys.modules['agentic_core']}"
        )
    
    # 3. Check Location
    pkg_path = Path(agentic_core.__file__).parent
    expected_path = PROJECT_ROOT / "agentic_core"
    
    # Resolve symlinks for strict comparison
    try:
        pkg_path = pkg_path.resolve()
        expected_path = expected_path.resolve()
    except OSError:
        pass

    assert pkg_path == expected_path, (
        f"LOCATION VIOLATION: Imported agentic_core is at {pkg_path}, "
        f"expected {expected_path}"
    )


def test_agentic_core_has_init(disable_path_shield):
    """
    Verifies agentic_core has a proper __init__.py file.
    Requires disable_path_shield to bypass test fixture mocks.
    """
    import agentic_core
    # Use the imported module's path to find __init__.py
    if hasattr(agentic_core, "__file__") and agentic_core.__file__:
        init_path = agentic_core.__file__
        # Use os.path.exists for Windows compatibility
        assert os.path.exists(init_path), (
            f"STRUCTURE VIOLATION: {init_path} does not exist. "
            f"Package may be incomplete."
        )
        assert os.path.basename(init_path) == "__init__.py", (
            f"STRUCTURE VIOLATION: agentic_core.__file__ is {init_path}, "
            f"expected __init__.py"
        )
    else:
        pytest.fail(
            "STRUCTURE VIOLATION: agentic_core has no __file__ attribute."
        )


def test_key_submodules_importable():
    """
    Verifies key agentic_core submodules are importable.
    """
    critical_modules = [
        "agentic_core.L0_maintenance",
        "agentic_core.L5_safety",
        "agentic_core.base_agents",
    ]
    
    for module_name in critical_modules:
        try:
            __import__(module_name)
        except ImportError as e:
            pytest.fail(
                f"IMPORT FAILURE: Cannot import {module_name}. "
                f"Error: {e}"
            )


def test_no_phantom_sys_modules():
    """
    Verifies there are no phantom/duplicate agentic_core entries in sys.modules.
    """
    agentic_entries = [k for k in sys.modules.keys() if "agentic_core" in k]
    
    # Check that main entry exists
    assert "agentic_core" in sys.modules, (
        "agentic_core not in sys.modules after import"
    )
    
    # Check that entries have valid __file__ attributes
    for entry in agentic_entries[:10]:  # Check first 10
        mod = sys.modules.get(entry)
        if mod is not None and hasattr(mod, "__file__") and mod.__file__:
            mod_path = Path(mod.__file__)
            # Should be under PROJECT_ROOT
            try:
                mod_path.relative_to(PROJECT_ROOT)
            except ValueError:
                pytest.fail(
                    f"PHANTOM MODULE: {entry} is at {mod_path}, "
                    f"which is outside PROJECT_ROOT {PROJECT_ROOT}"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
