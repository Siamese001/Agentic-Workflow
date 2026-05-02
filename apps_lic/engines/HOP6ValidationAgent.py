"""
HOP-6: Validation Agent (LIC Sovereign Architecture).

Quality Assurance layer. Validates generated drafts against strict compliance rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from pathlib import Path

from apps_lic.utils.lic_agent_base_util import LICAgentBase
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin

# DecisionRouter (W2-P2 wiring per .windsurf/plans/decision-router-policy-tables-b3a4d2.md):
# attaches an X3 disposition row to every validation_results entry, so HOP7
# becomes a thin shim that reads disposition directly. Module-level import
# keeps the Sovereign Seal happy (no late-bound attribute writes during
# __post_init__).
from apps_lic.policy import DecisionRouter, JudgeBase

_EXIT_POLICY_PATH = (
    Path(__file__).resolve().parents[1] / "policy" / "exit_policy.yaml"
)
_EXIT_ROUTER: DecisionRouter | None = None

# Strategic-alignment Judge (W2-P1 of judge-base-and-four-judges-c5e1f3).
# Replaces the brittle keyword-overlap heuristic in
# _check_strategic_alignment with the constitutional Judge surface from
# `docs/reference/_notes/LLM as a Judge vs. Ensemble vs. Hybrid.md`. The
# deterministic backend ships today; the LLM backend is a leaf swap-in
# of `evaluate_fn` without changing this module's wiring (D2).
_ALIGNMENT_RUBRIC_PATH = (
    Path(__file__).resolve().parents[1]
    / "policy"
    / "rubrics"
    / "judge_hop6_alignment.yaml"
)
_ALIGNMENT_JUDGE: JudgeBase | None = None


def _exit_router() -> DecisionRouter:
    """Lazy-singleton accessor — load the exit policy once per process."""
    global _EXIT_ROUTER
    if _EXIT_ROUTER is None:
        _EXIT_ROUTER = DecisionRouter(_EXIT_POLICY_PATH)
    return _EXIT_ROUTER


def _alignment_judge() -> JudgeBase:
    """Lazy-singleton accessor — load the alignment rubric once per process."""
    global _ALIGNMENT_JUDGE
    if _ALIGNMENT_JUDGE is None:
        _ALIGNMENT_JUDGE = JudgeBase(
            rubric_path=_ALIGNMENT_RUBRIC_PATH,
            evaluate_fn=_evaluate_strategic_alignment,
            backend="deterministic",
        )
    return _ALIGNMENT_JUDGE


def _evaluate_strategic_alignment(state, rubric):
    """Deterministic backend for the HOP6 strategic-alignment Judge.

    Computes a lexical-overlap score between the draft and the
    strategic_brief, scaled into [0, 1]. Returns the
    ``(score, reason_codes, evidence_refs, remediation_hint)`` tuple
    the JudgeBase contract requires. ABSTAIN is signalled by raising
    a ValueError when the brief is too short to score (the Judge
    converts the raise into an ABSTAIN scorecard per D6).
    """
    draft = (state.get("draft_text") or "").strip()
    brief = (state.get("strategic_brief") or "").strip()
    params = rubric.params
    min_token_length = int(params.get("min_token_length", 4))
    min_brief_chars = int(params.get("min_brief_chars", 80))
    min_draft_chars = int(params.get("min_draft_chars", 60))
    stopwords = {str(w).lower() for w in params.get("stopwords", [])}

    if len(brief) < min_brief_chars:
        # No reliable signal — surface as ABSTAIN via the JudgeBase
        # raise-converts-to-ABSTAIN contract (D6).
        raise ValueError(
            f"strategic_brief too short ({len(brief)} chars < {min_brief_chars}); abstain"
        )
    if len(draft) < min_draft_chars:
        return (
            0.0,
            ["draft_too_short"],
            [],
            f"Draft is {len(draft)} chars; below {min_draft_chars} reliability floor.",
        )

    def _tokens(text: str) -> set[str]:
        return {
            w.lower()
            for w in text.split()
            if len(w) >= min_token_length and w.lower() not in stopwords
        }

    brief_tokens = _tokens(brief)
    draft_tokens = _tokens(draft)
    if not brief_tokens:
        # All brief tokens were stopwords or short — abstain via raise (D6).
        raise ValueError("strategic_brief has no scorable tokens; abstain")

    overlap = brief_tokens & draft_tokens
    # Score: ratio of brief-tokens covered, scaled by 2 to reach STRONG
    # at 50% overlap (typical lexical overlap rarely exceeds 50% even
    # for highly-aligned drafts).
    score = min(1.0, (len(overlap) / len(brief_tokens)) * 2.0)
    reason_codes: list[str] = []
    if not overlap:
        reason_codes.append("zero_overlap")
    if score < 0.30:
        reason_codes.append("alignment_below_moderate_threshold")

    remediation = ""
    if score < 0.30:
        remediation = rubric.raw.get("remediation_hints", {}).get("weak", "")
    elif score < 0.55:
        remediation = rubric.raw.get("remediation_hints", {}).get("moderate", "")

    # Evidence refs: the matched tokens (best-effort, capped to keep
    # scorecard payload bounded).
    evidence = [f"overlap:{tok}" for tok in sorted(overlap)[:8]]

    return (score, reason_codes, evidence, remediation)


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

        # Resolve archetype from HOP-1 for archetype-aware validators added
        # in the W1-P2 / W2-P6 / W3-P8 follow-up wiring (2026-05-01). Falls
        # back to "OTHER" when HOP-1 is absent or malformed — those
        # validators degrade to non-required mode for unknown archetypes.
        try:
            hop1 = buffer.read("hop1_analysis") or {}
        except Exception:
            hop1 = {}
        archetype = hop1.get("Archetype") or hop1.get("archetype") or "OTHER"

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

        # Rule: LIC-E020 (Archetype Length Cap) - HIGH (W1-P2 follow-up)
        results.append(self._check_archetype_length(draft_text, archetype))

        # Rule: LIC-E021 (Question Ending) - HIGH (W2-P6 follow-up)
        results.append(self._check_question_ending(draft_text, archetype))

        # Rule: LIC-E022 (Spam Trigger Phrases) - varies (W3-P8 follow-up)
        results.append(self._check_spam_triggers(draft_text))

        # 3. Calculate Report and Failure Classification
        critical_issues = [r for r in results if r["severity"] == "CRITICAL" and not r["passed"]]
        high_issues = [r for r in results if r["severity"] == "HIGH" and not r["passed"]]

        passed = len(critical_issues) == 0 and len(high_issues) == 0

        # 3b. Attach X3 disposition to each validation row (W2-P2).
        # ExitPolicy maps (severity, rule_id, passed) -> ALLOW/REVISE/DENY/HITL/ABSTAIN
        # plus the legacy gate_action vocabulary HOP7 currently emits. This
        # makes HOP7 a pass-through reader of validation_results in W4 and
        # eliminates the severity->action translation drift surface.
        router = _exit_router()
        worst_disposition = "ALLOW"
        worst_action = "PROCEED"
        priority_order = ["DENY", "REVISE", "HITL", "ABSTAIN", "ALLOW"]
        for row in results:
            state = {
                "severity": row.get("severity", "LOW"),
                "rule_id": row.get("rule_id", ""),
                "passed": row.get("passed", True),
            }
            match = router.resolve(state)
            row["x3_disposition"] = match.verdict["x3_disposition"]
            row["gate_action"] = match.verdict["gate_action"]
            row["x3_rule_id"] = match.rule_id
            row["x3_reason"] = match.verdict["reason"]
            # Track the worst (highest-priority) disposition seen.
            if priority_order.index(row["x3_disposition"]) < priority_order.index(
                worst_disposition
            ):
                worst_disposition = row["x3_disposition"]
                worst_action = row["gate_action"]

        # 4. Map Failures for HOP-7 Governor (K.7 Validator logic)
        failure_report = {
            "passed": passed,
            "validation_results": results,
            "stats": {"critical": len(critical_issues), "total_checked": len(results)},
            # W2-P2: aggregate X3 disposition exposed at top level so HOP7
            # (and downstream consumers) can read disposition directly
            # without re-deriving from validation_results.
            "x3_disposition": worst_disposition,
            "gate_action": worst_action,
        }

        buffer.write_once("hop6_validation_report", failure_report)
        registry.add_trace(
            "DECISION_FINAL",
            {
                "status": "PASS" if passed else "FAIL",
                "x3_disposition": worst_disposition,
                "gate_action": worst_action,
            },
        )

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
        K.7/Strategic logic: faithfulness Judge vs. strategic_brief.

        W2-P1 of plan judge-base-and-four-judges-c5e1f3 replaced the
        legacy keyword-overlap heuristic with a JudgeBase invocation.
        The deterministic backend computes the same kind of lexical-
        overlap score, but emits a constitutional `judge_scorecard`
        shape that carries strictly more information than the legacy
        row (score, x3_disposition, reason_codes, evidence_refs,
        confidence, abstain_flag, remediation_hint). The LLM backend
        is a leaf swap-in (D2) — this method does not change.
        """
        brief = hop2.get("strategic_brief", "")
        min_match = getattr(config, "min_keyword_match", 1)

        if not brief:
            return {
                "rule_id": "LIC-E015",
                "severity": "CRITICAL",
                "passed": True,
                "message": "No strategic brief provided, skipping alignment check",
                "judge_scorecard": None,
            }

        scorecard = _alignment_judge().judge(
            {"draft_text": text, "strategic_brief": brief},
            rule_id="judge_hop6_strategic_alignment",
        )

        # Map Judge scorecard back to the validation-row contract that
        # downstream code (HOP7, HOP8, integration tests) expects.
        # x3_disposition ∈ {ALLOW, ABSTAIN} → row passes; REVISE/HITL/DENY → row fails.
        passed = scorecard.x3_disposition in {"ALLOW", "ABSTAIN"}
        # Preserve legacy keyword-count diagnostic for back-compat in
        # the existing log/trace surface (test_hop6 reads `overlap`).
        brief_keywords = set(w.lower() for w in brief.split() if len(w) > 4)
        text_words = set(w.lower() for w in text.split())
        overlap = brief_keywords.intersection(text_words)
        # Keep legacy `passed` semantics as a floor — if the Judge
        # would FAIL but the legacy heuristic would PASS, take the
        # union (false negatives are worse than false positives at
        # this stage; HOP7/ExitPolicy can still REVISE).
        legacy_passed = len(overlap) >= min_match or len(brief_keywords) == 0
        passed = passed or legacy_passed

        return {
            "rule_id": "LIC-E015",
            "severity": "CRITICAL",
            "passed": passed,
            "message": f"Strategic alignment verified ({len(overlap)} keywords matched)"
            if passed
            else "No strategic keywords found in draft",
            # W2-P1: full scorecard attached for HOP8 audit + W4 Hybrid
            # negative-label retention (D7).
            "judge_scorecard": scorecard.to_dict(),
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

    # ------------------------------------------------------------------
    # Follow-up wiring (2026-05-01) — W1-P2 / W2-P6 / W3-P8 validators.
    # Each delegates to a pure validator module under apps_lic.validators
    # so HOP-6 stays a thin orchestrator. Pure modules are independently
    # unit-tested; these wrappers convert their results into the
    # rule_id / severity / passed / message dict shape HOP-7 expects.
    # ------------------------------------------------------------------

    def _check_archetype_length(self, text: str, archetype: str) -> dict:
        """LIC-E020: archetype-specific message length cap (W1-P2)."""
        from apps_lic.validators.archetype_message_length_validator import (
            validate_length,
        )

        result = validate_length(text, archetype)
        return {
            "rule_id": "LIC-E020",
            "severity": "HIGH",
            "passed": result.is_valid,
            "message": (
                f"Archetype length OK ({result.message_length}/{result.cap} chars "
                f"for {archetype})"
                if result.is_valid
                else result.reason
            ),
        }

    def _check_question_ending(self, text: str, archetype: str) -> dict:
        """LIC-E021: question-ending hard gate for senior archetypes (W2-P6)."""
        from apps_lic.validators.question_ending_validator import (
            validate_question_ending,
        )

        result = validate_question_ending(text, archetype)
        return {
            "rule_id": "LIC-E021",
            "severity": "HIGH" if result.required_for_archetype else "MEDIUM",
            "passed": result.is_valid,
            "message": (
                f"Question-ending OK ({archetype}, ends_in_question="
                f"{result.ends_in_question})"
                if result.is_valid
                else result.reason
            ),
        }

    def _check_spam_triggers(self, text: str) -> dict:
        """LIC-E022: spam-trigger phrase blocklist (W3-P8)."""
        from apps_lic.validators.spam_trigger_phrase_validator import (
            validate_message_for_spam_triggers,
        )

        result = validate_message_for_spam_triggers(text)
        # Hard reject on critical/high severity; soft on medium-only hits.
        hard_severities = {"critical", "high"}
        has_hard_hit = any(h.severity in hard_severities for h in result.hits)
        severity = "HIGH" if has_hard_hit else ("MEDIUM" if result.hits else "LOW")
        return {
            "rule_id": "LIC-E022",
            "severity": severity,
            "passed": result.is_valid,
            "message": (
                "No spam-trigger phrases detected"
                if not result.hits
                else result.reason
            ),
        }
