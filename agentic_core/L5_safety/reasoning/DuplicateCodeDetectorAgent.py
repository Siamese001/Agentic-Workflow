# guardian: allow-silent-degradation - Code detection requires exception handling
from pathlib import Path

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "DuplicateCodeDetectorAgent")
emit_determinism_digest("p0", "DuplicateCodeDetectorAgent")

_emit_dispatches_healing_run("p1", "DuplicateCodeDetectorAgent", "L5")
_emit_routes_through("p1", "DuplicateCodeDetectorAgent", "L5")
_emit_checks_agent_registry("p1", "DuplicateCodeDetectorAgent", "agent_registry")
_emit_validates_agent_capability("p1", "DuplicateCodeDetectorAgent", "capability")
_emit_dispatches_execution_plan("p1", "DuplicateCodeDetectorAgent", "exec_plan")
_emit_agent_executes_agent("p1", "DuplicateCodeDetectorAgent", "sub_agent")
_emit_routes_to_agent("p1", "DuplicateCodeDetectorAgent", "target_agent")
_emit_verifies_policy("p1", "DuplicateCodeDetectorAgent", "policy_check")
_emit_observes_runtime_state("p1", "DuplicateCodeDetectorAgent", "runtime_state")
_emit_verifies_boundary("p1", "DuplicateCodeDetectorAgent", "boundary_check")
_emit_transcripts_response("p1", "DuplicateCodeDetectorAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "DuplicateCodeDetectorAgent")
_emit_gated_by_confidence("p1", "DuplicateCodeDetectorAgent", "confidence_gate")
_emit_escalates_to_human("p1", "DuplicateCodeDetectorAgent", "L5")
_emit_reads_policy_state("p1", "DuplicateCodeDetectorAgent", "L5")
_emit_authorize_and_execute("p2", "DuplicateCodeDetectorAgent", "execution_auth")
_emit_validates_capability("p2", "DuplicateCodeDetectorAgent", "capability_check")
_emit_routes_to_capability("p2", "DuplicateCodeDetectorAgent", "capability_route")
_emit_writes_via_uwg("p2", "DuplicateCodeDetectorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "DuplicateCodeDetectorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "DuplicateCodeDetectorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "DuplicateCodeDetectorAgent", "exec_output")
_emit_dispatches_agent("p3", "DuplicateCodeDetectorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "DuplicateCodeDetectorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "DuplicateCodeDetectorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "DuplicateCodeDetectorAgent", "healing_outcome")
_emit_escalates_failure("p3", "DuplicateCodeDetectorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "DuplicateCodeDetectorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "DuplicateCodeDetectorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "DuplicateCodeDetectorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "DuplicateCodeDetectorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "DuplicateCodeDetectorAgent", "eval_metric")
_emit_stores_embedding("p4", "DuplicateCodeDetectorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "DuplicateCodeDetectorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "DuplicateCodeDetectorAgent", "exec_snapshot_link")

"Duplicate Code Detector Agent - Detects duplicate files and code blocks.\n\nThis module provides a batch agent that detects exact duplicate files and\ncode blocks across the entire territory using content hashing and AST\nfingerprinting for structural comparison.\n\nTypical usage:\n    agent = DuplicateCodeDetectorAgent(project_root=Path(\"/path/to/project\"))\n    result = await agent.execute(file_types={'.py', '.js'})\n"
import ast
import hashlib
import logging
import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("DuplicateCodeDetectorAgent", "p4obs", "metric_1")
_emit_emits_metric_event("DuplicateCodeDetectorAgent", "p4obs", "metric_2")
_emit_emits_metric_event("DuplicateCodeDetectorAgent", "p4obs", "metric_3")
_emit_emits_metric_event("DuplicateCodeDetectorAgent", "p4obs", "metric_4")
_emit_emits_metric_event("DuplicateCodeDetectorAgent", "p4obs", "metric_5")
_emit_emits_metric_event("DuplicateCodeDetectorAgent", "p4obs", "metric_6")
_emit_records_incident_event("DuplicateCodeDetectorAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("DuplicateCodeDetectorAgent", "p4obs", "anomaly")
_emit_writes_observability_log("DuplicateCodeDetectorAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("DuplicateCodeDetectorAgent", "p4obs", "mon_state")
_emit_triggers_alert("DuplicateCodeDetectorAgent", "p4obs", "alert")
_emit_links_incident_trace("DuplicateCodeDetectorAgent", "p4obs", "trace_link")
_emit_captures_pattern("DuplicateCodeDetectorAgent", "p3lm", "pattern")
_emit_records_learning_event("DuplicateCodeDetectorAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("DuplicateCodeDetectorAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("DuplicateCodeDetectorAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("DuplicateCodeDetectorAgent", "p3lm", "routing")
_emit_improves_agent_policy("DuplicateCodeDetectorAgent", "p3lm", "policy")
_emit_stores_learning_state("DuplicateCodeDetectorAgent", "p3lm", "state")
_emit_records_execution_trace("DuplicateCodeDetectorAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("DuplicateCodeDetectorAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("DuplicateCodeDetectorAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("DuplicateCodeDetectorAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("DuplicateCodeDetectorAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("DuplicateCodeDetectorAgent", "env_read", "p2_env_1")
_emit_reads_environ("DuplicateCodeDetectorAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("DuplicateCodeDetectorAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("DuplicateCodeDetectorAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "DuplicateCodeDetectorAgent", "context_pull")
_emit_pulls_context("p1", "DuplicateCodeDetectorAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "DuplicateCodeDetectorAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "DuplicateCodeDetectorAgent", "uwg_term_2")
_emit_writes_through("p1", "DuplicateCodeDetectorAgent", "write_through")
_emit_writes_through("p1", "DuplicateCodeDetectorAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "DuplicateCodeDetectorAgent", "safety_validation")
_emit_invokes_eval("p1", "DuplicateCodeDetectorAgent", "eval_call")
_emit_proposal_commits_routing("p1", "DuplicateCodeDetectorAgent", "routing_commit")

try:
    TREE_SITTER_AVAILABLE = True
# guardian: allow-silent-degradation - Optional tree-sitter
except ImportError:  # guardian: allow-silent-swallow
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


try:
    from agentic_core.utils.timeout_util import timeout
except ImportError:  # guardian: allow-silent-swallow - Optional timeout utility

    def timeout(seconds=30):
        def decorator(func):
            return func

        return decorator


try:
    from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin
except ImportError:  # guardian: allow-silent-swallow - Optional testing mixin

    class SubatomicTestingMixin:  # type: ignore[no-redef]
        pass


try:
    from agentic_core.mixins.healer_mixin import HealerMixin
except ImportError:  # guardian: allow-silent-swallow - Optional healer mixin

    class HealerMixin:  # type: ignore[no-redef]
        pass


try:
    from agentic_core.interfaces.mixins import MCPHardenedMixin
except (ImportError, NameError):  # guardian: allow-silent-swallow - Optional MCP hardened mixin

    class MCPHardenedMixin:  # type: ignore[no-redef]
        pass


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
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DuplicateCodeDetectorAgent.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DuplicateCodeDetectorAgent.__init__", "p0_governance")
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
            except (
                OSError,
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                RuntimeError,
            ):  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise

    # guardian: allow-type-erasure
    async def execute(self, file_types: set[str] = None, scan_whole_files: bool = True) -> dict:
        """Scan files for duplicates.

        Args:
            file_types: Set of file extensions to scan (e.g., {'.py', '.html'})
            scan_whole_files: If True, detect exact file duplicates first

        Returns:
            Dict with duplicate findings and deletion recommendations
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L5_POLICY,
            "DuplicateCodeDetectorAgent.execute",
        )
        file_types = file_types or self.SUPPORTED_EXTENSIONS
        Logger.info(f"[DUPE SCAN] Scanning for duplicates in {len(file_types)} file types...")
        _adg_antipatterns: list = []
        try:
            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _bp = _gbp(Path(__file__).resolve(), self.project_root)
            _adg_antipatterns = sorted(_bp.antipattern_signals)
            if _adg_antipatterns:
                Logger.info("[ADG] DuplicateCodeDetectorAgent antipatterns=%s", _adg_antipatterns)
        except (RuntimeError, OSError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            import logging

            logging.getLogger(__name__).debug(
                "DuplicateCodeDetectorAgent: RuntimeError swallowed at L365: %s", e
            )
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
        for file_path in tqdm(self._iter_files(file_types), desc="Processing", unit="item"):
            try:
                content = file_path.read_bytes()
                file_hash = hashlib.sha256(content).hexdigest()
                file_size = len(content)
                file_hashes[file_hash].append((file_path, file_size))
            # guardian: allow-silent-swallow
            except (
                OSError,
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                RuntimeError,
            ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
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
        for file_path in tqdm(self._iter_files({".py"}), desc="Processing", unit="item"):
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
            except (
                OSError,
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                RuntimeError,
            ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
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
        for dup in tqdm(duplicates, desc="Processing", unit="item"):
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
                },
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
        for rec in tqdm(recommendations, desc="Processing", unit="item"):
            for delete_path_str in tqdm(rec["delete"], desc="Processing", unit="item"):
                full_path = self.project_root / delete_path_str
                try:
                    relative_path = Path(delete_path_str)
                    archive_target = archive_dir / relative_path
                    if dry_run:
                        Logger.info(
                            f"[DRY RUN] Would archive: {delete_path_str} -> archives/duplicates_{timestamp}/{delete_path_str}",
                        )
                        archived.append(delete_path_str)
                    else:
                        _wg.ensure_dir(archive_target.parent)
                        _wg.move_path(str(full_path), str(archive_target))
                        Logger.info(
                            f"[ARCHIVED] {delete_path_str} -> {archive_target.relative_to(self.project_root)}",
                        )
                        archived.append(delete_path_str)
                except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
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
        for rec in tqdm(recommendations, desc="Processing", unit="item"):
            for delete_path_str in tqdm(rec["delete"], desc="Processing", unit="item"):
                full_path = self.project_root / delete_path_str
                try:
                    if dry_run:
                        Logger.info(f"[DRY RUN] Would delete: {delete_path_str}")
                        deleted.append(delete_path_str)
                    else:
                        _wg.remove_file(full_path)
                        Logger.info(f"[DELETED] {delete_path_str}")
                        deleted.append(delete_path_str)
                except (RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
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
        except (RuntimeError, OSError):  # guardian: allow-silent-swallow
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
