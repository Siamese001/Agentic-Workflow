"""Semantic surface and violation analysis functions for ADG generation."""

from __future__ import annotations

import ast
import re
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from tqdm import tqdm

if TYPE_CHECKING:
    from agentic_core.adg.artifact.builder_types import ADGArtifact


def _audit_semantic_surfaces(repo_root: Path, realized_node_names: set[str]) -> dict[str, int]:
    from collections import Counter

    from agentic_core.adg.analysis.CanonicalSnapshot import canonical_name
    from tools.generate.generate_full_adg import (
        _BlockDecompositionVisitor,
        _ExecutionSemanticVisitor,
        _iter_python_files,
        _repo_relative,
        _TestExecutionLinkageVisitor,
        _TypeSurfaceCollector,
    )

    counts: Counter[str] = Counter()
    realized_type_candidates: set[str] = set()

    for filepath in _iter_python_files(repo_root):
        rel = _repo_relative(filepath, repo_root)
        try:
            source = filepath.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(filepath))
        except SyntaxError:
            counts["syntax_error_files"] += 1
            continue
        except OSError:
            counts["io_error_files"] += 1
            continue

        module_adg = canonical_name("Module", rel)

        execution_visitor = _ExecutionSemanticVisitor(module_adg, rel)
        execution_visitor.visit(tree)
        unique_execution_edges = set(execution_visitor.edges)
        counts["execution_expected"] += len(unique_execution_edges)
        counts["controls_flow_expected"] += sum(
            1 for edge in unique_execution_edges if edge.relation_type == "controls_flow"
        )
        counts["flows_to_expected"] += sum(
            1 for edge in unique_execution_edges if edge.relation_type == "flows_to"
        )
        counts["emits_side_effect_expected"] += sum(
            1 for edge in unique_execution_edges if edge.relation_type == "emits_side_effect"
        )
        counts["resolves_callsite_expected"] += sum(
            1 for edge in unique_execution_edges if edge.relation_type == "resolves_callsite"
        )

        block_visitor = _BlockDecompositionVisitor(module_adg, rel)
        block_visitor.visit(tree)
        counts["decomposes_into_expected"] += len(set(block_visitor.edges))

        type_collector = _TypeSurfaceCollector(rel)
        type_collector.visit(tree)
        realized_type_candidates.update(
            name for name in type_collector.type_map if name in realized_node_names
        )

        test_link_visitor = _TestExecutionLinkageVisitor(module_adg, rel)
        test_link_visitor.visit(tree)
        counts["tests_execution_of_expected"] += len(set(test_link_visitor.edges))

    counts["type_surface_expected"] = len(realized_type_candidates)
    return dict(counts)


def _semantic_precision_stats(conn: sqlite3.Connection) -> dict[str, int | float]:
    from tools.generate.utils.digest_utils import _ratio

    cur = conn.cursor()
    total_edges = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    semantic_edges = cur.execute("SELECT COUNT(*) FROM edges WHERE semantic_type != ''").fetchone()[0]
    execution_total = cur.execute("SELECT COUNT(*) FROM edges WHERE edge_kind='execution'").fetchone()[0]
    ordered_execution = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE edge_kind='execution' AND dynamic_resolution LIKE 'seq=%'",
    ).fetchone()[0]
    controls_flow_total = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='controls_flow'",
    ).fetchone()[0]
    flows_to_total = cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='flows_to'").fetchone()[0]
    side_effect_total = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='emits_side_effect'",
    ).fetchone()[0]
    callsite_total = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='resolves_callsite'",
    ).fetchone()[0]
    controls_flow_specific = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='controls_flow' "
        "AND semantic_type IN ('branch','loop','exception_handler')",
    ).fetchone()[0]
    flows_to_specific = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='flows_to' AND semantic_type='data_lineage'",
    ).fetchone()[0]
    side_effect_specific = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='emits_side_effect' "
        "AND semantic_type IN ('io','mutation')",
    ).fetchone()[0]
    callsite_specific = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='resolves_callsite' "
        "AND semantic_type='attribute_dispatch'",
    ).fetchone()[0]
    execution_generic = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE edge_kind='execution' "
        "AND semantic_type IN ('execution','call','read','write','controls_flow','flows_to','emits_side_effect','resolves_callsite')",
    ).fetchone()[0]
    return {
        "total_edges": total_edges,
        "semantic_edges": semantic_edges,
        "semantic_edge_ratio": _ratio(semantic_edges, total_edges),
        "execution_total": execution_total,
        "ordered_execution": ordered_execution,
        "temporal_ordering_ratio": _ratio(ordered_execution, execution_total),
        "controls_flow_total": controls_flow_total,
        "flows_to_total": flows_to_total,
        "side_effect_total": side_effect_total,
        "callsite_total": callsite_total,
        "controls_flow_specific": controls_flow_specific,
        "flows_to_specific": flows_to_specific,
        "side_effect_specific": side_effect_specific,
        "callsite_specific": callsite_specific,
        "controls_flow_specific_ratio": _ratio(controls_flow_specific, controls_flow_total),
        "flows_to_specific_ratio": _ratio(flows_to_specific, flows_to_total),
        "side_effect_specific_ratio": _ratio(side_effect_specific, side_effect_total),
        "callsite_specific_ratio": _ratio(callsite_specific, callsite_total),
        "execution_generic_semantic_count": execution_generic,
    }


def _violation_surface_stats(conn: sqlite3.Connection) -> dict[str, int | bool]:
    cur = conn.cursor()
    tables = {row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    violation_table_count = 0
    if "violations" in tables:
        violation_table_count = cur.execute("SELECT COUNT(*) FROM violations").fetchone()[0]
    layer_violation_edges = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='violates'",
    ).fetchone()[0]
    layer_violation_sources = cur.execute(
        "SELECT COUNT(DISTINCT src_id) FROM edges WHERE relation_type='violates'",
    ).fetchone()[0]
    antipattern_edges = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='antipattern'",
    ).fetchone()[0]
    guardian_exemptions = 0
    if "meta" in tables:
        row = cur.execute("SELECT value FROM meta WHERE key='guardian_exemptions'").fetchone()
        if row:
            guardian_exemptions = int(row[0])
    effective_violations = violation_table_count + guardian_exemptions
    surfaces_reconciled = bool(
        "violations" in tables
        and effective_violations >= antipattern_edges
        and effective_violations >= layer_violation_edges
        and layer_violation_edges >= layer_violation_sources,
    )
    return {
        "violations_table_exists": "violations" in tables,
        "violations_table_count": violation_table_count,
        "guardian_exemptions": guardian_exemptions,
        "antipattern_edge_count": antipattern_edges,
        "layer_violation_edge_count": layer_violation_edges,
        "layer_violation_source_count": layer_violation_sources,
        "surfaces_reconciled": surfaces_reconciled,
    }


def _violation_propagation_stats(conn: sqlite3.Connection) -> dict[str, int | float]:
    from tools.generate.utils.digest_utils import _ratio

    cur = conn.cursor()
    rows = cur.execute(
        "SELECT src.adg_name, e.relation_type, dst.adg_name "
        "FROM edges e "
        "JOIN nodes src ON src.id = e.src_id "
        "JOIN nodes dst ON dst.id = e.dst_id "
        "WHERE e.relation_type IN ('imports','violates')",
    ).fetchall()

    def _symbol_to_module_key(adg_name: str) -> str:
        raw = adg_name.replace("ADG::Symbol::", "").replace("ADG::Module::", "")
        return raw.split("::")[0].replace(".", "/")

    def _module_to_key(adg_name: str) -> str:
        raw = adg_name.replace("ADG::Module::", "")
        return raw.replace("/__init__.py", "").replace(".py", "")

    def _key_prefixes(module_key: str) -> tuple[str, ...]:
        parts = [part for part in module_key.split("/") if part]
        return tuple("/".join(parts[:idx]) for idx in range(1, len(parts) + 1))

    importers_of: dict[str, set[str]] = defaultdict(set)
    violating_modules: set[str] = set()

    for (
        src_name,
        relation_type,
        dst_name,
    ) in rows:  # guardian: Add error context logging
        if relation_type == "imports" and src_name.startswith("ADG::Module::"):
            for prefix in _key_prefixes(_symbol_to_module_key(dst_name)):
                importers_of[prefix].add(src_name)
        elif relation_type == "violates":
            violating_modules.add(src_name)

    eligible_edge_count = 0
    eligible_module_targets: set[str] = set()

    for violating_module in tqdm(violating_modules, desc="Processing", unit="item"):
        violating_key = _module_to_key(violating_module)
        visited: set[str] = {violating_module}
        frontier = {
            importer
            for importer in importers_of.get(
                violating_key,
                set(),
            )  # guardian: Add error context logging
            if importer not in violating_modules and importer not in visited
        }
        visited |= frontier
        eligible_module_targets |= frontier
        eligible_edge_count += len(frontier)
        for _depth in tqdm(range(2, 4), desc="Processing", unit="item"):
            next_frontier: set[str] = set()
            for node in frontier:
                node_key = _module_to_key(
                    node,
                )  # guardian: Add error context logging
                for importer in importers_of.get(node_key, set()):
                    if importer not in visited:
                        visited.add(importer)
                        next_frontier.add(importer)
            frontier = next_frontier
            eligible_module_targets |= frontier
            eligible_edge_count += len(frontier)

    actual_edge_count = cur.execute(
        "SELECT COUNT(*) FROM edges WHERE relation_type='violation_propagates_through'",
    ).fetchone()[0]
    actual_depth_counts = dict(
        cur.execute(
            "SELECT symbol, COUNT(*) FROM edges WHERE relation_type='violation_propagates_through' GROUP BY symbol",
        ).fetchall(),
    )
    return {  # guardian: Add error context logging
        "eligible_edge_count": eligible_edge_count,
        "eligible_target_module_count": len(eligible_module_targets),
        "actual_edge_count": actual_edge_count,
        "coverage_ratio": _ratio(actual_edge_count, eligible_edge_count),
        "depth_counts": actual_depth_counts,
    }


def _artifact_determinism_probe(
    adg_dir: Path,
    ts: str,
    artifact,
    result,
    repo_root: Path,
    enable_probe: bool,
) -> dict[str, object]:
    import tempfile

    from agentic_core.adg.artifact.builder import build_artifact
    from agentic_core.adg.artifact.ArtifactPaths import write_all_artifacts
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
    from tools.generate.utils.digest_utils import _sqlite_table_digest

    sqlite_path = adg_dir / f"adg_indexed_{ts}.sqlite"
    current_node_row_digest = _sqlite_table_digest(sqlite_path, "nodes")
    current_edge_row_digest = _sqlite_table_digest(sqlite_path, "edges")
    proof: dict[str, object] = {
        "probe_enabled": enable_probe,
        "scanner_digest": result.digest if result is not None else "",
        "artifact_digest": artifact.artifact_digest,
        "current_node_row_digest": current_node_row_digest,
        "current_edge_row_digest": current_edge_row_digest,
        "scanner_digest_match": False,
        "artifact_digest_match": False,
        "node_row_digest_match": False,
        "edge_row_digest_match": False,
        "determinism_status": "skipped",
    }
    if not enable_probe or result is None:
        return proof

    cache_path = adg_dir / "cache" / "scan_result_cache.json"
    probe_scanner = ADGStaticScanner(repo_root=repo_root, include_tests=True, cache_path=cache_path)
    probe_result = probe_scanner.scan(commit_sha=result.commit_sha or "determinism-probe")
    probe_result.repo_state_hash = result.repo_state_hash
    probe_artifact = build_artifact(probe_result)
    try:
        with tempfile.TemporaryDirectory() as tmpdir_str:
            tmpdir = Path(tmpdir_str)
            probe_paths = write_all_artifacts(cast(Any, probe_artifact), out_dir=tmpdir, ts=f"{ts}_probe")
            probe_node_row_digest = _sqlite_table_digest(probe_paths.sqlite, "nodes")
            probe_edge_row_digest = _sqlite_table_digest(probe_paths.sqlite, "edges")
    except (AttributeError, OSError, sqlite3.Error) as exc:
        proof["probe_error"] = str(exc)
        proof["determinism_status"] = "partial"
        return proof
    proof.update(
        {
            "probe_scanner_digest": probe_result.digest,
            "probe_artifact_digest": probe_artifact.artifact_digest,
            "probe_node_row_digest": probe_node_row_digest,
            "probe_edge_row_digest": probe_edge_row_digest,
            "scanner_digest_match": result.digest == probe_result.digest,
            "artifact_digest_match": artifact.artifact_digest == probe_artifact.artifact_digest,
            "node_row_digest_match": current_node_row_digest == probe_node_row_digest,
            "edge_row_digest_match": current_edge_row_digest == probe_edge_row_digest,
        },
    )
    proof["determinism_status"] = (
        "closed"
        if all(
            proof[key]
            for key in (
                "scanner_digest_match",
                "artifact_digest_match",
                "node_row_digest_match",
                "edge_row_digest_match",  # guardian: Add error context logging
            )
        )
        else "partial"
    )
    return proof


_TS_SUFFIX_RE = re.compile(r"_\d{8}_\d{4}$")


def _safe_unlink(path: Path) -> bool:
    """Best-effort unlink returning whether a file was removed."""
    try:
        if path.exists():
            path.unlink()
            return True
    except OSError as e:
        print(f"[ADG] Cleanup: error removing {path.name}: {e}")
    return False


def _cleanup_validation_files(adg_dir: Path, current_ts: str) -> None:
    """Clean up old validation packages, MANIFEST files, and non-timestamped reports.

    Keeps only the latest validation package (matching current_ts).
    Removes all MANIFEST files (low value).
    Removes non-timestamped report files (legacy cleanup).

    Args:    # guardian: Add error context logging
        adg_dir: ADG artifacts directory
        current_ts: Current timestamp (MMDDYYYY_HHMM format)
    """
    if not adg_dir.exists():
        return

    cleaned_count = 0

    # Remove all MANIFEST files (low value)    # guardian: Add error context logging
    for manifest_file in adg_dir.glob("MANIFEST_*.txt"):
        # guardian: allow-silent-swallow - acceptable exception handling
        if _safe_unlink(manifest_file):
            cleaned_count += 1

    # Remove non-timestamped report files (legacy cleanup)
    for report_file in tqdm(adg_dir.glob("*_report.json"), desc="Processing", unit="item"):
        if _TS_SUFFIX_RE.search(report_file.stem):
            continue
        if _safe_unlink(report_file):
            cleaned_count += 1
            print(f"[ADG] Cleanup: removed legacy report {report_file.name}")

    # Remove non-timestamped test_surface_coverage files (legacy cleanup)
    # guardian: allow-silent-swallow - acceptable exception handling
    for test_file in adg_dir.glob("test_surface_coverage.json"):
        if _safe_unlink(test_file):
            cleaned_count += 1
            print("[ADG] Cleanup: removed legacy test_surface_coverage.json")

    # Clean up old validation packages (keep only current timestamp)
    validation_patterns = [
        "chatgpt_validation_package_*.zip",
        "adg_validation_package_*.zip",
    ]

    for pattern in tqdm(validation_patterns, desc="Processing", unit="item"):
        for val_file in adg_dir.glob(pattern):
            # guardian: allow-silent-swallow - acceptable exception handling
            # Extract timestamp from validation package filename
            # e.g., chatgpt_validation_package_03132026_0427.zip
            if current_ts not in val_file.name:
                if _safe_unlink(val_file):
                    cleaned_count += 1

    if cleaned_count > 0:  # guardian: Add error context logging
        print(f"[ADG] Cleanup: removed {cleaned_count} old validation/manifest files")
