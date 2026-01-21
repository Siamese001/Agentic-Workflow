from __future__ import annotations
from dataclasses import dataclass
"""HOP-7: Gate Decision Agent - Make the 'Slow Loop' decision."""

__version__ = "13.1"

from typing import Dict, List, Any, Tuple

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

from apps_lic.domain.lic_models import FactualGapError, FailureClassifierAgent
from apps_shared.utils.state_manager import StateManager


@dataclass
class HOP7GateDecisionAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    v13.1: HOP-7 - Gate Decision Agent (MCP Hardened)

    Single Responsibility: Make the "Slow Loop" decision

    Input:  state/6_validation_report.json
    Output: state/7_gate_decision.json

    Decision Logic:
    - FACTUAL_FAILURE: raise FactualGapError → trigger S6->S2 meta-loop
    - CREATIVE_FAILURE: raise CreativeFailureError → HALT workflow
    - PASS: return True → proceed to output
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize with externalized configuration

        Args:
            config: Loaded from config/agent_specs_LIC.json
        """
        super().__init__()  # MCPHardenedMixin init
        self.config = config["gate_decision_agent"]
        self.factual_failure_rules = set(self.config["factual_failure_rules"])
        self.max_factual_loops = self.config["max_factual_loops"]
        self.max_creative_retries = self.config["max_creative_retries"]

        # Track loop counts
        self.factual_loop_count = 0
        self.creative_retry_count = 0

    def execute(self, state_mgr: StateManager) -> str:
        """
        Execute HOP-7: Make gate decision based on validation results

        Args:
            state_mgr: State manager for this mission

        Returns:
            Path to output state file

        Raises:
            FactualGapError: If factual failure detected (triggers S6->S2 loop)
            ValueError: If creative failure detected (halts workflow)
        """
        print(f"\nimport logging\n\nLogger = logging.getLogger(__name__)\n{'='*80}")
        print("HOP-7: GATE DECISION")
        print(f"{'='*80}\n")

        # Read HOP-6 validation results
        validation_state = state_mgr.read_state("HOP-6")

        validation_results = validation_state.get("validation_results", [])
        passed = validation_state.get("passed", False)

        # If validation passed, proceed
        if passed:
            decision = "PASS"
            reasoning = "All validation checks passed"

            output_state = {
                "decision": decision,
                "reasoning": reasoning,
                "factual_loop_count": self.factual_loop_count,
                "creative_retry_count": self.creative_retry_count
            }

            output_path = state_mgr.write_state("HOP-7", output_state)

            print(f"✓ Gate Decision: PASS")
            print(f"  All validations passed\n")

            return output_path

        # Validation failed - classify failures
        critical_failures = [
            r for r in validation_results
            if r.get("Severity") in ["CRITICAL", "HIGH"] and not r.get("passed", True)
        ]

        if not critical_failures:
            # No critical failures, allow proceed
            decision = "PASS"
            reasoning = "No critical failures detected"

            output_state = {
                "decision": decision,
                "reasoning": reasoning,
                "factual_loop_count": self.factual_loop_count,
                "creative_retry_count": self.creative_retry_count
            }

            output_path = state_mgr.write_state("HOP-7", output_state)

            print(f"✓ Gate Decision: PASS (non-critical issues only)")
            return output_path

        # Classify failure type
        failure_type, failure_message = self._classify_failure(critical_failures)

        print(f"  Failure Type: {failure_type}")
        print(f"  Reason: {failure_message}\n")

        # Make decision based on failure type
        if failure_type == FailureClassifierAgent.FACTUAL_FAILURE:
            # Check loop limit
            if self.factual_loop_count >= self.max_factual_loops:
                print(f"  ✗ Max factual loops ({self.max_factual_loops}) reached - HALTING")

                decision = "HALT_MAX_FACTUAL_LOOPS"
                reasoning = f"Exceeded max factual loops ({self.max_factual_loops})"

                output_state = {
                    "decision": decision,
                    "reasoning": reasoning,
                    "factual_loop_count": self.factual_loop_count,
                    "failure_message": failure_message
                }

                output_path = state_mgr.write_state("HOP-7", output_state)

                raise ValueError(f"Max factual loops exceeded: {failure_message}")

            # Trigger S6->S2 meta-loop
            self.factual_loop_count += 1

            decision = "FACTUAL_FAILURE"
            reasoning = f"Factual failure detected - triggering S6->S2 meta-loop (attempt {self.factual_loop_count}/{self.max_factual_loops})"

            output_state = {
                "decision": decision,
                "reasoning": reasoning,
                "factual_loop_count": self.factual_loop_count,
                "failure_message": failure_message,
                "action": "LOOP_TO_HOP2"
            }

            output_path = state_mgr.write_state("HOP-7", output_state)

            print(f"  → Triggering S6->S2 meta-loop (attempt {self.factual_loop_count})")

            raise FactualGapError(failure_message)

        else:  # CREATIVE_FAILURE
            # Check retry limit
            if self.creative_retry_count >= self.max_creative_retries:
                print(f"  ✗ Max creative retries ({self.max_creative_retries}) reached - HALTING")

                decision = "HALT_MAX_CREATIVE_RETRIES"
                reasoning = f"Exceeded max creative retries ({self.max_creative_retries})"

                output_state = {
                    "decision": decision,
                    "reasoning": reasoning,
                    "creative_retry_count": self.creative_retry_count,
                    "failure_message": failure_message
                }

                output_path = state_mgr.write_state("HOP-7", output_state)

                raise ValueError(f"Max creative retries exceeded: {failure_message}")

            # Trigger S5 creative retry
            self.creative_retry_count += 1

            decision = "CREATIVE_FAILURE"
            reasoning = f"Creative failure detected - triggering S5 retry with escalated temperature (attempt {self.creative_retry_count}/{self.max_creative_retries})"

            output_state = {
                "decision": decision,
                "reasoning": reasoning,
                "creative_retry_count": self.creative_retry_count,
                "failure_message": failure_message,
                "action": "RETRY_HOP5"
            }

            output_path = state_mgr.write_state("HOP-7", output_state)

            print(f"  → Triggering S5 creative retry (attempt {self.creative_retry_count})")

            # Return path - orchestrator will handle retry
            return output_path

    def _classify_failure(
        self,
        failures: List[Dict[str, Any]]
    ) -> Tuple[FailureClassifierAgent, str]:
        """
        Classify failure type to determine retry strategy

        Args:
            failures: List of validation failures

        Returns:
            (failure_classifier, failure_message)
        """
        for failure in failures:
            rule_id = failure.get("rule_id", "")

            # Check if this is a factual failure rule
            if rule_id in self.factual_failure_rules:
                return FailureClassifierAgent.FACTUAL_FAILURE, f"({rule_id}) {failure.get('message', '')}"

            # Check details for override
            details = failure.get("details", {})
            if details.get("failure_classifier") == "FACTUAL_FAILURE":
                return FailureClassifierAgent.FACTUAL_FAILURE, f"({rule_id}) {failure.get('message', '')}"

        # Default to creative failure
        return FailureClassifierAgent.CREATIVE_FAILURE, f"({failures[0].get('rule_id', '')}) {failures[0].get('message', '')}"

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set = None) -> Dict[str, int]:
        """Operational agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
        print(f"[{self.__class__.__name__}] Operational agent - healing chain invoked")
        return {"skipped": 1}
