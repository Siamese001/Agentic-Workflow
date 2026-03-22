#!/usr/bin/env python3
"""Check exact __all__ contents of structure_blueprint package."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from agentic_core.L5_safety.config import structure_blueprint as sb
from agentic_core.L5_safety.config import structure_blueprint_config as sbc

pkg_all = sorted(getattr(sb, '__all__', []))
sbc_all = sorted(getattr(sbc, '__all__', []))

print(f"structure_blueprint.__all__: {len(pkg_all)} names")
print(f"structure_blueprint_config.__all__: {len(sbc_all)} names")

# Check specific constants
checks = [
    'ALLOW_ROOT_PY_TERRITORIES',
    'LAYER_PREFIX_EXEMPT_TERRITORIES',
    'DEPTH_RULES',
    'PROJECT_ROOT_WHITELIST',
    'CORE_SUBFOLDER_MAP',
    'ENFORCED_TERRITORIES',
    'FORBIDDEN_PATTERNS',
    'SOVEREIGN_REGISTRY',
]
print("\n=== Key constants availability ===")
for c in checks:
    in_sb  = c in pkg_all
    in_sbc = c in sbc_all
    has_sb  = hasattr(sb, c)
    has_sbc = hasattr(sbc, c)
    print(f"  {c}")
    print(f"    structure_blueprint:        __all__={in_sb}  hasattr={has_sb}")
    print(f"    structure_blueprint_config: __all__={in_sbc}  hasattr={has_sbc}")

# Find what's in structure_blueprint but missing from sbc
missing_in_sbc = [n for n in pkg_all if n not in sbc_all]
print(f"\n=== In structure_blueprint.__all__ but NOT in sbc.__all__: {len(missing_in_sbc)} ===")
for n in missing_in_sbc:
    print(f"  {n}")

# Check if LAYER_PREFIX_EXEMPT_TERRITORIES is accessible via `from structure_blueprint import *`
print("\n=== location_validator import path check ===")
print("  Imports: from agentic_core.L5_safety.config.structure_blueprint import LAYER_PREFIX_EXEMPT_TERRITORIES")
print(f"  Available via that path: {hasattr(sb, 'LAYER_PREFIX_EXEMPT_TERRITORIES')}")
