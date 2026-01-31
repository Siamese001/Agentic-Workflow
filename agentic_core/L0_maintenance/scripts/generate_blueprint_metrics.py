#!/usr/bin/env python3
"""
Generate functionality metrics and unified diffs for blueprint duplicate pairs.
Phase 1 of duplicate cleanup workflow.
"""

from datetime import datetime
from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
)
from agentic_core.utils.security import safe_git_execute


def count_methods(file_path: Path) -> int:
    """Count method definitions in file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        return sum(1 for line in content.split("\n") if line.strip().startswith("def "))
    except:
        return 0


def has_pattern(file_path: Path, pattern: str) -> bool:
    """Check if file contains pattern."""
    try:
        content = file_path.read_text(encoding="utf-8")
        return pattern in content
    except:
        return False


def count_lines(file_path: Path) -> int:
    """Count lines in file."""
    try:
        return len(file_path.read_text(encoding="utf-8").split("\n"))
    except:
        return 0


def generate_unified_diff(canonical: Path, duplicate: Path) -> str:
    """Generate unified diff between files."""
    try:
        result = safe_git_execute(
            ["diff", "--no-index", "--unified=3", str(canonical), str(duplicate)],
            repo_root=canonical.parent,
            timeout=30,
            check=False,
        )
        return result.stdout
    except:
        return ""


def main():
    project_root = Path.cwd()
    blueprint_dir = project_root / AGENTIC_CORE_DIR / "config" / "blueprint_sovereign"
    validators_dir = project_root / AGENTIC_CORE_DIR / "L5_safety" / "validators"

    # Create output directory
    diff_dir = project_root / REPORTS_DIR / "blueprint_diffs"
    diff_dir.mkdir(parents=True, exist_ok=True)

    # Find blueprint agent files
    # Phase 6.9: Use ssot_discovery instead of glob
    from agentic_core.utils.ssot_discovery import get_agent_files

    blueprint_agents = list(get_agent_files(blueprint_dir))

    print("=" * 80)
    print("PHASE 1: BLUEPRINT DUPLICATE METRICS")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Blueprint directory: {blueprint_dir}")
    print(f"Validators directory: {validators_dir}")
    print(f"Found {len(blueprint_agents)} blueprint agent files")
    print("=" * 80)

    # Generate report
    report_file = project_root / REPORTS_DIR / "blueprint_metrics_report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Blueprint Duplicate Metrics Report\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Summary\n")
        f.write(f"- **Blueprint files found:** {len(blueprint_agents)}\n")
        f.write("- **Diff output directory:** `reports/blueprint_diffs/`\n\n")

        f.write("## Metrics Comparison\n\n")
        f.write(
            "| Agent | Canonical Lines | Dup Lines | Can Methods | Dup Methods | Can Heal | Dup Heal | Recommendation |\n"
        )
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")

        pairs_found = 0

        for blueprint_file in sorted(blueprint_agents):
            agent_name = blueprint_file.stem
            canonical_file = validators_dir / blueprint_file.name

            if not canonical_file.exists():
                print(f"[SKIP] {agent_name}: No canonical in validators/")
                continue

            pairs_found += 1

            # Metrics
            can_lines = count_lines(canonical_file)
            dup_lines = count_lines(blueprint_file)
            can_methods = count_methods(canonical_file)
            dup_methods = count_methods(blueprint_file)
            can_heal = has_pattern(canonical_file, "def heal")
            dup_heal = has_pattern(blueprint_file, "def heal")

            # Recommendation
            if can_lines >= dup_lines and can_methods >= dup_methods:
                recommendation = "✅ DELETE blueprint"
            elif dup_lines > can_lines or dup_methods > can_methods:
                recommendation = "⚠️ REVIEW - dup may have additions"
            else:
                recommendation = "✅ DELETE blueprint"

            print(f"\n[{agent_name}]")
            print(f"  Canonical: {can_lines} lines, {can_methods} methods, heal={can_heal}")
            print(f"  Blueprint: {dup_lines} lines, {dup_methods} methods, heal={dup_heal}")
            print(f"  → {recommendation}")

            f.write(
                f"| {agent_name} | {can_lines} | {dup_lines} | {can_methods} | {dup_methods} | "
            )
            f.write(
                f"{'✅' if can_heal else '❌'} | {'✅' if dup_heal else '❌'} | {recommendation} |\n"
            )

            # Generate diff
            diff_content = generate_unified_diff(canonical_file, blueprint_file)
            diff_file = diff_dir / f"{agent_name}_diff.patch"
            diff_file.write_text(diff_content, encoding="utf-8")

        f.write("\n## Diff Files\n\n")
        f.write(f"Generated {pairs_found} diff files in `reports/blueprint_diffs/`\n\n")
        f.write("```bash\n")
        f.write("# Open all diffs in Windsurf\n")
        f.write("code reports/blueprint_diffs/*.patch\n")
        f.write("```\n\n")

        f.write("## Delete Commands (After Review)\n\n")
        f.write("```bash\n")
        for blueprint_file in sorted(blueprint_agents):
            canonical_file = validators_dir / blueprint_file.name
            if canonical_file.exists():
                rel_path = blueprint_file.relative_to(project_root)
                f.write(f'git rm "{rel_path}"\n')
        f.write('git commit -m "chore: remove blueprint duplicate agents (Phase 1)"\n')
        f.write("```\n")

    print("\n" + "=" * 80)
    print(f"✅ Report generated: {report_file}")
    print(f"✅ Diff files generated: {diff_dir}")
    print(f"   Pairs found: {pairs_found}")
    print("=" * 80)


if __name__ == "__main__":
    main()
