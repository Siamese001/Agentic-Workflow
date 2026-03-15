"""Fix all Unicode emojis in Python files to ASCII equivalents.
Prevents Windows encoding issues.
"""

from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "emoji_fixer", "L0")
_emit_routes_through("p1", "emoji_fixer", "L0")
_emit_escalates_to_human("p1", "emoji_fixer", "L0")
_emit_reads_policy_state("p1", "emoji_fixer", "L0")

_emit_records_execution_trace("p0", "evidence", "emoji_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "emoji_fixer", "p0_governance")
_emit_snapshots_state("p0", "emoji_fixer", "state_snapshot")

try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import (
        AGENTIC_CORE_DIR,
        APPS_SHARED_DIR,
        get_python_files,
    )
except ImportError:
    AGENTIC_CORE_DIR = Path(AGENTIC_CORE_DIR)
    APPS_SHARED_DIR = Path(APPS_SHARED_DIR)

    def get_python_files(directory):
        return directory.rglob("*.py")


EMOJI_MAP = {
    "✅": "[OK]",
    "⚠️": "[!]",
    "🔧": "[+]",
    "🔄": "[~]",
    "🆕": "[NEW]",
    "♻️": "[REUSE]",
    "🚨": "[ALERT]",
    "🚫": "[X]",
    "❌": "[X]",
    "🧹": "[CLEAN]",
    "🏛️": "[ARCH]",
    "💾": "[SAVE]",
    "🔍": "[SCAN]",
    "📊": "[STATS]",
    "📂": "[DIR]",
    "📋": "[PLAN]",
    "🚀": "[START]",
    "🌱": "[GIT]",
    "🧬": "[CYCLE]",
}


def fix_emojis_in_file(file_path: str) -> bool:
    """Replace all emojis in a file with ASCII equivalents."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        original_content = content
        for emoji, replacement in EMOJI_MAP.items():
            content = content.replace(emoji, replacement)
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False


def main() -> None:
    """Find and fix all Python files with emojis."""
    root = Path.cwd()
    targets = [root / AGENTIC_CORE_DIR, root / APPS_SHARED_DIR]
    fixed_count = 0
    for target_dir in targets:
        if not target_dir.exists():
            continue
        for py_file in get_python_files(target_dir):
            if fix_emojis_in_file(str(py_file)):
                fixed_count += 1
    print(f"\n[*] Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
