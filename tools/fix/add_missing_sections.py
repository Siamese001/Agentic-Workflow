#!/usr/bin/env python3
"""
Add Missing Sections to Plans
Add ## Rules and ## Success Criteria sections to execution plans.
"""

import sys
from pathlib import Path


def detect_plan_type(content: str, filename: str) -> str:
    """Detect plan type from content and filename."""
    content_lower = content.lower()
    filename_lower = filename.lower()

    # RCA patterns
    if any(
        pattern in content_lower
        for pattern in ["## violation", "## root cause", "## corrective actions", "rca:"]
    ):
        return "rca"

    # Gap analysis patterns
    if any(pattern in content_lower for pattern in ["gap register", "gap analysis", "implementation gap"]):
        return "gap_analysis"

    # Execution plan patterns
    if any(
        pattern in content_lower
        for pattern in ["## wave structure", "## execution plan", "phase 1", "wave 1"]
    ):
        return "execution"

    # Investigation patterns
    if any(pattern in content_lower for pattern in ["## investigation", "## findings", "## assessment"]):
        return "investigation"

    # Default to execution if filename contains 'plan'
    if "plan" in filename_lower:
        return "execution"

    # Default fallback
    return "investigation"


def add_missing_sections(file_path: Path, dry_run: bool = True) -> tuple[bool, str]:
    """Add missing sections to a plan file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return False, "Encoding error"

    plan_type = detect_plan_type(content, file_path.name)

    # Define required sections by type
    section_requirements = {
        "execution": ["## Rules", "## Success Criteria"],
        "rca": ["## Violation", "## Root Cause", "## Corrective Actions"],
        "gap_analysis": ["## Gap Register", "## Execution Plan"],
        "investigation": ["## Findings", "## Evidence"]
    }

    required_sections = section_requirements.get(plan_type, [])
    missing_sections = []

    for section in required_sections:
        if section not in content:
            missing_sections.append(section)

    if not missing_sections:
        return True, "All required sections present"

    # Generate missing sections
    sections_to_add = []

    if "## Rules" in missing_sections:
        sections_to_add.append("""## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

""")

    if "## Success Criteria" in missing_sections:
        sections_to_add.append("""## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

""")

    if "## Violation" in missing_sections:
        sections_to_add.append("""## Violation

[Describe the violation or issue that triggered this RCA]

---

""")

    if "## Root Cause" in missing_sections:
        sections_to_add.append("""## Root Cause

[Identify and explain the root cause of the violation]

---

""")

    if "## Corrective Actions" in missing_sections:
        sections_to_add.append("""## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

""")

    if "## Gap Register" in missing_sections:
        sections_to_add.append("""## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

""")

    if "## Execution Plan" in missing_sections:
        sections_to_add.append("""## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

""")

    if "## Findings" in missing_sections:
        sections_to_add.append("""## Findings

[Document key findings from the investigation]

---

""")

    if "## Evidence" in missing_sections:
        sections_to_add.append("""## Evidence

[Provide evidence supporting the findings]

---

""")

    if dry_run:
        return False, f"Would add {len(missing_sections)} sections to {file_path.name}"

    # Add sections at the end of the file
    new_content = content + "\n" + "".join(sections_to_add)

    # Write back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True, f"Added {len(missing_sections)} sections to {file_path.name}"


def find_plans_needing_sections(repo_root: Path) -> list[Path]:
    """Find plans that need sections."""
    plan_dirs = [
        repo_root / "docs" / "reports" / "plans",
        repo_root / ".windsurf" / "plans",
    ]

    plans_needing_sections = []

    for plan_dir in plan_dirs:
        if not plan_dir.exists():
            continue

        for plan_path in plan_dir.rglob("*.md"):
            if plan_path.name == "README.md":
                continue

            try:
                with open(plan_path, encoding="utf-8") as f:
                    content = f.read()

                plan_type = detect_plan_type(content, plan_path.name)
                section_requirements = {
                    "execution": ["## Rules", "## Success Criteria"],
                    "rca": ["## Violation", "## Root Cause", "## Corrective Actions"],
                    "gap_analysis": ["## Gap Register", "## Execution Plan"],
                    "investigation": ["## Findings", "## Evidence"]
                }

                required_sections = section_requirements.get(plan_type, [])
                missing_sections = []

                for section in required_sections:
                    if section not in content:
                        missing_sections.append(section)

                if missing_sections:
                    plans_needing_sections.append(plan_path)

            except UnicodeDecodeError:
                continue  # Skip encoding errors

    return plans_needing_sections


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Add missing sections to plans")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--execute", action="store_true", help="Actually make changes")
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Error: Must specify either --dry-run or --execute")
        sys.exit(1)

    repo_root = Path(__file__).parent.parent
    plans_to_fix = find_plans_needing_sections(repo_root)

    print(f"Found {len(plans_to_fix)} plans needing sections")

    if not plans_to_fix:
        print("No plans need fixing!")
        return

    success_count = 0
    skip_count = 0
    error_count = 0

    for plan_path in plans_to_fix:
        rel_path = str(plan_path.relative_to(repo_root))
        success, message = add_missing_sections(plan_path, dry_run=args.dry_run)

        if success:
            print(f"✅ {rel_path}: {message}")
            success_count += 1
        elif "All required sections" in message:
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
        print(f"\nRun with --execute to actually add sections to {success_count} plans")


if __name__ == "__main__":
    main()
