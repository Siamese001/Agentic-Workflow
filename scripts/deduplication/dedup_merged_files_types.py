"""Types and models for dedup_merged_files."""
import logging
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


@dataclass
class DedupManifest:
    """TODO: Add docstring."""
    _timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    _total_scanned: int = 0
    _duplicate_groups: int = 0
    _files_removed: int = 0
    _bytes_saved: int = 0
    _kept_files: List[Dict] = field(default_factory=list)
    _removed_files: List[Dict] = field(default_factory=list)
    _errors: List[Dict] = field(default_factory=list)

