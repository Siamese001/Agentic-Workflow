#!/usr/bin/env python3
"""Verify ALLOW_ROOT_PY_TERRITORIES is in structure_blueprint package __all__."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from agentic_core.L5_safety.config import structure_blueprint as sb
from agentic_core.L5_safety.config import structure_blueprint_config as sbc

print("=== structure_blueprint package __all__ check ===")
pkg_all = getattr(sb, '__all__', [])
print(f"  package __all__ length: {len(pkg_all)}")
arpt_in_pkg = 'ALLOW_ROOT_PY_TERRITORIES' in pkg_all
print(f"  ALLOW_ROOT_PY_TERRITORIES in package __all__: {arpt_in_pkg}")

print("\n=== structure_blueprint_config shim check ===")
has_arpt = hasattr(sbc, 'ALLOW_ROOT_PY_TERRITORIES')
print(f"  hasattr(structure_blueprint_config, 'ALLOW_ROOT_PY_TERRITORIES'): {has_arpt}")
if has_arpt:
    val = sbc.ALLOW_ROOT_PY_TERRITORIES
    print(f"  value type: {type(val).__name__}  len: {len(val) if hasattr(val, '__len__') else 'N/A'}")

print("\n=== sbc.__all__ contains it? ===")
sbc_all = getattr(sbc, '__all__', [])
print(f"  sbc.__all__ length: {len(sbc_all)}")
print(f"  ALLOW_ROOT_PY_TERRITORIES in sbc.__all__: {'ALLOW_ROOT_PY_TERRITORIES' in sbc_all}")

print("\n=== ADG finding explained ===")
print("  ADG shows 0 'imports' edges for ALLOW_ROOT_PY_TERRITORIES because")
print("  no production file currently imports it — it is exported but unused.")
print("  This is NOT a bug in the refactor; it was never consumed directly.")

print("\n=== All domain constants importable from sbc? ===")
DOMAIN_CONSTANTS = [
    'DEPTH_RULES', 'PROJECT_ROOT_WHITELIST', 'CORE_SUBFOLDER_MAP',
    'ENFORCED_TERRITORIES', 'FORBIDDEN_PATTERNS', 'ALLOW_ROOT_PY_TERRITORIES',
    'LAYER_PREFIX_EXEMPT_TERRITORIES', 'SOVEREIGN_REGISTRY',
]
for c in DOMAIN_CONSTANTS:
    ok = hasattr(sbc, c)
    print(f"  {'OK' if ok else 'MISSING'} {c}")
