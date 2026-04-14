"""
Verify FileClassificationAgent classification behavior against targeted sample files.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

DEFAULT_TARGETS = [
    ("agentic_core/L3_orchestration", "ORCHESTRATION"),
    ("agentic_core/L5_safety", "SAFETY"),
    ("apps_shared", "SHARED"),
]


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _bootstrap(repo_root: Path) -> None:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))  # guardian: allow-global-mutation -- verifier bootstrap


def verify_classifications(repo_root: Path) -> int:
    _bootstrap(repo_root)
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

    agent = FileClassificationAgent(project_root=repo_root, dry_run=True, validate_only=True)
    failures = 0

    print("VERIFY FILE CLASSIFICATION FIXES")
    print("=" * 60)
    for relative_path, expected_label in DEFAULT_TARGETS:
        target = repo_root / relative_path
        if not target.exists():
            print(f"⚠️  Missing target: {target}")
            failures += 1
            continue

        try:
            classification = agent.classify_file(target)
            print(f"Target: {relative_path}")
            print(f"  Expected signal: {expected_label}")
            print(f"  Actual classification: {classification}")
            if expected_label.lower() not in str(classification).lower():
                failures += 1
                print("  ❌ Classification did not match expected signal")
            else:
                print("  ✅ Classification signal looks correct")
        except (AttributeError, ImportError, OSError, ValueError, RuntimeError) as exc:
            failures += 1
            print(f"  ❌ Error classifying {relative_path}: {exc}")

    print("\n" + "=" * 60)
    if failures == 0:
        print("✅ Classification verification passed")
        return 0

    print(f"❌ Classification verification found {failures} issue(s)")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify FileClassificationAgent classification fixes.")
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    return verify_classifications(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
