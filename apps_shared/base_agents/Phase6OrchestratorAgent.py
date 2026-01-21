from dataclasses import dataclass
"""
Phase6OrchestratorAgent - Extracted for one-class-per-file pattern.

Originally from: UnifiedOrchestratorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations

@dataclass
class Phase6OrchestratorAgent(MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin):
    """
    Orchestrates all Phase 6 intelligence components.

    Combines:
    - Security hardening
    - Semantic analysis
    - Strategic advising
    - Context management
    - Unified orchestration
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        """
        Initialize Phase 6 orchestrator.

        Args:
            ctx: Resume engine context for coordination

        Initializes all Phase 6 intelligence components including security,
        semantic analysis, strategic advising, and unified orchestration.
        """
        self.ctx = ctx

        self.security = SecurityHardener(ctx)
        self.semantic = SemanticAnalyzer(ctx)
        self.strategic = StrategicAdvisor(ctx)
        self.omni = OmniContext(ctx)
        self.unified = UnifiedOrchestratorAgent(ctx)

    async def analyze_resume(
        self,
        resume: Dict[str, Any],
        JobDescription: str = "",
    ) -> Dict[str, Any]:
        """
        Perform comprehensive resume analysis.

        Args:
            resume: Resume dictionary
            JobDescription: Optional job description

        Returns:
            Comprehensive analysis results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "security": {},
            "semantic": {},
            "strategic": {},
            "recommendations": [],
        }

        # Security scan
        security_issues = self.security.scan_resume(resume)
        results["security"] = {
            "issues": len(security_issues),
            "high_severity": len(self.security.get_issues_by_severity("high")),
        }

        # Build context
        self.omni.build_context(resume)

        # Semantic analysis
        semantic_result = self.semantic.analyze_resume(resume)
        results["semantic"] = {
            "overall_score": semantic_result["overall_score"],
            "sections_analyzed": len(semantic_result["sections"]),
        }

        # Strategic analysis
        proposals = self.strategic.analyze_structure(resume)
        ats_recs = self.strategic.get_ats_recommendations(resume, JobDescription)

        results["strategic"] = {
            "proposals": len(proposals),
            "ats_recommendations": len(ats_recs),
        }

        # Compile recommendations
        results["recommendations"].extend(semantic_result["recommendations"])
        results["recommendations"].extend(ats_recs)

        return results

    async def run_full_mission(
        self,
        resume: Dict[str, Any],
        JobDescription: str = "",
        max_cycles: int = 3,
    ) -> Dict[str, Any]:
        """
        Run a full intelligence mission.

        Args:
            resume: Resume dictionary
            JobDescription: Optional job description
            max_cycles: Maximum cycles

        Returns:
            Mission results
        """
        return await self.unified.run_mission(resume, JobDescription, max_cycles)

    def search_context(self, query: str) -> List[SemanticMatch]:
        """Search the context for relevant content."""
        return self.omni.search(query)

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components."""
        return {
            "security": self.security.get_stats(),
            "semantic": self.semantic.get_stats(),
            "strategic": self.strategic.get_stats(),
            "omni": self.omni.get_stats(),
            "unified": self.unified.get_comprehensive_stats(),
        }

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
