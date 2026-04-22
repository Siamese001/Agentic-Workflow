"""
Automated refactoring script to update all agents to use shared Sub-Atomic Engine.
This script systematically updates all agent files in agentic_core/agents/.
"""

import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "refactor_agents_to_subatomic", "uwg_governed_write")
_emit_writes_through("p1", "refactor_agents_to_subatomic", "uwg_governed_write_2")
_emit_pulls_context("p1", "refactor_agents_to_subatomic", "context_retrieval")
_emit_pulls_context("p1", "refactor_agents_to_subatomic", "context_retrieval_2")
emit_determinism_digest("trace_refactor_agents_to_subatomic", "refactor_agents_to_subatomic_dispatch")
emit_determinism_digest("trace_refactor_agents_to_subatomic", "refactor_agents_to_subatomic_complete")
_emit_validated_by_safety_plane("p1", "refactor_agents_to_subatomic", "safety_validation")

agent_files = [
    "memory_architect.py",
    "ContextCurator.py",
    "hallucination_hunter.py",
    "HealerAgent.py",
    "analysis.py",
    "dynamic_model_router.py",
]
agents_dir = get_validated_project_root() / "agentic_core/agents"


def add_subatomic_imports(content: str) -> str:
    """Add Sub-Atomic Engine imports if not present."""
    import_line = "from apps_shared.canon_validator_agentic_v2_1 import get_subatomic_engine, get_safety_guardrail, get_fission_manager"
    if import_line in content:
        return content
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
    pattern = "thinking_budget\\s*=\\s*(\\d+)"

    def replace_budget(match):
        budget = int(match.group(1))
        if budget > 24576:
            print(f"   Fixing thinking_budget: {budget} -> 24576")
            return "thinking_budget=24576"
        return match.group(0)

    return re.sub(pattern, replace_budget, content)


def add_engine_initialization(content: str, class_name: str) -> str:
    """Add engine initialization to __init__ method."""
    engine_init = "\n        # Initialize shared Sub-Atomic Engine components\n        if hasattr(self.ctx, '_client') and self.ctx._client:\n            try:\n                self.engine = get_subatomic_engine(gemini_client=self.ctx._client)\n                self.safety = get_safety_guardrail()\n                self.fission = get_fission_manager()\n            except Exception as e:\n                # TODO: Handle specific exception properly\n                raise  # Re-raise after logging/handling\n                Logger.warning(f\"Failed to initialize Sub-Atomic Engine: {e}\")\n                self.engine = None\n                self.safety = None\n                self.fission = None\n        else:\n            self.engine = None\n            self.safety = None\n            self.fission = None\n"
    if "self.engine = get_subatomic_engine" in content:
        return content
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
        content = add_subatomic_imports(content)
        content = remove_thinking_budget_over_limit(content)
        class_match = re.search("class\\s+(\\w+)\\s*\\(", content)
        if class_match:
            class_name = class_match.group(1)
            content = add_engine_initialization(content, class_name)
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"   ✅ Updated {file_path.name}")
            return True
        else:
            print(f"   ℹ️  No changes needed for {file_path.name}")
            return False
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as e:
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
