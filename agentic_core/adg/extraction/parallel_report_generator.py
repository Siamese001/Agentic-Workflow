"""Parallel ADG Report Generator - Wave 4 CPU Optimization.

Parallelizes report generation in generate_full_adg.py to utilize
all CPU cores during the 6+ sequential report generation phase.
"""

from __future__ import annotations

import concurrent.futures
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from agentic_core.L2_execution.utils import (
    AMDCPUOptimizer,
    CPUConfig,
)

logger = logging.getLogger(__name__)


@dataclass
class ReportTask:
    """Task specification for report generation."""
    report_name: str
    generator_func: Callable[[], dict]
    output_path: Path


@dataclass
class ReportResult:
    """Result from report generation."""
    report_name: str
    success: bool
    output_path: Path | None = None
    record_count: int = 0
    error: str | None = None
    generation_time_ms: float = 0.0


class ParallelReportGenerator:
    """Parallel report generator for ADG analysis.

    Replaces the sequential report generation in generate_full_adg.py
    with parallel execution across CPU cores.

    Reports generated in parallel:
    - layer_coverage_report
    - edge_density_report
    - provenance_report
    - replay_determinism_report
    - boundary_report
    - mutation_integrity_report
    - test_surface_coverage
    - closure_validation_report
    """

    def __init__(self, max_workers: int | None = None):
        self.config = CPUConfig(max_workers=max_workers, use_processes=False)
        self.optimizer = AMDCPUOptimizer(self.config)
        self._executor: concurrent.futures.Executor | None = None

    def _get_executor(self) -> concurrent.futures.Executor:
        """Get or create thread pool executor."""
        if self._executor is None:
            workers = self.optimizer.get_optimal_workers()
            self._executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=workers,
                thread_name_prefix="report_gen_",
            )
            logger.info(f"ReportGenerator using {workers} threads")

        return self._executor

    def generate_reports_parallel(
        self,
        report_tasks: list[ReportTask],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[ReportResult]:
        """Generate multiple reports in parallel.

        Args:
            report_tasks: List of ReportTask specifications
            progress_callback: Optional callback(current, total)

        Returns:
            List of ReportResult objects
        """
        if not report_tasks:
            return []

        total = len(report_tasks)
        results: list[ReportResult] = []

        logger.info(f"Generating {total} reports in parallel")

        # Submit all tasks
        executor = self._get_executor()
        futures = {
            executor.submit(self._generate_single_report, task): task
            for task in report_tasks
        }

        # Collect results
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
                results.append(result)

                if result.success:
                    logger.info(f"Generated {result.report_name}: {result.record_count} records")
                else:
                    logger.error(f"Failed {result.report_name}: {result.error}")

            except Exception as e:
                logger.error(f"Report generation failed for {task.report_name}: {e}")
                results.append(ReportResult(
                    report_name=task.report_name,
                    success=False,
                    error=str(e),
                ))

            completed += 1
            if progress_callback:
                progress_callback(completed, total)

        return results

    def _generate_single_report(self, task: ReportTask) -> ReportResult:
        """Generate a single report."""
        import time
        start = time.time()

        try:
            # Generate report data
            report_data = task.generator_func()

            # Write to file
            task.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(task.output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, sort_keys=True)

            elapsed_ms = (time.time() - start) * 1000

            # Count records (heuristic)
            record_count = self._count_records(report_data)

            return ReportResult(
                report_name=task.report_name,
                success=True,
                output_path=task.output_path,
                record_count=record_count,
                generation_time_ms=elapsed_ms,
            )

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            return ReportResult(
                report_name=task.report_name,
                success=False,
                error=str(e),
                generation_time_ms=elapsed_ms,
            )

    def _count_records(self, report_data: dict) -> int:
        """Count records in report data (heuristic)."""
        count = 0

        if isinstance(report_data, dict):
            for value in report_data.values():
                if isinstance(value, list):
                    count += len(value)
                elif isinstance(value, dict):
                    count += self._count_records(value)

        return max(1, count)

    def shutdown(self) -> None:
        """Shutdown the generator."""
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None


class LayerCoverageReportGenerator:
    """Generator for layer coverage reports."""

    @staticmethod
    def generate(
        conn,
        timestamp: str,
    ) -> dict[str, Any]:
        """Generate layer coverage report."""
        report = {
            "timestamp": timestamp,
            "schema_version": "1.0",
            "layers": {},
        }

        # Query layer distribution
        cursor = conn.execute("""
            SELECT layer, COUNT(*) as count
            FROM nodes
            GROUP BY layer
        """)

        for row in cursor:
            report["layers"][row["layer"]] = {
                "node_count": row["count"],
            }

        return report


class EdgeDensityReportGenerator:
    """Generator for edge density reports."""

    @staticmethod
    def generate(
        conn,
        timestamp: str,
    ) -> dict[str, Any]:
        """Generate edge density report."""
        report = {
            "timestamp": timestamp,
            "schema_version": "1.0",
            "total_edges": 0,
            "by_relation_type": {},
            "by_layer": {},
        }

        # Total edges
        cursor = conn.execute("SELECT COUNT(*) as count FROM edges")
        report["total_edges"] = cursor.fetchone()["count"]

        # By relation type
        cursor = conn.execute("""
            SELECT relation_type, COUNT(*) as count
            FROM edges
            GROUP BY relation_type
        """)
        for row in cursor:
            report["by_relation_type"][row["relation_type"]] = row["count"]

        return report


class BoundaryReportGenerator:
    """Generator for layer boundary reports."""

    @staticmethod
    def generate(
        violations: list[dict],
        timestamp: str,
    ) -> dict[str, Any]:
        """Generate boundary violation report."""
        report = {
            "timestamp": timestamp,
            "schema_version": "1.0",
            "total_violations": len(violations),
            "by_source_layer": {},
            "by_violation_type": {},
            "violations": violations[:100],  # Sample
        }

        # Group by source layer
        for v in violations:
            layer = v.get("source_layer", "unknown")
            report["by_source_layer"][layer] = report["by_source_layer"].get(layer, 0) + 1

        return report


def create_report_tasks(
    db_path: str,
    reports_dir: Path,
    timestamp: str,
    extra_data: dict | None = None,
) -> list[ReportTask]:
    """Create report generation tasks.

    Args:
        db_path: Path to ADG SQLite database
        reports_dir: Directory for report output
        timestamp: Report timestamp
        extra_data: Additional data for reports

    Returns:
        List of ReportTask objects
    """
    import sqlite3

    tasks = []
    extra_data = extra_data or {}

    # Layer coverage report
    def gen_layer_coverage():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        result = LayerCoverageReportGenerator.generate(conn, timestamp)
        conn.close()
        return result

    tasks.append(ReportTask(
        report_name="layer_coverage",
        generator_func=gen_layer_coverage,
        output_path=reports_dir / f"layer_coverage_report_{timestamp}.json",
    ))

    # Edge density report
    def gen_edge_density():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        result = EdgeDensityReportGenerator.generate(conn, timestamp)
        conn.close()
        return result

    tasks.append(ReportTask(
        report_name="edge_density",
        generator_func=gen_edge_density,
        output_path=reports_dir / f"edge_density_report_{timestamp}.json",
    ))

    # Boundary report (if violations provided)
    violations = extra_data.get("violations", [])
    if violations:
        def gen_boundary():
            return BoundaryReportGenerator.generate(violations, timestamp)

        tasks.append(ReportTask(
            report_name="boundary",
            generator_func=gen_boundary,
            output_path=reports_dir / f"boundary_report_{timestamp}.json",
        ))

    return tasks


# Singleton instance
_report_generator: ParallelReportGenerator | None = None


def get_report_generator(max_workers: int | None = None) -> ParallelReportGenerator:
    """Get singleton report generator."""
    global _report_generator
    if _report_generator is None:
        _report_generator = ParallelReportGenerator(max_workers)
    return _report_generator


def shutdown_report_generator() -> None:
    """Shutdown singleton report generator."""
    global _report_generator
    if _report_generator:
        _report_generator.shutdown()
        _report_generator = None


__all__ = [
    "ParallelReportGenerator",
    "ReportTask",
    "ReportResult",
    "LayerCoverageReportGenerator",
    "EdgeDensityReportGenerator",
    "BoundaryReportGenerator",
    "create_report_tasks",
    "get_report_generator",
    "shutdown_report_generator",
]
