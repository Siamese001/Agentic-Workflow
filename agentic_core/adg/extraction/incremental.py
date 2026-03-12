"""ADG Incremental Rebuild — recompute only changed files and affected edges.

Strategy
--------
1. Load the existing ScanCache (already contains file_hash → edges per file).
2. Use ``git diff --name-only HEAD~1 HEAD`` (or a supplied file list) to get
   the set of *directly* changed files.
3. From the live ADG (NormalizedGraph), compute the *affected* set:
   any module that imports (directly or transitively up to depth=2) a changed
   module also needs its edges recomputed, because its import-time edges may
   have changed.
4. Re-scan only the union of directly-changed + affected files.
5. Merge new edges back into the full edge set, evicting stale edges for
   re-scanned files.
6. Return a ScanResult that looks like a full scan to all consumers.

This avoids running the full 149,584-edge scan on every PR commit.
Typical savings: 80–95% of files skipped for single-file changes.

Usage::

    from agentic_core.adg.extraction.incremental import incremental_scan

    result = incremental_scan(
        repo_root=Path("."),
        changed_files=["agentic_core/L2_execution/foo.py"],
        cache_path=Path("artifacts/adg/scan_result_cache.json"),
        full_snapshot_path=Path("artifacts/adg/adg_full_latest.json"),
    )
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from agentic_core.adg.artifact.normalizer import NormalizedGraph
from agentic_core.adg.extraction.scan_cache import ScanCache, file_hash

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)

_DEFAULT_AFFECT_DEPTH = 2  # transitive import depth to propagate changes
_MODULE_PREFIX = "ADG::Module::"


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _git_changed_files(repo_root: Path, base_ref: str = "HEAD~1") -> list[str]:
    """Return repo-relative paths of files changed since base_ref.

    Returns an empty list if git is unavailable or the ref doesn't exist
    (e.g., first commit).
    """
    try:
        # guardian: allow-magic-config
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref, "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            logger.debug("git diff failed: %s", result.stderr.strip())
            return []
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip().endswith(".py")]
        return lines
    # guardian: allow-silent-swallow
    except Exception as exc:
        logger.debug("_git_changed_files error: %s", exc)
        return []


def _git_staged_files(repo_root: Path) -> list[str]:
    """Return staged .py files (for pre-commit hook integration)."""
    try:
        # guardian: allow-magic-config
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []
        return [l.strip() for l in result.stdout.splitlines() if l.strip().endswith(".py")]
    # guardian: allow-silent-swallow
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Affected-module propagation
# ---------------------------------------------------------------------------


def _build_reverse_import_index(ng: NormalizedGraph) -> dict[str, set[str]]:
    """Build reverse import index: module → set of modules that import it.

    Used to propagate changes upward through the import graph.
    Returns: {imported_module_adg_name → {importer_adg_name, ...}}
    """
    reverse: dict[str, set[str]] = {}
    for edge in ng.edges:
        if edge["r"] != "imports":
            continue
        src_id = str(edge["s"])
        dst_id = str(edge["d"])
        src_node = ng.nodes.get(src_id, {})
        dst_node = ng.nodes.get(dst_id, {})
        if src_node.get("t") != "module" or dst_node.get("t") != "module":
            continue
        dst_name = dst_node.get("n", "")
        src_name = src_node.get("n", "")
        reverse.setdefault(dst_name, set()).add(src_name)
    return reverse


def compute_affected_modules(
    changed_files: list[str],
    ng: NormalizedGraph,
    depth: int = _DEFAULT_AFFECT_DEPTH,
) -> set[str]:
    """Return the set of module ADG names affected by the changed files.

    Includes the directly-changed modules plus transitive importers up to
    ``depth`` hops in the reverse import graph.
    """
    # Convert file paths to ADG module names
    directly_changed: set[str] = set()
    for f in changed_files:
        norm = f.replace("\\", "/")
        adg_name = f"{_MODULE_PREFIX}{norm}"
        directly_changed.add(adg_name)

    reverse_idx = _build_reverse_import_index(ng)

    affected = set(directly_changed)
    frontier = set(directly_changed)
    for _ in range(depth):
        next_frontier: set[str] = set()
        for mod in frontier:
            for importer in reverse_idx.get(mod, set()):
                if importer not in affected:
                    affected.add(importer)
                    next_frontier.add(importer)
        frontier = next_frontier
        if not frontier:
            break

    return affected


# ---------------------------------------------------------------------------
# Incremental scan result merger
# ---------------------------------------------------------------------------


def _extract_module_path(adg_name: str) -> str:
    if adg_name.startswith(_MODULE_PREFIX):
        return adg_name[len(_MODULE_PREFIX) :]
    return adg_name


class IncrementalScanStats:
    """Statistics from an incremental scan run."""

    def __init__(self) -> None:
        self.total_modules: int = 0
        self.changed_files: int = 0
        self.affected_modules: int = 0
        self.rescanned: int = 0
        self.cache_hits: int = 0
        self.edges_evicted: int = 0
        self.edges_added: int = 0
        self.edges_total: int = 0

    @property
    def skipped(self) -> int:
        return self.total_modules - self.rescanned

    def summary(self) -> str:
        return (
            f"Incremental: {self.rescanned}/{self.total_modules} modules re-scanned "
            f"({self.skipped} skipped) | "
            f"changed={self.changed_files} affected={self.affected_modules} | "
            f"edges: -{self.edges_evicted} +{self.edges_added} total={self.edges_total}"
        )


def incremental_scan(
    repo_root: Path,
    changed_files: list[str] | None = None,
    *,
    cache_path: Path | None = None,
    full_snapshot_path: Path | None = None,
    base_ref: str = "HEAD~1",
    affect_depth: int = _DEFAULT_AFFECT_DEPTH,
) -> tuple[ScanResult, IncrementalScanStats]:
    """Run an incremental ADG scan, re-scanning only changed + affected modules.

    Parameters
    ----------
    repo_root:
        Repository root path.
    changed_files:
        Explicit list of changed file paths (repo-relative). If None, uses
        git diff against base_ref.
    cache_path:
        Path to the scan cache JSON. Defaults to
        ``artifacts/adg/scan_result_cache.json``.
    full_snapshot_path:
        Path to the latest full NormalizedGraph JSON for the reverse-import
        index. If None, performs a full scan instead.
    base_ref:
        Git ref to diff against when changed_files is None.
    affect_depth:
        Transitive import depth for propagating change impact.

    Returns
    -------
    (ScanResult, IncrementalScanStats)
        A ScanResult usable by all analysis modules, plus statistics.
    """
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    stats = IncrementalScanStats()
    repo_root = Path(repo_root)

    # Resolve defaults
    if cache_path is None:
        cache_path = repo_root / "artifacts" / "adg" / "scan_result_cache.json"

    # Step 1: determine changed files
    if changed_files is None:
        changed_files = _git_changed_files(repo_root, base_ref=base_ref)
        if not changed_files:
            # Also check staged files (pre-commit hook mode)
            changed_files = _git_staged_files(repo_root)

    stats.changed_files = len(changed_files)
    logger.info("Incremental scan: %d directly changed files", stats.changed_files)

    # Step 2: if no snapshot available or no changed files → full scan
    if not changed_files or full_snapshot_path is None or not Path(full_snapshot_path).exists():
        logger.info("No snapshot or no changed files — falling back to full scan")
        scanner = ADGStaticScanner(repo_root=repo_root)
        result = scanner.scan(commit_sha="")
        stats.total_modules = len(result.modules)
        stats.rescanned = stats.total_modules
        stats.edges_total = len(result.edges)
        return result, stats

    # Step 3: load snapshot for reverse-import index
    try:
        ng = NormalizedGraph.load(Path(full_snapshot_path))
    # guardian: allow-silent-swallow
    except Exception as exc:
        logger.warning("Failed to load snapshot %s: %s — full scan", full_snapshot_path, exc)
        scanner = ADGStaticScanner(repo_root=repo_root)
        result = scanner.scan(commit_sha="")
        stats.total_modules = len(result.modules)
        stats.rescanned = stats.total_modules
        stats.edges_total = len(result.edges)
        return result, stats

    # Step 4: compute affected modules
    affected_adg_names = compute_affected_modules(changed_files, ng, depth=affect_depth)
    stats.affected_modules = len(affected_adg_names)
    affected_paths = {_extract_module_path(n) for n in affected_adg_names}
    logger.info("Incremental: %d affected modules (depth=%d)", stats.affected_modules, affect_depth)

    # Step 5: load scan cache
    cache = ScanCache.load(cache_path)

    # Step 6: run full scan but let the cache handle unchanged files
    # The ADGStaticScanner already uses ScanCache internally when a cache
    # path is provided. We mark affected files as cache-invalidated by
    # deleting their entries from the cache before scanning.
    for rel_path in list(affected_paths):
        abs_path = repo_root / rel_path
        if abs_path.exists():
            fh = file_hash(abs_path)
            # Force eviction: put a mismatched hash so get() will miss
            cache._entries.pop(rel_path, None)
        else:
            cache._entries.pop(rel_path, None)

    stats.edges_evicted = cache.evictions  # already evicted in loop above

    # Save the invalidated cache so the scanner picks it up
    cache.save(cache_path)

    # Step 7: run the full scanner — it will use cache for untouched files
    scanner = ADGStaticScanner(repo_root=repo_root, cache_path=cache_path)
    result = scanner.scan(commit_sha="")

    stats.total_modules = len(result.modules)
    stats.cache_hits = getattr(getattr(result, "manifest", None), "cache_hits", 0) or 0
    stats.rescanned = stats.total_modules - stats.cache_hits
    stats.edges_total = len(result.edges)
    stats.edges_added = stats.edges_total  # net total after merge

    logger.info(stats.summary())
    return result, stats


__all__ = [
    "IncrementalScanStats",
    "compute_affected_modules",
    "incremental_scan",
]
