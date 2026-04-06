"""ADG Repair Orchestrator - Main orchestration class.

Coordinates deficiency detection, categorization, and repair.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add repo root to path for imports
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_records_execution_trace,
)

from .base_rule import BaseRepairRule
from .rule_engine import RuleEngine, register_builtin_rules
from .types import Deficiency, FixCategory, FixResult, RepairRunResult

_emit_records_execution_trace("p0", "repair", "orchestrator_init")
_emit_applies_guardrail("p0", "repair_orchestrator", "safety_check")


class ADGRepairOrchestrator:
    """Orchestrates ADG repair operations.

    This class coordinates:
    1. Loading and analyzing ADG reports
    2. Detecting deficiencies from multiple sources
    3. Categorizing deficiencies (AUTO_FIX, SUGGEST_FIX, BLOCK_FIX)
    4. Matching rules to deficiencies
    5. Executing fixes with rollback support
    6. Logging all operations deterministically

    Usage:
        orchestrator = ADGRepairOrchestrator(
            adg_dir=Path("artifacts/adg"),
            timestamp="03122026_0512"
        )
        result = orchestrator.run(dry_run=True)
    """

    def __init__(
        self,
        adg_dir: Path,
        timestamp: str,
        repo_root: Path | None = None,
    ):
        """Initialize the repair orchestrator.

        Args:
            adg_dir: Directory containing ADG artifacts
            timestamp: ADG timestamp (MMDDYYYY_HHMM format)
            repo_root: Repository root path (default: auto-detect)
        """
        self.adg_dir = Path(adg_dir)
        self.timestamp = timestamp
        self.repo_root = repo_root or ROOT

        # Initialize components
        self.rule_engine = RuleEngine()
        self.deficiencies: list[Deficiency] = []
        self.results: RepairRunResult | None = None

        # Logging
        self.log: list[dict[str, Any]] = []
        self.log_path: Path | None = None

        # Register built-in rules
        register_builtin_rules()

        self._log_event(
            "orchestrator_init",
            {
                "adg_dir": str(self.adg_dir),
                "timestamp": self.timestamp,
                "repo_root": str(self.repo_root),
            },
        )

    def _log_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Log an event with timestamp.

        Args:
            event_type: Type of event
            data: Event data dictionary
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            **data,
        }
        self.log.append(event)

    def load_reports(self) -> dict[str, Any]:
        """Load all ADG reports for analysis.

        Returns:
            Dictionary mapping report names to parsed data
        """
        reports = {}
        report_files = [
            ("closure", f"closure_validation_report_{self.timestamp}.json"),
            ("layer", f"layer_coverage_report_{self.timestamp}.json"),
            ("edge", f"edge_density_report_{self.timestamp}.json"),
            ("provenance", f"provenance_report_{self.timestamp}.json"),
            ("determinism", f"replay_determinism_report_{self.timestamp}.json"),
            ("boundary", f"boundary_report_{self.timestamp}.json"),
            ("mutation", f"mutation_integrity_report_{self.timestamp}.json"),
        ]

        for report_name, filename in report_files:
            report_path = self.adg_dir / filename
            if report_path.exists():
                try:
                    with open(report_path, encoding="utf-8") as f:
                        reports[report_name] = json.load(f)
                    self._log_event(
                        "report_loaded",
                        {
                            "report_name": report_name,
                            "file": filename,
                        },
                    )
                except (json.JSONDecodeError, OSError) as e:
                    self._log_event(
                        "report_load_failed",
                        {
                            "report_name": report_name,
                            "file": filename,
                            "error": str(e),
                        },
                    )
            else:
                self._log_event(
                    "report_missing",
                    {
                        "report_name": report_name,
                        "file": filename,
                    },
                )

        return reports

    def detect_deficiencies(self, reports: dict[str, Any] | None = None) -> list[Deficiency]:
        """Detect deficiencies from reports.

        Args:
            reports: Pre-loaded reports (optional, will load if not provided)

        Returns:
            List of detected deficiencies
        """
        if reports is None:
            reports = self.load_reports()

        self.deficiencies = []

        # Extract deficiencies from closure report
        if "closure" in reports:
            self._extract_closure_deficiencies(reports["closure"])

        # Extract deficiencies from layer report
        if "layer" in reports:
            self._extract_layer_deficiencies(reports["layer"])

        # Extract deficiencies from edge report
        if "edge" in reports:
            self._extract_edge_deficiencies(reports["edge"])

        # Extract deficiencies from determinism report
        if "determinism" in reports:
            self._extract_determinism_deficiencies(reports["determinism"])

        # Extract deficiencies from boundary report
        if "boundary" in reports:
            self._extract_boundary_deficiencies(reports["boundary"])

        # Extract deficiencies from mutation report
        if "mutation" in reports:
            self._extract_mutation_deficiencies(reports["mutation"])

        self._log_event(
            "deficiencies_detected",
            {
                "count": len(self.deficiencies),
                "auto_fix": sum(1 for d in self.deficiencies if d.category == FixCategory.AUTO_FIX),
                "suggest_fix": sum(1 for d in self.deficiencies if d.category == FixCategory.SUGGEST_FIX),
                "block_fix": sum(1 for d in self.deficiencies if d.category == FixCategory.BLOCK_FIX),
            },
        )

        return self.deficiencies

    def _extract_closure_deficiencies(self, report: dict[str, Any]) -> None:
        """Extract deficiencies from closure validation report."""
        rows = report.get("closure_rows", [])

        for row in rows:
            if not row.get("passed", True):
                capability = row.get("capability", "UNKNOWN")
                ratio = row.get("ratio", 0.0)

                # Determine category based on capability type
                category = FixCategory.BLOCK_FIX  # Default to requiring human

                if capability in ("EDGE SEMANTIC PRECISION", "NODE GRANULARITY"):
                    category = FixCategory.AUTO_FIX
                elif capability in ("STRUCTURAL COVERAGE", "DATA LINEAGE"):
                    category = FixCategory.SUGGEST_FIX

                deficiency = Deficiency(
                    id=f"closure_{capability.lower().replace(' ', '_')}",
                    category=category,
                    file_path="ADG_METADATA",
                    line_no=None,
                    issue_type=f"closure_fail_{capability.lower().replace(' ', '_')}",
                    description=f"Closure validation failed for {capability}: {ratio:.2%}",
                    confidence=0.9 if category == FixCategory.AUTO_FIX else 0.7,
                    metadata={
                        "capability": capability,
                        "ratio": ratio,
                        "threshold": row.get("threshold"),
                        "evidence": row.get("evidence"),
                    },
                )
                self.deficiencies.append(deficiency)

    def _extract_layer_deficiencies(self, report: dict[str, Any]) -> None:
        """Extract deficiencies from layer coverage report."""
        unknown_modules = report.get("unknown_modules", [])
        coverage_pct = report.get("coverage_metrics", {}).get("coverage_percentage", 100.0)

        # If coverage is very low, this is a suggest-level issue
        if coverage_pct < 50.0:
            deficiency = Deficiency(
                id="layer_low_coverage",
                category=FixCategory.SUGGEST_FIX,
                file_path="ADG_METADATA",
                line_no=None,
                issue_type="layer_low_coverage",
                description=f"Layer coverage is only {coverage_pct:.1f}%",
                confidence=0.8,
                metadata={"coverage_percentage": coverage_pct},
            )
            self.deficiencies.append(deficiency)

        # Each unknown module can potentially be auto-fixed
        for module in unknown_modules[:50]:  # Limit to first 50
            module_path = module.get("resolved_path", "")
            if not module_path:
                continue

            # Check if layer is inferrable from path
            inferred_layer = self._infer_layer_from_path(module_path)

            deficiency = Deficiency(
                id=f"unknown_layer_{module_path.replace('/', '_').replace('.', '_')}",
                category=FixCategory.AUTO_FIX if inferred_layer else FixCategory.SUGGEST_FIX,
                file_path=module_path,
                line_no=1,
                issue_type="unknown_layer",
                description=f"Module has unknown layer (inferred: {inferred_layer or 'none'})",
                suggested_fix=f"# Layer: {inferred_layer}" if inferred_layer else None,
                confidence=0.85 if inferred_layer else 0.6,
                metadata={
                    "adg_name": module.get("adg_name"),
                    "inferred_layer": inferred_layer,
                },
            )
            self.deficiencies.append(deficiency)

    def _extract_edge_deficiencies(self, report: dict[str, Any]) -> None:
        """Extract deficiencies from edge density report."""
        critical_coverage = report.get("critical_edge_coverage", {})

        for edge_type, count in critical_coverage.items():
            if count == 0:
                deficiency = Deficiency(
                    id=f"missing_critical_edge_{edge_type}",
                    category=FixCategory.BLOCK_FIX,  # Requires human engineering
                    file_path="ADG_METADATA",
                    line_no=None,
                    issue_type="missing_critical_edge",
                    description=f"Critical edge type '{edge_type}' has 0 instances",
                    confidence=0.5,  # Low confidence for auto-fix
                    metadata={"edge_type": edge_type, "count": count},
                )
                self.deficiencies.append(deficiency)

    def _extract_determinism_deficiencies(self, report: dict[str, Any]) -> None:
        """Extract deficiencies from determinism report."""
        determinism_status = report.get("validation", {}).get("determinism_status", "unknown")

        if determinism_status != "closed":
            proof = report.get("proof", {})

            # Check which digests failed
            failed_checks = []
            for key in [
                "scanner_digest_match",
                "artifact_digest_match",
                "node_row_digest_match",
                "edge_row_digest_match",
            ]:
                if not proof.get(key, False):
                    failed_checks.append(key)

            if failed_checks:
                deficiency = Deficiency(
                    id=f"determinism_fail_{determinism_status}",
                    category=FixCategory.BLOCK_FIX,  # Cannot auto-fix determinism issues
                    file_path="ADG_METADATA",
                    line_no=None,
                    issue_type="determinism_failure",
                    description=f"Determinism check failed: {', '.join(failed_checks)}",
                    confidence=0.3,  # Very low confidence for auto-fix
                    metadata={
                        "determinism_status": determinism_status,
                        "failed_checks": failed_checks,
                        "proof": proof,
                    },
                )
                self.deficiencies.append(deficiency)

    def _extract_boundary_deficiencies(self, report: dict[str, Any]) -> None:
        """Extract deficiencies from boundary report."""
        unresolved = report.get("boundary_metrics", {}).get("total_unresolved", 0)

        if unresolved > 0:
            deficiency = Deficiency(
                id=f"boundary_unresolved_{unresolved}",
                category=FixCategory.SUGGEST_FIX,  # May be auto-fixable with import analysis
                file_path="ADG_METADATA",
                line_no=None,
                issue_type="unresolved_boundary_imports",
                description=f"{unresolved} unresolved boundary imports detected",
                confidence=0.7,
                metadata={"unresolved_count": unresolved},
            )
            self.deficiencies.append(deficiency)

    def _extract_mutation_deficiencies(self, report: dict[str, Any]) -> None:
        """Extract deficiencies from mutation integrity report."""
        signature_coverage = report.get("signature_coverage", {})
        coverage_pct = signature_coverage.get("coverage_percentage", 100.0)

        if coverage_pct < 90.0:
            deficiency = Deficiency(
                id="mutation_low_signature_coverage",
                category=FixCategory.AUTO_FIX,  # Can add missing signatures
                file_path="ADG_METADATA",
                line_no=None,
                issue_type="low_mutation_signature_coverage",
                description=f"Mutation signature coverage is only {coverage_pct:.1f}%",
                confidence=0.8,
                metadata={
                    "coverage_percentage": coverage_pct,
                    "modules_with_signatures": signature_coverage.get("modules_with_signatures", 0),
                    "total_modules": signature_coverage.get("total_modules", 0),
                },
            )
            self.deficiencies.append(deficiency)

    def _infer_layer_from_path(self, path: str) -> str | None:
        """Infer layer from file path.

        Args:
            path: File path

        Returns:
            Inferred layer (L0-L6, L_APP) or None
        """
        path_lower = path.lower()

        # Check for layer prefixes
        for layer in ("L0", "L1", "L2", "L3", "L4", "L5", "L6"):
            if f"/{layer}_" in path_lower or f"\\{layer}_" in path_lower:
                return layer

        # Check for apps
        for app_prefix in (
            "apps_eval",
            "apps_exec",
            "apps_lic",
            "apps_research",
            "apps_rfp",
            "apps_rg",
            "apps_shared",
        ):
            if path_lower.startswith(app_prefix) or f"/{app_prefix}" in path_lower:
                return "L_APP"

        return None

    def match_rules(self) -> dict[str, BaseRepairRule | None]:
        """Match rules to all detected deficiencies.

        Returns:
            Dictionary mapping deficiency IDs to matched rules
        """
        matches = {}

        for deficiency in self.deficiencies:
            if deficiency.category != FixCategory.AUTO_FIX:
                # Only match rules for AUTO_FIX deficiencies
                matches[deficiency.id] = None
                continue

            rule = self.rule_engine.find_best_rule(deficiency)
            matches[deficiency.id] = rule

            self._log_event(
                "rule_matched",
                {
                    "deficiency_id": deficiency.id,
                    "rule_id": rule.rule_id if rule else None,
                    "category": deficiency.category.value,
                },
            )

        return matches

    def run(
        self,
        dry_run: bool = True,
        skip_rules: list[str] | None = None,
    ) -> RepairRunResult:
        """Run the repair orchestrator.

        Args:
            dry_run: If True, only show what would be fixed
            skip_rules: List of rule IDs to skip

        Returns:
            RepairRunResult with full execution details
        """
        self._log_event("run_start", {"dry_run": dry_run})

        # Detect deficiencies
        self.detect_deficiencies()

        # Categorize
        auto_fix_count = sum(1 for d in self.deficiencies if d.category == FixCategory.AUTO_FIX)
        suggest_fix_count = sum(1 for d in self.deficiencies if d.category == FixCategory.SUGGEST_FIX)
        block_fix_count = sum(1 for d in self.deficiencies if d.category == FixCategory.BLOCK_FIX)

        # Match rules
        rule_matches = self.match_rules()

        # Execute fixes (or simulate)
        fix_results: list[FixResult] = []
        applied_count = 0
        failed_count = 0

        if not dry_run:
            for deficiency in self.deficiencies:
                if deficiency.category != FixCategory.AUTO_FIX:
                    continue

                rule = rule_matches.get(deficiency.id)
                if rule is None:
                    continue

                if skip_rules and rule.rule_id in skip_rules:
                    self._log_event(
                        "fix_skipped",
                        {
                            "deficiency_id": deficiency.id,
                            "reason": "rule_skipped",
                        },
                    )
                    continue

                try:
                    # Apply fix
                    result = rule.apply_fix(deficiency)
                    fix_results.append(result)

                    if result.success:
                        applied_count += 1
                        # Verify
                        if not rule.verify_fix(deficiency, result):
                            self._log_event(
                                "fix_verify_failed",
                                {
                                    "deficiency_id": deficiency.id,
                                    "rule_id": rule.rule_id,
                                },
                            )
                    else:
                        failed_count += 1

                except Exception as e:
                    failed_count += 1
                    self._log_event(
                        "fix_exception",
                        {
                            "deficiency_id": deficiency.id,
                            "rule_id": rule.rule_id,
                            "error": str(e),
                        },
                    )

        # Save log
        self.log_path = self._save_log()

        # Build result
        self.results = RepairRunResult(
            timestamp=datetime.now(timezone.utc).isoformat(),
            deficiencies_found=len(self.deficiencies),
            fixes_applied=applied_count if not dry_run else 0,
            fixes_suggested=suggest_fix_count,
            fixes_blocked=block_fix_count,
            failed_fixes=failed_count,
            fix_results=fix_results,
            git_checkpoint=None,  # TODO: Implement git checkpointing
            log_path=str(self.log_path) if self.log_path else None,
        )

        self._log_event(
            "run_complete",
            {
                "deficiencies_found": len(self.deficiencies),
                "auto_fix": auto_fix_count,
                "suggest_fix": suggest_fix_count,
                "block_fix": block_fix_count,
                "applied": applied_count,
                "failed": failed_count,
                "dry_run": dry_run,
            },
        )

        return self.results

    def _save_log(self) -> Path:
        """Save execution log to file.

        Returns:
            Path to saved log file
        """
        log_filename = f"repair_log_{self.timestamp}.json"
        log_path = self.adg_dir / log_filename

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": self.timestamp,
                    "adg_dir": str(self.adg_dir),
                    "events": self.log,
                },
                f,
                indent=2,
            )

        return log_path

    def print_summary(self) -> None:
        """Print a summary of the repair run."""
        if self.results is None:
            print("[ADG Repair] No results available. Run orchestrator first.")
            return

        print("\n" + "=" * 60)
        print("ADG Repair Orchestrator Summary")
        print("=" * 60)
        print(f"Timestamp: {self.results.timestamp}")
        print(f"\nDeficiencies Found: {self.results.deficiencies_found}")
        print(f"  - AUTO_FIX (auto-fixable):     {self.results.fixes_applied + self.results.failed_fixes}")
        print(f"  - SUGGEST_FIX (needs HITL):      {self.results.fixes_suggested}")
        print(f"  - BLOCK_FIX (requires human):    {self.results.fixes_blocked}")

        if self.results.fixes_applied > 0:
            print(f"\nFixes Applied: {self.results.fixes_applied}")
        if self.results.failed_fixes > 0:
            print(f"Fixes Failed: {self.results.failed_fixes}")

        if self.results.log_path:
            print(f"\nDetailed log: {self.results.log_path}")

        print("=" * 60)
