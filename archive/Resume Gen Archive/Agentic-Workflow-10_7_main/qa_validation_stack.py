"""Layer-5 QA validation stack for v10.8."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from agent_tools_v10_7 import (
    QAAdversarialReviewerTool,
    QABiasDetectorTool,
    QAClaimValidatorTool,
    QAJDSkillsValidatorTool,
    QAMissedOpportunityTool,
    QANarrativeThreadTool,
    QAThematicAlignmentTool,
    QAToneValidatorTool,
    QATenureValidatorTool,
    QASemanticEntailmentTool,
    QASignalScoreValidatorTool,
    QAWordCountValidatorTool,
)

from core_v10_7 import StrategyPlan
from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack


class QAValidationStack:
    """Runs the QA tool suite and emits a normalized patch."""

    STYLE_GUIDE = "Style: Ensure professional, clear, and unbiased language."
    WORD_COUNT_RANGE = (50, 150)

    _TOOL_BUILDERS: Tuple[Tuple[str, Any], ...] = (
        ("validate_claims", QAClaimValidatorTool),
        ("validate_tone", QAToneValidatorTool),
        ("validate_thematic_alignment", QAThematicAlignmentTool),
        ("validate_semantic_entailment", QASemanticEntailmentTool),
        ("validate_narrative_thread", QANarrativeThreadTool),
        ("validate_jd_skills", QAJDSkillsValidatorTool),
        ("validate_signal_score", QASignalScoreValidatorTool),
        ("validate_bias", QABiasDetectorTool),
        ("validate_tenure", QATenureValidatorTool),
        ("find_missed_opportunities", QAMissedOpportunityTool),
        ("validate_word_count", QAWordCountValidatorTool),
        ("adversarial_review", QAAdversarialReviewerTool),
    )

    def __init__(
        self,
        context: Any,
        debug_mode: bool = False,
        *,
        validators: Optional[Sequence[Tuple[str, Any]]] = None,
    ) -> None:
        self.context = context
        self.debug_mode = debug_mode
        self._validators: Tuple[Tuple[str, Any], ...] = (
            tuple(validators) if validators is not None else self._build_validators()
        )
        self._adapter = StateAdapterStack(context, debug_mode)

    def _build_validators(self) -> Tuple[Tuple[str, Any], ...]:
        instances: List[Tuple[str, Any]] = []
        for tool_name, tool_cls in self._TOOL_BUILDERS:
            instances.append((tool_name, tool_cls(self.context, self.debug_mode)))
        return tuple(instances)

    async def run_async(self, state: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Execute all QA validators and return a structured patch."""

        tool_input = self._build_tool_input(state)
        validator_results: List[Tuple[str, Dict[str, Any]]] = []

        for tool_name, tool in self._validators:
            result = await tool.run_async(dict(tool_input), workflow_id)
            normalized_result = result if isinstance(result, dict) else {"status": "unknown"}
            validator_results.append((tool_name, normalized_result))

        issues = self._collect_issues(validator_results)
        qa_passed = len(issues) == 0
        total_validators = max(len(validator_results), 1)
        confidence = 1.0 if qa_passed else max(0.0, 1.0 - len(issues) / total_validators)
        summary = self._summarize_results(qa_passed, len(issues), total_validators)

        return {
            "qa": {
                "issues": issues,
                "confidence": round(confidence, 3),
                "summary": summary,
                "qa_passed": qa_passed,
            }
        } | self._adapter.patch_memory(
            agent_notes=self._append_agent_note(state, summary)
        ).model_dump(exclude_none=True)

    async def run_from_state_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Normalize the strategy plan and delegate to ``run_async``."""

        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        strategy_payload = state.get("strategy", {}).get("strategy_plan")
        typed_plan: Optional[StrategyPlan] = None
        needs_patch = False
        if isinstance(strategy_payload, dict):
            typed_plan = StrategyPlan.model_validate(strategy_payload)
            needs_patch = True
        elif isinstance(strategy_payload, StrategyPlan):
            typed_plan = strategy_payload

        patch = await self.run_async(state, workflow_id)
        if needs_patch and typed_plan is not None:
            strategy_patch = {"strategy": {"strategy_plan": typed_plan}}
            patch = self._merge_patch(patch, strategy_patch)
        return patch

    def _build_tool_input(self, state: Dict[str, Any]) -> Dict[str, Any]:
        draft_sections = state.get("draft", {}).get("sections", {})
        resume_payload = state.get("resume", {}).get("master_resume", {})
        job_description = state.get("job", {}).get("raw_jd", "")
        strategy_plan = self._normalize_strategy(state.get("strategy", {}).get("strategy_plan"))
        summary_text = self._extract_summary_text(draft_sections)
        min_words, max_words = self.WORD_COUNT_RANGE

        return {
            "draft_text": json.dumps(draft_sections, default=str),
            "master_resume": resume_payload,
            "job_description": job_description,
            "strategy": strategy_plan,
            "style_guide": self.STYLE_GUIDE,
            "text_to_check": summary_text,
            "min_words": min_words,
            "max_words": max_words,
            "llm_reported_count": len(summary_text.split()),
        }

    def _normalize_strategy(self, strategy: Any) -> Dict[str, Any]:
        if hasattr(strategy, "model_dump"):
            return strategy.model_dump()
        if isinstance(strategy, dict):
            return strategy
        return {}

    def _extract_summary_text(self, draft_sections: Any) -> str:
        summary = draft_sections.get("summary") if isinstance(draft_sections, dict) else None
        if isinstance(summary, str):
            return summary
        if isinstance(summary, dict):
            for candidate_key in ("draft", "text", "content"):
                value = summary.get(candidate_key)
                if isinstance(value, str):
                    return value
            return json.dumps(summary, default=str)
        return ""

    def _collect_issues(
        self, validator_results: Iterable[Tuple[str, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        for tool_name, result in validator_results:
            issue_description = self._detect_issue(tool_name, result)
            if issue_description:
                issues.append(
                    {
                        "tool": tool_name,
                        "description": issue_description,
                        "details": result,
                        "severity": self._severity_for(tool_name),
                    }
                )
        return issues

    def _detect_issue(self, tool_name: str, result: Dict[str, Any]) -> Optional[str]:
        if tool_name == "validate_claims" and result.get("unsupported_claims", 0) > 0:
            return f"{result['unsupported_claims']} unsupported claims detected"
        if tool_name == "validate_tone" and not result.get("tone_match", True):
            tone = result.get("current_tone", "unknown")
            return f"Tone mismatch detected (found: {tone})"
        if tool_name == "validate_thematic_alignment" and result.get("alignment_score", 1.0) < 0.75:
            return "Low thematic alignment score"
        if tool_name == "validate_semantic_entailment" and result.get("entailment_score", 1.0) < 0.7:
            return "Semantic entailment below threshold"
        if tool_name == "validate_narrative_thread" and not result.get("narrative_clear", True):
            return "Narrative thread unclear"
        if tool_name == "validate_jd_skills" and result.get("missing_keywords"):
            return f"Missing critical keywords: {', '.join(result['missing_keywords'])}"
        if tool_name == "validate_signal_score" and result.get("avg_signal_score", 10) < 6:
            return "Average signal score is low"
        if tool_name == "validate_bias" and result.get("bias_detected"):
            score = result.get("bias_score")
            return f"Bias patterns detected (score={score})"
        if tool_name == "validate_tenure" and (
            result.get("gaps_found", 0) > 0 or result.get("overlaps_found", 0) > 0
        ):
            return "Tenure inconsistencies detected"
        if tool_name == "find_missed_opportunities" and result.get("opportunities_found"):
            return "Relevant opportunities were omitted"
        if tool_name == "validate_word_count" and not result.get("validation_passed", True):
            return result.get("message", "Word count outside range")
        if tool_name == "adversarial_review" and result.get("red_flags"):
            return "Adversarial reviewer raised red flags"
        return None

    def _severity_for(self, tool_name: str) -> str:
        high_severity = {
            "validate_claims",
            "validate_bias",
            "adversarial_review",
            "validate_tenure",
        }
        return "high" if tool_name in high_severity else "medium"

    def _summarize_results(self, qa_passed: bool, issue_count: int, total: int) -> str:
        if qa_passed:
            return f"All {total} QA validators passed."
        plural = "issue" if issue_count == 1 else "issues"
        return f"{issue_count} {plural} flagged across {total} validators."

    def _merge_patch(self, base: Dict[str, Any], addition: Dict[str, Any]) -> Dict[str, Any]:
        merged: Dict[str, Any] = dict(base)
        for key, value in addition.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = self._merge_patch(
                    merged[key], value
                )  # type: ignore[arg-type]
            else:
                merged[key] = value
        return merged

    def _append_agent_note(self, state: Dict[str, Any], summary: str) -> List[str]:
        existing = state.get("memory", {}).get("episodic", {}).get("agent_notes") or []
        note = f"QA summary: {summary}"
        return [*existing, note]


__all__ = ["QAValidationStack"]

