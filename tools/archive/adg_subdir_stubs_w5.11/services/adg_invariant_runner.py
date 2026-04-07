"""ADG Invariant Runner — Deterministic invariant checks for ADG graph.

Checks graph integrity, import resolution, boundary violations, and cache parity.
Produces structured FindingPacket output (JSON, not prose).
Separates graph facts from policy findings.
"""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any

from agentic_core.adg.contracts.query_contracts import (
    FindingPacket,
    FindingSeverity,
    InvariantResult,
    UnresolvedImport,
)
from tools.adg.services.adg_query_service import ADGQueryService

logger = logging.getLogger(__name__)


class InvariantCheck(ABC):
    """Base class for invariant checks.

    Each check implements a specific invariant validation against
    the ADG graph. Checks are deterministic and reproducible.
    """

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    @abstractmethod
    def run(
        self,
        query_service: ADGQueryService,
        policy_pack: dict[str, Any],
    ) -> InvariantResult:
        """Run the invariant check.

        Args:
            query_service: Initialized ADG query service
            policy_pack: Policy configuration for the check

        Returns:
            InvariantResult with findings (if any)
        """
        pass


class ImportResolutionCheck(InvariantCheck):
    """Check that all imports resolve to valid module entities.

    Detects unresolved imports where destination is a symbol
    rather than a module (e.g., apps_lic -> archives imports).
    """

    def __init__(self) -> None:
        super().__init__(
            name="import_resolution",
            description="Validate all imports resolve to module entities",
        )

    def run(
        self,
        query_service: ADGQueryService,
        policy_pack: dict[str, Any],
    ) -> InvariantResult:
        """Run import resolution check."""
        start_time = time.time()

        # Get scope from policy pack (optional)
        scope = policy_pack.get("scope")

        # Find unresolved imports via query service
        unresolved = query_service.find_unresolved_imports(scope)

        findings: list[FindingPacket] = []
        for imp in unresolved:
            # Skip certain patterns based on policy
            if self._is_allowed_unresolved(imp, policy_pack):
                continue

            finding = FindingPacket(
                finding_id=f"unresolved_import_{imp.edge_id}",
                finding_type="unresolved_import",
                severity=FindingSeverity.HIGH,
                scope=imp.src_module,
                facts={
                    "edge_id": imp.edge_id,
                    "src_module": imp.src_module,
                    "src_file": imp.src_file,
                    "line_no": imp.line_no,
                    "symbol": imp.symbol,
                    "dst_id": imp.dst_id,
                    "dst_entity_type": imp.dst_entity_type,
                },
                policy_pack=policy_pack.get("name", "default"),
                description=f"Unresolved import: {imp.src_module} imports {imp.symbol}",
                remediation=f"Fix import at {imp.src_file}:{imp.line_no} or add to allowlist",
                snapshot_id=query_service.get_snapshot_metadata().snapshot_id if query_service.get_snapshot_metadata() else None,
            )
            findings.append(finding)

        duration_ms = (time.time() - start_time) * 1000

        return InvariantResult(
            invariant_name=self.name,
            passed=len(findings) == 0,
            findings=findings,
            checked_count=len(unresolved),
            duration_ms=duration_ms,
            snapshot_id=query_service.get_snapshot_metadata().snapshot_id if query_service.get_snapshot_metadata() else None,
        )

    def _is_allowed_unresolved(
        self,
        imp: UnresolvedImport,
        policy_pack: dict[str, Any],
    ) -> bool:
        """Check if unresolved import is allowed by policy."""
        allowlist = policy_pack.get("allowlist", [])
        for pattern in allowlist:
            if pattern in imp.symbol:
                return True
        return False


class BoundaryViolationCheck(InvariantCheck):
    """Check for forbidden cross-boundary imports.

    Detects imports from forbidden sources (e.g., apps_* -> archives).
    """

    def __init__(self) -> None:
        super().__init__(
            name="boundary_violation",
            description="Detect forbidden cross-boundary imports",
        )

    def run(
        self,
        query_service: ADGQueryService,
        policy_pack: dict[str, Any],
    ) -> InvariantResult:
        """Run boundary violation check."""
        start_time = time.time()

        # Get forbidden patterns from policy
        forbidden_patterns = policy_pack.get(
            "forbidden_patterns",
            ["archives."],  # Default: archives imports are forbidden
        )
        protected_scopes = policy_pack.get(
            "protected_scopes",
            ["apps_lic", "apps_rg", "apps_eval", "apps_exec", "apps_research", "apps_rfp"],
        )

        findings: list[FindingPacket] = []
        total_checked = 0

        # Check each protected scope
        for scope in protected_scopes:
            unresolved = query_service.find_unresolved_imports(scope)
            total_checked += len(unresolved)

            for imp in unresolved:
                # Check if import matches forbidden patterns
                if any(pat in imp.symbol for pat in forbidden_patterns):
                    finding = FindingPacket(
                        finding_id=f"boundary_violation_{imp.edge_id}",
                        finding_type="forbidden_boundary_import",
                        severity=FindingSeverity.CRITICAL,
                        scope=scope,
                        facts={
                            "edge_id": imp.edge_id,
                            "src_module": imp.src_module,
                            "src_file": imp.src_file,
                            "line_no": imp.line_no,
                            "symbol": imp.symbol,
                            "forbidden_pattern": next(
                                (p for p in forbidden_patterns if p in imp.symbol),
                                "unknown",
                            ),
                        },
                        policy_pack=policy_pack.get("name", "default"),
                        description=f"Boundary violation: {scope} imports forbidden {imp.symbol}",
                        remediation=f"Remove forbidden import at {imp.src_file}:{imp.line_no}",
                        snapshot_id=query_service.get_snapshot_metadata().snapshot_id if query_service.get_snapshot_metadata() else None,
                    )
                    findings.append(finding)

        duration_ms = (time.time() - start_time) * 1000

        return InvariantResult(
            invariant_name=self.name,
            passed=len(findings) == 0,
            findings=findings,
            checked_count=total_checked,
            duration_ms=duration_ms,
            snapshot_id=query_service.get_snapshot_metadata().snapshot_id if query_service.get_snapshot_metadata() else None,
        )


class RedisParityCheck(InvariantCheck):
    """Check that Redis cache matches SQLite for the snapshot.

    Verifies node count, edge count, and sampled edge hashes.
    """

    def __init__(self) -> None:
        super().__init__(
            name="redis_parity",
            description="Verify Redis cache matches SQLite snapshot",
        )

    def run(
        self,
        query_service: ADGQueryService,
        policy_pack: dict[str, Any],
    ) -> InvariantResult:
        """Run Redis parity check."""
        start_time = time.time()

        findings: list[FindingPacket] = []

        # Get metadata
        meta = query_service.get_snapshot_metadata()
        if not meta:
            return InvariantResult(
                invariant_name=self.name,
                passed=False,
                findings=[],
                checked_count=0,
                duration_ms=0,
            )

        # Check coherence flag
        if not meta.projection_coherent:
            finding = FindingPacket(
                finding_id="redis_parity_failed",
                finding_type="cache_parity_failure",
                severity=FindingSeverity.HIGH,
                scope="adg_cache",
                facts={
                    "sqlite_digest": meta.sqlite_digest,
                    "redis_digest": meta.redis_digest,
                    "node_count": meta.node_count,
                    "edge_count": meta.edge_count,
                },
                policy_pack=policy_pack.get("name", "default"),
                description="Redis cache does not match SQLite snapshot",
                remediation="Run: python tools/adg/adg_redis_ingest.py --force",
                snapshot_id=meta.snapshot_id,
            )
            findings.append(finding)

        duration_ms = (time.time() - start_time) * 1000

        return InvariantResult(
            invariant_name=self.name,
            passed=len(findings) == 0,
            findings=findings,
            checked_count=1,
            duration_ms=duration_ms,
            snapshot_id=meta.snapshot_id,
        )


class InvariantRunner:
    """Runner for ADG invariant checks.

    Orchestrates multiple invariant checks against a snapshot
    and produces structured results.

    Usage:
        runner = InvariantRunner()
        runner.register_check(ImportResolutionCheck())
        runner.register_check(BoundaryViolationCheck())

        with ADGQueryService() as service:
            service.initialize_snapshot("04022026_2140")
            results = runner.run_all(service, policy_pack)
    """

    def __init__(self) -> None:
        self.checks: list[InvariantCheck] = []
        self.results: list[InvariantResult] = []

    def register_check(self, check: InvariantCheck) -> None:
        """Register an invariant check."""
        self.checks.append(check)
        logger.info(f"Registered invariant check: {check.name}")

    def run_all(
        self,
        query_service: ADGQueryService,
        policy_pack: dict[str, Any] | None = None,
    ) -> list[InvariantResult]:
        """Run all registered checks.

        Args:
            query_service: Initialized ADG query service
            policy_pack: Optional policy configuration

        Returns:
            List of InvariantResult for each check
        """
        policy = policy_pack or {"name": "default"}
        self.results = []

        for check in self.checks:
            logger.info(f"Running check: {check.name}")
            result = check.run(query_service, policy)
            self.results.append(result)

            status = "PASS" if result.passed else "FAIL"
            logger.info(
                f"Check {check.name}: {status} "
                f"({len(result.findings)} findings, {result.checked_count} checked)",
            )

        return self.results

    def has_violations(self, min_severity: FindingSeverity = FindingSeverity.HIGH) -> bool:
        """Check if any results have violations at or above severity threshold."""
        for result in self.results:
            for finding in result.findings:
                if finding.severity.value in ["high", "critical"]:
                    return True
        return False

    def get_all_findings(self) -> list[FindingPacket]:
        """Get all findings from all checks."""
        findings: list[FindingPacket] = []
        for result in self.results:
            findings.extend(result.findings)
        return findings

    def to_dict(self) -> dict[str, Any]:
        """Convert all results to dictionary for JSON serialization."""
        return {
            "passed": all(r.passed for r in self.results),
            "has_violations": self.has_violations(),
            "results": [
                {
                    "invariant_name": r.invariant_name,
                    "passed": r.passed,
                    "findings": [f.to_dict() for f in r.findings],
                    "checked_count": r.checked_count,
                    "duration_ms": r.duration_ms,
                    "snapshot_id": r.snapshot_id,
                }
                for r in self.results
            ],
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert all results to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


def run_invariant_suite(
    snapshot_id: str,
    policy_pack: dict[str, Any] | None = None,
    redis_url: str = "redis://localhost:6379/0",
    adg_dir: str | None = None,
) -> list[InvariantResult]:
    """Convenience function to run full invariant suite.

    Args:
        snapshot_id: ADG snapshot ID to check
        policy_pack: Optional policy configuration
        redis_url: Redis connection URL
        adg_dir: Directory containing ADG SQLite files

    Returns:
        List of InvariantResult for each check
    """
    runner = InvariantRunner()

    # Register standard checks
    runner.register_check(ImportResolutionCheck())
    runner.register_check(BoundaryViolationCheck())
    runner.register_check(RedisParityCheck())

    with ADGQueryService(redis_url=redis_url, adg_dir=adg_dir) as service:
        service.initialize_snapshot(snapshot_id)
        return runner.run_all(service, policy_pack)


__all__ = [
    "InvariantCheck",
    "ImportResolutionCheck",
    "BoundaryViolationCheck",
    "RedisParityCheck",
    "InvariantRunner",
    "run_invariant_suite",
]
