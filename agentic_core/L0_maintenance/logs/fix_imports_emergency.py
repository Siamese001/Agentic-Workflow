from pathlib import Path


def fix_sovereign_imports():
    """
    Emergency Fix Script for 2026-01-22 Governance Crisis.
    Target: 212 files importing SovereignBaseAgent from 'observability'.
    Action: Point them to 'base_agents'.
    """
    # Auto-detect root (assuming script is run from root or close to it)
    root_dir = Path.cwd()
    if not (root_dir / "agentic_core").exists():
        print("❌ Error: Run this script from the project root (where 'agentic_core' exists).")
        return

    print(f"🔧 Starting Import Repair in: {root_dir}")

    broken_str = "from agentic_core.base_agents.SovereignBaseAgent"
    fixed_str = "from agentic_core.base_agents.SovereignBaseAgent"

    count_fixed = 0
    count_errors = 0

    # Walk all .py files
    for file_path in root_dir.rglob("*.py"):
        try:
            # Read content
            original_content = file_path.read_text(encoding="utf-8")

            # Check for broken import
            if broken_str in original_content:
                # Perform atomic replacement
                new_content = original_content.replace(broken_str, fixed_str)

                # Write back
                file_path.write_text(new_content, encoding="utf-8")
                print(f"  ✅ Fixed: {file_path.relative_to(root_dir)}")
                count_fixed += 1

        except Exception as e:
            print(f"  ❌ Failed to read/write {file_path.name}: {e}")
            count_errors += 1

    print("-" * 50)
    print("🎉 REPAIR COMPLETE")
    print(f"Files Fixed: {count_fixed}")
    print(f"Errors:      {count_errors}")
    print("Next Step:   Run 'pytest tests/unit/test_hierarchy_agent_phase1.py' to verify.")


if __name__ == "__main__":
    fix_sovereign_imports()
