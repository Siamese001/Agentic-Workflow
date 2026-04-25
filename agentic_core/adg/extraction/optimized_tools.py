"""Optimized ADG Tools - Wave 4/5 CPU Optimization.

Integrates parallel processing into ADG tool suite:
- coverage_analysis.py
- adg_layer_boundary_checker.py
- adg_redis_ingest.py
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Callable

from agentic_core.L2_execution.utils import (
    get_file_processor,
)

logger = logging.getLogger(__name__)

_SQLITE_TIMEOUT_SECONDS = 30


def _connect_sqlite_readonly(db_path: str) -> sqlite3.Connection:
    """Open a read-only SQLite connection for worker-safe queries."""
    resolved = Path(db_path).resolve()
    conn = sqlite3.connect(f"file:{resolved}?mode=ro", uri=True, timeout=_SQLITE_TIMEOUT_SECONDS)
    conn.row_factory = sqlite3.Row
    return conn


class OptimizedCoverageAnalyzer:
    """Optimized coverage analysis using parallel processing.

    Replaces sequential iteration in coverage_analysis.py
    with parallel file processing.
    """

    def __init__(
        self,
        db_path: str,
        max_workers: int | None = None,
    ):
        self.db_path = db_path
        self.max_workers = max_workers
        self.metrics = {
            "files_processed": 0,
            "coverage_calculated": 0,
            "time_ms": 0.0,
        }

    def analyze_parallel(self) -> dict[str, Any]:
        """Run parallel coverage analysis."""
        import time

        start = time.time()

        with closing(_connect_sqlite_readonly(self.db_path)) as conn:
            cursor = conn.execute("""
                SELECT DISTINCT resolved_path
                FROM nodes
                WHERE resolved_path LIKE 'agentic_core/%'
                AND resolved_path NOT LIKE '%__pycache__%'
            """)
            src_paths = [row["resolved_path"] for row in cursor]

        # Get test coverage in parallel
        processor = get_file_processor(max_workers=self.max_workers)

        def check_coverage(src_path: str) -> dict[str, Any]:
            """Check coverage for single source file using a worker-local SQLite connection."""
            with closing(_connect_sqlite_readonly(self.db_path)) as worker_conn:
                cursor = worker_conn.execute(
                    """
                    SELECT COUNT(*) as test_count
                    FROM edges e
                    JOIN nodes n1 ON e.src_id = n1.id
                    JOIN nodes n2 ON e.dst_id = n2.id
                    WHERE e.relation_type = 'imports'
                    AND n1.resolved_path LIKE 'tests/%'
                    AND n2.resolved_path = ?
                """,
                    (src_path,),
                )

                row = cursor.fetchone()
                test_count = row["test_count"] if row else 0
                return {
                    "src_path": src_path,
                    "test_count": test_count,
                    "covered": test_count > 0,
                }

        # Process in parallel
        results = processor.process_files(src_paths, check_coverage)

        # Calculate statistics
        covered = sum(1 for r in results if r.success and r.data and r.data.get("covered"))
        total = len(results)

        elapsed_ms = (time.time() - start) * 1000
        self.metrics.update(
            {
                "files_processed": total,
                "coverage_calculated": covered,
                "time_ms": elapsed_ms,
            }
        )

        return {
            "total_modules": total,
            "covered_modules": covered,
            "coverage_pct": (covered / total * 100) if total else 0,
            "time_ms": elapsed_ms,
        }


class OptimizedLayerBoundaryChecker:
    """Optimized layer boundary checker with parallel validation."""

    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers

    def check_directory_parallel(
        self,
        directory: str,
        pattern: str = "**/*.py",
    ) -> list[dict]:
        """Check all files in directory in parallel."""
        import time

        start = time.time()

        # Get all Python files
        path = Path(directory)
        files = list(path.glob(pattern))
        file_paths = [str(f) for f in files if f.is_file()]

        logger.info(f"Checking {len(file_paths)} files for layer boundary violations")

        # Process in parallel
        processor = get_file_processor(max_workers=self.max_workers)

        def check_file(file_path: str) -> list[dict]:
            """Check single file for violations."""
            violations = []

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                # Detect layer from path
                layer = self._detect_layer(file_path)

                # Check imports
                for line_no, line in enumerate(lines, 1):
                    if line.strip().startswith(("import ", "from ")):
                        violation = self._check_import(layer, line, line_no, file_path)
                        if violation:
                            violations.append(violation)

            except (
                OSError,
                UnicodeDecodeError,
            ) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                logger.warning("Failed to check %s: %s", file_path, exc)

            return violations

        results = processor.process_files(file_paths, check_file)

        # Flatten results
        all_violations = []
        for r in results:
            if r.success and r.data:
                all_violations.extend(r.data)

        elapsed_ms = (time.time() - start) * 1000

        logger.info(
            f"Found {len(all_violations)} violations in {len(file_paths)} files ({elapsed_ms:.1f}ms)",
        )

        return all_violations

    def _detect_layer(self, file_path: str) -> str:
        """Detect layer from file path."""
        parts = Path(file_path).parts
        for part in parts:
            if part.startswith("L") and len(part) <= 3:
                return part
        return "unknown"

    def _check_import(
        self,
        source_layer: str,
        line: str,
        line_no: int,
        file_path: str,
    ) -> dict | None:
        """Check if import violates layer boundary."""
        # Simplified check - full implementation would use ADG
        if "agentic_core" in line:
            # Extract target layer from import
            target_layer = "unknown"
            if "L0_" in line:
                target_layer = "L0"
            elif "L1_" in line:
                target_layer = "L1"
            elif "L2_" in line:
                target_layer = "L2"
            elif "L3_" in line:
                target_layer = "L3"
            elif "L4_" in line:
                target_layer = "L4"
            elif "L5_" in line:
                target_layer = "L5"
            elif "L6_" in line:
                target_layer = "L6"

            # Check if violation
            if source_layer != "unknown" and target_layer != "unknown":
                src_num = int(source_layer[1:]) if source_layer[1:].isdigit() else 99
                tgt_num = int(target_layer[1:]) if target_layer[1:].isdigit() else 0

                if tgt_num > src_num:
                    return {
                        "file_path": file_path,
                        "line_number": line_no,
                        "source_layer": source_layer,
                        "target_layer": target_layer,
                        "import_line": line.strip(),
                        "violation_type": "layer_inversion",
                    }

        return None


class OptimizedRedisIngest:
    """Optimized Redis ingest with batch pipeline processing."""

    def __init__(
        self,
        redis_client,
        pipeline_size: int = 5000,
    ):
        self.redis = redis_client
        self.pipeline_size = pipeline_size

    def ingest_parallel(
        self,
        db_path: str,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> dict[str, Any]:
        """Ingest ADG data to Redis using batch pipelines."""
        import time

        start = time.time()

        if self.pipeline_size <= 0:
            raise ValueError("pipeline_size must be greater than zero")

        metrics = {
            "nodes_ingested": 0,
            "edges_ingested": 0,
            "time_ms": 0.0,
        }

        with closing(_connect_sqlite_readonly(db_path)) as conn:
            # Ingest nodes in batches
            cursor = conn.execute("SELECT * FROM nodes")
            pipe = self.redis.pipeline(transaction=False)
            pending = 0

            for row in cursor:  # progress_bar: ingest node rows into Redis
                node_data = dict(row)
                node_id = node_data.pop("id", None)
                if node_id:
                    pipe.hset(f"adg:node:{node_id}", mapping=node_data)
                    pending += 1
                    metrics["nodes_ingested"] += 1

                    if pending >= self.pipeline_size:
                        pipe.execute()
                        pipe = self.redis.pipeline(transaction=False)
                        pending = 0

            if pending:
                pipe.execute()

            # Ingest edges in batches
            cursor = conn.execute("SELECT * FROM edges")
            pipe = self.redis.pipeline(transaction=False)
            pending = 0

            for row in cursor:  # progress_bar: ingest edge rows into Redis
                edge_data = dict(row)
                edge_id = edge_data.pop("id", None)
                if edge_id:
                    pipe.hset(f"adg:edge:{edge_id}", mapping=edge_data)
                    pending += 1
                    metrics["edges_ingested"] += 1

                    if pending >= self.pipeline_size:
                        pipe.execute()
                        pipe = self.redis.pipeline(transaction=False)
                        pending = 0

            if pending:
                pipe.execute()

        elapsed_ms = (time.time() - start) * 1000
        metrics["time_ms"] = elapsed_ms

        logger.info(
            f"Redis ingest: {metrics['nodes_ingested']} nodes, "
            f"{metrics['edges_ingested']} edges in {elapsed_ms:.1f}ms",
        )

        return metrics


__all__ = [
    "OptimizedCoverageAnalyzer",
    "OptimizedLayerBoundaryChecker",
    "OptimizedRedisIngest",
]
