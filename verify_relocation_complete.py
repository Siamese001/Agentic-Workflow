#!/usr/bin/env python3
"""Verify P1_core and domain folder relocations are complete"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.runtime.shared.void_compliance import validate_canonical_hierarchy

project_root = Path(__file__).parent

print("="*70)
print("P1_CORE & DOMAIN RELOCATION VERIFICATION")
print("="*70)

# Check for P1_core folder
p1_core_path = project_root / "agentic_core" / "config" / "P1_core"
domain_path = project_root / "agentic_core" / "domain"

print(f"\n1. Folder Existence Check:")
print(f"   P1_core exists: {p1_core_path.exists()}")
print(f"   domain exists: {domain_path.exists()}")

# Check hierarchy violations
violations = validate_canonical_hierarchy(project_root)

# Filter for P1_core and domain violations
p1_violations = [v for v in violations if 'P1_core' in str(v[0])]
domain_violations = [v for v in violations if 'domain' in str(v[0]).lower()]

print(f"\n2. Hierarchy Violations:")
print(f"   P1_core violations: {len(p1_violations)}")
print(f"   domain violations: {len(domain_violations)}")

if p1_violations:
    print(f"\n   P1_core violations found:")
    for path, reason in p1_violations[:5]:
        print(f"      • {path.name}: {reason[:80]}")

if domain_violations:
    print(f"\n   domain violations found:")
    for path, reason in domain_violations[:5]:
        print(f"      • {path.name}: {reason[:80]}")

# Check blueprint_sovereign has files
blueprint_path = project_root / "agentic_core" / "config" / "blueprint_sovereign"
if blueprint_path.exists():
    file_count = len(list(blueprint_path.glob("*.py")))
    print(f"\n3. blueprint_sovereign status:")
    print(f"   Python files: {file_count}")
    print(f"   structure_blueprint.py exists: {(blueprint_path / 'structure_blueprint.py').exists()}")
else:
    print(f"\n3. ❌ blueprint_sovereign folder not found!")

# Summary
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

if not p1_core_path.exists() and not domain_path.exists():
    print("✅ Unauthorized folders removed")
else:
    print("❌ Unauthorized folders still exist")

if len(p1_violations) == 0 and len(domain_violations) == 0:
    print("✅ No hierarchy violations for P1_core or domain")
else:
    print(f"❌ {len(p1_violations) + len(domain_violations)} violations remaining")

if (blueprint_path / 'structure_blueprint.py').exists():
    print("✅ structure_blueprint.py relocated successfully")
else:
    print("❌ structure_blueprint.py not found in blueprint_sovereign")

print(f"\n{'✅ RELOCATION COMPLETE' if not p1_core_path.exists() and not domain_path.exists() and len(p1_violations) == 0 and len(domain_violations) == 0 else '❌ RELOCATION INCOMPLETE'}")
