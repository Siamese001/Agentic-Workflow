"""Types and models for comprehensive_dedup_analysis."""
import logging
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


@dataclass
class FileFingerprint:
    """Complete fingerprint for a Python file."""
    _path: Path
    _content_hash: str
    _ast_hash: str
    _normalized_hash: str
    _semantic_hash: str
    _size: int
    _line_count: int
    _imports: List[str] = field(default_factory=list)
    _functions: List[str] = field(default_factory=list)
    _classes: List[str] = field(default_factory=list)
    _is_stub: bool = False
    _parse_error: Optional[str] = None


@dataclass
class DuplicateCluster:
    """A cluster of duplicate files."""
    _cluster_id: str
    _match_type: str
    _canonical_path: Optional[Path] = None
    _duplicates: List[Path] = field(default_factory=list)
    _fingerprints: List[FileFingerprint] = field(default_factory=list)
    _merge_plan: Dict = field(default_factory=dict)


@dataclass
class DedupReport:
    """Complete deduplication analysis report."""
    _timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    _total_files_scanned: int = 0
    _total_duplicates: int = 0
    _exact_duplicates: int = 0
    _ast_duplicates: int = 0
    _normalized_duplicates: int = 0
    _semantic_duplicates: int = 0
    _clusters: List[DuplicateCluster] = field(default_factory=list)
    _bytes_recoverable: int = 0
