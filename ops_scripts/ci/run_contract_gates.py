#!/usr/bin/env python3
"""Public contract-gate entrypoint with hardened Agent Skills validation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_IMPL_PATH = Path(__file__).with_name("_run_contract_gates_impl.py")
_SPEC = importlib.util.spec_from_file_location("agentic_workflow_contract_gates_impl", _IMPL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Unable to load contract-gate implementation: {_IMPL_PATH}")
_IMPL = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _IMPL
_SPEC.loader.exec_module(_IMPL)

_ORIGINAL_VALIDATE_MCP_HEALTH = _IMPL.validate_mcp_health
_SKILL_GATES = (
    ("skill catalog integrity", "ops_scripts/ci/check_skill_catalog_integrity.py"),
    ("skill evaluation coverage", "ops_scripts/ci/check_skill_eval_coverage.py"),
)


def validate_mcp_health() -> bool:
    """Run the existing MCP/skill checks, then enforce catalog and eval coverage."""

    if not _ORIGINAL_VALIDATE_MCP_HEALTH():
        return False
    for label, relative_path in _SKILL_GATES:
        returncode, stdout, stderr = _IMPL.run_cmd(
            [sys.executable, str(_IMPL._script(relative_path))],
            cwd=_IMPL.ROOT,
        )
        if returncode != 0:
            print(f"❌ {label} check failed")
            print(stdout or stderr)
            return False
        print(f"✅ {label} validated")
    return True


_IMPL.validate_mcp_health = validate_mcp_health

for _name in dir(_IMPL):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_IMPL, _name)
validate_mcp_health = _IMPL.validate_mcp_health


def main() -> None:
    _IMPL.main()


if __name__ == "__main__":
    main()
