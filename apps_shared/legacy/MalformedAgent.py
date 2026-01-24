#!/usr/bin/env python3
"""
Malformed Agents Audit Script

Scans agentic_core/ for Agent files that contain both class definitions
and orphaned top-level functions (zombie methods). Generates a detailed
report classifying each issue and recommending remediation.

CONSTRAINT: This is a READ-ONLY audit. No files are modified.
"""

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin

PROJECT_ROOT = Path(__file__).parent.parent
AGENTIC_CORE = PROJECT_ROOT / "agentic_core"

# Suspicious function names that might be orphaned
SUSPICIOUS_NAMES = [
    "heal_repository",
    "execute",
    "run",
    "validate_tasks",
    "scan_and_fix",
    "_validate_tasks",
    "_scan_and_fix",
    "_validate_mutation",
    "_validate_search_count",
]


@dataclass
class OrphanedFunction:
    """Represents a top-level function that should be inside a class."""

    name: str
    lineno: int
    source: str
    end_lineno: int


@dataclass
class ClassMethod:
    """Represents a method inside a class."""

    name: str
    lineno: int
    source: str
    class_name: str
    end_lineno: int


@dataclass
class MalformedAgent(SubatomicTestingMixin):
    """Represents an agent file with structural issues."""

    file_path: Path
    class_names: list[str]
    orphaned_functions: list[OrphanedFunction]
    class_methods: dict[str, list[ClassMethod]]
    status: str  # EXACT_DUPLICATE, DIVERGENT, ORPHAN_ONLY
    action: str
    details: str


def normalize_source(source: str) -> str:
    """Normalize source code for comparison (remove whitespace, comments)."""
    # Remove comments
    lines = []
    for line in source.split("\n"):
        # Remove inline comments
        if "#" in line:
            line = line[: line.index("#")]
        lines.append(line.strip())

    # Join and normalize whitespace
    normalized = " ".join(lines)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def get_function_source(file_content: str, node: ast.FunctionDef) -> str:
    """Extract source code for a function node."""
    lines = file_content.split("\n")
    start = node.lineno - 1
    end = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start + 1
    return "\n".join(lines[start:end])


def analyze_file(file_path: Path) -> MalformedAgent | None:
    """Analyze a single agent file for malformed structure."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError):
        return None

    # Find all class definitions
    classes = []
    class_methods: dict[str, list[ClassMethod]] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
            class_methods[node.name] = []

            # Find methods in this class
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_source = get_function_source(content, item)
                    class_methods[node.name].append(
                        ClassMethod(
                            name=item.name,
                            lineno=item.lineno,
                            source=method_source,
                            class_name=node.name,
                            end_lineno=item.end_lineno
                            if hasattr(item, "end_lineno")
                            else item.lineno,
                        )
                    )

    # Find top-level functions (orphans)
    orphans: list[OrphanedFunction] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            # This is a top-level function
            if node.name in SUSPICIOUS_NAMES or node.name.startswith("_"):
                orphan_source = get_function_source(content, node)
                orphans.append(
                    OrphanedFunction(
                        name=node.name,
                        lineno=node.lineno,
                        source=orphan_source,
                        end_lineno=node.end_lineno if hasattr(node, "end_lineno") else node.lineno,
                    )
                )

    # If no classes or no orphans, not malformed
    if not classes or not orphans:
        return None

    # Classify each orphan
    status_list = []
    action_list = []
    details_list = []

    for orphan in orphans:
        # Check if any class has a method with the same name
        matching_method = None
        for class_name, methods in class_methods.items():
            for method in methods:
                if method.name == orphan.name:
                    matching_method = method
                    break
            if matching_method:
                break

        if matching_method:
            # Compare the two
            orphan_normalized = normalize_source(orphan.source)
            method_normalized = normalize_source(matching_method.source)

            if orphan_normalized == method_normalized:
                status_list.append("EXACT_DUPLICATE")
                action_list.append("DELETE Orphan")
                details_list.append(
                    f"Orphan `{orphan.name}` at line {orphan.lineno} is identical to class method at line {matching_method.lineno}"
                )
            else:
                # Count line difference
                orphan_lines = len(orphan.source.split("\n"))
                method_lines = len(matching_method.source.split("\n"))
                diff = abs(orphan_lines - method_lines)

                status_list.append("DIVERGENT")
                action_list.append("MANUAL MERGE required")
                details_list.append(
                    f"Orphan `{orphan.name}` at line {orphan.lineno} differs from class method at line {matching_method.lineno} (diff: {diff} lines)"
                )
        else:
            status_list.append("ORPHAN_ONLY")
            action_list.append("MOVE Orphan into Class")
            details_list.append(
                f"Orphan `{orphan.name}` at line {orphan.lineno} has no matching class method"
            )

    # Aggregate status (worst case wins)
    if "DIVERGENT" in status_list:
        final_status = "DIVERGENT"
        final_action = "MANUAL MERGE required"
    elif "ORPHAN_ONLY" in status_list:
        final_status = "ORPHAN_ONLY"
        final_action = "MOVE Orphan into Class"
    else:
        final_status = "EXACT_DUPLICATE"
        final_action = "DELETE Orphan"

    return MalformedAgent(
        file_path=file_path,
        class_names=classes,
        orphaned_functions=orphans,
        class_methods=class_methods,
        status=final_status,
        action=final_action,
        details="\n".join(details_list),
    )


def scan_agentic_core() -> list[MalformedAgent]:
    """Scan agentic_core for malformed agent files."""
    malformed = []

    for agent_file in AGENTIC_CORE.rglob("*Agent.py"):
        # Skip __pycache__ and archives
        if "__pycache__" in str(agent_file) or "archives" in str(agent_file):
            continue

        result = analyze_file(agent_file)
        if result:
            malformed.append(result)

    return malformed


def generate_report(malformed: list[MalformedAgent]) -> str:
    """Generate markdown report."""
    lines = [
        "# Malformed Agents Audit Report",
        "",
        f"**Generated**: {__import__('datetime').datetime.now().isoformat()}",
        f"**Total Malformed Files**: {len(malformed)}",
        "",
        "---",
        "",
    ]

    # Summary by status
    exact_dup = sum(1 for m in malformed if m.status == "EXACT_DUPLICATE")
    divergent = sum(1 for m in malformed if m.status == "DIVERGENT")
    orphan_only = sum(1 for m in malformed if m.status == "ORPHAN_ONLY")

    lines.extend(
        [
            "## Summary",
            "",
            "| Status | Count | Action |",
            "|--------|-------|--------|",
            f"| EXACT_DUPLICATE | {exact_dup} | DELETE Orphan |",
            f"| DIVERGENT | {divergent} | MANUAL MERGE |",
            f"| ORPHAN_ONLY | {orphan_only} | MOVE to Class |",
            "",
            "---",
            "",
            "## Detailed Findings",
            "",
        ]
    )

    for agent in sorted(malformed, key=lambda x: str(x.file_path)):
        rel_path = agent.file_path.relative_to(PROJECT_ROOT)

        lines.append(f"### `{rel_path}`")
        lines.append("")
        lines.append(f"* **Classes**: {', '.join(agent.class_names)}")
        lines.append(f"* **Status**: `{agent.status}`")
        lines.append(f"* **Action**: {agent.action}")
        lines.append("")

        for orphan in agent.orphaned_functions:
            lines.append(f"#### Orphan: `{orphan.name}` (line {orphan.lineno})")
            lines.append("")

            # Find matching class method
            matching = None
            for class_name, methods in agent.class_methods.items():
                for method in methods:
                    if method.name == orphan.name:
                        matching = method
                        break

            if matching:
                orphan_norm = normalize_source(orphan.source)
                method_norm = normalize_source(matching.source)

                if orphan_norm == method_norm:
                    lines.append(
                        f"* **Comparison**: IDENTICAL to `{matching.class_name}.{matching.name}` at line {matching.lineno}"
                    )
                    lines.append("* **Recommendation**: DELETE the orphan function")
                else:
                    orphan_lines = len(orphan.source.split("\n"))
                    method_lines = len(matching.source.split("\n"))
                    lines.append(
                        f"* **Comparison**: DIFFERS from `{matching.class_name}.{matching.name}` at line {matching.lineno}"
                    )
                    lines.append(f"* **Orphan Lines**: {orphan_lines}")
                    lines.append(f"* **Method Lines**: {method_lines}")
                    lines.append("* **Recommendation**: MERGE logic, then DELETE orphan")
            else:
                lines.append("* **Comparison**: NO matching class method found")
                lines.append("* **Recommendation**: MOVE into appropriate class")

            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("MALFORMED AGENTS AUDIT")
    print("=" * 70)
    print(f"\nScanning: {AGENTIC_CORE}")
    print("Looking for: Agent files with orphaned top-level functions\n")

    malformed = scan_agentic_core()

    print(f"Found {len(malformed)} malformed agent files\n")

    if malformed:
        report = generate_report(malformed)

        # Print to console
        print(report)

        # Save to file
        report_path = PROJECT_ROOT / "MALFORMED_AGENTS_REPORT.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"\n[SAVED] Report written to: {report_path}")
    else:
        print("No malformed agents found!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
