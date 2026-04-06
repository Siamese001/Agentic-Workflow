"""SovereignDecisionEngine module for execute_ssot - extracted from monolith.

This module contains the main SovereignDecisionEngine class which orchestrates
the compliance and healing process across all architectural layers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

# Module-level constants
RETRIEVAL_CACHE: dict[str, Any] = {}


def execute_phase1_discovery(project_root: str, targets: list[str]) -> dict[str, Any]:
    """Execute Phase 1 discovery to find issues across the project.

    Args:
        project_root: Project root directory
        targets: List of target paths to scan

    Returns:
        Discovery results with findings
    """
    findings = []

    # Run FilesystemSSOTValidatorAgent
    try:
        from agentic_core.L5_safety.reasoning.filesystem_ssot_validator import FilesystemSSOTValidatorAgent

        fs_validator = FilesystemSSOTValidatorAgent(project_root=project_root)
        fs_check = fs_validator.to_check_dict()
        violations_count = fs_check.get("violations_count", 0)
        if violations_count > 0:
            findings.append(
                {
                    "agent": "FilesystemSSOTValidatorAgent",
                    "type": "ssot_drift",
                    "severity": "high" if violations_count > 5 else "medium",
                    "violations_count": violations_count,
                    "valid": True,
                }
            )
    except Exception as e:
        logging.warning(f"FilesystemSSOTValidatorAgent failed: {e}")

    # Run LocationValidatorAgent for each target
    try:
        from pathlib import Path

        from agentic_core.L5_safety.reasoning.location_validator import LocationValidatorAgent

        for target in targets:
            target_path = Path(target).resolve()
            if target_path.exists():
                location_validator = LocationValidatorAgent(project_root=project_root)
                scan_result = location_validator.run(target_territory=str(target_path))
                violations = scan_result.get("violations", [])
                if violations:
                    findings.extend(
                        [
                            {
                                "agent": "LocationValidatorAgent",
                                "type": "location_violation",
                                "severity": v.get("severity", "medium"),
                                "file": v.get("file"),
                                "message": v.get("message", ""),
                                "valid": True,
                            }
                            for v in violations
                        ]
                    )
    except Exception as e:
        logging.warning(f"LocationValidatorAgent failed: {e}")

    # Run FileClassificationAgent for each target
    try:
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

        for target in targets:
            fc_agent = FileClassificationAgent(project_root=project_root)
            if hasattr(fc_agent, "scan"):
                scan_results = fc_agent.scan(target_path=target)
                issues = scan_results.get("issues", [])
                if issues:
                    findings.extend(
                        [
                            {
                                "agent": "FileClassificationAgent",
                                "type": "classification_issue",
                                "severity": i.get("severity", "medium"),
                                "file": i.get("file"),
                                "message": i.get("message", ""),
                                "valid": True,
                            }
                            for i in issues
                        ]
                    )
    except Exception as e:
        logging.warning(f"FileClassificationAgent failed: {e}")

    return {"phase": "discovery", "findings": findings, "total_findings": len(findings), "success": True}


def execute_phase3_alignment(findings: list[dict], strategy: str = "auto") -> list[dict]:
    """Execute Phase 3 alignment to generate healing strategies.

    Args:
        findings: List of findings from discovery/validation
        strategy: Strategy type (auto, conservative, aggressive)

    Returns:
        List of alignment objects with healing strategies
    """
    alignments = []

    for finding in findings:
        if not finding.get("valid"):
            continue

        agent = finding.get("agent", "")
        issue_type = finding.get("type", "")

        # Generate alignment based on issue type and strategy
        if "ssot" in issue_type or "FilesystemSSOT" in agent:
            alignments.append(
                {
                    "finding": finding,
                    "strategy": "heal_ssot",
                    "healer": "FilesystemSSOTReconcilerAgent",
                    "priority": "high",
                    "estimated_time": 30,
                }
            )
        elif "location" in issue_type or "Location" in agent:
            alignments.append(
                {
                    "finding": finding,
                    "strategy": "heal_location",
                    "healer": "LocationHealerAgent",
                    "priority": "medium",
                    "estimated_time": 15,
                }
            )
        elif "classification" in issue_type or "FileClassification" in agent:
            alignments.append(
                {
                    "finding": finding,
                    "strategy": "heal_classification",
                    "healer": "FileClassificationHealerAgent",
                    "priority": "medium",
                    "estimated_time": 10,
                }
            )
        else:
            # Default: manual review
            alignments.append(
                {
                    "finding": finding,
                    "strategy": "manual_review",
                    "healer": None,
                    "priority": "low",
                    "estimated_time": 5,
                }
            )

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    alignments.sort(key=lambda a: priority_order.get(a.get("priority", "low"), 3))

    return alignments


def execute_phase4_architectural_validation(findings: list[dict], alignments: list[dict]) -> dict[str, Any]:
    """Execute Phase 4 architectural validation.

    Args:
        findings: Original findings
        alignments: Generated alignments

    Returns:
        Validation results
    """
    validated = []
    rejected = []

    for alignment in alignments:
        finding = alignment.get("finding", {})
        strategy = alignment.get("strategy", "")

        # Validation logic
        if strategy == "manual_review":
            # Always accept manual review items
            validated.append(alignment)
        elif finding.get("severity") == "critical":
            # Require explicit approval for critical items
            alignment["requires_approval"] = True
            validated.append(alignment)
        else:
            # Auto-validate non-critical items
            validated.append(alignment)

    return {
        "phase": "validation",
        "validated": validated,
        "rejected": rejected,
        "total_validated": len(validated),
        "total_rejected": len(rejected),
        "success": True,
    }


def execute_phase5_healing(
    alignments: list[dict], project_root: str, dry_run: bool = False
) -> dict[str, Any]:
    """Execute Phase 5 healing actions.

    Args:
        alignments: List of validated alignments
        project_root: Project root directory
        dry_run: If True, don't actually execute healing

    Returns:
        Healing results
    """
    results = []
    success_count = 0
    failure_count = 0

    for alignment in alignments:
        strategy = alignment.get("strategy", "")
        finding = alignment.get("finding", {})

        if dry_run:
            result = {
                "alignment": alignment,
                "executed": False,
                "dry_run": True,
                "message": "Would execute: " + strategy,
            }
            results.append(result)
            success_count += 1
            continue

        # Execute based on strategy
        try:
            if strategy == "heal_ssot":
                from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (
                    FilesystemSSOTReconcilerAgent,
                )

                reconciler = FilesystemSSOTReconcilerAgent(project_root=project_root)
                heal_result = reconciler.heal_repository(dry_run=False, execute=True, force=True)
                result = {
                    "alignment": alignment,
                    "executed": True,
                    "success": heal_result.get("success", True),
                    "applied": heal_result.get("applied", 0),
                    "method": "FilesystemSSOTReconcilerAgent",
                }
            elif strategy == "heal_location":
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

                file_path = finding.get("file", "")
                healer = LocationHealerAgent(project_root=project_root)
                heal_result = healer.heal_file(file_path) if file_path else {"success": False}
                result = {
                    "alignment": alignment,
                    "executed": True,
                    "success": heal_result.get("success", True),
                    "file": file_path,
                    "method": "LocationHealerAgent",
                }
            elif strategy == "heal_classification":
                from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
                    FileClassificationHealerAgent,
                )

                file_path = finding.get("file", "")
                healer = FileClassificationHealerAgent(project_root=project_root)
                heal_result = healer.heal_file(file_path) if file_path else {"success": False}
                result = {
                    "alignment": alignment,
                    "executed": True,
                    "success": heal_result.get("success", True),
                    "file": file_path,
                    "method": "FileClassificationHealerAgent",
                }
            else:
                result = {
                    "alignment": alignment,
                    "executed": False,
                    "success": True,
                    "message": "Skipped (manual review or unknown strategy)",
                }

            results.append(result)
            if result.get("success"):
                success_count += 1
            else:
                failure_count += 1

        except Exception as e:
            results.append({"alignment": alignment, "executed": False, "success": False, "error": str(e)})
            failure_count += 1

    return {
        "phase": "healing",
        "results": results,
        "success_count": success_count,
        "failure_count": failure_count,
        "total": len(results),
        "success": failure_count == 0 or success_count > failure_count,
    }


def _get_retrieval_telemetry(query: str, tier: str) -> dict[str, Any]:
    """Get telemetry data for a retrieval operation.

    Args:
        query: The retrieval query
        tier: The tier being queried (L0-L5)

    Returns:
        Telemetry data dictionary
    """
    return {"query": query, "tier": tier, "cache_hit": False, "latency_ms": 0, "timestamp": 0}


def _multi_tier_retrieval(
    query: str, project_root: str, tiers: list[str] | None = None
) -> list[dict[str, Any]]:
    """Perform multi-tier retrieval across L0-L5.

    Args:
        query: The retrieval query
        project_root: Project root directory
        tiers: List of tiers to query (defaults to all)

    Returns:
        List of retrieval results from each tier
    """
    if tiers is None:
        tiers = ["L0", "L1", "L2", "L3", "L4", "L5"]

    results = []
    for tier in tiers:
        try:
            # Check cache first
            cache_key = f"{tier}:{query}"
            if cache_key in RETRIEVAL_CACHE:
                results.append({"tier": tier, "result": RETRIEVAL_CACHE[cache_key], "cached": True})
                continue

            # Placeholder for actual tier retrieval
            result = {"tier": tier, "query": query, "status": "not_implemented"}
            results.append(result)

        except Exception as e:
            results.append({"tier": tier, "error": str(e), "status": "error"})

    return results


def _store_in_retrieval_cache(key: str, value: Any, ttl_seconds: int = 3600) -> bool:
    """Store a value in the retrieval cache.

    Args:
        key: Cache key
        value: Value to store
        ttl_seconds: Time-to-live in seconds

    Returns:
        True if stored successfully
    """
    RETRIEVAL_CACHE[key] = {
        "value": value,
        "ttl": ttl_seconds,
        "stored_at": 0,  # Would use actual timestamp
    }
    return True


# Healing Outcome Event for meta-learning
@dataclass
class HealingOutcomeEvent:
    """Event representing a healing outcome."""

    healer_id: str
    tier: str
    failure_type: str
    success: bool
    timestamp_utc: int


class HealingOutcomeAggregator:
    """Aggregates healing outcome events for meta-learning."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self._events: list = []

    def ingest(self, event: HealingOutcomeEvent) -> None:
        """Add an event to the aggregator."""
        self._events.append(event)
        # Trim to window size
        if len(self._events) > self.window_size:
            self._events = self._events[-self.window_size :]

    def snapshot(self) -> dict:
        """Return a deterministic snapshot of aggregated outcomes."""
        if not self._events:
            return {
                "window_size": self.window_size,
                "event_count": 0,
                "success_rate": 0.0,
                "by_tier": {},
                "by_failure_type": {},
            }

        # Calculate statistics
        success_count = sum(1 for e in self._events if e.success)
        by_tier: dict[str, dict] = {}
        by_failure_type: dict[str, dict] = {}

        for event in self._events:
            # Tier aggregation
            if event.tier not in by_tier:
                by_tier[event.tier] = {"total": 0, "success": 0}
            by_tier[event.tier]["total"] += 1
            if event.success:
                by_tier[event.tier]["success"] += 1

            # Failure type aggregation
            if event.failure_type not in by_failure_type:
                by_failure_type[event.failure_type] = {"total": 0, "success": 0}
            by_failure_type[event.failure_type]["total"] += 1
            if event.success:
                by_failure_type[event.failure_type]["success"] += 1

        return {
            "window_size": self.window_size,
            "event_count": len(self._events),
            "success_rate": success_count / len(self._events),
            "by_tier": by_tier,
            "by_failure_type": by_failure_type,
        }


@dataclass
class HealingOutcomeRecord:
    """Record of healing outcomes for storage."""

    schema_version: str
    created_utc: int
    window_size: int
    snapshot: dict
    proposal: dict


class InMemoryHealingOutcomeIntakeStore:
    """In-memory store for healing outcome records."""

    def __init__(self):
        self._records: list[HealingOutcomeRecord] = []

    def store(self, record: HealingOutcomeRecord) -> None:
        """Store a healing outcome record."""
        self._records.append(record)

    def get_all(self) -> list[HealingOutcomeRecord]:
        """Get all stored records."""
        return self._records.copy()


class HealingOutcomeIntakeAdapter:
    """Adapter for building healing outcome records."""

    def __init__(self, store: InMemoryHealingOutcomeIntakeStore):
        self._store = store

    def build_record(
        self,
        aggregator: HealingOutcomeAggregator,
        created_utc: int,
        source: str,
    ) -> HealingOutcomeRecord:
        """Build a healing outcome record from an aggregator."""
        snapshot = aggregator.snapshot()

        # Generate proposal based on outcomes
        proposal = self._generate_proposal(snapshot, source)

        record = HealingOutcomeRecord(
            schema_version="1.0",
            created_utc=created_utc,
            window_size=snapshot["window_size"],
            snapshot=snapshot,
            proposal=proposal,
        )

        # Store the record
        self._store.store(record)

        return record

    def _generate_proposal(self, snapshot: dict, source: str) -> dict:
        """Generate a meta-learning proposal from snapshot data."""
        if snapshot["event_count"] == 0:
            return {"action": "none", "reason": "no_events"}

        # Simple proposal logic based on success rate
        success_rate = snapshot["success_rate"]
        if success_rate < 0.5:
            return {"action": "investigate", "reason": "low_success_rate", "target": source}
        elif success_rate < 0.8:
            return {"action": "monitor", "reason": "moderate_success_rate"}
        else:
            return {"action": "continue", "reason": "high_success_rate"}


class SovereignDecisionEngine:
    """Main orchestration engine for compliance and healing workflows.

    This class coordinates all phases of execution:
    1. Discovery - Find issues across layers
    2. Validation - Verify findings
    3. Alignment - Determine healing strategy
    4. Healing - Execute healing actions
    5. Reporting - Generate execution reports
    """

    def __init__(self, registry: Any, args: Any, console: Any = None):
        self.registry = registry
        self.args = args
        self.console = console
        self.phase_results: dict[str, Any] = {}
        self.heal_context: Any = None
        self.checkpoints: list[dict] = []
        self.logger = logging.getLogger(__name__)

    def run_discovery_phase(self, context: Any) -> tuple[bool, Any]:
        """Run the discovery phase to find issues using registered agents.

        Returns:
            Tuple of (success, findings)
        """
        self.logger.info("Starting discovery phase")
        findings = []

        if not self.registry:
            self.logger.error("No registry available for discovery")
            return False, []

        # Convert registry list to dict by agent key if needed
        agents = self.registry
        if isinstance(agents, list):
            agents = {a.get("class_name", a.get("name", f"agent_{i}")): a for i, a in enumerate(agents)}

        try:
            # Phase 1: Filesystem SSOT validation
            print("[DISCOVERY] Running FilesystemSSOTValidatorAgent...")
            try:
                from agentic_core.L5_safety.reasoning.filesystem_ssot_validator import (
                    FilesystemSSOTValidatorAgent,
                )

                fs_validator = FilesystemSSOTValidatorAgent(
                    project_root=context.targets[0] if context.targets else "."
                )
                fs_check = fs_validator.to_check_dict()
                drift_report = fs_check.get("evidence", {})
                violations_count = fs_check.get("violations_count", 0)
                if violations_count > 0:
                    findings.append(
                        {
                            "agent": "FilesystemSSOTValidatorAgent",
                            "type": "ssot_drift",
                            "severity": "high" if violations_count > 5 else "medium",
                            "violations_count": violations_count,
                            "drift_report": drift_report,
                            "valid": True,
                        }
                    )
                print(f"[DISCOVERY] FilesystemSSOTValidatorAgent: {violations_count} violations found")
            except Exception as e:
                self.logger.warning(f"FilesystemSSOTValidatorAgent failed: {e}")

            # Phase 2: Location validation for each target
            print("[DISCOVERY] Running LocationValidatorAgent...")
            try:
                from pathlib import Path

                from agentic_core.L5_safety.reasoning.location_validator import LocationValidatorAgent

                for target in context.targets or ["."]:
                    target_path = Path(target).resolve()
                    if target_path.exists():
                        location_validator = LocationValidatorAgent(project_root=target)
                        scan_result = location_validator.run(target_territory=str(target_path))
                        violations = scan_result.get("violations", [])
                        if violations:
                            findings.extend(
                                [
                                    {
                                        "agent": "LocationValidatorAgent",
                                        "type": "location_violation",
                                        "severity": v.get("severity", "medium"),
                                        "file": v.get("file"),
                                        "message": v.get("message", ""),
                                        "valid": True,
                                    }
                                    for v in violations
                                ]
                            )
                        print(
                            f"[DISCOVERY] LocationValidatorAgent for {target}: {len(violations)} violations"
                        )
            except Exception as e:
                self.logger.warning(f"LocationValidatorAgent failed: {e}")

            # Phase 3: File classification scan
            print("[DISCOVERY] Running FileClassificationAgent...")
            try:
                from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

                for target in context.targets or ["."]:
                    fc_agent = FileClassificationAgent(project_root=target)
                    if hasattr(fc_agent, "scan"):
                        scan_results = fc_agent.scan(target_path=target)
                        issues = scan_results.get("issues", [])
                        if issues:
                            findings.extend(
                                [
                                    {
                                        "agent": "FileClassificationAgent",
                                        "type": "classification_issue",
                                        "severity": i.get("severity", "medium"),
                                        "file": i.get("file"),
                                        "message": i.get("message", ""),
                                        "valid": True,
                                    }
                                    for i in issues
                                ]
                            )
                        print(f"[DISCOVERY] FileClassificationAgent for {target}: {len(issues)} issues")
            except Exception as e:
                self.logger.warning(f"FileClassificationAgent failed: {e}")

            self.logger.info(f"Discovery found {len(findings)} total issues")
            print(f"[DISCOVERY] Total findings: {len(findings)}")
            return True, findings

        except Exception as e:
            self.logger.error(f"Discovery failed: {e}")
            return False, []

    def run_validation_phase(self, context: Any, findings: list) -> tuple[bool, Any]:
        """Validate discovered issues using extracted validation function."""
        self.logger.info(f"Starting validation phase with {len(findings)} findings")
        try:
            # Call extracted validation function
            result = execute_phase4_architectural_validation(findings, [])
            validated = result.get("validated", [])
            self.logger.info(f"Validated {len(validated)} findings")
            return True, validated
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return False, []

    def _validate_finding(self, finding: Any) -> bool:
        """Validate a single finding."""
        # Basic validation logic
        if finding is None:
            return False
        if isinstance(finding, dict):
            return bool(finding.get("valid", True))
        return True

    def run_alignment_phase(self, context: Any, validated: list) -> tuple[bool, Any]:
        """Determine healing strategy using extracted alignment function."""
        self.logger.info(f"Starting alignment phase with {len(validated)} validated issues")
        try:
            # Call extracted alignment function
            alignments = execute_phase3_alignment(validated)
            self.logger.info(f"Created {len(alignments)} alignment strategies")
            return True, alignments
        except Exception as e:
            self.logger.error(f"Alignment failed: {e}")
            return False, []

    def _determine_healing_strategy(self, issue: Any) -> dict | None:
        """Determine the healing strategy for an issue."""
        if isinstance(issue, dict):
            return {
                "issue": issue,
                "strategy": issue.get("suggested_fix", "manual_review"),
                "priority": issue.get("priority", "medium"),
            }
        return {"issue": issue, "strategy": "manual_review", "priority": "medium"}

    def run_healing_phase(self, context: Any, alignments: list) -> tuple[bool, Any]:
        """Execute healing actions using extracted healing function."""
        self.logger.info(f"Starting healing phase with {len(alignments)} alignments")
        try:
            # Call extracted healing function with dry_run from args
            dry_run = getattr(self.args, 'dry_run', True)
            project_root = context.targets[0] if context.targets else "."
            result = execute_phase5_healing(alignments, project_root, dry_run=dry_run)
            results = result.get("results", [])
            all_success = result.get("success_count", 0) == result.get("total", 0)
            self.logger.info(f"Healing completed: {result.get('success_count', 0)}/{result.get('total', 0)} succeeded")
            return all_success, results
        except Exception as e:
            self.logger.error(f"Healing failed: {e}")
            return False, []

    def _execute_healing(self, alignment: dict) -> dict:
        """Execute a single healing action using the appropriate agent."""
        try:
            issue = alignment.get("issue", {})
            agent_name = issue.get("agent", "")
            issue_type = issue.get("type", "")

            # Route to appropriate healer based on agent/issue type
            if "ssot" in issue_type or "FilesystemSSOT" in agent_name:
                return self._heal_ssot_drift(issue)
            elif "location" in issue_type or "Location" in agent_name:
                return self._heal_location_violation(issue)
            elif "classification" in issue_type or "FileClassification" in agent_name:
                return self._heal_classification_issue(issue)
            else:
                # Default: mark for manual review
                return {
                    "success": True,
                    "alignment": alignment,
                    "method": "manual_review",
                    "requires_review": True,
                    "message": f"No auto-healer available for {agent_name}",
                }

        except Exception as e:
            return {"success": False, "alignment": alignment, "error": str(e)}

    def _heal_ssot_drift(self, issue: dict) -> dict:
        """Heal SSOT drift using FilesystemSSOTReconcilerAgent."""
        try:
            from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (
                FilesystemSSOTReconcilerAgent,
            )

            project_root = self.heal_context.targets[0] if self.heal_context.targets else "."
            reconciler = FilesystemSSOTReconcilerAgent(project_root=project_root)

            # Run reconciliation
            result = reconciler.heal_repository(dry_run=False, execute=True, force=True)

            return {
                "success": result.get("success", True),
                "method": "FilesystemSSOTReconcilerAgent",
                "applied": result.get("applied", 0),
                "skipped": result.get("skipped", 0),
                "message": f"SSOT reconciliation: {result.get('applied', 0)} applied",
            }
        except Exception as e:
            return {"success": False, "method": "FilesystemSSOTReconcilerAgent", "error": str(e)}

    def _heal_location_violation(self, issue: dict) -> dict:
        """Heal location violations using LocationHealerAgent."""
        try:
            from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

            project_root = self.heal_context.targets[0] if self.heal_context.targets else "."
            healer = LocationHealerAgent(project_root=project_root)

            file_path = issue.get("file", "")
            if file_path:
                result = healer.heal_file(file_path)
                return {
                    "success": result.get("success", True),
                    "method": "LocationHealerAgent",
                    "file": file_path,
                    "message": result.get("message", "Healed location violation"),
                }
            else:
                return {"success": False, "method": "LocationHealerAgent", "error": "No file specified"}
        except Exception as e:
            return {"success": False, "method": "LocationHealerAgent", "error": str(e)}

    def _heal_classification_issue(self, issue: dict) -> dict:
        """Heal classification issues using FileClassificationHealerAgent."""
        try:
            from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationHealerAgent

            project_root = self.heal_context.targets[0] if self.heal_context.targets else "."
            healer = FileClassificationHealerAgent(project_root=project_root)

            file_path = issue.get("file", "")
            if file_path:
                result = healer.heal_file(file_path)
                return {
                    "success": result.get("success", True),
                    "method": "FileClassificationHealerAgent",
                    "file": file_path,
                    "message": result.get("message", "Healed classification issue"),
                }
            else:
                return {
                    "success": False,
                    "method": "FileClassificationHealerAgent",
                    "error": "No file specified",
                }
        except Exception as e:
            return {"success": False, "method": "FileClassificationHealerAgent", "error": str(e)}

    def run_reporting_phase(self, context: Any, results: Any) -> tuple[bool, Any]:
        """Generate execution reports.

        Returns:
            Tuple of (success, report)
        """
        self.logger.info("Starting reporting phase")

        try:
            report = {
                "phases_completed": list(self.phase_results.keys()),
                "total_phases": 5,
                "healing_results": results,
                "summary": self._generate_summary(results),
            }

            return True, report
        except Exception as e:
            self.logger.error(f"Reporting failed: {e}")
            return False, {}

    def _generate_summary(self, results: Any) -> dict:
        """Generate a summary of results."""
        if isinstance(results, list):
            successes = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
            failures = len(results) - successes
            return {
                "total": len(results),
                "successes": successes,
                "failures": failures,
            }
        return {"total": 1, "status": "unknown"}

    def execute_full_workflow(self, targets: Any) -> tuple[bool, Any]:
        """Execute the complete compliance and healing workflow.

        Args:
            targets: Targets to heal/validate

        Returns:
            Tuple of (overall_success, final_results)
        """
        # PTC: Workflow initialization
        _emit_records_execution_trace(str(id(self)), LayerSegment.L2_EXECUTION, "execute_ssot.workflow.init")
        # Initialize heal context
        from .execute_ssot_context import HealContext

        self.heal_context = HealContext(targets=targets, registry=self.registry, args=self.args)

        # Phase 1: Discovery
        _emit_records_execution_trace(
            str(id(self)), LayerSegment.L1_REASONING, "execute_ssot.phase.discovery.start"
        )
        try:
            success, findings = self.run_discovery_phase(self.heal_context)
            _emit_records_execution_trace(
                str(id(self)),
                LayerSegment.L1_REASONING,
                f"execute_ssot.phase.discovery.end:success={success}",
            )
            if not success:
                return False, {
                    "phase": "discovery",
                    "error": "Discovery failed",
                    "context": self.heal_context,
                }
            self.heal_context.record_phase_result("discovery", findings)
        except Exception as e:
            return False, {
                "phase": "discovery",
                "error": f"Discovery exception: {str(e)}",
                "context": self.heal_context,
            }

        # Phase 2: Validation
        _emit_records_execution_trace(
            str(id(self)), LayerSegment.L1_REASONING, "execute_ssot.phase.validation.start"
        )
        try:
            success, validated = self.run_validation_phase(self.heal_context, findings)
            _emit_records_execution_trace(
                str(id(self)),
                LayerSegment.L1_REASONING,
                f"execute_ssot.phase.validation.end:success={success}",
            )
            if not success:
                return False, {
                    "phase": "validation",
                    "error": "Validation failed",
                    "context": self.heal_context,
                }
            self.heal_context.record_phase_result("validation", validated)
        except Exception as e:
            return False, {
                "phase": "validation",
                "error": f"Validation exception: {str(e)}",
                "context": self.heal_context,
            }

        # Phase 3: Alignment
        _emit_records_execution_trace(
            str(id(self)), LayerSegment.L3_ORCHESTRATION, "execute_ssot.phase.alignment.start"
        )
        try:
            success, alignments = self.run_alignment_phase(self.heal_context, validated)
            _emit_records_execution_trace(
                str(id(self)),
                LayerSegment.L3_ORCHESTRATION,
                f"execute_ssot.phase.alignment.end:success={success}",
            )
            if not success:
                return False, {
                    "phase": "alignment",
                    "error": "Alignment failed",
                    "context": self.heal_context,
                }
            self.heal_context.record_phase_result("alignment", alignments)
        except Exception as e:
            return False, {
                "phase": "alignment",
                "error": f"Alignment exception: {str(e)}",
                "context": self.heal_context,
            }

        # Phase 4: Healing
        _emit_records_execution_trace(
            str(id(self)), LayerSegment.L2_EXECUTION, "execute_ssot.phase.healing.start"
        )
        try:
            success, healing_results = self.run_healing_phase(self.heal_context, alignments)
            _emit_records_execution_trace(
                str(id(self)), LayerSegment.L2_EXECUTION, f"execute_ssot.phase.healing.end:success={success}"
            )
            if not success:
                return False, {"phase": "healing", "error": "Healing failed", "context": self.heal_context}
            self.heal_context.record_phase_result("healing", healing_results)
        except Exception as e:
            return False, {
                "phase": "healing",
                "error": f"Healing exception: {str(e)}",
                "context": self.heal_context,
            }

        # Phase 5: Reporting
        _emit_records_execution_trace(
            str(id(self)), LayerSegment.L4_STATE, "execute_ssot.phase.reporting.start"
        )
        try:
            success, report = self.run_reporting_phase(self.heal_context, healing_results)
            _emit_records_execution_trace(
                str(id(self)), LayerSegment.L4_STATE, f"execute_ssot.phase.reporting.end:success={success}"
            )
            self.heal_context.record_phase_result("reporting", report)
        except Exception as e:
            return False, {
                "phase": "reporting",
                "error": f"Reporting exception: {str(e)}",
                "context": self.heal_context,
            }

        # PTC: Workflow completion
        _emit_records_execution_trace(
            str(id(self)), LayerSegment.L2_EXECUTION, "execute_ssot.workflow.complete"
        )
        return True, {
            "heal_context": self.heal_context,
            "phase_results": self.heal_context.phase_results,
            "final_report": report,
        }

    def save_checkpoint(self) -> None:
        """Save current state as checkpoint for recovery."""
        checkpoint = {"phase_results": self.phase_results.copy(), "heal_context": self.heal_context}
        self.checkpoints.append(checkpoint)
        self.logger.info(f"Checkpoint saved ({len(self.checkpoints)} total)")

    def restore_checkpoint(self, index: int = -1) -> bool:
        """Restore state from a checkpoint.

        Args:
            index: Checkpoint index (-1 for latest)

        Returns:
            True if restore successful
        """
        if not self.checkpoints:
            self.logger.warning("No checkpoints available")
            return False
        try:
            checkpoint = self.checkpoints[index]
            self.phase_results = checkpoint["phase_results"]
            self.heal_context = checkpoint["heal_context"]
            self.logger.info(f"Restored checkpoint {index if index >= 0 else len(self.checkpoints) + index}")
            return True
        except (IndexError, KeyError) as e:
            self.logger.error(f"Failed to restore checkpoint: {e}")
            return False

    def get_execution_status(self) -> dict[str, Any]:
        """Get current execution status."""
        return {
            "phases_completed": len(self.phase_results),
            "checkpoints_available": len(self.checkpoints),
            "has_context": self.heal_context is not None,
            "phase_names": list(self.phase_results.keys()),
        }

    def reset_call_path(self) -> None:
        """Reset the call path tracking."""
        self.logger.debug("Call path reset")
