"""Fix LIC import paths from agent_base to LICAgentBase."""

from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

root = Path("apps_lic/engines")
old_import = "from apps_lic.utils.LICAgentBase import LICAgentBase"
new_import = "from apps_lic.utils.LICAgentBase import LICAgentBase"

fixed_count = 0
for py_file in root.glob("*.py"):
    content = py_file.read_text(encoding="utf-8")
    if old_import in content:
        new_content = content.replace(old_import, new_import)
        py_file.write_text(new_content, encoding="utf-8")
        print(f"Fixed: {py_file.name}")
        fixed_count += 1

print(f"\nTotal files fixed: {fixed_count}")
