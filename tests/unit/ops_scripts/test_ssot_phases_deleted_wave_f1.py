"""Wave F1 regression: `_ssot_phases.py` has been deleted as orphaned dead code.

Finding during F1.1 fan-in scan (2026-04-21):
  - Zero Python importers of `_ssot_phases.py`
  - Its parent module `execute_ssot.py` was already deleted
  - No `if __name__ == "__main__":` CLI entry point
  - Only references outside the file itself are in ADG snapshots, plan docs,
    and one CI-gate exempt list

The file was 1635 lines of dead code. The planned "migration to L2 healers"
(parent plan P3.FUTURE) collapsed to a pure deletion because nothing needed
to be ported.

Plan reference: `.windsurf/plans/routing-followups-7a2c91.md` Wave F1.
Parent plan: `.windsurf/plans/routing-unification-qwen-abe735.md` P3.FUTURE.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_ssot_phases_module_file_is_deleted():
    """The source file must not exist in the repo."""
    path = Path("ops_scripts/dev_tools/L0_routing_scripts/_ssot_phases.py")
    assert not path.exists(), (
        f"{path} must remain deleted. If this test fails, a restoration was "
        "committed in error — remove the file again."
    )


def test_ssot_phases_module_cannot_be_imported():
    """ImportError is the correct behavior — the module has been removed."""
    with pytest.raises((ImportError, ModuleNotFoundError)):
        import ops_scripts.dev_tools.L0_routing_scripts._ssot_phases  # noqa: F401, PLC0415


def test_ssot_routing_still_exists_as_wave3_shim():
    """`_ssot_routing.py` remains alive as a Wave 3 shim for the 9 existing
    tests in `test_ssot_routing_wave3_shim.py`. Full deletion requires
    migrating those tests first and is deferred to a future plan.
    """
    path = Path("ops_scripts/dev_tools/L0_routing_scripts/_ssot_routing.py")
    assert path.exists(), "_ssot_routing.py must remain until shim tests migrate"
