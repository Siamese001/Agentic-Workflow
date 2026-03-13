"""
Extract agent duplicates from find_duplicate_agents.py output.
Filters to actual agent files only (excludes tests).
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def is_agent_file(path: str) -> bool:
    """Check if path is an actual agent file (not test).

    [REFACTORED 2026-02-08] Aligned with classification kernel naming rules.
    For full AST-based classification, use:
        from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file
    """
    if not path.endswith("Agent.py"):
        return False
    path_lower = path.lower()
    if "test" in path_lower or "/tests/" in path or "\\tests\\" in path:
        return False
    if "Mixin" in path:
        return False
    return True


def infer_rationale(canonical: str, dup_path: str, action: str) -> str:
    """Infer rationale based on path patterns."""
    if "blueprint_sovereign" in dup_path:
        return "Leftover blueprint template — production version is canonical"
    if (
        "validators" in canonical
        and "agents" in dup_path
        or ("agents" in canonical and "validators" in dup_path)
    ):
        return "Location overlap: same agent in agents/ vs validators/ directories"
    if action == "REVIEW":
        return "Minor differences detected (comments/formatting/incomplete features) — manual merge needed"
    return "Exact or structural duplicate — likely copy-paste or migration artifact"


data = json.load(sys.stdin)
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
            }
        )
results.sort(key=lambda x: (0 if x["action"] == "DELETE" else 1, x["agent_name"]))
print("# Duplicated Agents Table")
print(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"**Total Duplicates:** {len(results)}\n")
delete_count = sum(1 for r in results if r["action"] == "DELETE")
review_count = sum(1 for r in results if r["action"] == "REVIEW")
print(f"**Action Summary:** {delete_count} auto-delete, {review_count} manual review\n")
print("| Agent Name | Canonical Path | Duplicate Path | Action | Quality (C/D) | Rationale |")
print("| --- | --- | --- | --- | --- | --- |")
for r in results:
    print(
        f"| {r['agent_name']} | `{r['canonical']}` | `{r['duplicate']}` | **{r['action']}** | {r['canonical_quality']}/{r['duplicate_quality']} | {r['rationale']} |"
    )
print("\n---\n")
print("## Quick Actions\n")
print("### Delete Safe Duplicates")
print("```bash")
for r in results:
    if r["action"] == "DELETE":
        print(f'''git rm "{r["duplicate"]}"''')
print("```\n")
print("### Review Required (Manual Diff)")
print("```bash")
for r in results:
    if r["action"] == "REVIEW":
        print(f"# {r['agent_name']}")
        print(f'''code --diff "{r["canonical"]}" "{r["duplicate"]}"\n''')
print("```")
