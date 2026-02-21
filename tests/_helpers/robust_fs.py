"""Robust filesystem utilities for testing."""

import os
import shutil
import time
from pathlib import Path


def robust_rmtree(path: Path, max_retries: int = 3, delay: float = 0.1) -> None:
    """Robustly remove a directory tree, retrying on Windows."""
    for i in range(max_retries):
        try:
            if path.exists():
                shutil.rmtree(str(path))
            return
        except (OSError, PermissionError) as e:
            if i == max_retries - 1:
                raise
            time.sleep(delay)
            # Try to make files writable on Windows
            for root, dirs, files in os.walk(str(path)):
                for file in files:
                    try:
                        os.chmod(os.path.join(root, file), 0o644)
                    except OSError:
                        pass
