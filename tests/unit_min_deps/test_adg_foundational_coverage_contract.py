"""Structural governance contract: fan_in >= 3 modules must have a foundational test.

Enforces §ADG-COVERAGE-POLICY:
  Any production module with fan_in >= FAN_IN_THRESHOLD (3) must be covered by at
  least one non-ADG-derived test file (a file NOT ending in _adg.py).

  Rationale: fan_in >= 3 means at least 3 other modules depend on this module.
  A regression in such a module propagates to 3+ callers — importability-only
  ADG stubs are insufficient; behavioral assertions are required.

  ADG stubs (_adg.py) count only toward GT_covers reachability, not this contract.

Ceiling behaviour (§29-style):
  - On first run, a snapshot is written with the current violation count as the ceiling.
  - Subsequent runs enforce count <= ceiling (no new violations allowed).
  - Ceiling can only be reduced, never increased, by editing the snapshot.
"""

from __future__ import annotations

import ast
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = ROOT / "artifacts" / "structure" / "adg_foundational_coverage_snapshot.json"

FAN_IN_THRESHOLD = 3  # minimum fan_in to require foundational test
FOUNDATIONAL_DEPTH_MIN = 1  # at least 1 assert/raises in the foundational test


# ---------------------------------------------------------------------------
# Scanning helpers (pure AST — no ADG scanner import to stay min-deps)
# ---------------------------------------------------------------------------

_INTERNAL_PREFIXES = (
    "agentic_core",
    "apps_rg",
    "apps_lic",
    "apps_shared",
    "system_learning",
    "ops_scripts",
)


def _is_prod(path: str) -> bool:
    p = path.replace("\\", "/")
    return (
        not p.startswith("tests/")
        and not p.startswith("tools/")
        and "ops_scripts" not in p
        and "__pycache__" not in p
        and p.endswith(".py")
    )


def _collect_prod_modules() -> list[str]:
    """Return relative paths of all production .py files."""
    modules = []
    for root_pkg in _INTERNAL_PREFIXES:
        pkg_dir = ROOT / root_pkg
        if not pkg_dir.exists():
            continue
        for f in pkg_dir.rglob("*.py"):
            if "__pycache__" in f.parts:
                continue
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            if _is_prod(rel):
                modules.append(rel)
    return sorted(modules)


def _build_fan_in(prod_modules: list[str]) -> dict[str, int]:
    """Count inbound import edges per production module via AST scan."""
    # Build dotted->path lookup
    dotted_to_path: dict[str, str] = {}
    for m in prod_modules:
        d = m.removesuffix(".py").replace("/", ".")
        dotted_to_path[d] = m

    fan_in: dict[str, int] = defaultdict(int)

    for m in prod_modules:
        src_path = ROOT / m
        try:
            tree = ast.parse(src_path.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            targets: list[str] = []
            if isinstance(node, ast.Import):
                for alias in node.names:
                    targets.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    targets.append(node.module)
                    # Also check parent (symbol import)
                    parts = node.module.rsplit(".", 1)
                    if len(parts) == 2:
                        targets.append(parts[0])
            for t in targets:
                if t in dotted_to_path:
                    fan_in[dotted_to_path[t]] += 1
                # symbol-level: strip last component
                parent = ".".join(t.rsplit(".", 1)[:-1])
                if parent in dotted_to_path:
                    fan_in[dotted_to_path[parent]] += 1

    return dict(fan_in)


def _count_assertions(path: Path) -> int:
    """Count assert statements + pytest.raises calls as depth proxy."""
    if not path.exists():
        return 0
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, OSError):
        return 0
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            count += 1
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "raises":
                count += 1
    return count


def _has_foundational_test(module_path: str) -> bool:
    """Return True if at least one non-_adg test file covers this module."""
    parts = Path(module_path).parts
    stem = Path(parts[-1]).stem

    # Check tests/unit/<module_path_dir>/
    test_dir = ROOT / "tests" / "unit" / Path(*parts[:-1])
    if test_dir.exists():
        for f in test_dir.iterdir():
            if (
                f.name.startswith(f"test_{stem}")
                and f.suffix == ".py"
                and not f.name.endswith("_adg.py")
                and _count_assertions(f) >= FOUNDATIONAL_DEPTH_MIN
            ):
                return True

    # Always also check tests/unit_min_deps/ (flat directory, stem-based glob)
    for f in (ROOT / "tests" / "unit_min_deps").glob(f"test_{stem}*.py"):
        if not f.name.endswith("_adg.py") and _count_assertions(f) >= FOUNDATIONAL_DEPTH_MIN:
            return True

    return False


def _compute_violations(
    prod_modules: list[str],
    fan_in: dict[str, int],
) -> list[dict]:
    """Return list of modules violating the fan_in >= threshold → foundational test rule."""
    violations = []
    for m in prod_modules:
        fi = fan_in.get(m, 0)
        if fi < FAN_IN_THRESHOLD:
            continue
        if not _has_foundational_test(m):
            violations.append({"module": m, "fan_in": fi})
    return sorted(violations, key=lambda x: -x["fan_in"])


# ---------------------------------------------------------------------------
# Contract tests
# ---------------------------------------------------------------------------


class TestADGFoundationalCoverageContract:
    """fan_in >= 3 production modules must have a behavioral (non-ADG) test."""

    def test_snapshot_exists_or_created(self) -> None:
    """Test snapshot_exists_or_created contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
            "total_production_modules": len(prod),
            "modules_above_threshold": sum(1 for m in prod if fi.get(m, 0) >= FAN_IN_THRESHOLD),
            "violation_sample": [v["module"] for v in violations[:20]],
        }
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2) + "\n")
        assert SNAPSHOT_PATH.exists()

    def test_violation_count_non_growing(self) -> None:
    """Test violation_count_non_growing contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
            f"ADG foundational coverage violations grew: {current} > ceiling {ceiling}\n"
            f"fan_in >= {threshold} modules without a behavioral test:\n"
            + "\n".join(f"  fan_in={v['fan_in']:>4}  {v['module']}" for v in violations[:30])
        )

    def test_zero_new_high_fanin_violations(self) -> None:
    """Test zero_new_high_fanin_violations contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"
        ]
        assert not hard_violations, (
            f"{len(hard_violations)} NEW high-fan_in (>=10) modules lack foundational tests:\n"
            + "\n".join(f"  fan_in={fi.get(m, 0):>4}  {m}" for m in hard_violations[:20])
        )

    def test_snapshot_threshold_matches_policy(self) -> None:
    """Test snapshot_threshold_matches_policy contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    """Test synthetic_violation_detected contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    """Test fan_in_computation_nonzero_for_shared_types contract compliance."""
    # Arrange
    # TODO: Set up contract parties and terms
    contract_terms = {}  # Replace with actual contract terms

    # Act
    # TODO: Execute contract operations
    contract_result = None  # Replace with actual contract operation

    # Assert - Core Contract
    assert contract_result is not None, "Contract operation should produce a result"
    assert isinstance(contract_result, dict), "Contract result should be structured"
    # TODO: Add specific contract assertions
    # assert contract_result.get("enforced", False), "Contract terms should be enforced"