from dataclasses import dataclass

"""
Phase7OrchestratorAgent - Extracted for one-class-per-file pattern.

Originally from: StrictDocEnforcerAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations


@dataclass
class Phase7OrchestratorAgent(MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin):
    """
    Orchestrates all Phase 7 governance components.

    Combines:
    - Dependency arbitration
    - Documentation enforcement
    - Dashboard generation
    - Prompt governance
    - Predictive budgeting
    """

    def __init__(self, ctx: ResumeEngineContext, budget_limit: float = 1.0) -> None:
        """
        Initialize Phase 7 orchestrator.

        Args:
            ctx: Resume engine context for coordination
            budget_limit: Budget limit for cost prediction (default 1.0)

        Initializes all Phase 7 governance components including dependency
        arbitration, documentation enforcement, and dashboard generation.
        """
        self.ctx = ctx

        self.dependency = DependencyArbiter(ctx)
        self.doc_enforcer = StrictDocEnforcerAgent(ctx)
        self.dashboard = DashboardGenerator(ctx)
        self.prompt_gov = PromptGovernor(ctx)
        self.budget = PredictiveBudgetManager(ctx, budget_limit)

    def check_dependencies(self) -> List[DependencyIssue]:
        """Check environment dependencies."""
        return self.dependency.check_environment()

    def check_documentation(self, content: str, file_path: str = "unknown") -> List[DocViolation]:
        """Check documentation compliance."""
        return self.doc_enforcer.check_content(content, file_path)

    def scan_prompts(self, content: str, file_path: str = "unknown") -> List[PromptIssue]:
        """Scan for prompt security issues."""
        return self.prompt_gov.scan_content(content, file_path)

    def predict_mission_cost(
        self,
        files_count: int,
        agents_count: int,
        cycles: int = 1,
    ) -> CostPrediction:
        """Predict cost for a mission."""
        return self.budget.predict_cost(files_count, agents_count, cycles)

    def generate_dashboard(
        self,
        results: Dict[str, Any],
        signals: Set[str],
        output_path: str = "observability/mission_control.html",
    ) -> str:
        """Generate mission control dashboard."""
        return self.dashboard.generate(results, signals, output_path)

    async def run_governance_checks(
        self,
        content: str,
        file_path: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Run all governance checks on content.

        Args:
            content: Python source code
            file_path: Path for reporting

        Returns:
            Comprehensive governance results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "dependencies": {},
            "documentation": {},
            "prompts": {},
            "passed": True,
        }

        # Check dependencies (environment-wide)
        dep_issues = self.dependency.check_environment()
        results["dependencies"] = {
            "issues": len(dep_issues),
            "conflicts": len(self.dependency.get_issues_by_status(DependencyStatus.CONFLICT)),
        }

        # Check documentation
        doc_violations = self.doc_enforcer.check_content(content, file_path)
        results["documentation"] = {
            "violations": len(doc_violations),
            "compliance_level": self.doc_enforcer.get_compliance_level(content).value,
        }

        # Scan prompts
        prompt_issues = self.prompt_gov.scan_content(content, file_path)
        results["prompts"] = {
            "issues": len(prompt_issues),
            "high_risk": len(self.prompt_gov.get_issues_by_risk(PromptRisk.HIGH)),
            "critical_risk": len(self.prompt_gov.get_issues_by_risk(PromptRisk.CRITICAL)),
        }

        # Determine overall pass/fail
        results["passed"] = (
            len(self.dependency.get_issues_by_status(DependencyStatus.CONFLICT)) == 0
            and len(self.prompt_gov.get_issues_by_risk(PromptRisk.CRITICAL)) == 0
        )

        return results

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components."""
        return {
            "dependency": self.dependency.get_stats(),
            "documentation": self.doc_enforcer.get_stats(),
            "dashboard": self.dashboard.get_stats(),
            "prompts": self.prompt_gov.get_stats(),
            "budget": self.budget.get_stats(),
        }

    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()
