"""Types and models for dedup_merged_files."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

@dataclass
class DedupManifest:
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_scanned: int = 0
    duplicate_groups: int = 0
    files_removed: int = 0
    bytes_saved: int = 0
    kept_files: List[Dict] = field(default_factory=list)
    removed_files: List[Dict] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)

