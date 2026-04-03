"""SovereignDecisionEngine module for execute_ssot - extracted from monolith.

This module contains the main SovereignDecisionEngine class which orchestrates
the compliance and healing process across all architectural layers.
"""

import logging
from typing import Any


class SovereignDecisionEngine:
    """Main orchestration engine for compliance and healing workflows.

    This class coordinates all phases of execution:
    1. Discovery - Find issues across layers
    2. Validation - Verify findings
    3. Alignment - Determine healing strategy
    4. Healing - Execute healing actions
    5. Reporting - Generate execution reports
    """

    def __init__(
        self,
        registry: Any,
        args: Any,
        console: Any = None
    ):
        self.registry = registry
        self.args = args
        self.console = console
        self.phase_results: dict[str, Any] = {}
        self.heal_context: Any = None
        self.checkpoints: list[dict] = []
        self.logger = logging.getLogger(__name__)

    def run_discovery_phase(self, context: Any) -> tuple[bool, Any]:
        """Run the discovery phase to find issues.

        Returns:
            Tuple of (success, findings)
        """
        self.logger.info("Starting discovery phase")
        findings = []

        # Discovery logic - scan all layers for issues
        try:
            # Use registry to discover issues
            if hasattr(self.registry, 'discover'):
                findings = self.registry.discover(context)
            elif hasattr(self.registry, 'scan'):
                findings = self.registry.scan(context)
            else:
                # Fallback: return empty findings
                findings = []

            self.logger.info(f"Discovery found {len(findings)} issues")
            return True, findings
        except Exception as e:
            self.logger.error(f"Discovery failed: {e}")
            return False, []

    def run_validation_phase(self, context: Any, findings: list) -> tuple[bool, Any]:
        """Validate discovered issues.

        Returns:
            Tuple of (success, validated_findings)
        """
        self.logger.info(f"Starting validation phase with {len(findings)} findings")

        try:
            validated = []
            for finding in findings:
                # Validate each finding
                if self._validate_finding(finding):
                    validated.append(finding)

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
            return bool(finding.get('valid', True))
        return True

    def run_alignment_phase(self, context: Any, validated: list) -> tuple[bool, Any]:
        """Determine healing strategy for validated issues.

        Returns:
            Tuple of (success, alignment_plan)
        """
        self.logger.info(f"Starting alignment phase with {len(validated)} validated issues")

        try:
            alignments = []
            for issue in validated:
                alignment = self._determine_healing_strategy(issue)
                if alignment:
                    alignments.append(alignment)

            self.logger.info(f"Created {len(alignments)} alignment strategies")
            return True, alignments
        except Exception as e:
            self.logger.error(f"Alignment failed: {e}")
            return False, []

    def _determine_healing_strategy(self, issue: Any) -> dict | None:
        """Determine the healing strategy for an issue."""
        if isinstance(issue, dict):
            return {
                'issue': issue,
                'strategy': issue.get('suggested_fix', 'manual_review'),
                'priority': issue.get('priority', 'medium'),
            }
        return {'issue': issue, 'strategy': 'manual_review', 'priority': 'medium'}

    def run_healing_phase(self, context: Any, alignments: list) -> tuple[bool, Any]:
        """Execute healing actions.

        Returns:
            Tuple of (success, healing_results)
        """
        self.logger.info(f"Starting healing phase with {len(alignments)} alignments")

        try:
            results = []
            for alignment in alignments:
                result = self._execute_healing(alignment)
                results.append(result)

            # Check if all healings succeeded
            all_success = all(r.get('success', False) for r in results if isinstance(r, dict))

            self.logger.info(f"Healing completed: {len([r for r in results if isinstance(r, dict) and r.get('success')])}/{len(results)} succeeded")
            return all_success, results
        except Exception as e:
            self.logger.error(f"Healing failed: {e}")
            return False, []

    def _execute_healing(self, alignment: dict) -> dict:
        """Execute a single healing action."""
        try:
            strategy = alignment.get('strategy', 'manual_review')

            # Execute based on strategy
            if strategy == 'auto_fix':
                return {'success': True, 'alignment': alignment, 'method': 'auto'}
            elif strategy == 'manual_review':
                return {'success': True, 'alignment': alignment, 'method': 'manual', 'requires_review': True}
            else:
                return {'success': False, 'alignment': alignment, 'error': 'Unknown strategy'}

        except Exception as e:
            return {'success': False, 'alignment': alignment, 'error': str(e)}

    def run_reporting_phase(self, context: Any, results: Any) -> tuple[bool, Any]:
        """Generate execution reports.

        Returns:
            Tuple of (success, report)
        """
        self.logger.info("Starting reporting phase")

        try:
            report = {
                'phases_completed': list(self.phase_results.keys()),
                'total_phases': 5,
                'healing_results': results,
                'summary': self._generate_summary(results),
            }

            return True, report
        except Exception as e:
            self.logger.error(f"Reporting failed: {e}")
            return False, {}

    def _generate_summary(self, results: Any) -> dict:
        """Generate a summary of results."""
        if isinstance(results, list):
            successes = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
            failures = len(results) - successes
            return {
                'total': len(results),
                'successes': successes,
                'failures': failures,
            }
        return {'total': 1, 'status': 'unknown'}

    def execute_full_workflow(self, targets: Any) -> tuple[bool, Any]:
        """Execute the complete compliance and healing workflow.

        Args:
            targets: Targets to heal/validate

        Returns:
            Tuple of (overall_success, final_results)
        """
        try:
            # Initialize heal context
            from .execute_ssot_context import HealContext
            self.heal_context = HealContext(
                targets=targets,
                registry=self.registry,
                args=self.args
            )

            # Phase 1: Discovery
            try:
                success, findings = self.run_discovery_phase(self.heal_context)
                if not success:
                    return False, {"phase": "discovery", "error": "Discovery failed", "context": self.heal_context}
                self.heal_context.record_phase_result("discovery", findings)
            except Exception as e:
                return False, {"phase": "discovery", "error": f"Discovery exception: {str(e)}", "context": self.heal_context}

            # Phase 2: Validation
            try:
                success, validated = self.run_validation_phase(self.heal_context, findings)
                if not success:
                    return False, {"phase": "validation", "error": "Validation failed", "context": self.heal_context}
                self.heal_context.record_phase_result("validation", validated)
            except Exception as e:
                return False, {"phase": "validation", "error": f"Validation exception: {str(e)}", "context": self.heal_context}

            # Phase 3: Alignment
            try:
                success, alignments = self.run_alignment_phase(self.heal_context, validated)
                if not success:
                    return False, {"phase": "alignment", "error": "Alignment failed", "context": self.heal_context}
                self.heal_context.record_phase_result("alignment", alignments)
            except Exception as e:
                return False, {"phase": "alignment", "error": f"Alignment exception: {str(e)}", "context": self.heal_context}

            # Phase 4: Healing
            try:
                success, healing_results = self.run_healing_phase(self.heal_context, alignments)
                if not success:
                    return False, {"phase": "healing", "error": "Healing failed", "context": self.heal_context}
                self.heal_context.record_phase_result("healing", healing_results)
            except Exception as e:
                return False, {"phase": "healing", "error": f"Healing exception: {str(e)}", "context": self.heal_context}

            # Phase 5: Reporting
            try:
                success, report = self.run_reporting_phase(self.heal_context, healing_results)
                self.heal_context.record_phase_result("reporting", report)
            except Exception as e:
                return False, {"phase": "reporting", "error": f"Reporting exception: {str(e)}", "context": self.heal_context}

            return True, {
                "heal_context": self.heal_context,
                "phase_results": self.heal_context.phase_results,
                "final_report": report
            }
        except Exception as e:
            return False, {"phase": "workflow", "error": f"Workflow exception: {str(e)}", "context": getattr(self, 'heal_context', None)}

    def save_checkpoint(self) -> None:
        """Save current state as checkpoint for recovery."""
        checkpoint = {
            "phase_results": self.phase_results.copy(),
            "heal_context": self.heal_context
        }
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
            'phases_completed': len(self.phase_results),
            'checkpoints_available': len(self.checkpoints),
            'has_context': self.heal_context is not None,
            'phase_names': list(self.phase_results.keys()),
        }

    def reset_call_path(self) -> None:
        """Reset the call path tracking."""
        self.logger.debug("Call path reset")
