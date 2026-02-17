#!/usr/bin/env python3
"""
Add heal/heal_repository stubs to agents missing them.

Phase 1, Wave 3: Enforcement stubs
- Adds explicit NotImplementedError stubs
- Minimal, localized diffs
- No behavioral changes

Uses AST end_lineno for precise insertion.
"""

import ast
import json
import sys
from pathlib import Path


def get_repo_root() -> Path:
    """Get repository root."""
    cur = Path(__file__).resolve()
    for p in (cur, *cur.parents):
        if (p / "agentic_core").is_dir() and (p / "ops_scripts").is_dir():
            return p
    raise RuntimeError("Cannot find repo root")


REPO_ROOT = get_repo_root()


def load_audit_data() -> dict:
    """Load audit data from snapshot."""
    audit_file = REPO_ROOT / "artifacts" / "consolidation" / "heal_audit_snapshot.json"
    with open(audit_file, encoding="utf-8") as f:
        return json.load(f)


def generate_stub_lines(method_name: str, class_name: str, indent: str) -> list[str]:
    """Generate stub method as list of lines with newlines."""
    return [
        f"{indent}def {method_name}(self, *args, **kwargs):\n",
        f'{indent}    """{method_name}() not implemented for {class_name}."""\n',
        f'{indent}    raise NotImplementedError("{method_name}() not implemented for {class_name}")\n',
        "\n",
    ]


def add_stubs_to_file(file_path: Path, agents_in_file: list[dict]) -> bool:
    """Add stubs to agents in a file. Returns True if modified."""
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        source_lines = source.splitlines(keepends=True)

        # Ensure last line has newline
        if source_lines and not source_lines[-1].endswith("\n"):
            source_lines[-1] += "\n"

        # Build map of class name -> ClassDef node
        class_nodes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_nodes[node.name] = node

        # Collect insertions: (line_number, lines_to_insert)
        # line_number is 1-indexed, insert AFTER this line
        insertions = []

        for agent in agents_in_file:
            class_name = agent["class_name"]
            if class_name not in class_nodes:
                continue

            node = class_nodes[class_name]

            # Get indentation from first body element
            if node.body:
                first_body_line = source_lines[node.body[0].lineno - 1]
                indent = " " * (len(first_body_line) - len(first_body_line.lstrip()))
            else:
                # Empty class - use class indent + 4
                class_line = source_lines[node.lineno - 1]
                class_indent = len(class_line) - len(class_line.lstrip())
                indent = " " * (class_indent + 4)

            # Get end line of class
            end_line = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else node.lineno

            stub_lines = []
            if not agent["has_heal"]:
                stub_lines.extend(generate_stub_lines("heal", class_name, indent))
            if not agent["has_heal_repository"]:
                stub_lines.extend(generate_stub_lines("heal_repository", class_name, indent))

            if stub_lines:
                insertions.append((end_line, stub_lines))

        if not insertions:
            return False

        # Sort by line number descending to avoid offset issues
        insertions.sort(key=lambda x: x[0], reverse=True)

        # Insert stubs
        for insert_after_line, stub_lines in insertions:
            # Insert after the end line of the class
            insert_idx = insert_after_line  # 0-indexed position after line
            for i, line in enumerate(stub_lines):
                source_lines.insert(insert_idx + i, line)

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("".join(source_lines))

        return True

    except (SyntaxError, UnicodeDecodeError, OSError) as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    audit_data = load_audit_data()

    # Group agents by file
    agents_by_file: dict[str, list[dict]] = {}
    for agent in audit_data["audit_results"]:
        if not agent["has_heal"] or not agent["has_heal_repository"]:
            path = agent["repo_relative_path"]
            if path not in agents_by_file:
                agents_by_file[path] = []
            agents_by_file[path].append(agent)

    print(f"Found {len(agents_by_file)} files with agents missing heal methods")

    modified_count = 0
    for rel_path, agents in sorted(agents_by_file.items()):
        file_path = REPO_ROOT / rel_path.replace("/", "\\")
        print(f"Processing: {rel_path}")

        for agent in agents:
            missing = []
            if not agent["has_heal"]:
                missing.append("heal")
            if not agent["has_heal_repository"]:
                missing.append("heal_repository")
            print(f"  {agent['class_name']}: missing {', '.join(missing)}")

        if add_stubs_to_file(file_path, agents):
            modified_count += 1
            print("  -> Modified")
        else:
            print("  -> No changes")

    print(f"\nModified {modified_count} files")


if __name__ == "__main__":
    main()
