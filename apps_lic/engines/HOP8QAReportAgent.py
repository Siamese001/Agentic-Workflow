# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, validator, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations

from dataclasses import dataclass

"""HOP-8: QA Report Agent - Persistent markdown report generation."""

__version__ = "13.1"

from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from apps_shared.utils.state_manager import StateManager

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout


@dataclass
class HOP8QAReportAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    v13.1: QA Report Agent - Persistent markdown report generation (MCP Hardened)

    Single Responsibility: Generate audit trail report

    Input:  state/* (all state files)
    Output: outputs/QA_Report.md
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize the QA report agent.

        Args:
            config: Configuration dictionary containing qa_report_agent settings
        """
        super().__init__()
        self.config: dict[str, Any] = config["qa_report_agent"]
        self.sections: list = self.config["report_sections"]
        self.scoring_weights: dict[str, float] = self.config["scoring_weights"]

    async def execute(self, state_mgr: StateManager) -> str:
        """
        Execute HOP-8: Generate comprehensive QA report.

        Args:
            state_mgr: State manager containing mission states

        Returns:
            Path to generated QA report file
        """
        print(f"\nimport logging\n\nLogger = logging.getLogger(__name__)\n{'=' * 80}")
        print("HOP-8: QA REPORT GENERATION")
        print(f"{'=' * 80}\n")

        states: dict[str, Any] = {}
        for hop_id in ["HOP-1", "HOP-2", "HOP-3", "HOP-4", "HOP-5", "HOP-6", "HOP-7"]:
            if state_mgr.state_exists(hop_id):
                states[hop_id] = state_mgr.read_state(hop_id)

        print(f"Synthesizing report from {len(states)} state files...")

        report: str = self._generate_markdown_report(states, state_mgr.mission_id)

        output_dir: Path = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        report_path = output_dir / f"QA_Report_{state_mgr.mission_id}.md"

        with open(report_path, "w") as f:
            f.write(report)

        print(f"\n✓ QA Report Generated: {report_path}\n")

        return str(report_path)

    def _generate_markdown_report(self, states: dict[str, Any], mission_id: str) -> str:
        """
        Generate comprehensive markdown report from mission states.

        Args:
            states: Dictionary of HOP states
            mission_id: Unique mission identifier

        Returns:
            Markdown-formatted report string
        """
        lines: list = []

        lines.append("# LIC v13.0 QA Report")
        lines.append(f"\n**Mission ID**: `{mission_id}`")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("\n---\n")

        # 1. Executive Summary
        lines.append("## 1. Executive Summary\n")
        validation = states.get("HOP-6", {})
        passed = validation.get("passed", False)

        if passed:
            lines.append("**Status**: ✅ **PASS** - Message ready for production")
        else:
            lines.append("**Status**: ❌ **FAIL** - Message requires revision")

        lines.append(f"\n**Critical Issues**: {validation.get('critical_issues', 0)}")
        lines.append(f"**High Issues**: {validation.get('high_issues', 0)}")
        lines.append(f"**Medium Issues**: {validation.get('medium_issues', 0)}")
        lines.append("\n")

        # 2. Archetype & Route Selection
        lines.append("## 2. Archetype & Route Selection\n")
        profile = states.get("HOP-1", {})
        routing = states.get("HOP-4", {})

        lines.append(f"**Archetype**: {profile.get('Archetype', 'N/A')}")
        lines.append(f"**Confidence**: {profile.get('confidence', 0):.2f}")
        lines.append(f"**Reasoning**: {profile.get('reasoning', 'N/A')}")
        lines.append(f"\n**Route**: {routing.get('Route', 'N/A')}")
        lines.append(f"**Route Reasoning**: {routing.get('reasoning', 'N/A')}")
        lines.append("\n")

        # 3. Research Quality Assessment
        lines.append("## 3. Research Quality Assessment\n")
        research = states.get("HOP-2", {})
        lines.append(f"**Total Sources**: {research.get('total_sources', 0)}")
        lines.append(f"**Signal Score**: {research.get('signal_score', 0):.2f}")
        lines.append(
            f"**Cache Hit**: {'Yes' if research.get('cache_hit', False) else 'No (Fallback RAG used)'}"
        )
        lines.append(
            f"**Fallback Used**: {'Yes' if research.get('fallback_used', False) else 'No'}"
        )
        lines.append("\n")

        # 4. Generation Strategy
        lines.append("## 4. Generation Strategy\n")
        generation = states.get("HOP-5", {})
        lines.append(f"**Candidates Generated**: {generation.get('n_candidates', 1)}")
        lines.append(f"**Temperature**: {generation.get('generation_temperature', 0.5):.2f}")
        lines.append(f"**Generation Attempts**: {generation.get('generation_attempts', 1)}")
        lines.append("\n")

        # 5. Validation Results
        lines.append("## 5. Validation Results\n")
        results = validation.get("validation_results", [])
        lines.append(f"**Total Rules Checked**: {len(results)}")
        lines.append("\n### Failed Checks:\n")

        failed = [r for r in results if not r.get("passed", True)]
        if failed:
            for result in failed:
                lines.append(
                    f"- **{result['rule_id']}** ({result['Severity']}): {result['message']}"
                )
        else:
            lines.append("_No failed checks_")
        lines.append("\n")

        # 6. Loop Execution Details
        lines.append("## 6. Loop Execution Details\n")
        gate = states.get("HOP-7", {})
        lines.append(f"**Factual Loops (S6→S2)**: {gate.get('factual_loop_count', 0)}")
        lines.append(f"**Creative Retries (S5)**: {gate.get('creative_retry_count', 0)}")
        lines.append(f"**Gate Decision**: {gate.get('decision', 'N/A')}")
        lines.append("\n")

        # 7. Final Message
        lines.append("## 7. Final Generated Message\n")
        draft = generation.get("selected_draft", {})
        lines.append(f"**Word Count**: {draft.get('word_count', 0)}")
        lines.append(f"**Character Count**: {draft.get('char_count', 0)}")
        lines.append("\n```")
        lines.append(draft.get("text", "N/A"))
        lines.append("```\n")

        # 8. Quality Score
        lines.append("## 8. Overall Quality Score\n")
        score = self._calculate_quality_score(states)
        lines.append(f"**Final Score**: {score:.1f}/100")
        lines.append("\n---")
        lines.append("\n*Generated by LIC v13.0 QA Report Agent*")

        return "\n".join(lines)

    def _calculate_quality_score(self, states: dict[str, Any]) -> float:
        """Calculate overall quality score"""
        research = states.get("HOP-2", {})
        validation = states.get("HOP-6", {})
        gate = states.get("HOP-7", {})

        research_score = min(30, research.get("signal_score", 0.5) * 30)

        passed = validation.get("passed", False)
        critical = validation.get("critical_issues", 0)
        alignment_score = 30 if passed and critical == 0 else 0

        results = validation.get("validation_results", [])
        passed_count = sum(1 for r in results if r.get("passed", False))
        total_count = len(results) if results else 1
        validation_score = (passed_count / total_count) * 20

        factual_loops = gate.get("factual_loop_count", 0)
        creative_retries = gate.get("creative_retry_count", 0)
        loop_penalty = (factual_loops * 3) + (creative_retries * 2)
        loop_score = max(0, 10 - loop_penalty)

        generation = states.get("HOP-5", {})
        draft = generation.get("selected_draft", {})
        word_count = draft.get("word_count", 0)
        in_range = 150 <= word_count <= 300
        generation_score = 10 if in_range else 5

        total_score = (
            research_score + alignment_score + validation_score + loop_score + generation_score
        )
        return total_score

    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set = None,
    ) -> dict[str, int]:
        """Operational agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        super().heal_repository(
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path,
        )
        print(f"[{self.__class__.__name__}] Operational agent - healing chain invoked")
        return {"skipped": 1}
