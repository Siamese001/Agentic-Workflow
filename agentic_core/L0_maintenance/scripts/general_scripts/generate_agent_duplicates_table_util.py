#!/usr/bin/env python3
"""
Generate Markdown table of duplicated agents (excluding test files).
Filters to actual production/blueprint agent files only.
"""

import json
import sys
from pathlib import Path


def extract_basename(path: str) -> str:
    """Extract agent name from path."""
    return Path(path).stem


def infer_rationale(canonical: str, duplicates: list, action: str) -> str:
    """Infer rationale based on path patterns."""
    dup_paths = [d["path"] for d in duplicates]

    # Check for blueprint pattern
    if any("blueprint_sovereign" in p for p in dup_paths):
        return "Leftover blueprint template — production version is canonical"

    # Check for location overlap (agents/ vs validators/)
    if "validators" in canonical or any("validators" in p for p in dup_paths):
        if "agents" in canonical or any("agents" in p for p in dup_paths):
            return "Location overlap: same agent in agents/ vs validators/ directories"

    # Review cases
    if action == "REVIEW":
        return "Minor differences detected (comments/formatting/incomplete features) — manual merge needed"

    # Default
    return "Exact or structural duplicate — likely copy-paste or migration artifact"


def is_actual_agent_file(path: str) -> bool:
    """Check if path is an actual agent file (not test)."""
    path_lower = path.lower()

    # Must end with Agent.py
    if not path.endswith("Agent.py"):
        return False

    # Exclude test files
    if "test" in path_lower or "tests/" in path or "tests\\" in path:
        return False

    return True


def generate_table(json_file: Path, output_file: Path):
    """Generate Markdown table from JSON report."""
    with open(json_file, encoding="utf-8") as f:
        content = f.read()
        # Skip log lines at the beginning
        json_start = content.find("[")
        if json_start > 0:
            content = content[json_start:]
        data = json.loads(content)

    # Filter to actual agent files
    agent_duplicates = []
    for item in data:
        canonical = item["canonical_file"]

        # Skip if canonical is not an agent file
        if not is_actual_agent_file(canonical):
            continue

        # Filter duplicates to only agent files
        agent_dups = [d for d in item["duplicates"] if is_actual_agent_file(d["path"])]

        # Skip if no agent duplicates
        if not agent_dups:
            continue

        # Add to results
        for dup in agent_dups:
            agent_duplicates.append(
                {
                    "agent_name": extract_basename(canonical),
                    "canonical": canonical,
                    "duplicate": dup["path"],
                    "action": item["action"],
                    "canonical_quality": item["canonical_quality"]["quality_score"],
                    "duplicate_quality": dup["quality"]["quality_score"],
                    "rationale": infer_rationale(canonical, [dup], item["action"]),
                }
            )

    # Sort by action (DELETE first), then by agent name
    agent_duplicates.sort(key=lambda x: (0 if x["action"] == "DELETE" else 1, x["agent_name"]))

    # Generate Markdown table
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Duplicated Agents Table\n")
        f.write(f"**Generated:** {Path(json_file).stat().st_mtime}\n")
        f.write(f"**Total Duplicates:** {len(agent_duplicates)}\n\n")

        # Summary stats
        delete_count = sum(1 for d in agent_duplicates if d["action"] == "DELETE")
        review_count = sum(1 for d in agent_duplicates if d["action"] == "REVIEW")
        f.write(f"**Action Summary:** {delete_count} auto-delete, {review_count} manual review\n\n")

        # Table header
        f.write("| Agent Name | Canonical Path | Duplicate Path | Action | Quality (C/D) | Rationale |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")

        # Table rows
        for item in agent_duplicates:
            f.write(f"| {item['agent_name']} | ")
            f.write(f"`{item['canonical']}` | ")
            f.write(f"`{item['duplicate']}` | ")
            f.write(f"**{item['action']}** | ")
            f.write(f"{item['canonical_quality']}/{item['duplicate_quality']} | ")
            f.write(f"{item['rationale']} |\n")

        # Footer with commands
        f.write("\n---\n\n")
        f.write("## Quick Actions\n\n")
        f.write("### Delete Safe Duplicates\n")
        f.write("```bash\n")
        for item in agent_duplicates:
            if item["action"] == "DELETE":
                f.write(f'git rm "{item["duplicate"]}"\n')
        f.write("```\n\n")

        f.write("### Review Required (Manual Diff)\n")
        f.write("```bash\n")
        for item in agent_duplicates:
            if item["action"] == "REVIEW":
                f.write(f"# {item['agent_name']}\n")
                f.write(f'code --diff "{item["canonical"]}" "{item["duplicate"]}"\n\n')
        f.write("```\n")

    print(f"✅ Generated table: {output_file}")
    print(f"   Total agent duplicates: {len(agent_duplicates)}")
    print(f"   DELETE: {delete_count}")
    print(f"   REVIEW: {review_count}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_agent_duplicates_table_util.py <duplicates_report.json>")
        sys.exit(1)

    json_file = Path(sys.argv[1])
    if not json_file.exists():
        print(f"Error: {json_file} not found")
        sys.exit(1)

    output_file = json_file.parent / "duplicated_agents_table.md"
    generate_table(json_file, output_file)


if __name__ == "__main__":
    main()
