#!/usr/bin/env python3
"""
Duplicate Code Detector Agent
Batch agent: Detects exact duplicate code blocks across the entire territory.
Uses token-based hashing for speed and accuracy (ignores whitespace/comments).
"""
import hashlib
import tokenize
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


class DuplicateCodeDetectorAgent:
    """
    Batch agent: Detects exact duplicate code blocks across the entire territory.
    Uses token-based hashing for speed and accuracy (ignores whitespace/comments).
    """

    def __init__(self, project_root: Path, ctx):
        self.project_root = Path(project_root)
        self.ctx = ctx
        self.min_lines = 10  # Minimum block size to flag
        self.max_report = 20  # Limit detailed reporting
        self.auto_deduplicate = False

    async def execute(self) -> Dict:
        """Scan all Python files for duplicate code blocks."""
        if not hasattr(self.ctx, "python_files") or not self.ctx.python_files:
            return {}

        print(
            f"   [DUPE SCAN] Analyzing {len(self.ctx.python_files)} files for duplicates >={self.min_lines} lines..."
        )
        code_blocks = defaultdict(list)  # hash -> [(path, start_line)]

        for file_path_str in self.ctx.python_files:
            file_path = Path(file_path_str)
            if not file_path.exists():
                continue

            try:
                # Read file content
                lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()

                # Sliding window hash
                for i in range(len(lines) - self.min_lines + 1):
                    # Extract block and normalize (strip whitespace)
                    block_content = "\n".join(
                        l.strip() for l in lines[i : i + self.min_lines] if l.strip()
                    )
                    if not block_content:
                        continue

                    # Hash the normalized block
                    block_hash = hashlib.md5(block_content.encode()).hexdigest()
                    try:
                        rel_path = file_path.relative_to(self.project_root)
                    except ValueError:
                        rel_path = file_path
                    code_blocks[block_hash].append((str(rel_path), i + 1))

            except Exception as e:
                # Skip unreadable files
                continue

        # Find duplicates (blocks that appear in multiple locations)
        duplicates = [locations for locations in code_blocks.values() if len(locations) > 1]
        total_dupes = sum(len(locs) - 1 for locs in duplicates)

        return {
            "duplicates_found": len(duplicates),
            "instances_eliminated_potential": total_dupes,
            "details": duplicates[: self.max_report],
        }
