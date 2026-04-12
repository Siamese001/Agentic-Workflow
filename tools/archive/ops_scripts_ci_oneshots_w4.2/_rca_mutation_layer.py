"""RCA: find where safe_shutil_mutate / assert_no_persistent_write are called with layer=L0."""

import pathlib
import re

roots = [AGENTIC_CORE_DIR, SYSTEM_LEARNING_DIR, TOOLS_DIR]
for root in roots:
    for fp in pathlib.Path(root).rglob("*.py"):
        try:
            src = fp.read_text(encoding="utf-8", errors="replace")
        except (
            OSError,
            UnicodeDecodeError,
        ):  # guardian: File operations with encoding need error-specific handling
            continue
        for i, line in enumerate(src.splitlines(), 1):
            if re.search("safe_shutil_mutate|assert_no_persistent_write|layer=[\"\\']L0", line):
                print(f"{fp}:{i}: {line.strip()[:120]}")
