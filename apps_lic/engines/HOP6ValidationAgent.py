"""
HOP-6: Validation Agent (LIC Sovereign Architecture).

Quality Assurance layer. Validates generated drafts against strict compliance rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from apps_lic.utils.lic_agent_base_util import LICAgentBase
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class HOP6ValidationAgent(LICAgentBase, SubatomicTestingMixin):
    """
    V2 Implementation of HOP-6 QA.

    Architecture:
    - Base: LICAgentBase
    - Inputs: HOP-5 (Draft), HOP-2 (Context), HOP-3 (Grounding)
    - Logic: Rule-based validation engine (Regex, Keyword matching).
    - Output: 'hop6_validation_report'
    """

    # Sovereign Configuration
    validation_rules: dict[str, Any] = field(
        default_factory=lambda: {"strict_mode": True, "max_violations": 5}
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute specialist validation logic.

        1. Read Generation and Research Context.
        2. Specialist Validation Execution (K.7 Heuristics).
        3. Calculate Report and Failure Classification.
        4. Map Failures for HOP-7 Governor.
        """
        registry.add_trace("PHASE_START", {"agent": self.__class__.__name__})

        # 1. Read Generation and Research Context
        try:
            hop5 = buffer.read("hop5_generation")
            hop2 = buffer.read("hop2_research")
        except Exception as e:
            registry.add_trace("DATA_ERROR", {"msg": str(e)})
            raise RuntimeError("HOP-6 missing HOP-5 draft or HOP-2 research")

        draft_text = hop5["selected_draft"]["text"]

        # 2. Specialist Validation Execution (K.7 Heuristics)
        registry.add_trace("PHASE_STEP", {"action": "starting_rule_execution"})

        # Load externalized rules from config
        rules_config = self.config.validation_agent

        results = []
        # Rule: LIC-E001 (Placeholders) - CRITICAL
        results.append(self._check_placeholders(draft_text, rules_config))

        # Rule: LIC-E015 (Strategic Alignment) - CRITICAL
        results.append(self._check_strategic_alignment(draft_text, hop2, rules_config))

        # Rule: LIC-E008 (Forbidden Verbs) - MEDIUM
        results.append(self._check_forbidden_verbs(draft_text, rules_config))

        # 3. Calculate Report and Failure Classification
        critical_issues = [r for r in results if r["severity"] == "CRITICAL" and not r["passed"]]
        high_issues = [r for r in results if r["severity"] == "HIGH" and not r["passed"]]

        passed = len(critical_issues) == 0 and len(high_issues) == 0

        # 4. Map Failures for HOP-7 Governor (K.7 Validator logic)
        failure_report = {
            "passed": passed,
            "validation_results": results,
            "stats": {"critical": len(critical_issues), "total_checked": len(results)},
        }

        buffer.write_once("hop6_validation_report", failure_report)
        registry.add_trace("DECISION_FINAL", {"status": "PASS" if passed else "FAIL"})

    def _check_placeholders(self, text: str, config: Any) -> dict:
        """
        K.7/PlaceholderDetector logic: Zero tolerance for [bracketed] text.
        """
        # Logic: Use patterns from config or default to sovereign standards
        pattern = getattr(config, "placeholder_regex", r"\[.*?\]|\{.*?\}|<.*?>")
        found = re.findall(pattern, text)
        return {
            "rule_id": "LIC-E001",
            "severity": "CRITICAL",
            "passed": len(found) == 0,
            "message": f"Found placeholders: {found}" if found else "No placeholders detected",
        }

    def _check_strategic_alignment(self, text: str, hop2: dict, config: Any) -> dict:
        """
        K.7/Strategic logic: Ensure overlap with strategic brief keywords.
        """
        min_match = getattr(config, "min_keyword_match", 1)
        brief = hop2.get("strategic_brief", "")

        if not brief:
            # No brief to validate against
            return {
                "rule_id": "LIC-E015",
                "severity": "CRITICAL",
                "passed": True,
                "message": "No strategic brief provided, skipping alignment check",
            }

        # Extract keywords > 4 chars from brief
        brief_keywords = set(w.lower() for w in brief.split() if len(w) > 4)
        text_words = set(w.lower() for w in text.split())
        overlap = brief_keywords.intersection(text_words)

        passed = len(overlap) >= min_match or len(brief_keywords) == 0

        return {
            "rule_id": "LIC-E015",
            "severity": "CRITICAL",
            "passed": passed,
            "message": f"Strategic alignment verified ({len(overlap)} keywords matched)"
            if passed
            else "No strategic keywords found in draft",
        }

    def _check_forbidden_verbs(self, text: str, config: Any) -> dict:
        """
        K.7/ForbiddenVerbs logic: Detect overly promotional language.
        """
        # Logic: Ingest forbidden list from config
        forbidden_verbs = getattr(config, "forbidden_verbs", ["revolutionize", "disrupt"])
        text_lower = text.lower()

        found = [verb for verb in forbidden_verbs if verb in text_lower]

        return {
            "rule_id": "LIC-E008",
            "severity": "MEDIUM",
            "passed": len(found) == 0,
            "message": f"Found forbidden verbs: {found}"
            if found
            else "No forbidden verbs detected",
        }
