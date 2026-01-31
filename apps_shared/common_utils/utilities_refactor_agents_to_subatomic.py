#!/usr/bin/env python3
"""
Automated refactoring script to update all agents to use shared Sub-Atomic Engine.
This script systematically updates all agent files in agentic_core/agents/.
"""

import re

# NAMING FIXED: AGENT_FILES → agent_files
agent_files = [
    "memory_architect.py",
    "ContextCurator.py",
    "hallucination_hunter.py",
    "HealerAgent.py",
    "analysis.py",
    "dynamic_model_router.py",
]

# NAMING FIXED: AGENTS_DIR → agents_dir
agents_dir = Path("c:/Git/Agentic-Workflow/agentic_core/agents")


def add_subatomic_imports(content: str) -> str:
    """Add Sub-Atomic Engine imports if not present."""
    import_line = "from apps_shared.canon_validator_agentic_v2_1 import get_subatomic_engine, get_safety_guardrail, get_fission_manager"

    if import_line in content:
        return content

    # Find the last import statement
    lines = content.split("\n")
    last_import_idx = -1

    for i, line in enumerate(lines):
        if line.strip().startswith(("import ", "from ")) and "import" in line:
            last_import_idx = i

    if last_import_idx >= 0:
        lines.insert(last_import_idx + 1, import_line)
        return "\n".join(lines)

    return content


def remove_thinking_budget_over_limit(content: str) -> str:
    """Replace thinking_budget values over 24576 with 24576."""
    # Pattern: thinking_budget=<number>
    pattern = r"thinking_budget\s*=\s*(\d+)"

    def replace_budget(match):
        budget = int(match.group(1))
        if budget > 24576:
            print(f"   Fixing thinking_budget: {budget} -> 24576")
            return "thinking_budget=24576"
        return match.group(0)

    return re.sub(pattern, replace_budget, content)


def add_engine_initialization(content: str, class_name: str) -> str:
    """Add engine initialization to __init__ method."""
    # Find __init__ method

    engine_init = """
        # Initialize shared Sub-Atomic Engine components
        if hasattr(self.ctx, '_client') and self.ctx._client:
            try:
                self.engine = get_subatomic_engine(gemini_client=self.ctx._client)
                self.safety = get_safety_guardrail()
                self.fission = get_fission_manager()
            except Exception as e:
                Logger.warning(f"Failed to initialize Sub-Atomic Engine: {e}")
                self.engine = None
                self.safety = None
                self.fission = None
        else:
            self.engine = None
            self.safety = None
            self.fission = None
"""

    # Check if already initialized
    if "self.engine = get_subatomic_engine" in content:
        return content

    # Try to add after super().__init__() or at end of __init__
    if "super().__init__" in content:
        content = content.replace("super().__init__(ctx)", f"super().__init__(ctx){engine_init}")

    return content


def process_agent_file(file_path: Path) -> bool:
    """Process a single agent file."""
    print(f"\n📝 Processing: {file_path.name}")

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Step 1: Add imports
        content = add_subatomic_imports(content)

        # Step 2: Fix thinking budgets
        content = remove_thinking_budget_over_limit(content)

        # Step 3: Add engine initialization (detect class name)
        class_match = re.search(r"class\s+(\w+)\s*\(", content)
        if class_match:
            class_name = class_match.group(1)
            content = add_engine_initialization(content, class_name)

        # Only write if changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"   ✅ Updated {file_path.name}")
            return True
        else:
            print(f"   ℹ️  No changes needed for {file_path.name}")
            return False

    except Exception as e:
        print(f"   ❌ Error processing {file_path.name}: {e}")
        return False


def main():
    """Main refactoring execution."""
    print("=" * 60)
    print("🚀 AGENT REFACTORING: Sub-Atomic Engine Integration")
    print("=" * 60)

    updated_count = 0

    for agent_file in AGENT_FILES:
        file_path = AGENTS_DIR / agent_file
        if file_path.exists():
            if process_agent_file(file_path):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {agent_file}")

    print("\n" + "=" * 60)
    print(f"✅ Refactoring Complete: {updated_count} files updated")
    print("=" * 60)


if __name__ == "__main__":
    main()
