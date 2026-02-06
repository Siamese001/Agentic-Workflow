#!/usr/bin/env python3
"""
Simple script to generate agent duplicates table.
Runs find_duplicate_agents.py internally and processes output.
"""

import json
from datetime import datetime
from pathlib import Path

from agentic_core.utils.security import safe_execute


def is_agent_file(path: str) -> bool:
    """Check if path is an actual agent file (not test)."""
    if not path.endswith("Agent.py"):
        return False
    path_lower = path.lower()
    if "test" in path_lower or "/tests/" in path or "\\tests\\" in path:
        return False
    return True


def infer_rationale(canonical: str, dup_path: str, action: str) -> str:
    """Infer rationale based on path patterns."""
    if "blueprint_sovereign" in dup_path:
        return "Leftover blueprint template — production version is canonical"

    if ("validators" in canonical and "agents" in dup_path) or (
        "agents" in canonical and "validators" in dup_path
    ):
        return "Location overlap: same agent in agents/ vs validators/ directories"

    if action == "REVIEW":
        return "Minor differences detected (comments/formatting/incomplete features) — manual merge needed"

    return "Exact or structural duplicate — likely copy-paste or migration artifact"


def main():
    print("Running duplicate detection...")

    # Run find_duplicate_agents.py and capture output
    result = safe_execute(
        ["python", "scripts/find_duplicate_agents.py", "--output", "json"],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
        check=False,
    )

    if result.returncode != 0:
        print(f"Error running find_duplicate_agents.py: {result.stderr}")
        return 1

    # Parse JSON from stdout (skip log lines)
    output = result.stdout

    # The output has log lines at the start - skip them
    lines = output.split("\n")
    json_lines = []
    in_json = False

    for line in lines:
        if line.strip() == "[":
            in_json = True
        if in_json:
            if line.strip().startswith("="):
                break
            json_lines.append(line)

    json_output = "\n".join(json_lines)

    try:
        data = json.loads(json_output)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"JSON output length: {len(json_output)}")
        print(f"First 200 chars: {json_output[:200]}")
        print(f"Last 200 chars: {json_output[-200:]}")
        with open("reports/json_debug.txt", "w") as f:
            f.write(json_output)
        return 1

    # Filter and format
    results = []
    for item in data:
        canonical = item["canonical_file"]

        if not is_agent_file(canonical):
            continue

        for dup in item["duplicates"]:
            dup_path = dup["path"]
            if not is_agent_file(dup_path):
                continue

            results.append(
                {
                    "agent_name": Path(canonical).stem,
                    "canonical": canonical,
                    "duplicate": dup_path,
                    "action": item["action"],
                    "canonical_quality": item["canonical_quality"]["quality_score"],
                    "duplicate_quality": dup["quality"]["quality_score"],
                    "rationale": infer_rationale(canonical, dup_path, item["action"]),
                },
            )

    # Sort: DELETE first, then by agent name
    results.sort(key=lambda x: (0 if x["action"] == "DELETE" else 1, x["agent_name"]))

    # Generate output
    output_file = Path("reports/duplicated_agents_table.md")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Duplicated Agents Table\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Duplicates:** {len(results)}\n\n")

        delete_count = sum(1 for r in results if r["action"] == "DELETE")
        review_count = sum(1 for r in results if r["action"] == "REVIEW")
        f.write(f"**Action Summary:** {delete_count} auto-delete, {review_count} manual review\n\n")

        f.write("| Agent Name | Canonical Path | Duplicate Path | Action | Quality (C/D) | Rationale |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")

        for r in results:
            f.write(
                f"| {r['agent_name']} | `{r['canonical']}` | `{r['duplicate']}` | "
                f"**{r['action']}** | {r['canonical_quality']}/{r['duplicate_quality']} | "
                f"{r['rationale']} |\n",
            )

        f.write("\n---\n\n")
        f.write("## Quick Actions\n\n")
        f.write("### Delete Safe Duplicates\n")
        f.write("```bash\n")
        for r in results:
            if r["action"] == "DELETE":
                f.write(f'git rm "{r["duplicate"]}"\n')
        f.write("```\n\n")

        f.write("### Review Required (Manual Diff)\n")
        f.write("```bash\n")
        for r in results:
            if r["action"] == "REVIEW":
                f.write(f"# {r['agent_name']}\n")
                f.write(f'code --diff "{r["canonical"]}" "{r["duplicate"]}"\n\n')
        f.write("```\n")

    print(f"✅ Generated: {output_file}")
    print(f"   Total agent duplicates: {len(results)}")
    print(f"   DELETE: {delete_count}")
    print(f"   REVIEW: {review_count}")

    return 0


if __name__ == "__main__":
    exit(main())
