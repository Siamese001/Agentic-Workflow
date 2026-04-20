#!/usr/bin/env python3
"""
Branch cleanup helper for Agentic-Workflow repository
Analyze and suggest safe branch removal strategies
"""

import subprocess
from datetime import datetime


def run_git_command(cmd: str) -> str:
    """Run git command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="c:/Git/Agentic-Workflow")
    if result.returncode != 0:
        print(f"Error running {cmd}: {result.stderr}")
        return ""
    return result.stdout.strip()


def get_remote_branches() -> list[str]:
    """Get list of remote branches"""
    output = run_git_command("git branch -r")
    branches = []
    for line in output.split("\n"):
        if line.strip() and "HEAD" not in line:
            branch = line.strip().replace("remotes/origin/", "")
            branches.append(branch)
    return branches


def get_branch_last_date(branch: str) -> str:
    """Get last commit date for a branch"""
    cmd = f"git log -1 --format=%ci origin/{branch}"
    return run_git_command(cmd)


def get_branch_commit_count(branch: str) -> int:
    """Get number of commits unique to this branch"""
    cmd = f"git rev-list --count main..origin/{branch}"
    output = run_git_command(cmd)
    return int(output) if output else 0


def categorize_branches() -> dict[str, list[dict]]:
    """Categorize branches by cleanup priority"""
    branches = get_remote_branches()
    categories = {"safe_to_delete": [], "review_needed": [], "keep": []}

    # Branches to always keep
    keep_branches = {"main", "governance_hardening", "HEAD"}

    for branch in branches:
        if branch in keep_branches:
            categories["keep"].append({"name": branch, "reason": "Protected branch"})
            continue

        last_date = get_branch_last_date(branch)
        commit_count = get_branch_commit_count(branch)

        # Parse date
        try:
            branch_date = datetime.strptime(last_date.split()[0], "%Y-%m-%d")
            days_old = (datetime.now() - branch_date).days
        except Exception:  # guardian: allow-silent-swallow
            days_old = 999

        branch_info = {
            "name": branch,
            "last_commit": last_date,
            "days_old": days_old,
            "unique_commits": commit_count,
        }

        # Categorization logic
        if days_old > 90 and commit_count == 0:
            categories["safe_to_delete"].append(branch_info)
        elif days_old > 60 or "phase" in branch.lower() or "test" in branch.lower():
            categories["review_needed"].append(branch_info)
        else:
            categories["keep"].append(branch_info)

    return categories


def generate_cleanup_commands() -> None:
    """Generate cleanup commands for review"""
    categories = categorize_branches()

    print("=== BRANCH CLEANUP ANALYSIS ===\n")

    print(f"SAFE TO DELETE ({len(categories['safe_to_delete'])} branches):")
    for branch in categories["safe_to_delete"]:
        print(f"  - {branch['name']} (last: {branch['last_commit']}, {branch['days_old']} days old)")

    print(f"\nREVIEW NEEDED ({len(categories['review_needed'])} branches):")
    for branch in categories["review_needed"]:
        print(
            f"  - {branch['name']} (last: {branch['last_commit']}, {branch['days_old']} days old, {branch['unique_commits']} unique commits)",
        )

    print(f"\nKEEP ({len(categories['keep'])} branches):")
    for branch in categories["keep"]:
        reason = branch.get("reason", "Active/Recent")
        print(f"  - {branch['name']} ({reason})")

    # Generate safe delete commands
    if categories["safe_to_delete"]:
        print("\n=== SAFE DELETE COMMANDS ===")
        print("# Review these commands carefully before running:")
        for branch in categories["safe_to_delete"]:
            print(f"git push origin --delete {branch['name']}")

    # Generate backup commands
    print("\n=== BACKUP COMMANDS ===")
    print("# Create backup tags before deletion:")
    for branch in categories["safe_to_delete"]:
        tag_name = f"backup/{branch['name']}"
        print(f"git tag {tag_name} origin/{branch['name']}")
        print(f"git push origin {tag_name}")


if __name__ == "__main__":
    generate_cleanup_commands()
