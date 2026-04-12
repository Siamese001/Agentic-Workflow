"""
Test Territory Mirror Enforcer

Enforces strict "Mirror-Image" folder sovereignty between source code and test suite.
Every test file must reside in a directory that exactly parallels its source component.

Example: apps_lic/engines/SomeAgent.py → tests/unit/apps_lic/engines/test_SomeAgent.py
"""

import ast
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
)


@dataclass
class SourceFile:
    """Represents a classified source file."""

    path: Path
    file_type: str
    class_name: str | None
    expected_test_path: Path | None = None


@dataclass
class TestFile:
    """Represents a test file with its expected location."""

    path: Path
    current_territory: str
    expected_territory: str | None
    source_file: SourceFile | None = None
    is_violation: bool = False
    target_path: Path | None = None


@dataclass
class MirrorAuditReport:
    """Report of mirror territory audit."""

    source_files: list[SourceFile] = field(default_factory=list)
    test_files: list[TestFile] = field(default_factory=list)
    violations: list[TestFile] = field(default_factory=list)
    moves_executed: int = 0
    imports_fixed: int = 0


def to_smart_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case while preserving acronyms."""
    atomic_words = {
        "Grounding": "grounding",
        "Routing": "routing",
        "Sender": "sender",
        "Receiver": "receiver",
        "Planner": "planner",
        "Scheduler": "scheduler",
        "RG": "rg",
        "PII": "pii",
        "LLM": "llm",
        "ATS": "ats",
        "API": "api",
    }

    if name in atomic_words:
        return atomic_words[name]

    placeholders = {}
    temp_name = name
    for idx, (word, replacement) in enumerate(atomic_words.items()):
        if word in temp_name:
            placeholder = f"__ATOMIC_{idx}__"
            placeholders[placeholder] = replacement
            temp_name = temp_name.replace(word, placeholder)

    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", temp_name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    result = s2
    for placeholder, replacement in placeholders.items():
        result = result.replace(placeholder.lower(), replacement)

    return result


def classify_file_simple(path: Path) -> str:
    """Simple file classification based on AST analysis."""
    try:
        content = path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (
        SyntaxError,
        UnicodeDecodeError,
    ):  # guardian: Parsing and encoding errors need separate handling strategies
        return "UNKNOWN"

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            name = node.name
            bases = [
                b.id if isinstance(b, ast.Name) else b.attr if isinstance(b, ast.Attribute) else ""
                for b in node.bases
            ]

            # Priority classification
            if any("Orchestrator" in b for b in bases) or "Orchestrator" in name:
                return "ORCHESTRATOR"
            if any("Validator" in b for b in bases) or "Validator" in name:
                return "VALIDATOR"
            if any("Mixin" in b for b in bases) or "Mixin" in name:
                return "MIXIN"
            if any("Agent" in b for b in bases) or "Agent" in name:
                return "AGENT"
            if any("Strategy" in b for b in bases) or "Strategy" in name:
                return "ADAPTER"
            if any("Config" in b for b in bases) or "Config" in name:
                return "CONFIG"
            if any("Factory" in b for b in bases) or "Factory" in name:
                return "FACTORY"

    if path.stem.startswith("test_"):
        return "TEST"

    return "CLASS"


def get_expected_test_territory(source_path: Path, project_root: Path) -> Path | None:
    """Calculate the expected test file path for a source file."""
    try:
        rel_path = source_path.relative_to(project_root)
    except ValueError:
        return None

    parts = rel_path.parts
    if not parts:
        return None

    # Determine test type based on source location
    if parts[0] in (AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR):
        # Build mirror path: tests/unit/{source_territory}/{subfolders}/test_{snake_case}.py
        test_filename = f"test_{to_smart_snake_case(source_path.stem)}.py"
        test_path = project_root / TESTS_DIR / "unit" / rel_path.parent / test_filename
        return test_path

    return None


def get_source_for_test(test_path: Path, project_root: Path) -> tuple[Path | None, str | None]:
    """
    Given a test file path, determine what source file it should be testing.
    Returns (expected_source_path, expected_territory).
    """
    try:
        rel_path = test_path.relative_to(project_root / TESTS_DIR / "unit")
    except ValueError:
        try:
            rel_path = test_path.relative_to(project_root / TESTS_DIR / "integration")
        except ValueError:
            return None, None

    parts = rel_path.parts
    if not parts:
        return None, None

    # Extract territory (e.g., apps_lic, agentic_core)
    territory = parts[0] if parts else None

    # Convert test filename to source filename
    # test_SomeAgent.py -> SomeAgent.py (approximate)
    test_stem = test_path.stem
    if test_stem.startswith("test_"):
        test_stem[5:]  # Remove test_ prefix
        # This is the expected subfolder structure
        expected_source_dir = project_root / Path(*parts[:-1])
        return expected_source_dir, territory

    return None, territory


def scan_source_files(project_root: Path) -> list[SourceFile]:
    """Scan and classify all source files."""
    source_files = []
    source_dirs = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]

    for source_dir in source_dirs:
        dir_path = project_root / source_dir
        if not dir_path.exists():
            continue

        for py_file in dir_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or py_file.name == "__init__.py":
                continue

            file_type = classify_file_simple(py_file)

            # Get primary class name
            class_name = None
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        break
            except (ValueError, TypeError, RuntimeError) as e:
                pass

            expected_test = get_expected_test_territory(py_file, project_root)

            source_files.append(
                SourceFile(
                    path=py_file,
                    file_type=file_type,
                    class_name=class_name,
                    expected_test_path=expected_test,
                ),
            )

    return source_files


def scan_test_files(project_root: Path, source_files: list[SourceFile]) -> list[TestFile]:
    """
    Scan all test files and check for territory violations.

    Mirror-Image Principle: Tests should mirror their SOURCE file locations.
    A test is only a violation if it's in an "Anarchy Zone" (misc, temp, etc.)
    or doesn't mirror any valid source structure.
    """
    test_files = []
    test_dirs = [
        project_root / TESTS_DIR / "unit",
        project_root / TESTS_DIR / "integration",
    ]

    # Anarchy zones - folders that should NOT contain tests
    anarchy_zones = {"misc", "temp", "old", "deprecated", "archive", "scratch"}

    # Valid source territory folders that tests CAN mirror

    # Build source lookup by expected test path
    source_lookup = {}
    for sf in source_files:
        if sf.expected_test_path:
            source_lookup[sf.expected_test_path] = sf

    for test_dir in test_dirs:
        if not test_dir.exists():
            continue

        for test_file in test_dir.rglob("test_*.py"):
            if "__pycache__" in str(test_file):
                continue

            current_territory = test_file.parent.name.lower()

            # Check if this test file matches any expected source location
            matched_source = source_lookup.get(test_file)

            # Determine if this is a violation
            is_violation = False
            expected_territory = None
            target_path = None

            if matched_source:
                # Perfect match with source - no violation
                expected_territory = matched_source.path.parent.name
            elif current_territory in anarchy_zones:
                # Test is in an anarchy zone - THIS IS A VIOLATION
                is_violation = True

                # Try to infer correct location from filename
                test_stem = test_file.stem.replace("test_", "")

                if "_validator" in test_stem:
                    expected_territory = "validators"
                elif "_orchestrator" in test_stem:
                    expected_territory = "orchestration"
                elif "_agent" in test_stem:
                    expected_territory = "agents"
                elif "_config" in test_stem:
                    expected_territory = "config"
                elif "_strategy" in test_stem or "_adapter" in test_stem:
                    expected_territory = "strategies"
                elif "_mixin" in test_stem:
                    expected_territory = "mixins"
                else:
                    expected_territory = "core"  # Default fallback

                # Calculate target path by replacing anarchy zone with correct territory
                try:
                    rel_from_test_type = test_file.relative_to(test_dir)
                    parts = list(rel_from_test_type.parts)
                    for i, part in enumerate(parts):
                        if part.lower() in anarchy_zones:
                            parts[i] = expected_territory
                            break
                    target_path = test_dir / Path(*parts)
                except ValueError:
                    pass
            # else: test is in a valid territory that mirrors source structure - OK

            test_files.append(
                TestFile(
                    path=test_file,
                    current_territory=test_file.parent.name,  # Keep original case
                    expected_territory=expected_territory,
                    source_file=matched_source,
                    is_violation=is_violation,
                    target_path=target_path,
                ),
            )

    return test_files


def move_test_file(test_file: TestFile, dry_run: bool = True) -> bool:
    """Move a test file to its correct territory."""
    if not test_file.target_path:
        return False

    src = test_file.path
    dest = test_file.target_path

    if dry_run:
        print(
            f"  [PLAN] MOVE {src.relative_to(src.parent.parent.parent.parent)} -> {dest.relative_to(dest.parent.parent.parent.parent)}",
        )
        return True

    # Create target directory if needed
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Check for collision
    if dest.exists():
        print(f"  [COLLISION] {dest.name} already exists, skipping")
        return False

    try:
        shutil.move(str(src), str(dest))
        print(f"  [MOVED] {src.name} -> {dest.parent.name}/{dest.name}")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to move: {e}")
        return False


def run_mirror_audit(project_root: Path, dry_run: bool = True, execute: bool = False) -> MirrorAuditReport:
    """Run the full mirror territory audit."""
    report = MirrorAuditReport()

    print("=" * 70)
    print("TEST TERRITORY MIRROR ENFORCER")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"Project Root: {project_root}")
    print()

    # Step 1: Scan source files
    print("[1/4] Scanning source files...")
    report.source_files = scan_source_files(project_root)
    print(f"  Found {len(report.source_files)} source files")

    # Step 2: Scan test files
    print("[2/4] Scanning test files...")
    report.test_files = scan_test_files(project_root, report.source_files)
    print(f"  Found {len(report.test_files)} test files")

    # Step 3: Identify violations
    print("[3/4] Identifying territory violations...")
    report.violations = [tf for tf in report.test_files if tf.is_violation]
    print(f"  Found {len(report.violations)} violations")

    # Step 4: Execute moves (if not dry run)
    if report.violations:
        print("[4/4] Processing violations...")
        for violation in report.violations:
            print(f"\n[VIOLATION] {violation.path.name}")
            print(f"  Current:  {violation.current_territory}")
            print(f"  Expected: {violation.expected_territory}")

            if execute and not dry_run:
                if move_test_file(violation, dry_run=False):
                    report.moves_executed += 1
            else:
                move_test_file(violation, dry_run=True)

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Source Files Analyzed:  {len(report.source_files)}")
    print(f"Test Files Analyzed:    {len(report.test_files)}")
    print(f"Territory Violations:   {len(report.violations)}")
    if not dry_run:
        print(f"Files Moved:            {report.moves_executed}")

    return report


def generate_violation_report(report: MirrorAuditReport) -> dict[str, Any]:
    """Generate a JSON report of violations."""
    return {
        "summary": {
            "source_files": len(report.source_files),
            "test_files": len(report.test_files),
            "violations": len(report.violations),
            "moves_executed": report.moves_executed,
        },
        "violations": [
            {
                "path": str(v.path),
                "current_territory": v.current_territory,
                "expected_territory": v.expected_territory,
                "target_path": str(v.target_path) if v.target_path else None,
            }
            for v in report.violations
        ],
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Territory Mirror Enforcer")
    parser.add_argument("--execute", action="store_true", help="Execute moves (default: dry run)")
    parser.add_argument(
        "--output",
        type=str,
        default="territory_mirror_report.json",
        help="Report output file",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    report = run_mirror_audit(project_root, dry_run=not args.execute, execute=args.execute)

    # Save report
    json_report = generate_violation_report(report)
    output_path = project_root / args.output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_report, f, indent=2)
    print(f"\nReport saved to: {output_path}")
