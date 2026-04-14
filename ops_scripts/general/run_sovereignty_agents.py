"""
Run RootHygieneAgent and PascalSovereigntyAgent, then perform a validation audit.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


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
        sys.path.insert(0, str(repo_root))  # guardian: allow-global-mutation -- runtime bootstrap


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run sovereignty guardians and their validation audit.")
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Run hygiene and sovereignty agents in dry-run mode."
    )
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    _bootstrap(repo_root)

    from agentic_core.L5_safety.reasoning.PascalSovereigntyAgent import PascalSovereigntyAgent
    from agentic_core.L5_safety.reasoning.root_hygiene_healer import RootHygieneAgent

    print("=" * 80)
    print("SOVEREIGNTY GUARDIANS EXECUTION")
    print("=" * 80)

    print("\n[PHASE 1] Executing RootHygieneAgent...")
    hygiene_agent = RootHygieneAgent(project_root=repo_root, dry_run=args.dry_run)
    hygiene_result = hygiene_agent.run()
    print("\n=== ROOT HYGIENE RESULTS ===")
    print(f"Success: {hygiene_result.get('success')}")
    print(f"Stats: {hygiene_result.get('stats')}")
    print(f"Summary: {hygiene_result.get('summary')}")

    print("\n[PHASE 2] Executing PascalSovereigntyAgent...")
    pascal_agent = PascalSovereigntyAgent(project_root=repo_root, dry_run=args.dry_run)
    pascal_result = pascal_agent.run()
    print("\n=== PASCAL SOVEREIGNTY RESULTS ===")
    print(f"Success: {pascal_result.get('success')}")
    print(f"Stats: {pascal_result.get('stats')}")
    print(f"Summary: {pascal_result.get('summary')}")

    print("\n[PHASE 3] Running validation audit...")
    validator = PascalSovereigntyAgent(project_root=repo_root, dry_run=True, validate_only=True)
    validator.run()
    total_violations = sum(validator.stats["violations"].values())

    print("\n=== VALIDATION AUDIT ===")
    print(f"Total Violations Remaining: {total_violations}")
    print(f"Compliant Files: {validator.stats['compliant']}")
    print(f"Analyzed Files: {validator.stats['analyzed']}")

    if total_violations == 0:
        print("\n✅ 100% COMPLIANT - All sovereignty standards enforced!")
        return 0

    print(f"\n⚠️  {total_violations} violations remain - manual review required")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
