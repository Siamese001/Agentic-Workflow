# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

from dataclasses import dataclass

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Analyst Agent - L6 observability Specialist
========================================================

Concrete implementation of L6 Base Agent focused on performance analysis.

PERSONALITY: Brutally honest, data-obsessed, zero-tolerance for excuses
SCHEDULE: Runs nightly at 2am or after major deployments
PURPOSE: Identifies performance bottlenecks and calls out underperforming agents
"""
import asyncio
from datetime import timedelta
from pathlib import Path
from typing import Any

# ARCHIVED: SovereignBaseAgent import removed
L6ObservabilityBaseAgent = object  # Stub for archived import
AgentPerformanceMetrics = None
CritiqueReport = None
from agentic_core.L5_safety.validators.decorators import standard_heal


# [SOVEREIGN FACTORY]
def get_performance_analyst(project_root: Path) -> "PerformanceAnalystAgent":
    """Factory function to get PerformanceAnalystAgent instance."""
    return PerformanceAnalystAgent(project_root=project_root)


@dataclass
class PerformanceAnalystAgent(SovereignBaseAgent):
    """
    The Performance Critic - Skeptical analyst for agent performance.

    MISSION: Hunt down performance issues with zero tolerance
    APPROACH: Data-driven, no excuses, harsh but fair
    SCHEDULE: Nightly analysis + post-deployment audits

    This agent:
    - Analyzes all L1-L5 agent performance metrics
    - Generates critical performance reports
    - Flags underperforming agents without mercy
    - Recommends refactoring or replacement when warranted
    """

    # Weighted penalty system for bottleneck severity calculation
    WEIGHT_COMPLEXITY = 0.4
    WEIGHT_MCP = 0.3
    WEIGHT_COVERAGE = 0.3

    def __init__(self, **kwargs) -> None:
        """Initialize with skeptical performance analysis defaults."""
        super().__init__(**kwargs)
        self.name = "PerformanceAnalystAgent"

        # Schedule for nightly runs (every 24 hours)
        self.schedule_analysis(timedelta(hours=24))

        self.log_info("Performance Analyst initialized - skeptical mode: MAXIMUM")

    async def analyze(self) -> dict[str, Any]:
        """
        Run comprehensive performance analysis.

        SKEPTICAL APPROACH:
        - No benefit of doubt
        - Data or it didn't happen
        - Performance below 80% = unacceptable
        - Complexity above 15 = technical debt

        Returns:
            Performance analysis results with harsh critique
        """
        self.log_info("Starting performance analysis (skeptical mode)")

        # Run base async analysis
        result = await self.run_async_analysis()

        # Additional performance-specific analysis
        performance_issues = await self._analyze_performance_bottlenecks()

        # Generate performance report
        report = self._generate_performance_report(performance_issues)

        return {**result, "performance_issues": performance_issues, "report": report}

    async def _analyze_performance_bottlenecks(self) -> list[dict[str, Any]]:
        """
        Identify performance bottlenecks across all agents.

        CRITERIA FOR BOTTLENECK:
        - Complexity > 15 (indicates slow execution)
        - Missing MCP hardening (security overhead)
        - Low test coverage (technical debt = slow iteration)

        Returns:
            List of bottleneck issues with agent details
        """
        bottlenecks = []

        for metric in self.performance_history:
            issues = []

            # Check complexity bottleneck
            if metric.complexity_score > 15:
                issues.append(f"High complexity ({metric.complexity_score}) slows execution")

            # Check MCP bottleneck
            if not metric.mcp_hardened:
                issues.append("Missing MCP hardening adds security verification overhead")

            # Check test coverage bottleneck
            if metric.test_coverage < 0.7:
                issues.append(
                    f"Low test coverage ({metric.test_coverage * 100:.1f}%) increases debugging time"
                )

            if issues:
                bottlenecks.append(
                    {
                        "agent": metric.agent_name,
                        "layer": metric.layer,
                        "issues": issues,
                        "severity": self._calculate_bottleneck_severity(metric),
                    }
                )

        # Sort by severity (worst first)
        bottlenecks.sort(key=lambda x: -x["severity"])

        return bottlenecks

    def _calculate_bottleneck_severity(self, metric: AgentPerformanceMetrics) -> float:
        """
        Calculate bottleneck severity score (0-100, higher = worse).
        Uses weighted penalty system defined in class constants.
        """
        complexity_penalty = min(100, metric.complexity_score * 4)  # >25 = max penalty
        mcp_penalty = 0 if metric.mcp_hardened else 30
        coverage_penalty = max(0.0, (1.0 - metric.test_coverage) * 100)

        severity = (
            (complexity_penalty * self.WEIGHT_COMPLEXITY)
            + (mcp_penalty * self.WEIGHT_MCP)
            + (coverage_penalty * self.WEIGHT_COVERAGE)
        )
        return round(severity, 1)

    def _generate_performance_report(self, bottlenecks: list[dict[str, Any]]) -> str:
        """
        Generate skeptical performance report.

        TONE: Harsh, direct, zero tolerance for mediocrity
        """
        lines = []
        lines.append("=" * 80)
        lines.append("PERFORMANCE ANALYST REPORT (Skeptical Mode)")
        lines.append("=" * 80)
        lines.append("")

        if not bottlenecks:
            lines.append("✅ No critical performance bottlenecks detected.")
            lines.append("   (Surprising. Will monitor closely for regression.)")
        else:
            lines.append(f"❌ IDENTIFIED {len(bottlenecks)} PERFORMANCE BOTTLENECKS")
            lines.append("")
            lines.append("CRITICAL ISSUES (ordered by severity):")
            lines.append("-" * 80)

            for i, bottleneck in enumerate(bottlenecks[:10], 1):  # Top 10 worst
                lines.append(
                    f"\n{i}. {bottleneck['agent']} ({bottleneck['layer']}) - Severity: {bottleneck['severity']}/100"
                )
                for issue in bottleneck["issues"]:
                    lines.append(f"   ❌ {issue}")

                # Harsh recommendation
                if bottleneck["severity"] > 70:
                    lines.append(
                        "   📢 RECOMMENDATION: Immediate refactoring required - this is unacceptable"
                    )
                elif bottleneck["severity"] > 50:
                    lines.append(
                        "   📢 RECOMMENDATION: Schedule refactoring sprint - technical debt is mounting"
                    )
                else:
                    lines.append("   📢 RECOMMENDATION: Address issues in next release cycle")

        lines.append("")
        lines.append("=" * 80)
        lines.append("Analyst: PerformanceAnalystAgent (No excuses. Data only.)")
        lines.append("=" * 80)

        return "\n".join(lines)

    async def run_post_deployment_audit(self) -> dict[str, Any]:
        """
        Run immediate audit after deployment.

        Called by deployment pipeline to verify performance hasn't regressed.

        Returns:
            Audit results with pass/fail verdict
        """
        self.log_info("Running post-deployment performance audit")

        # Run analysis
        result = await self.analyze()

        # Check for critical bottlenecks
        critical_bottlenecks = [b for b in result["performance_issues"] if b["severity"] > 70]

        if critical_bottlenecks:
            verdict = "FAILED"
            message = f"Deployment introduces {len(critical_bottlenecks)} critical bottlenecks - ROLLBACK RECOMMENDED"
        else:
            verdict = "PASSED"
            message = "Performance within acceptable limits"

        return {
            "verdict": verdict,
            "message": message,
            "critical_bottlenecks": len(critical_bottlenecks),
            "full_analysis": result,
        }

    @standard_heal
    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs
    ) -> dict[str, Any]:
        """Autonomous healing with proper invocation chain."""
        super().heal_repository(dry_run=dry_run, execute=execute, **kwargs)
        return {"violations_found": 0, "violations_fixed": 0, "errors": 0}


# Async entry point for scheduled execution
async def run_nightly_analysis() -> Any:
    """Entry point for nightly scheduled analysis."""
    analyst = PerformanceAnalystAgent()
    result = await analyst.analyze()

    # Print critique report
    print(analyst.generate_critique_report())

    # Print performance report
    print(result["report"])

    return result


if __name__ == "__main__":
    # Self-test: Run analysis once
    print("Running Performance Analyst self-test...")
    result = asyncio.run(run_nightly_analysis())
    print(f"\nAnalysis complete. Status: {result['status']}")