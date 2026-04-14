#!/usr/bin/env python3
"""
Validate pre-commit configuration to prevent hook ordering issues.

Checks for:
- Hook ordering conflicts
- Missing auto-stage hook
- Known problematic hook combinations
"""

import sys
from pathlib import Path
from typing import Any

import yaml


PRE_COMMIT_HOOKS_REPO = "https://github.com/pre-commit/pre-commit-hooks"
T0_HOOK_ORDER = (
    "trailing-whitespace",
    "end-of-file-fixer",
    "mixed-line-ending",
    "check-merge-conflict",
    "auto-stage-hook-fixes",
)
T0_HOOK_SET = frozenset(T0_HOOK_ORDER)


def _load_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError("Top-level YAML structure must be a mapping")
    return loaded


def _iter_matching_repos(config: dict[str, Any]) -> list[dict[str, Any]]:
    repos = config.get("repos", [])
    if not isinstance(repos, list):
        return []
    matches: list[dict[str, Any]] = []
    for repo in repos:
        if not isinstance(repo, dict):
            continue
        if PRE_COMMIT_HOOKS_REPO in str(repo.get("repo", "")):
            matches.append(repo)
    return matches


def _hook_ids(repo: dict[str, Any]) -> list[str]:
    hooks = repo.get("hooks", [])
    if not isinstance(hooks, list):
        return []
    hook_ids: list[str] = []
    for hook in hooks:
        if not isinstance(hook, dict):
            continue
        hook_id = hook.get("id")
        if isinstance(hook_id, str):
            hook_ids.append(hook_id)
    return hook_ids


def check_auto_stage_hook_present(config):
    """Ensure auto-stage-hook-fixes is present and last in T0."""
    all_t0_hooks = []
    matching_repos = _iter_matching_repos(config)

    if not matching_repos:
        print("❌ pre-commit-hooks repo not found")
        return False

    for repo in matching_repos:
        all_t0_hooks.extend([hook_id for hook_id in _hook_ids(repo) if hook_id in T0_HOOK_SET])

    auto_stage_position = next(
        (idx for idx, hook_id in enumerate(all_t0_hooks) if hook_id == "auto-stage-hook-fixes"),
        -1,
    )

    if auto_stage_position == -1:
        print("❌ Missing auto-stage-hook-fixes hook")
        return False

    if auto_stage_position != len(all_t0_hooks) - 1:
        print("❌ auto-stage-hook-fixes is not last in T0")
        print(f"   Expected position: {len(all_t0_hooks) - 1}, got: {auto_stage_position}")
        print(f"   T0 hooks found: {all_t0_hooks}")
        return False

    print("✅ auto-stage-hook-fixes is properly positioned")
    return True


def check_hook_ordering(config):
    """Check for known problematic hook ordering."""
    issues = []
    for repo in _iter_matching_repos(config):
        hooks = _hook_ids(repo)
        t0_in_config = [hook for hook in hooks if hook in T0_HOOK_SET]
        expected_order = [hook for hook in T0_HOOK_ORDER if hook in t0_in_config]
        if t0_in_config != expected_order:
            issues.append(f"T0 hooks not in recommended order for repo={repo.get('repo', '<unknown>')}")

    if issues:
        for issue in issues:
            print(f"⚠️  {issue}")
        return False

    print("✅ Hook ordering looks good")
    return True


def check_exclude_patterns(config):
    """Check for exclude patterns that might cause issues."""
    global_exclude = config.get("exclude", "")
    if global_exclude and not isinstance(global_exclude, str):
        print("❌ Global exclude must be a string")
        return False

    if r".*\.md$" not in global_exclude:
        print("⚠️  Consider excluding .md files from formatting hooks")

    print("✅ Exclude patterns look reasonable")
    return True


def main():
    """Validate pre-commit configuration."""
    config_path = Path(".pre-commit-config.yaml")

    if not config_path.exists():
        print("❌ .pre-commit-config.yaml not found")
        return 1

    try:
        config = _load_config(config_path)
    except (OSError, ValueError) as e:
        print(f"❌ Failed to load config: {e}")
        return 1
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML: {e}")
        return 1

    print("Validating pre-commit configuration...")
    print()

    results = [
        check_auto_stage_hook_present(config),
        check_hook_ordering(config),
        check_exclude_patterns(config),
    ]
    all_good = all(results)

    print()
    if all_good:
        print("✅ Pre-commit configuration is valid")
        return 0

    print("❌ Pre-commit configuration has issues")
    return 1


if __name__ == "__main__":
    sys.exit(main())
