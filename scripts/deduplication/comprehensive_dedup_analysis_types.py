"""Types and models for comprehensive_dedup_analysis."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

@dataclass
class FileFingerprint:
    """Complete fingerprint for a Python file."""
    path: Path
    content_hash: str
    ast_hash: str
    normalized_hash: str
    semantic_hash: str
    size: int
    line_count: int
    imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    is_stub: bool = False
    parse_error: Optional[str] = None

@dataclass
class DuplicateCluster:
    """A cluster of duplicate files."""
    cluster_id: str
    match_type: str
    canonical_path: Optional[Path] = None
    duplicates: List[Path] = field(default_factory=list)
    fingerprints: List[FileFingerprint] = field(default_factory=list)
    merge_plan: Dict = field(default_factory=dict)

@dataclass
class DedupReport:
    """Complete deduplication analysis report."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_files_scanned: int = 0
    total_duplicates: int = 0
    exact_duplicates: int = 0
    ast_duplicates: int = 0
    normalized_duplicates: int = 0
    semantic_duplicates: int = 0
    clusters: List[DuplicateCluster] = field(default_factory=list)
    bytes_recoverable: int = 0

