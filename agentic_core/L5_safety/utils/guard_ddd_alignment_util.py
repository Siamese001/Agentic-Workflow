"""
DDD Alignment Guardian - Sovereign Edition (December 29, 2025)
Detects violations of Domain-Driven Design tactical patterns:
- Anemic Domain models (data holders without behavior)
- God Classes (excessive responsibilities)
- Mutable Value Objects
- Service layer bloat indicators
- Aggregate root misuse patterns
"""

import ast
from pathlib import Path

try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import (
        SCRIPTS_DIR,
        TESTS_DIR,
    )
except ImportError:
    SCRIPTS_DIR = OPS_SCRIPTS_DIR
    TESTS_DIR = TESTS_DIR


def get_ddd_violations_detailed(root_path: str) -> list[dict]:
    """
    [NEW] Detailed DDD Violation detector — structured output for L0 healing/forensics.

    Returns:
        List of dicts with keys: file, line, type, description, Severity
    """
    violations: list[dict] = []
    root = Path(root_path)
    # [ROBUSTNESS] Handle case where root path doesn't exist
    if not root.exists():
        return violations

    # Phase 6.9: Use ssot_discovery instead of rglob

    python_files = list(get_python_files(root))

    if not python_files:
        return violations

    for py_file in python_files:
        try:
            relative_path = py_file.relative_to(root)
        except ValueError:
            # Handle edge case where file is not relative to root (symlinks etc)
            relative_path = py_file.name

        # Skip tests, migrations, and private modules
        # [SOVEREIGN FILTER] Adjusted to catch more valid code while skipping infrastructure
        if any(
            skip in str(relative_path) for skip in [TESTS_DIR, "migrations", "__pycache__", ".venv", "venv"]
        ) or py_file.name.startswith("_"):
            continue

        try:
            code = py_file.read_text(encoding="utf-8", errors="ignore")  # [ROBUSTNESS] Ignore encoding errors
            tree = ast.parse(code, filename=str(py_file))
        except SyntaxError as e:
            violations.append(
                {
                    "file": str(relative_path),
                    "line": 1,
                    "type": "Parse Error",
                    "description": f"Invalid syntax: {e}",
                    "Severity": "LOW",
                },
            )
            continue
        # guardian: allow-silent-swallow
        except Exception as e:
            violations.append(
                {
                    "file": str(relative_path),
                    "line": 1,
                    "type": "Read Error",
                    "description": f"Failed to read/parse: {e}",
                    "Severity": "LOW",
                },
            )
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            # Extract class body analysis
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("__")]
            attrs = [n for n in node.body if isinstance(n, ast.Assign)]
            # Also count type-annotated attributes (e.g. x: int) common in Pydantic/DataClasses
            ann_attrs = [n for n in node.body if isinstance(n, ast.AnnAssign)]
            total_methods = len(methods)
            total_attrs = len(attrs) + len(ann_attrs)

            # 1. Anemic Domain Model Detection
            # High attributes + low behavior = likely DTO/anemic entity
            if total_attrs >= 6 and total_methods <= 2:
                # Exclude intentionally data-only structures (DTOs, Value Objects):
                # - schemas/, config/, scripts/, types/ folders
                # - Common DTO/VO naming patterns
                # - @dataclass decorated classes (check decorator)
                path_str = str(relative_path).lower()
                class_name_lower = node.name.lower()

                # Check for @dataclass decorator
                has_dataclass_decorator = any(
                    (isinstance(d, ast.Name) and d.id == "dataclass")
                    or (isinstance(d, ast.Attribute) and d.attr == "dataclass")
                    or (
                        isinstance(d, ast.Call)
                        and (
                            (isinstance(d.func, ast.Name) and d.func.id == "dataclass")
                            or (isinstance(d.func, ast.Attribute) and d.func.attr == "dataclass")
                        )
                    )
                    for d in node.decorator_list
                )

                is_data_class_exempt = (
                    has_dataclass_decorator
                    or "schemas" in path_str
                    or "config" in path_str
                    or SCRIPTS_DIR in path_str
                    or "types" in path_str
                    or "deprecated" in path_str
                    or "_registry" in path_str
                    or "_policy" in path_str
                    or "_config" in path_str
                    or "_types" in path_str
                    or class_name_lower.endswith("_task")
                    or class_name_lower.endswith("_result")
                    or class_name_lower.endswith("_config")
                    or class_name_lower.endswith("_context")
                    or class_name_lower.endswith("_finding")
                    or class_name_lower.endswith("_pattern")
                    or class_name_lower.endswith("_gap")
                    or class_name_lower.endswith("_recommendation")
                    or class_name_lower.endswith("_entry")
                    or class_name_lower.endswith("_record")
                    or class_name_lower.endswith("_state")
                    or class_name_lower.endswith("_info")
                    or class_name_lower.endswith("_data")
                    or class_name_lower.endswith("_dto")
                    or class_name_lower.endswith("_vo")
                    or class_name_lower.endswith("bundle")
                    or class_name_lower.endswith("_phase")
                    or class_name_lower.endswith("_type")
                    or class_name_lower.endswith("_status")
                    or class_name_lower.endswith("_response")
                    or class_name_lower.endswith("_request")
                    or class_name_lower.endswith("_event")
                    or class_name_lower.endswith("_message")
                    or class_name_lower.endswith("_model")
                    or class_name_lower == "Provider"
                    or class_name_lower == "ExecutionPhase"
                    or "result" in class_name_lower
                    or "bundle" in class_name_lower
                    or "type" in class_name_lower
                    or "status" in class_name_lower
                    or "role" in class_name_lower
                    or "spec" in class_name_lower
                    or "agent" in class_name_lower
                )
                if not is_data_class_exempt:
                    violations.append(
                        {
                            "file": str(relative_path),
                            "line": node.lineno,
                            "type": "Anemic Domain Model",
                            "description": f"Class '{node.name}' has {total_attrs} attributes but only {total_methods} behaviors — probable data holder without domain logic",
                            "Severity": "HIGH",
                        },
                    )

            # 2. God Class Detection
            # Excessive methods indicate SRP Violation
            if total_methods > 25:
                violations.append(
                    {
                        "file": str(relative_path),
                        "line": node.lineno,
                        "type": "God Class",
                        "description": f"Class '{node.name}' has {total_methods} methods — potential Violation of Single Responsibility Principle",
                        "Severity": "MEDIUM",
                    },
                )

            # 3. Mutable Value Object Detection
            # Value Objects must be immutable — no setters or mutable ops
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(base.attr)

            # [HEURISTIC] Check for naming conventions like "ValueObject" or "VO"
            if (
                any(vo_indicator in bases for vo_indicator in ["ValueObject", "VO", "Immutable"])
                or "ValueObject" in node.name
            ):
                setters_or_mutators = [
                    m
                    for m in methods
                    if m.name.startswith(("set_", "update_", "add_", "remove_")) or "mutat" in m.name.lower()
                ]
                if setters_or_mutators:
                    violations.append(
                        {
                            "file": str(relative_path),
                            "line": node.lineno,
                            "type": "Mutable Value Object",
                            "description": f"Value Object '{node.name}' contains mutating methods ({[m.name for m in setters_or_mutators]}) — VOs must be immutable",
                            "Severity": "CRITICAL",
                        },
                    )

            # 4. Service Layer Bloat (heuristic)
            # Services should orchestrate, not contain domain logic
            if node.name.endswith("Service") or node.name.endswith("Manager"):
                complex_methods = 0
                for method in methods:
                    # Rough complexity: nested loops, conditionals, long body
                    # Count flow control statements
                    method_complexity = len(
                        [
                            n
                            for n in ast.walk(method)
                            if isinstance(n, ast.If | ast.For | ast.While | ast.Try)
                        ],
                    )
                    if method_complexity > 8:  # Slightly relaxed threshold
                        complex_methods += 1

                if complex_methods > 5:
                    violations.append(
                        {
                            "file": str(relative_path),
                            "line": node.lineno,
                            "type": "Fat Service",
                            "description": f"Service '{node.name}' has {complex_methods} complex methods — likely containing domain logic instead of orchestration",
                            "Severity": "MEDIUM",
                        },
                    )

    return violations


def validate_ddd_alignment(root_path: str) -> tuple[float, list[str]]:
    """
    Existing Auditor-compatible validator — simple score + string issues.
    Used directly by Sovereign Auditor v3.1.
    """
    detailed_violations = get_ddd_violations_detailed(root_path)

    # scoring: 5 points per Violation, clamped to 0-100
    base_score = 100.0
    penalty_per_violation = 5.0

    # [SOVEREIGN SCORING] Critical violations hit harder
    critical_count = sum(1 for v in detailed_violations if v["Severity"] == "CRITICAL")
    penalty_per_violation += critical_count * 10.0  # Bonus penalty for criticals

    score = max(0.0, base_score - len(detailed_violations) * penalty_per_violation)

    # Format issues as strings for Auditor consumption
    issues: list[str] = []
    for v in detailed_violations:
        line_info = f"line {v['line']}" if v["line"] > 0 else ""
        issues.append(f"{v['file']}:{line_info} [{v['Severity']}] {v['type']}: {v['description']}")

    return score, issues
