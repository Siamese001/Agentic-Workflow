#!/usr/bin/env python3
"""
Add Wave Tables to Legacy Execution Plans
Automatically adds wave structure tables to execution plans that are missing them.
"""

import sys
from pathlib import Path


def is_execution_plan(content: str, filename: str) -> bool:
    """Check if this is an execution plan that needs a wave table."""
    content_lower = content.lower()
    filename_lower = filename.lower()

    # Has execution plan indicators
    exec_indicators = ["## execution plan", "phase 1", "phase 2", "implementation", "## steps", "## commands"]

    # Missing wave structure
    has_wave = "## wave structure" in content_lower

    # Check if it looks like an execution plan without waves
    if not has_wave and any(indicator in content_lower for indicator in exec_indicators):
        return True

    # Filename contains 'plan' and no waves
    if "plan" in filename_lower and not has_wave:
        return True

    return False


def generate_wave_table() -> str:
    """Generate a standard wave table template."""
    return """## Wave Structure

| Waves | Metric | Scope | Checkpoint | [Tokens |]
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---

"""


def add_wave_table_to_plan(file_path: Path, dry_run: bool = True) -> tuple[bool, str]:
    """Add wave table to a plan file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return False, "Encoding error"

    if not is_execution_plan(content, file_path.name):
        return True, "Not an execution plan (no wave table needed)"

    if "## Wave Structure" in content:
        return True, "Already has wave table"

    # Find insertion point (after title, before first section)
    lines = content.split("\n")
    insert_index = 1  # After title

    # Find first ## section to insert before it
    for i, line in enumerate(lines):
        if line.startswith("##") and not line.startswith("## Wave Structure"):
            insert_index = i
            break

    # Insert wave table
    wave_table = generate_wave_table()
    new_content = lines[:insert_index] + [wave_table] + lines[insert_index:]
    new_content_str = "\n".join(new_content)

    if dry_run:
        return False, f"Would add wave table to {file_path.name}"

    # Write back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content_str)

    return True, f"Added wave table to {file_path.name}"


def find_execution_plans_needing_waves(repo_root: Path) -> list[Path]:
    """Find execution plans that need wave tables."""
    plan_dirs = [
        repo_root / "docs" / "reports" / "plans",
        repo_root / ".windsurf" / "plans",
    ]

    plans_needing_waves = []

    for plan_dir in plan_dirs:
        if not plan_dir.exists():
            continue

        for plan_path in plan_dir.rglob("*.md"):
            if plan_path.name == "README.md":
                continue

            try:
                with open(plan_path, encoding="utf-8") as f:
                    content = f.read()

                if is_execution_plan(content, plan_path.name):
                    plans_needing_waves.append(plan_path)

            except UnicodeDecodeError:
                continue  # Skip encoding errors

    return plans_needing_waves


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Add wave tables to execution plans")
    parser.add_argument(
        "--type", choices=["execution", "all"], default="execution", help="Type of plans to process",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--execute", action="store_true", help="Actually make changes")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Error: Must specify either --dry-run or --execute")
        sys.exit(1)

    repo_root = Path(__file__).parent.parent

    if args.type == "execution":
        plans_to_process = find_execution_plans_needing_waves(repo_root)
        print(f"Found {len(plans_to_process)} execution plans needing wave tables")
    else:
        print("Error: Only 'execution' type is currently supported")
        sys.exit(1)

    if not plans_to_process:
        print("No plans need wave tables!")
        return

    success_count = 0
    skip_count = 0
    error_count = 0

    for plan_path in plans_to_process:
        rel_path = str(plan_path.relative_to(repo_root))
        success, message = add_wave_table_to_plan(plan_path, dry_run=args.dry_run)

        if success:
            print(f"✅ {rel_path}: {message}")
            success_count += 1
        elif "Not an execution plan" in message:
            print(f"⏭️  {rel_path}: {message}")
            skip_count += 1
        elif "Already has" in message:
            print(f"⏭️  {rel_path}: {message}")
            skip_count += 1
        else:
            print(f"❌ {rel_path}: {message}")
            error_count += 1

    print("\nSummary:")
    print(f"  Total plans: {len(plans_to_process)}")
    print(f"  Success: {success_count}")
    print(f"  Skipped: {skip_count}")
    print(f"  Errors: {error_count}")

    if args.dry_run:
        print(f"\nRun with --execute to actually add wave tables to {success_count} plans")


if __name__ == "__main__":
    main()
