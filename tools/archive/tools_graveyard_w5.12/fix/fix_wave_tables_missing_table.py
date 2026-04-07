#!/usr/bin/env python3
"""
Fix Wave Tables Missing Table
Add wave tables to plans that have ## Wave Structure section but no table.
"""

import re
import sys
from pathlib import Path


def has_wave_table(content: str) -> bool:
    """Check if content has a wave table after ## Wave Structure."""
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if line.startswith("## Wave Structure"):
            # Look for table in next 10 lines
            for j in range(i + 1, min(i + 11, len(lines))):
                if re.match(r"\| Waves \| Metric \| Scope \| Checkpoint \|(\s*\| Tokens \|)?", lines[j]):
                    return True
            break
    return False


def generate_wave_table() -> str:
    """Generate a standard wave table template."""
    return """| Waves | Metric | Scope | Checkpoint | [Tokens |]
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**


---


"""


def fix_wave_table(file_path: Path, dry_run: bool = True) -> tuple[bool, str]:
    """Add wave table to a plan file that has ## Wave Structure but no table."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return False, "Encoding error"

    if "## Wave Structure" not in content:
        return True, "No Wave Structure section"

    if has_wave_table(content):
        return True, "Already has wave table"

    # Find insertion point (after ## Wave Structure)
    lines = content.split("\n")
    insert_index = -1

    for i, line in enumerate(lines):
        if line.startswith("## Wave Structure"):
            # Insert after this line and any empty lines
            insert_index = i + 1
            while insert_index < len(lines) and lines[insert_index].strip() == "":
                insert_index += 1
            break

    if insert_index == -1:
        return False, "Could not find insertion point"

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


def find_plans_needing_table(repo_root: Path) -> list[Path]:
    """Find plans that have ## Wave Structure but no table."""
    plan_dirs = [
        repo_root / "docs" / "reports" / "plans",
        repo_root / ".windsurf" / "plans",
    ]

    plans_needing_table = []

    for plan_dir in plan_dirs:
        if not plan_dir.exists():
            continue

        for plan_path in plan_dir.rglob("*.md"):
            if plan_path.name == "README.md":
                continue

            try:
                with open(plan_path, encoding="utf-8") as f:
                    content = f.read()

                if "## Wave Structure" in content and not has_wave_table(content):
                    plans_needing_table.append(plan_path)

            except UnicodeDecodeError:
                continue  # Skip encoding errors

    return plans_needing_table


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fix wave tables missing table")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--execute", action="store_true", help="Actually make changes")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Error: Must specify either --dry-run or --execute")
        sys.exit(1)

    repo_root = Path(__file__).parent.parent
    plans_to_fix = find_plans_needing_table(repo_root)

    print(f"Found {len(plans_to_fix)} plans with ## Wave Structure but no table")

    if not plans_to_fix:
        print("No plans need fixing!")
        return

    success_count = 0
    skip_count = 0
    error_count = 0

    for plan_path in plans_to_fix:
        rel_path = str(plan_path.relative_to(repo_root))
        success, message = fix_wave_table(plan_path, dry_run=args.dry_run)

        if success:
            print(f"✅ {rel_path}: {message}")
            success_count += 1
        elif "No Wave Structure" in message or "Already has" in message:
            print(f"⏭️  {rel_path}: {message}")
            skip_count += 1
        else:
            print(f"❌ {rel_path}: {message}")
            error_count += 1

    print("\nSummary:")
    print(f"  Total plans: {len(plans_to_fix)}")
    print(f"  Success: {success_count}")
    print(f"  Skipped: {skip_count}")
    print(f"  Errors: {error_count}")

    if args.dry_run:
        print(f"\nRun with --execute to actually add wave tables to {success_count} plans")


if __name__ == "__main__":
    main()
