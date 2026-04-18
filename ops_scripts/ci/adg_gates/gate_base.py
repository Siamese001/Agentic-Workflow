"""Base class for ADG materialized-view-driven CI gates.

All gates consume materialized views from the canonical ADG SQLite database
and emit actionable artifacts with provenance, first-hop detection, and
snapshot-aware operation.

Extended by the P0-P3 execution policy enhancement wave to carry full
operational context: stage, repairability, gate_action, artifact_policy,
signal_source, evidence_tier, path-aware ratchet, and P3 trend/promotion.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


REPO_ROOT = _bootstrap_repo_root()

from ops_scripts.ci.adg_gates.gate_policy import (
    ExecutionPolicy,
    RatchetResult,
    TrendResult,
    VALID_PATH_CRITICALITY_CLASSES,
)

ADG_DIR = REPO_ROOT / "artifacts" / "adg"
CI_RATchet_DIR = ADG_DIR / "ci_ratchets"
CI_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "ci_gates"


@dataclass
class GateViolation:
    """Single violation record with full provenance."""

    violation_id: str
    source_view: str
    source_node: str | None
    source_edge: str | None
    file: str | None
    line: int | None
    layer_src: str | None
    layer_dst: str | None
    path_id: str | None
    first_illegal_hop: str | None
    path_criticality: float
    in_modified_area: bool
    message: str
    extra: dict[str, Any] = field(default_factory=dict)
    path_criticality_class: str = "unknown"
    structured_action_required: bool = False
    approval_required: bool = False


@dataclass
class GateResult:
    """Result from a single gate execution."""

    gate_family: str
    severity: str  # P0, P1, P2, P3
    snapshot_id: str
    timestamp: str
    status: str  # blocked, passed, warn
    violations: list[GateViolation]
    summary: dict[str, Any]
    policy: ExecutionPolicy = field(default_factory=ExecutionPolicy)
    ratchet: RatchetResult | None = None
    trend: TrendResult | None = None
    stage: str = "full"  # mirrors policy.stage for fast access

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "gate_family": self.gate_family,
            "severity": self.severity,
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "stage": self.stage,
            "policy": self.policy.to_dict(),
            "violations": [
                {
                    "violation_id": v.violation_id,
                    "source_view": v.source_view,
                    "source_node": v.source_node,
                    "source_edge": v.source_edge,
                    "file": v.file,
                    "line": v.line,
                    "layer_src": v.layer_src,
                    "layer_dst": v.layer_dst,
                    "path_id": v.path_id,
                    "first_illegal_hop": v.first_illegal_hop,
                    "path_criticality": v.path_criticality,
                    "path_criticality_class": v.path_criticality_class,
                    "in_modified_area": v.in_modified_area,
                    "structured_action_required": v.structured_action_required,
                    "approval_required": v.approval_required,
                    "message": v.message,
                    "extra": v.extra,
                }
                for v in self.violations
            ],
            "summary": self.summary,
        }
        if self.ratchet is not None:
            d["ratchet"] = self.ratchet.to_dict()
        if self.trend is not None:
            d["trend"] = self.trend.to_dict()
        return d


class ADGGateBase(ABC):
    """Base class for all ADG materialized-view-driven CI gates.

    Subclasses must implement:
        - gate_family: str — unique gate identifier
        - severity: str — P0, P1, P2, or P3
        - source_views: list[str] — materialized views to query
        - execution_policy: ExecutionPolicy — operational classification
        - _execute_gate_logic() — perform the actual gate check

    Subclasses supporting preflight must also implement:
        - _execute_preflight_logic() — lightweight seed-graph check
    """

    gate_family: str = ""
    severity: str = ""
    source_views: list[str] = []
    execution_policy: ExecutionPolicy = ExecutionPolicy()

    def __init__(
        self,
        sqlite_path: Path | None = None,
        modified_files: list[str] | None = None,
        preflight_mode: bool = False,
    ):
        """Initialize gate with SQLite path and optional modified file list.

        Args:
            sqlite_path: Path to ADG SQLite database. If None, finds latest.
            modified_files: List of files in current change set for modified-area focus.
            preflight_mode: If True, run lightweight preflight logic instead of
                full materialized-view logic. Only supported by gates whose
                execution_policy.stage includes 'preflight'.
        """
        self.sqlite_path = sqlite_path or self._find_latest_sqlite()
        self.modified_files = set(modified_files or [])
        self.preflight_mode = preflight_mode
        self.conn: sqlite3.Connection | None = None
        self._snapshot_id: str = ""

    def _find_latest_sqlite(self) -> Path:
        """Find the latest ADG SQLite file."""
        files = [p for p in ADG_DIR.glob("adg_indexed_*.sqlite") if p.is_file()]
        if not files:
            raise RuntimeError("No ADG SQLite file found in artifacts/adg/")
        return max(files, key=lambda p: (p.stat().st_mtime_ns, p.name))

    def _connect(self) -> None:
        """Establish SQLite connection."""
        db_uri = f"file:{self.sqlite_path.as_posix()}?mode=ro&immutable=1"
        self.conn = sqlite3.connect(db_uri, uri=True, timeout=5)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA query_only = ON")

    def _close(self) -> None:
        """Close SQLite connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _get_snapshot_id(self) -> str:
        """Get snapshot ID from meta table."""
        if not self.conn:
            return ""
        try:
            cur = self.conn.execute("SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1")
            row = cur.fetchone()
            return row[0] if row else ""
        except sqlite3.Error:
            return ""

    def _is_in_modified_area(self, file_path: str | None) -> bool:
        """Check if a file is in the modified area."""
        if not file_path or not self.modified_files:
            return False
        # Normalize path for comparison
        normalized = file_path.replace("\\", "/")
        return any(normalized.endswith(mf) or mf.endswith(normalized) for mf in self.modified_files)

    def _load_baseline(self, baseline_name: str) -> dict[str, Any]:
        """Load ratchet baseline from file."""
        baseline_file = CI_RATchet_DIR / f"{baseline_name}_baseline.json"
        if not baseline_file.exists():
            return {}
        try:
            data: dict[str, Any] = json.loads(baseline_file.read_text(encoding="utf-8"))
            return data
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_baseline(self, baseline_name: str, data: dict[str, Any]) -> None:
        """Save ratchet baseline atomically."""
        CI_RATchet_DIR.mkdir(parents=True, exist_ok=True)
        baseline_file = CI_RATchet_DIR / f"{baseline_name}_baseline.json"
        content = json.dumps(data, indent=2, sort_keys=True) + "\n"
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=CI_RATchet_DIR,
                prefix=f".{baseline_name}_",
                suffix=".tmp",
                delete=False,
            ) as fh:
                fh.write(content)
                fh.flush()
                os.fsync(fh.fileno())
                tmp_path = Path(fh.name)
            if sys.platform == "win32" and baseline_file.exists():
                baseline_file.unlink()
            if tmp_path is None:
                raise OSError("Failed to create temporary baseline file")
            tmp_path.replace(baseline_file)
        except OSError:
            if tmp_path is not None:
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            raise

    def _load_trend(self, trend_name: str) -> dict[str, Any]:
        """Load trend tracking data for P2 gates."""
        trend_file = CI_RATchet_DIR / f"{trend_name}_trend.json"
        if not trend_file.exists():
            return {"history": [], "consecutive_increases": 0}
        try:
            data: dict[str, Any] = json.loads(trend_file.read_text(encoding="utf-8"))
            return data
        except (OSError, json.JSONDecodeError):
            return {"history": [], "consecutive_increases": 0}

    def _save_trend(self, trend_name: str, data: dict[str, Any]) -> None:
        """Save trend data atomically."""
        CI_RATchet_DIR.mkdir(parents=True, exist_ok=True)
        trend_file = CI_RATchet_DIR / f"{trend_name}_trend.json"
        content = json.dumps(data, indent=2, sort_keys=True) + "\n"
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=CI_RATchet_DIR,
                prefix=f".{trend_name}_",
                suffix=".tmp",
                delete=False,
            ) as fh:
                fh.write(content)
                fh.flush()
                os.fsync(fh.fileno())
                tmp_path = Path(fh.name)
            if sys.platform == "win32" and trend_file.exists():
                trend_file.unlink()
            if tmp_path is None:
                raise OSError("Failed to create temporary trend file")
            tmp_path.replace(trend_file)
        except OSError:
            if tmp_path is not None:
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            raise

    def _write_artifacts(self, result: GateResult) -> Path:
        """Write gate result artifacts to disk, shaped by artifact_policy."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        artifact_dir = CI_ARTIFACTS_DIR / ts
        artifact_dir.mkdir(parents=True, exist_ok=True)

        policy = result.policy.artifact_policy

        if policy == "minimal_failure_artifact":
            # Preflight P0 hit — emit compact artifact only
            minimal: dict[str, Any] = {
                "gate_family": result.gate_family,
                "severity": result.severity,
                "stage": result.stage,
                "status": result.status,
                "snapshot_id": result.snapshot_id,
                "timestamp": result.timestamp,
                "policy": result.policy.to_dict(),
                "violations": [
                    {
                        "violation_id": v.violation_id,
                        "file": v.file,
                        "first_illegal_hop": v.first_illegal_hop,
                        "path_criticality_class": v.path_criticality_class,
                        "message": v.message,
                        "structured_action_required": v.structured_action_required,
                        "approval_required": v.approval_required,
                    }
                    for v in result.violations
                ],
                "run_metadata": {
                    "sqlite_path": str(self.sqlite_path),
                    "preflight_mode": self.preflight_mode,
                },
            }
            out = artifact_dir / f"gate_{result.gate_family}_minimal_failure.json"
            out.write_text(json.dumps(minimal, indent=2), encoding="utf-8")
            return artifact_dir

        if policy == "trend_only":
            # P3 watch — emit trend artifact only
            trend_data: dict[str, Any] = {
                "gate_family": result.gate_family,
                "severity": result.severity,
                "timestamp": result.timestamp,
                "policy": result.policy.to_dict(),
                "trend": result.trend.to_dict() if result.trend else {},
                "violation_count": len(result.violations),
            }
            out = artifact_dir / f"gate_{result.gate_family}_trend.json"
            out.write_text(json.dumps(trend_data, indent=2), encoding="utf-8")
            return artifact_dir

        # Default: full_adg_report (and all other policies — include full payload)
        artifact_file = artifact_dir / f"gate_{result.gate_family}.json"
        artifact_file.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

        # Human-readable findings
        findings_file = artifact_dir / f"gate_{result.gate_family}_findings.txt"
        findings = self._format_findings(result)
        findings_file.write_text(findings, encoding="utf-8")

        # Provenance linkage
        provenance: dict[str, Any] = {
            "gate_family": result.gate_family,
            "snapshot_id": result.snapshot_id,
            "sqlite_path": str(self.sqlite_path),
            "source_views": self.source_views,
            "preflight_mode": self.preflight_mode,
            "violation_count": len(result.violations),
            "violations_with_provenance": [
                {
                    "violation_id": v.violation_id,
                    "source_view": v.source_view,
                    "source_node": v.source_node,
                    "source_edge": v.source_edge,
                }
                for v in result.violations
            ],
        }
        if result.ratchet is not None:
            provenance["ratchet"] = result.ratchet.to_dict()
        provenance_file = artifact_dir / f"gate_{result.gate_family}_provenance.json"
        provenance_file.write_text(json.dumps(provenance, indent=2), encoding="utf-8")

        return artifact_dir

    def _format_findings(self, result: GateResult) -> str:
        """Format human-readable findings."""
        lines = [
            f"{'=' * 60}",
            f"Gate: {result.gate_family} [{result.severity}]",
            f"Status: {result.status.upper()}",
            f"Snapshot: {result.snapshot_id[:16]}..."
            if len(result.snapshot_id) > 16
            else f"Snapshot: {result.snapshot_id}",
            f"Timestamp: {result.timestamp}",
            f"{'=' * 60}",
            "",
            f"Total Violations: {len(result.violations)}",
            f"In Modified Area: {sum(1 for v in result.violations if v.in_modified_area)}",
            "",
        ]

        if result.violations:
            lines.append("Violations:")
            lines.append("-" * 40)
            for v in result.violations[:20]:  # Show first 20
                loc = f"{v.file}:{v.line}" if v.line else v.file
                flag = " [MODIFIED]" if v.in_modified_area else ""
                lines.append(f"  {v.violation_id}: {v.message}{flag}")
                lines.append(f"    Location: {loc}")
                if v.first_illegal_hop:
                    lines.append(f"    First Illegal Hop: {v.first_illegal_hop}")
                lines.append(f"    Criticality Score: {v.path_criticality:.2f}")
                lines.append("")
            if len(result.violations) > 20:
                lines.append(f"  ... and {len(result.violations) - 20} more violations")
                lines.append("")

        lines.append("-" * 40)
        lines.append(f"Summary: {result.summary}")
        lines.append("")

        return "\n".join(lines)

    @abstractmethod
    def _execute_gate_logic(self) -> GateResult:
        """Execute the full gate logic against materialized views.

        Must be implemented by subclasses. Should:
        1. Query relevant materialized views
        2. Detect violations
        3. Build GateViolation records with full provenance
        4. Return GateResult with status determined by severity/rules
        """

    def _execute_preflight_logic(self) -> GateResult:
        """Execute lightweight preflight logic against seed graph.

        Override in subclasses that support preflight mode
        (execution_policy.stage includes 'preflight').

        Default implementation returns a passed result — gates that do not
        support preflight are never registered for preflight runs.
        """
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary={"preflight_supported": False},
            policy=getattr(self, "execution_policy", ExecutionPolicy()),
            stage="preflight",
        )

    def _compute_ratchet(
        self,
        violations: list[GateViolation],
        baseline_key: str,
    ) -> RatchetResult:
        """Compute path-aware ratchet from current violations vs saved baseline.

        Loads the baseline, computes gross/net/new/resolved/critical_* counts,
        and saves the updated baseline if not blocked.
        """
        baseline = self._load_baseline(baseline_key)
        baseline_ids: set[str] = set(baseline.get("violation_ids", []))
        current_ids = {v.violation_id for v in violations}

        new_violations = [v for v in violations if v.violation_id not in baseline_ids]
        resolved_ids = baseline_ids - current_ids

        critical_classes = {"sink", "write", "provider"}
        critical_new = [v for v in new_violations if v.path_criticality_class in critical_classes]
        critical_near_sink = [v for v in new_violations if v.path_criticality >= 0.8]
        critical_cross_layer = [
            v for v in new_violations if v.layer_src and v.layer_dst and v.layer_src != v.layer_dst
        ]
        modified_area_new = [v for v in new_violations if v.in_modified_area]

        net = len(current_ids) - len(baseline_ids)
        blocked = net > 0 or len(critical_new) > 0
        reason = ""
        if blocked:
            parts = []
            if net > 0:
                parts.append(f"net regression={net}")
            if critical_new:
                parts.append(f"critical_new={len(critical_new)}")
            reason = "; ".join(parts)

        ratchet = RatchetResult(
            gross=len(violations),
            net=net,
            new=len(new_violations),
            resolved=len(resolved_ids),
            critical_new=len(critical_new),
            critical_near_sink=len(critical_near_sink),
            critical_cross_layer=len(critical_cross_layer),
            modified_area_count=len(modified_area_new),
            blocked=blocked,
            reason=reason,
        )

        if not blocked:
            self._save_baseline(baseline_key, {"violation_ids": sorted(current_ids)})

        return ratchet

    def run(self, emit_artifacts: bool = True) -> GateResult:
        """Execute the gate and optionally emit artifacts.

        Dispatches to preflight or full logic based on self.preflight_mode.

        Args:
            emit_artifacts: If True, write artifacts to disk.

        Returns:
            GateResult with full violation details.
        """
        try:
            self._connect()
            self._snapshot_id = self._get_snapshot_id()

            if self.preflight_mode:
                result = self._execute_preflight_logic()
                result.stage = "preflight"
            else:
                result = self._execute_gate_logic()
                result.stage = "full"

            if emit_artifacts:
                self._write_artifacts(result)

            return result
        finally:
            self._close()

    def run_and_exit(self) -> int:
        """Execute gate and exit with appropriate code for CI.

        Returns:
            0 = passed (no blocking violations)
            1 = blocked (P0/P1 enforce-mode violations)
            2 = error (gate execution failure)
        """
        try:
            result = self.run(emit_artifacts=True)

            if result.status == "blocked":
                print(f"\n[CI-GATE] BLOCKED: {self.gate_family}", file=sys.stderr)
                print(f"[CI-GATE] Violations: {len(result.violations)}", file=sys.stderr)
                print(f"[CI-GATE] Artifacts: {CI_ARTIFACTS_DIR}", file=sys.stderr)
                return 1
            else:
                print(
                    f"[CI-GATE] PASSED: {self.gate_family} ({len(result.violations)} violations, non-blocking)"
                )
                return 0

        except (sqlite3.Error, OSError, RuntimeError) as e:
            print(f"\n[CI-GATE] ERROR: {self.gate_family} failed to execute: {e}", file=sys.stderr)
            return 2
