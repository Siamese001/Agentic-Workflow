from agentic_core.L2_execution.tools import write_gateway as _wg

"Duplicate Code Detector Agent - Detects duplicate files and code blocks.\n\nThis module provides a batch agent that detects exact duplicate files and\ncode blocks across the entire territory using content hashing and AST\nfingerprinting for structural comparison.\n\nTypical usage:\n    agent = DuplicateCodeDetectorAgent(project_root=Path(\"/path/to/project\"))\n    result = await agent.execute(file_types={'.py', '.js'})\n"
import ast
import hashlib
import logging

from agentic_core.L5_safety.config.structure_blueprint import (
    GLOBAL_EXCLUDED_DIRS,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
)
from agentic_core.mixins.atomic_execution_mixin import AtomicExecutionMixin

Logger: logging.Logger = logging.getLogger(__name__)
UTILS_DIR = "agentic_core/utils"
from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR

try:
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    Parser = None
    Language = None


@dataclass
class DuplicateFile:
    """Represents a duplicate file with metadata."""

    hash: str
    size: int
    paths: list[Path]
    file_type: str
    keep_path: Path | None = None
    delete_paths: list[Path] = None
    rationale: str = ""


@dataclass
class DuplicateCodeDetectorAgent(AtomicExecutionMixin, SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """L5 Safety agent that detects duplicate files and code blocks.

    This batch agent detects exact duplicate files and code blocks across the
    entire territory using content hashing and AST fingerprinting.

    Attributes:
        project_root: Root directory of the project.
        ctx: Execution context.
        min_lines: Minimum block size to flag as duplicate.
        max_report: Maximum number of duplicates to report.

    Inherits:
        SubatomicTestingMixin: Provides testing utilities.
        HealerMixin: Provides healing chain support.
        MCPHardenedMixin: Provides MCP hardening and telemetry.
    """

    def __post_init__(self):
        """Initialize mixins after dataclass initialization."""
        super().__init__()

    SUPPORTED_EXTENSIONS = {
        ".py",
        ".html",
        ".htm",
        ".css",
        ".js",
        ".json",
        ".yaml",
        ".yml",
        ".md",
        ".txt",
        ".xml",
        ".svg",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
    }
    WHOLE_FILE_TYPES = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"}
    CANONICAL_PREFIXES = [
        L5_SAFETY_DIR,
        L4_STATE_DIR,
        L3_ORCHESTRATION_DIR,
        L2_EXECUTION_DIR,
        L1_COGNITION_DIR,
        L0_MAINTENANCE_DIR,
        "agentic_core/observability",
        UTILS_DIR,
    ]
    EXCLUDE_DIRS = set(GLOBAL_EXCLUDED_DIRS)

    def __init__(self, project_root: Path | None = None, ctx: Any | None = None) -> None:
        """
        Initialize duplicate code detector.

        Args:
            project_root: Optional project root directory
            ctx: Optional validation context
        """
        super().__init__()
        self.project_root: Path = Path(project_root) if project_root else Path.cwd()
        self.ctx: Any | None = ctx
        self.min_lines: int = 10
        self.max_report: int = 100
        self.auto_deduplicate = False
        self.ts_parser: Parser | None = None
        if TREE_SITTER_AVAILABLE:
            try:
                self.ts_parser = Parser()
                self.ts_parser.language = language()
            except Exception:
                raise
                self.ts_parser = None

    # guardian: allow-type-erasure
    async def execute(self, file_types: set[str] = None, scan_whole_files: bool = True) -> dict:
        """Scan files for duplicates.

        Args:
            file_types: Set of file extensions to scan (e.g., {'.py', '.html'})
            scan_whole_files: If True, detect exact file duplicates first

        Returns:
            Dict with duplicate findings and deletion recommendations
        """
        file_types = file_types or self.SUPPORTED_EXTENSIONS
        Logger.info(f"[DUPE SCAN] Scanning for duplicates in {len(file_types)} file types...")
        _adg_antipatterns: list = []
        try:
            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _bp = _gbp(Path(__file__).resolve(), self.project_root)
            _adg_antipatterns = sorted(_bp.antipattern_signals)
            if _adg_antipatterns:
                Logger.info("[ADG] DuplicateCodeDetectorAgent antipatterns=%s", _adg_antipatterns)
        # guardian: allow-silent-swallow
        except Exception:
            pass
        results = {
            "whole_file_duplicates": [],
            "code_block_duplicates": [],
            "deletion_recommendations": [],
            "adg_antipattern_signals": _adg_antipatterns,
        }
        if scan_whole_files:
            whole_file_dupes = self._scan_whole_files(file_types)
            results["whole_file_duplicates"] = whole_file_dupes
            results["deletion_recommendations"].extend(self._generate_deletion_plan(whole_file_dupes))
        if ".py" in file_types:
            block_dupes = await self._scan_code_blocks()
            results["code_block_duplicates"] = block_dupes
        return results

    def _scan_whole_files(self, file_types: set[str]) -> list[DuplicateFile]:
        """Scan for exact duplicate files by content hash."""
        file_hashes = defaultdict(list)
        for file_path in self._iter_files(file_types):
            try:
                content = file_path.read_bytes()
                file_hash = hashlib.sha256(content).hexdigest()
                file_size = len(content)
                file_hashes[file_hash].append((file_path, file_size))
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                Logger.warning(f"Failed to read {file_path}: {e}")
                continue
        duplicates = []
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                paths = [f[0] for f in files]
                size = files[0][1]
                file_type = paths[0].suffix
                duplicate = DuplicateFile(hash=file_hash, size=size, paths=paths, file_type=file_type)
                duplicates.append(duplicate)
        Logger.info(f"[DUPE SCAN] Found {len(duplicates)} sets of duplicate files")
        return duplicates

    async def _scan_code_blocks(self) -> list[dict]:
        """Scan Python files for duplicate code blocks."""
        code_blocks = defaultdict(list)
        for file_path in self._iter_files({".py"}):
            try:
                lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                for i in range(len(lines) - self.min_lines + 1):
                    block_content = "\n".join(lines[i : i + self.min_lines])
                    if not block_content.strip():
                        continue
                    block_hash = self._hash_block_ast(block_content)
                    try:
                        rel_path = file_path.relative_to(self.project_root)
                    except ValueError:
                        rel_path = file_path
                    code_blocks[block_hash].append((str(rel_path), i + 1))
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                Logger.warning(f"Failed to scan {file_path}: {e}")
                continue
        duplicates = [{"hash": h, "locations": locs} for h, locs in code_blocks.items() if len(locs) > 1]
        Logger.info(f"[DUPE SCAN] Found {len(duplicates)} duplicate code blocks")
        return duplicates[: self.max_report]

    # guardian: allow-type-erasure
    def _iter_files(self, file_types: set[str]) -> Any:
        """Iterate over files matching the given extensions."""
        for file_path in self.project_root.rglob("*"):
            if any(excluded in file_path.parts for excluded in self.EXCLUDE_DIRS):
                continue
            if file_path.suffix in file_types and file_path.is_file():
                yield file_path

    def _generate_deletion_plan(self, duplicates: list[DuplicateFile]) -> list[dict]:
        """Generate deletion recommendations with rationale."""
        recommendations = []
        for dup in duplicates:
            keep_path = self._choose_canonical_path(dup.paths)
            delete_paths = [p for p in dup.paths if p != keep_path]
            rationale = self._generate_rationale(keep_path, delete_paths, dup)
            dup.keep_path = keep_path
            dup.delete_paths = delete_paths
            dup.rationale = rationale
            recommendations.append(
                {
                    "keep": str(keep_path.relative_to(self.project_root)),
                    "delete": [str(p.relative_to(self.project_root)) for p in delete_paths],
                    "rationale": rationale,
                    "size": dup.size,
                    "file_type": dup.file_type,
                    "hash": dup.hash[:16],
                }
            )
        return recommendations

    def _choose_canonical_path(self, paths: list[Path]) -> Path:
        """Choose the canonical path to keep based on location priority."""
        for prefix in self.CANONICAL_PREFIXES:
            for path in paths:
                if prefix in str(path):
                    return path
        paths_sorted = sorted(paths, key=lambda p: len(p.parts))
        return paths_sorted[0]

    def _generate_rationale(self, keep_path: Path, delete_paths: list[Path], dup: DuplicateFile) -> str:
        """Generate human-readable rationale for deletion."""
        keep_str = str(keep_path.relative_to(self.project_root))
        is_canonical = any(prefix in keep_str for prefix in self.CANONICAL_PREFIXES)
        if is_canonical:
            return f"Keep canonical location in {keep_str.split('/')[0]}/{keep_str.split('/')[1]}"
        else:
            return f"Keep shortest path: {len(keep_path.parts)} levels deep"

    # guardian: allow-type-erasure
    def archive_duplicates(self, recommendations: list[dict], dry_run: bool = True) -> dict:
        """Archive duplicate files to archives/ directory (Phase 2.2).

        Args:
            recommendations: List of deletion recommendations from execute()
            dry_run: If True, only simulate archiving

        Returns:
            Dict with archiving results
        """
        from datetime import datetime

        archived = []
        errors = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = self.project_root / ARCHIVES_DIR / f"duplicates_{timestamp}"
        if not dry_run:
            _wg.ensure_dir(archive_dir)
            Logger.info(f"Created archive directory: {archive_dir}")
        for rec in recommendations:
            for delete_path_str in rec["delete"]:
                full_path = self.project_root / delete_path_str
                try:
                    relative_path = Path(delete_path_str)
                    archive_target = archive_dir / relative_path
                    if dry_run:
                        Logger.info(
                            f"[DRY RUN] Would archive: {delete_path_str} -> archives/duplicates_{timestamp}/{delete_path_str}"
                        )
                        archived.append(delete_path_str)
                    else:
                        _wg.ensure_dir(archive_target.parent)
                        _wg.move_path(str(full_path), str(archive_target))
                        Logger.info(
                            f"[ARCHIVED] {delete_path_str} -> {archive_target.relative_to(self.project_root)}"
                        )
                        archived.append(delete_path_str)
                # guardian: allow-silent-swallow
                except Exception as e:
                    Logger.error(f"Failed to archive {delete_path_str}: {e}")
                    errors.append({"path": delete_path_str, "error": str(e)})
        return {
            "archived_count": len(archived),
            "archived_files": archived,
            "archive_location": str(archive_dir.relative_to(self.project_root))
            if not dry_run
            else f"archives/duplicates_{timestamp}",
            "errors": errors,
            "dry_run": dry_run,
        }

    # guardian: allow-type-erasure
    def delete_duplicates(self, recommendations: list[dict], dry_run: bool = True) -> dict:
        """Delete duplicate files based on recommendations.

        Args:
            recommendations: List of deletion recommendations from execute()
            dry_run: If True, only simulate deletion

        Returns:
            Dict with deletion results
        """
        deleted = []
        errors = []
        for rec in recommendations:
            for delete_path_str in rec["delete"]:
                full_path = self.project_root / delete_path_str
                try:
                    if dry_run:
                        Logger.info(f"[DRY RUN] Would delete: {delete_path_str}")
                        deleted.append(delete_path_str)
                    else:
                        _wg.remove_file(full_path)
                        Logger.info(f"[DELETED] {delete_path_str}")
                        deleted.append(delete_path_str)
                # guardian: allow-silent-swallow
                except Exception as e:
                    Logger.error(f"Failed to delete {delete_path_str}: {e}")
                    errors.append({"path": delete_path_str, "error": str(e)})
        return {"deleted_count": len(deleted), "deleted_files": deleted, "errors": errors, "dry_run": dry_run}

    def _hash_block_ast(self, code: str) -> str:
        """Generate AST fingerprint for code block."""
        try:
            if self.ts_parser:
                tree = self.ts_parser.parse(bytes(code, "utf8"))
                norm_tree = self._normalize_ts_tree(tree.root_node)
                return hashlib.md5(str(norm_tree).encode()).hexdigest()
            else:
                tree = ast.parse(code)
                norm_tree = self._normalize_ast_tree(tree)
                return hashlib.sha256(code.encode()).hexdigest()
        # guardian: allow-silent-swallow
        except Exception:
            return hashlib.sha256(code.encode()).hexdigest()

    def _normalize_ast_tree(self, node: ast.AST) -> str:
        """Anonymize variables and constants in AST for structural comparison."""
        if isinstance(node, ast.Name):
            return "VAR"
        elif isinstance(node, ast.Constant):
            return f"CONST_{type(node.value).__name__}"
        elif isinstance(node, ast.Num | ast.Str):
            return "CONST"
        children = [self._normalize_ast_tree(child) for child in ast.iter_child_nodes(node)]
        return f"{type(node).__name__}({'|'.join(children)})" if children else type(node).__name__

    def _normalize_ts_tree(self, node: Any) -> str:
        """Normalize tree-sitter node for structural comparison."""
        if node.type == "identifier":
            return "VAR"
        elif node.type in ["string", "integer", "float", "true", "false", "none"]:
            return f"CONST_{node.type}"
        children = [self._normalize_ts_tree(child) for child in node.children]
        return f"{node.type}({'|'.join(children)})" if children else node.type

    @timeout(300)
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
    ) -> dict[str, int]:
        """Execute L5 safety healing operations.

        This is an operational agent - no repository healing required.
        Implements cycle detection and depth limiting.

        Args:
            dry_run: If True, only report what would be done (default: True).
            execute: If True, execute healing actions (default: False).
            depth: Current recursion depth for cycle detection (default: 0).
            max_depth: Maximum recursion depth allowed (default: 3).
            _call_path: Set of agent names in current call chain for cycle detection.

        Returns:
            Dictionary with healing results: {"skipped": 1} for operational agents.
        """
        super().heal_repository()
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    def heal(self, violation, **kwargs):
        return {"status": "skipped", "reason": "detector_only", "handler": self.__class__.__name__}
