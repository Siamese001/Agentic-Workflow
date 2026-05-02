"""
HOP-8: QA Report Agent (LIC Sovereign Architecture).

Aggregates mission state into a persistent Markdown Audit Trail and calculates quality scores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from apps_lic.utils.lic_agent_base_util import LICAgentBase
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class HOP8QAReportAgent(LICAgentBase, SubatomicTestingMixin):
    """
    V2 Implementation of HOP-8.

    Responsibilities:
    - Aggregate all HOP outputs from the ImmutableStagingBuffer.
    - Calculate a multi-dimensional Quality Score.
    - Generate and save a Markdown report to disk.
    """

    # Sovereign Configuration
    report_config: dict[str, Any] = field(
        default_factory=lambda: {"output_dir": "reports", "include_timestamps": True}
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute QA report generation logic.

        1. Aggregate all HOP outputs from buffer.
        2. Calculate multi-dimensional quality scores.
        3. Generate Markdown audit trail.
        4. Persist report to disk and write summary to buffer.
        """
        # 1. Aggregate All State
        states = {
            "hop1": buffer.read("hop1_analysis") or {},
            "hop2": buffer.read("hop2_research") or {},
            "hop3": buffer.read("hop3_sender_grounding") or {},
            "hop4": buffer.read("hop4_routing") or {},
            "hop5": buffer.read("hop5_generation") or {},
            "hop6": buffer.read("hop6_validation_report") or {},
            "hop7": buffer.read("hop7_gate_decision") or {},
        }

        # 2. Calculate scoring
        scores = self._calculate_scores(states)
        total_score = sum(scores.values())

        registry.add_trace("PHASE_STEP", {"action": "scoring_complete", "total_score": total_score})

        # 2b. W3-P3: narrative executive_summary Judge.
        # The deterministic backend selects a score-band template and
        # interpolates top_signal / top_gap from the breakdown. The
        # narrative is shipped as the first evidence_ref of the
        # scorecard; we extract it for the buffer payload below.
        # LLM backend swap-in is a leaf change per D2.
        executive_summary = ""
        hop8_judge_scorecard = None
        try:
            from pathlib import Path as _Path

            from apps_lic.policy import JudgeBase as _JudgeBase
            from apps_lic.policy.judge_evaluators import (
                evaluate_hop8_narrative as _evaluate_hop8_narrative,
            )

            _rubric_path = (
                _Path(__file__).resolve().parents[1]
                / "policy"
                / "rubrics"
                / "judge_hop8_narrative.yaml"
            )
            _judge = _JudgeBase(
                rubric_path=_rubric_path,
                evaluate_fn=_evaluate_hop8_narrative,
                backend="deterministic",
            )
            _scorecard = _judge.judge(
                {"total_score": total_score, "score_breakdown": scores},
                rule_id="judge_hop8_narrative",
            )
            hop8_judge_scorecard = _scorecard.to_dict()
            # First evidence_ref is "narrative:<text>" by convention.
            for ref in _scorecard.evidence_refs:
                if ref.startswith("narrative:"):
                    executive_summary = ref[len("narrative:"):]
                    break
            registry.add_trace(
                "JUDGE_RESOLVED",
                {
                    "judge": "HOP8_ExecutiveSummary",
                    "x3_disposition": _scorecard.x3_disposition,
                    "score": _scorecard.score,
                },
            )
        except Exception:  # guardian: allow-log-and-swallow -- Judge failure must not block report generation
            executive_summary = ""
            hop8_judge_scorecard = None

        # 3. Generate Markdown
        report_md = self._generate_markdown(states, scores, total_score)

        # 4. Persistence (Physical Disk + Buffer)
        report_path = self._save_report(report_md, states.get("hop1", {}))

        output_data = {
            "total_score": total_score,
            "score_breakdown": scores,
            "executive_summary": executive_summary,  # W3-P3
            "judge_scorecard": hop8_judge_scorecard,  # W3-P3
            "report_path": str(report_path),
            "timestamp": datetime.utcnow().isoformat(),
        }

        buffer.write_once("hop8_qa_report", output_data)

        registry.add_trace("DECISION_FINAL", {"score": total_score, "path": str(report_path)})

    def _calculate_scores(self, states: dict[str, Any]) -> dict[str, float]:
        """Calculates weighted scores across 4 dimensions."""
        weights = self.config.qa_report_agent.scoring_weights

        # Research Score (0-100)
        h2 = states.get("hop2") or {}
        research_raw = (h2.get("signal_score", 0) * 100) if h2 else 0

        # Alignment Score (0-100)
        h6 = states.get("hop6") or {}
        val_results = h6.get("validation_results", [])
        passed_rules = sum(1 for r in val_results if r.get("passed"))
        alignment_raw = (passed_rules / len(val_results) * 100) if val_results else 0

        # Validation Success (Binary multiplier)
        val_raw = 100 if h6.get("passed") else 0

        # Generation Quality (Constraints check)
        h5 = states.get("hop5") or {}
        draft_score = h5.get("selected_draft", {}).get("score", 0)
        gen_raw = max(0, draft_score * 10)  # Mapping 10pt base to 100

        return {
            "research": research_raw * weights.get("research", 0.25),
            "alignment": alignment_raw * weights.get("alignment", 0.25),
            "validation": val_raw * weights.get("validation", 0.25),
            "generation": gen_raw * weights.get("generation", 0.25),
        }

    def _generate_markdown(self, states: dict, scores: dict, total: float) -> str:
        """Constructs the Audit Trail Markdown string."""
        h1 = states.get("hop1") or {}
        h4 = states.get("hop4") or {}
        h5 = states.get("hop5") or {}

        md = [
            f"# Mission Audit Report: {h1.get('recipient_name', 'Unknown')}",
            f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"**Archetype:** {h1.get('Archetype', 'N/A')} | **Route:** {h4.get('route', 'N/A')}",
            "\n## 📊 Quality Score: " + ("✅ " if total > 70 else "⚠️ ") + f"{total:.1f}/100",
            "\n### Score Breakdown",
            f"- Research Logic: {scores['research']:.1f}",
            f"- Alignment Logic: {scores['alignment']:.1f}",
            f"- Validation Gate: {scores['validation']:.1f}",
            f"- Generation Quality: {scores['generation']:.1f}",
            "\n## 📝 Generated Draft",
            "```text",
            f"{h5.get('selected_draft', {}).get('text', 'NO DRAFT GENERATED')}",
            "```",
            "\n## 🔍 Trace Logs",
            "Refer to TraceRegistry for granular execution steps.",
        ]
        return "\n".join(md)

    def _save_report(self, content: str, hop1: dict) -> Path:
        """Persists report to the configured output directory."""
        out_dir = Path(self.config.qa_report_agent.output_directory)
        out_dir.mkdir(parents=True, exist_ok=True)

        safe_name = "".join(x for x in hop1.get("recipient_name", "Report") if x.isalnum())
        filename = f"QA_{safe_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"

        report_path = out_dir / filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        return report_path
