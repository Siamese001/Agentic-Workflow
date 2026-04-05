#!/usr/bin/env python3
"""
Plan Categorization Tool
Classifies all plans by type to determine which need wave tables vs which are exempt.
"""

import json
from datetime import datetime
from pathlib import Path


def detect_plan_type(content: str, filename: str) -> tuple[str, float]:
    """Detect plan type with confidence score."""
    content_lower = content.lower()
    filename_lower = filename.lower()

    # RCA patterns
    rca_patterns = [
        "## violation",
        "## root cause",
        "## corrective actions",
        "rca:",
        "root cause analysis",
        "violation report",
    ]
    rca_score = sum(1 for pattern in rca_patterns if pattern in content_lower)

    # Gap analysis patterns
    gap_patterns = ["gap analysis", "gap register", "missing elements", "implementation gap", "gap:"]
    gap_score = sum(1 for pattern in gap_patterns if pattern in content_lower)

    # Execution plan patterns
    exec_patterns = [
        "## wave structure",
        "## execution plan",
        "## implementation commands",
        "phase 1",
        "phase 2",
        "wave 1",
        "wave 2",
    ]
    exec_score = sum(1 for pattern in exec_patterns if pattern in content_lower)

    # Investigation/report patterns
    inv_patterns = [
        "## investigation",
        "## analysis",
        "## findings",
        "## assessment",
        "## summary",
        "## conclusion",
    ]
    inv_score = sum(1 for pattern in inv_patterns if pattern in content_lower)

    # Filename hints
    if "rca" in filename_lower:
        rca_score += 2
    if "gap" in filename_lower:
        gap_score += 2
    if "investigation" in filename_lower or "analysis" in filename_lower:
        inv_score += 2
    if "plan" in filename_lower and "execution" in filename_lower:
        exec_score += 2

    # Determine type with highest score
    scores = {
        "rca": rca_score,
        "gap_analysis": gap_score,
        "execution": exec_score,
        "investigation": inv_score,
    }

    max_type = max(scores, key=scores.get)
    max_score = scores[max_type]

    # Normalize confidence (0-1)
    confidence = min(max_score / 5.0, 1.0) if max_score > 0 else 0.0

    return max_type, confidence


def categorize_all_plans(repo_root: Path) -> dict:
    """Categorize all plans in the repository."""
    plan_dirs = [
        repo_root / "docs" / "reports" / "plans",
        repo_root / ".windsurf" / "plans",
    ]

    categories = {"execution": [], "rca": [], "gap_analysis": [], "investigation": [], "uncategorized": []}

    stats = {"total": 0, "encoding_errors": 0, "by_type": dict.fromkeys(categories, 0)}

    for plan_dir in plan_dirs:
        if not plan_dir.exists():
            continue

        for plan_path in plan_dir.rglob("*.md"):
            if plan_path.name == "README.md":
                continue

            stats["total"] += 1
            rel_path = str(plan_path.relative_to(repo_root))

            try:
                with open(plan_path, encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                stats["encoding_errors"] += 1
                categories["uncategorized"].append({"path": rel_path, "error": "encoding_error"})
                continue

            plan_type, confidence = detect_plan_type(content, plan_path.name)

            if confidence < 0.2:  # Low confidence
                categories["uncategorized"].append(
                    {"path": rel_path, "detected_type": plan_type, "confidence": confidence}
                )
            else:
                categories[plan_type].append({"path": rel_path, "confidence": confidence})
                stats["by_type"][plan_type] += 1

    return {"categories": categories, "stats": stats, "timestamp": datetime.utcnow().isoformat()}


def main():
    repo_root = Path(__file__).parent.parent
    result = categorize_all_plans(repo_root)

    # Print summary
    print("=== Plan Categorization Summary ===")
    print(f"Total plans: {result['stats']['total']}")
    print(f"Encoding errors: {result['stats']['encoding_errors']}")
    print("\nBy type:")
    for plan_type, count in result["stats"]["by_type"].items():
        print(f"  {plan_type}: {count}")
    print(f"  uncategorized: {len(result['categories']['uncategorized'])}")

    # Save detailed results
    output_path = repo_root / "artifacts" / "plan_classification.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nDetailed results saved to: {output_path}")

    # Export lists for processing
    for plan_type, plans in result["categories"].items():
        if plans and plan_type != "uncategorized":
            list_path = repo_root / "artifacts" / f"plans_{plan_type}.txt"
            with open(list_path, "w") as f:
                for plan in plans:
                    f.write(f"{plan['path']}\n")
            print(f"  {plan_type} plans: {list_path}")


if __name__ == "__main__":
    main()
