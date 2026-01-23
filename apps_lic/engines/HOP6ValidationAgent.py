"""
HOP-6: Validation Agent (V2 Architecture).

Quality Assurance layer. Validates generated drafts against strict compliance rules.
"""

from __future__ import annotations

import re

from apps_lic.shared.v2_patterns.agent_base import V2AgentBase
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class HOP6ValidationAgent(V2AgentBase):
    """
    V2 Implementation of HOP-6 QA.

    Architecture:
    - Base: V2AgentBase
    - Inputs: HOP-5 (Draft), HOP-2 (Context), HOP-3 (Grounding)
    - Logic: Rule-based validation engine (Regex, Keyword matching).
    - Output: 'hop6_validation_report'
    """

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute validation logic.

        1. Read draft from HOP-5 and context from HOP-2/3.
        2. Run validation rules (placeholders, word count, strategic alignment).
        3. Calculate pass/fail status based on severity.
        4. Write validation report.
        """
        # 1. Read Inputs
        try:
            gen_state = buffer.read("hop5_generation")
            research_state = buffer.read("hop2_research")
            grounding_state = buffer.read("hop3_sender_grounding")
        except Exception:
            registry.add_trace("DATA_ERROR", {"msg": "Failed to read required inputs"})
            raise ValueError("HOP-6 requires inputs from HOP 5, 2, and 3")

        # Validate existence (HOP-3 is optional but recommended)
        if not gen_state or not research_state:
            registry.add_trace("CRITICAL_FAILURE", {"msg": "Missing upstream state (HOP5 or HOP2)"})
            raise RuntimeError("Missing upstream state for validation")

        draft = gen_state["selected_draft"]
        text = draft["text"]

        registry.add_trace("PHASE_STEP", {"action": "validating_draft", "length": len(text)})

        # 2. Execute Validation Logic
        results = self._validate_draft(text, draft, research_state, grounding_state)

        # 3. Calculate Status
        critical_issues = sum(1 for r in results if r["severity"] == "CRITICAL" and not r["passed"])
        high_issues = sum(1 for r in results if r["severity"] == "HIGH" and not r["passed"])
        medium_issues = sum(1 for r in results if r["severity"] == "MEDIUM" and not r["passed"])

        passed = critical_issues == 0 and high_issues == 0

        # 4. Write Output
        output = {
            "passed": passed,
            "validation_results": results,
            "stats": {
                "critical": critical_issues,
                "high": high_issues,
                "medium": medium_issues,
                "total_checked": len(results),
            },
        }

        buffer.write_once("hop6_validation_report", output)

        status_msg = "PASS" if passed else "FAIL"
        registry.add_trace(
            "DECISION_FINAL", {"status": status_msg, "critical_issues": critical_issues}
        )

    def _validate_draft(
        self, text: str, draft: dict, research: dict, grounding: dict
    ) -> list[dict]:
        """
        Run all validation checks.

        Args:
            text: Draft message text
            draft: Full draft object
            research: Research context from HOP-2
            grounding: Sender grounding from HOP-3

        Returns:
            List of validation results with rule_id, severity, passed, and optional message
        """
        results = []

        # 1. Placeholder Check (CRITICAL)
        # Regex for [bracketed] or <angled> placeholders
        if re.search(r"\[.*?\]|<.*?>", text):
            results.append(
                {
                    "rule_id": "PLACEHOLDERS",
                    "severity": "CRITICAL",
                    "passed": False,
                    "message": "Placeholder patterns detected",
                }
            )
        else:
            results.append({"rule_id": "PLACEHOLDERS", "severity": "CRITICAL", "passed": True})

        # 2. Word Count (HIGH)
        word_count = len(text.split())
        if word_count < 10 or word_count > 1000:
            results.append(
                {
                    "rule_id": "WORD_COUNT_SANITY",
                    "severity": "HIGH",
                    "passed": False,
                    "message": f"Word count {word_count} suspicious",
                }
            )
        else:
            results.append({"rule_id": "WORD_COUNT_SANITY", "severity": "HIGH", "passed": True})

        # 3. Strategic Alignment (CRITICAL)
        # Check if strategic brief keywords appear in text
        brief = research.get("strategic_brief", "")
        if brief:
            # Simplified keyword extraction (words > 5 chars)
            brief_keywords = set(w.lower() for w in brief.split() if len(w) > 5)
            text_words = set(w.lower() for w in text.split())
            overlap = brief_keywords.intersection(text_words)

            if not overlap and len(brief_keywords) > 0:
                results.append(
                    {
                        "rule_id": "STRATEGIC_ALIGNMENT",
                        "severity": "CRITICAL",
                        "passed": False,
                        "message": "No strategic keywords found in draft",
                    }
                )
            else:
                results.append(
                    {"rule_id": "STRATEGIC_ALIGNMENT", "severity": "CRITICAL", "passed": True}
                )

        return results
