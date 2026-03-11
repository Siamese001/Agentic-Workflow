from __future__ import annotations

import shutil
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

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write


def extract_net_incremental() -> None:
    """Extract files that don't exist in sovereign codebase."""
    source_dir: Any = Path("archives/legacy_lic")
    staging_dir: Any = Path("archive_code")
    if staging_dir.exists():
        assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()
    existing_files: Any = get_existing_files()
    extracted_files: Any = []
    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(source_dir):
        FILENAME: Any = py_file.name
        name_exists: Any = any(FILENAME in existing for existing in existing_files)
        if not name_exists:
            dest_path: Any = staging_dir / FILENAME
            shutil.copy2(py_file, dest_path)
            extracted_files.append(FILENAME)
    return extracted_files
