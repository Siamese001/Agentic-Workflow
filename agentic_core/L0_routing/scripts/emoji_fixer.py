"""Fix all Unicode emojis in Python files to ASCII equivalents.
Prevents Windows encoding issues.
"""

from pathlib import Path
from agentic_core.L0_routing.config import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
)

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
