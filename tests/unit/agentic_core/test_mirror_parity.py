"""
file: tests/migration/test_mirror_parity.py
description: |
    Verifies that the tests/ directory strictly mirrors the source tree.
    Explicitly checks L0, L5, and L6 layers.
"""
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def test_mirror_structure_exactness():
    # Critical files that MUST be mirrored if they exist in source
    critical_pairs = [
        # L5 Safety
        ("agentic_core/L5_safety/guardrails.py", "tests/unit/agentic_core/L5_safety/test_guardrails.py"),
        # L0 Maintenance
        ("agentic_core/L0_maintenance/arch_guard.py", "tests/unit/agentic_core/L0_maintenance/test_arch_guard.py"),
        # L6 Observability (Explicit check)
        ("agentic_core/L6_observability/trace.py", "tests/unit/agentic_core/L6_observability/test_trace.py")
    ]
    
    failures = []
    for src_rel, test_rel in critical_pairs:
        src = PROJECT_ROOT / src_rel
        expected_test = PROJECT_ROOT / test_rel
        
        if src.exists():
            if not expected_test.exists():
                # Check if it drifted elsewhere
                found = list(PROJECT_ROOT.glob(f"**/test_{src.stem}.py"))
                loc = found[0] if found else "NOWHERE"
                failures.append(f"Broken Mirror: {src.name} -> Found at {loc}, Expected {expected_test}")

    assert not failures, f"Mirror Parity Failed:\n" + "\n".join(failures)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])