#!/usr/bin/env python3
"""Analyze exact duplicate clusters for Wave 2.2 refactoring."""

import json
from pathlib import Path


def main():
    repo_root = Path.cwd()

    # Load clusters
    with open(repo_root / "docs/reports/sub/ast_fuzzy_clusters.json", encoding="utf-8") as f:
        clusters = json.load(f)

    exact = clusters["exact_dupe_clusters"]
    print(f"Total exact duplicate clusters: {len(exact)}\n")

    # Sort by member count (descending) to find highest-confidence dupes
    sorted_clusters = sorted(exact, key=lambda c: len(c["members"]), reverse=True)

    print("Top 5 exact duplicate clusters by member count:\n")
    for i, cluster in enumerate(sorted_clusters[:5], 1):
        members = cluster["members"]
        print(f"{i}. Hash: {cluster['hash'][:16]}...")
        print(f"   Members: {len(members)}")
        for j, member in enumerate(members[:3], 1):
            print(f"   {j}. {member['path']}:{member['line']} ({member['kind']}) - {member['name']}")
        if len(members) > 3:
            print(f"   ... and {len(members) - 3} more")
        print()


if __name__ == "__main__":
    main()
