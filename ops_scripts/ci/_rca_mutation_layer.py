"""RCA: find where safe_shutil_mutate / assert_no_persistent_write are called with layer=L0."""

import pathlib
import re

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

roots = [AGENTIC_CORE_DIR, SYSTEM_LEARNING_DIR, TOOLS_DIR]
for root in roots:
    for fp in pathlib.Path(root).rglob("*.py"):
        try:
            src = fp.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(src.splitlines(), 1):
            if re.search(r'safe_shutil_mutate|assert_no_persistent_write|layer=["\']L0', line):
                print(f"{fp}:{i}: {line.strip()[:120]}")
