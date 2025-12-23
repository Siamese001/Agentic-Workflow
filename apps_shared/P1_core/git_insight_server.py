# servers/git_insight_server.py
import time

import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP
from pydriller import Repository

# Initialize the Server
mcp = FastMCP("GitInsight")


def _get_repo_path() -> str:
    """Helper to get the current working directory safely."""
    return os.getcwd()


@mcp.tool()
def analyze_hotspots(days: int = 30, limit: int = 10) -> str:
    """
    Identifies files with the highest 'churn' (lines modified) in the last N days.
    High churn often correlates with technical debt or active bug clusters.

    Args:
        days: How far back to look (default 30).
        limit: Number of top files to return (default 10).
    """
    since_date = datetime.now() - timedelta(days=days)
    churn_map = defaultdict(int)
    commit_count = 0

    path = _get_repo_path()
    try:
        # Traverse commits efficiently
        for commit in Repository(path, since=since_date).traverse_commits():
            commit_count += 1
            for file in commit.modified_files:
                # changes = added + deleted lines
                churn_map[file.filename] += file.added_lines + \
                    file.deleted_lines
    except Exception as e:
        return f"Error analyzing repository at {path}: {str(e)}"

    if commit_count == 0:
        return f"No commits found in the last {days} days."

    # Sort and Format
    sorted_churn = sorted(
        churn_map.items(), key=lambda x: x[1], reverse=True)[:limit]

    report = [
        f"🔥 Repository Hotspots (Last {days} days, {commit_count} commits scanned):"]
    report.append(f"{'File':<50} | {'Lines Changed':<15}")
    report.append("-" * 70)

    for filename, churn in sorted_churn:
        report.append(f"{filename:<50} | {churn:<15}")

    return "\n".join(report)


@mcp.tool()
def file_history_analytics(file_path: str) -> str:
    """
    Detailed analytics for a specific file:
    - Primary Author (who knows this code best?)
    - Revision Count
    - Last Modified Date
    """
    path = _get_repo_path()
    authors = Counter()
    revisions = 0
    last_modified = None
    created_at = None

    try:
        # Only traverse commits touching this specific file
        for commit in Repository(path, filepath=file_path).traverse_commits():
            revisions += 1
            authors[commit.author.name] += 1
            last_modified = commit.author_date
            if created_at is None:
                created_at = commit.author_date
    except Exception as e:
        return f"Error analyzing file {file_path}: {str(e)}"

    if revisions == 0:
        return f"File '{file_path}' not found in git history."

    # Calculate statistics
    primary_author, primary_count = authors.most_common(1)[0]
    ownership_percent = (primary_count / revisions) * 100

    return f"""
    📄 File Intelligence: {file_path}
    -------------------------------------------
    👑 Code Owner:   {primary_author} ({ownership_percent:.1f}% of revisions)
    [STATS] Total Edits:  {revisions}
    📅 Created:      {created_at.strftime('%Y-%m-%d')}
    📅 Last Update:  {last_modified.strftime('%Y-%m-%d')}

    👥 Top Contributors:
    {_format_counter(authors)}
    """


@mcp.tool()
def detect_logical_coupling(file_path: str, min_correlation: float = 0.3) -> str:
    """
    Finds 'Implicit Dependencies'.
    If I change 'file_path', what OTHER files usually change in the same commit?

    Args:
        file_path: The target file.
        min_correlation: Threshold (0.0 to 1.0) to report a link. 0.3 means 30% of the time.
    """
    path = _get_repo_path()
    co_changed = Counter()
    total_commits_involving_target = 0

    try:
        # Scan history for the target file
        for commit in Repository(path, filepath=file_path).traverse_commits():
            total_commits_involving_target += 1

            for file in commit.modified_files:
                if file.filename != file_path:
                    co_changed[file.filename] += 1
    except Exception as e:
        return f"Error analyzing coupling: {str(e)}"

    if total_commits_involving_target < 3:
        return f"Not enough history ({total_commits_involving_target} commits) to determine coupling for {file_path}."

    # Analyze Correlations
    report = [f"🔗 Logical Coupling Analysis for: {file_path}"]
    report.append(f"(Based on {total_commits_involving_target} commits)")
    report.append("-" * 60)

    found_coupling = False
    for other_file, count in co_changed.most_common(10):
        correlation = count / total_commits_involving_target
        if correlation >= min_correlation:
            found_coupling = True
            report.append(
                f"- {other_file:<40} (Changed together {correlation:.0%} of the time)")

    if not found_coupling:
        report.append(
            "No significant coupling detected. This file is relatively isolated.")

    return "\n".join(report)


def _format_counter(counter: Counter) -> str:
    return "\n".join([f"  - {name}: {count}" for name, count in counter.most_common(5)])


if __name__ == "__main__":
    mcp.run()

