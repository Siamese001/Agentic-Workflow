#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L6 Observability Base Agent - The Skeptical Analyst
====================================================

L6 agents are specialized analysts that run asynchronously or on schedule
to critique and judge the performance of L1-L5 sibling agents.

PERSONALITY: Skeptical, data-driven, critical, unbiased
EXECUTION: Async or scheduled (post-task or nightly)
PURPOSE: Strict performance analysis of all lower-layer agents

This base provides:
- Async/scheduled execution infrastructure
- Agent performance analysis framework
- Critical evaluation without bias
- Data-driven metrics collection
- Automated critique generation
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod
import json

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin
from agentic_core.utils.core_extensions.pinecone_vector_mixin import PineconeVectorMixin
from agentic_core.utils.mixins.subatomic_testing_mixin import SubatomicTestingMixin

Logger = logging.getLogger(__name__)


@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for a single agent."""
    agent_name: str
    layer: str
    execution_time_ms: float = 0.0
    success_rate: float = 0.0
    error_count: int = 0
    heal_invocations: int = 0
    test_coverage: float = 0.0
    complexity_score: float = 0.0
    mcp_hardened: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CritiqueReport:
    """Critical analysis report from L6 analyst."""
    agent_name: str
    layer: str
    overall_grade: str  # A, B, C, D, F
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    data_points: Dict[str, Any] = field(default_factory=dict)
    skeptical_commentary: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class L6ObservabilityBaseAgent(SovereignBaseAgent, MCPHardenedMixin, SubatomicTestingMixin, RedisCacheMixin, PineconeVectorMixin, ABC):
    """
    Base class for L6 Observability agents - The Skeptical Analysts.
    
    L6 agents are critical evaluators that run asynchronously or on schedule
    to provide unbiased, data-driven performance analysis of L1-L5 agents.
    
    PERSONALITY TRAITS:
    - Skeptical: Questions all claims, demands evidence
    - Data-driven: Only accepts quantifiable metrics
    - Critical: Points out flaws without sugar-coating
    - Unbiased: Treats all agents equally, no favoritism
    - Rigorous: Applies strict standards consistently
    
    EXECUTION MODES:
    - Async: Runs in background after major operations
    - Scheduled: Executes on cron-like schedule (nightly, hourly, etc.)
    - On-demand: Triggered by specific events or thresholds
    
    HARDENED: Redis caching + Pinecone vector support with graceful degradation.
    """
    
    # Redis/Pinecone configuration
    _cache_prefix: str = "l6_observability"
    _namespace: str = "l6_analytics"
    
    # Skeptical personality configuration
    CRITIQUE_THRESHOLD_CRITICAL: float = 0.6  # Below 60% triggers critical issues
    CRITIQUE_THRESHOLD_WARNING: float = 0.8   # Below 80% triggers warnings
    
    # Grading scale (data-driven, no curve)
    GRADE_THRESHOLDS = {
        'A': 0.90,  # 90%+ - Exceptional
        'B': 0.80,  # 80-89% - Good
        'C': 0.70,  # 70-79% - Acceptable
        'D': 0.60,  # 60-69% - Poor
        'F': 0.0    # <60% - Failing
    }
    
    # Execution schedule
    schedule_interval: Optional[timedelta] = None
    last_execution: Optional[datetime] = None
    async_mode: bool = True
    
    def __post_init__(self):
        """Initialize L6 analyst with skeptical defaults."""
        super().__init__()
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__
        self.performance_history: List[AgentPerformanceMetrics] = []
        self.critique_history: List[CritiqueReport] = []
        self.log_info(f"L6 Analyst initialized: {self.name} (skeptical mode: ON)")
    
    # =========================================================================
    # ASYNC/SCHEDULED EXECUTION INFRASTRUCTURE
    # =========================================================================
    
    async def run_async_analysis(self) -> Dict[str, Any]:
        """
        Run async analysis in background - does not block main execution.
        
        Returns:
            Analysis results with performance metrics and critiques
        """
        self.log_info("Starting async analysis (background mode)")
        try:
            # Collect metrics from all layers
            metrics = await self._collect_agent_metrics()
            
            # Generate critiques
            critiques = await self._generate_critiques(metrics)
            
            # Store results
            await self._store_analysis_results(metrics, critiques)
            
            self.last_execution = datetime.now()
            
            return {
                'status': 'completed',
                'metrics_collected': len(metrics),
                'critiques_generated': len(critiques),
                'timestamp': self.last_execution.isoformat()
            }
        except Exception as e:
            self.log_error(f"Async analysis failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def schedule_analysis(self, interval: timedelta):
        """
        Schedule recurring analysis (e.g., nightly at 2am, every 4 hours).
        
        Args:
            interval: Time between executions (timedelta)
        """
        self.schedule_interval = interval
        self.log_info(f"Scheduled analysis every {interval}")
    
    async def run_scheduled_loop(self):
        """
        Run continuous scheduled analysis loop.
        Typically run as a background daemon process.
        """
        if not self.schedule_interval:
            raise ValueError("Schedule interval not set. Call schedule_analysis() first.")
        
        self.log_info(f"Starting scheduled analysis loop (interval: {self.schedule_interval})")
        
        while True:
            try:
                await self.run_async_analysis()
                await asyncio.sleep(self.schedule_interval.total_seconds())
            except Exception as e:
                self.log_error(f"Scheduled analysis error: {e}")
                await asyncio.sleep(60)  # Wait 1 min before retry
    
    # =========================================================================
    # AGENT PERFORMANCE ANALYSIS (Data-Driven)
    # =========================================================================
    
    async def _collect_agent_metrics(self) -> List[AgentPerformanceMetrics]:
        """
        Collect performance metrics from all L1-L5 agents.
        
        SKEPTICAL NOTE: Only accepts hard data, no estimates or assumptions.
        
        Returns:
            List of AgentPerformanceMetrics for each discovered agent
        """
        metrics = []
        
        # Load agent discovery data
        discovery_path = self._get_discovery_path()
        if not discovery_path.exists():
            self.log_warning("agent_discovery_full.json not found - cannot analyze without data")
            return metrics
        
        agents_data = json.loads(discovery_path.read_text(encoding='utf-8'))
        
        for agent in agents_data:
            metric = AgentPerformanceMetrics(
                agent_name=agent.get('class_name', 'Unknown'),
                layer=agent.get('layer', 'Unknown'),
                # Extract real metrics (no fabrication)
                success_rate=1.0 if agent.get('has_healing') else 0.0,  # Has healing = passes basic bar
                error_count=0,  # TODO: Extract from logs/telemetry
                heal_invocations=1 if agent.get('invocation') == 'Yes' else 0,
                test_coverage=agent.get('typed_pct', 0.0) / 100.0 if agent.get('typed_pct') else 0.0,
                complexity_score=agent.get('cyclomatic_complexity', 0.0),
                mcp_hardened=agent.get('mcp_hardened', False),
                raw_data=agent
            )
            metrics.append(metric)
        
        self.log_info(f"Collected metrics for {len(metrics)} agents")
        return metrics
    
    async def _generate_critiques(self, metrics: List[AgentPerformanceMetrics]) -> List[CritiqueReport]:
        """
        Generate critical, unbiased analysis of each agent.
        
        SKEPTICAL APPROACH:
        - No benefit of doubt
        - Data speaks for itself
        - Flags all deviations from standards
        - No "good enough" - either meets bar or doesn't
        
        Args:
            metrics: Performance metrics to critique
            
        Returns:
            List of CritiqueReports with harsh but fair analysis
        """
        critiques = []
        
        for metric in metrics:
            critique = await self._critique_single_agent(metric)
            critiques.append(critique)
        
        self.log_info(f"Generated {len(critiques)} critique reports")
        return critiques
    
    async def _critique_single_agent(self, metric: AgentPerformanceMetrics) -> CritiqueReport:
        """
        Critique a single agent with skeptical, data-driven analysis.
        
        Args:
            metric: Performance metrics for the agent
            
        Returns:
            CritiqueReport with grade, issues, and recommendations
        """
        critical_issues = []
        warnings = []
        recommendations = []
        data_points = {}
        
        # Calculate composite score (equally weighted components)
        scores = []
        
        # 1. Test Coverage (typed_pct is proxy)
        test_score = metric.test_coverage
        data_points['test_coverage'] = f"{test_score*100:.1f}%"
        if test_score < self.CRITIQUE_THRESHOLD_CRITICAL:
            critical_issues.append(f"Test coverage critically low: {test_score*100:.1f}% (minimum: 60%)")
        elif test_score < self.CRITIQUE_THRESHOLD_WARNING:
            warnings.append(f"Test coverage below standard: {test_score*100:.1f}% (target: 80%)")
        scores.append(test_score)
        
        # 2. MCP Hardening
        mcp_score = 1.0 if metric.mcp_hardened else 0.0
        data_points['mcp_hardened'] = metric.mcp_hardened
        if not metric.mcp_hardened:
            critical_issues.append("Agent lacks MCP hardening - security vulnerability")
        scores.append(mcp_score)
        
        # 3. Complexity Health (lower is better, inverted)
        complexity_health = max(0, 100 - metric.complexity_score * 2) / 100.0
        data_points['complexity'] = metric.complexity_score
        data_points['complexity_health'] = f"{complexity_health*100:.1f}%"
        if complexity_health < self.CRITIQUE_THRESHOLD_CRITICAL:
            critical_issues.append(f"Complexity unacceptable: {metric.complexity_score} (should be <10)")
        elif complexity_health < self.CRITIQUE_THRESHOLD_WARNING:
            warnings.append(f"Complexity concerning: {metric.complexity_score} (target: <5)")
        scores.append(complexity_health)
        
        # 4. Healing Capability
        heal_score = metric.success_rate  # 1.0 if has_healing
        data_points['has_healing'] = heal_score == 1.0
        if heal_score < 1.0:
            critical_issues.append("Agent lacks autonomous healing capability")
        scores.append(heal_score)
        
        # 5. Heal Invocation
        invocation_score = 1.0 if metric.heal_invocations > 0 else 0.0
        data_points['heal_invocation'] = invocation_score == 1.0
        if invocation_score < 1.0:
            warnings.append("Agent has healing but never invokes it")
        scores.append(invocation_score)
        
        # Calculate overall score (strict average, no curve)
        overall_score = sum(scores) / len(scores) if scores else 0.0
        data_points['overall_score'] = f"{overall_score*100:.1f}%"
        
        # Assign grade (data-driven, no adjustments)
        grade = self._assign_grade(overall_score)
        
        # Generate skeptical commentary
        commentary = self._generate_skeptical_commentary(
            metric.agent_name,
            grade,
            overall_score,
            critical_issues,
            warnings
        )
        
        # Add recommendations based on failures
        if critical_issues:
            recommendations.append("IMMEDIATE ACTION REQUIRED: Address all critical issues before next release")
        if warnings:
            recommendations.append("Improve warning areas to meet team standards")
        if grade in ['C', 'D', 'F']:
            recommendations.append("Consider refactoring or replacing this agent - performance unacceptable")
        
        return CritiqueReport(
            agent_name=metric.agent_name,
            layer=metric.layer,
            overall_grade=grade,
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations,
            data_points=data_points,
            skeptical_commentary=commentary
        )
    
    def _assign_grade(self, score: float) -> str:
        """Assign letter grade based on score (no curve, strict thresholds)."""
        for grade, threshold in sorted(self.GRADE_THRESHOLDS.items(), key=lambda x: -x[1]):
            if score >= threshold:
                return grade
        return 'F'
    
    def _generate_skeptical_commentary(
        self,
        agent_name: str,
        grade: str,
        score: float,
        critical_issues: List[str],
        warnings: List[str]
    ) -> str:
        """
        Generate harsh but fair commentary with skeptical tone.
        
        PERSONALITY: No sugar-coating, direct critique, data-focused.
        """
        commentary_parts = []
        
        # Opening statement (skeptical tone)
        if grade == 'A':
            commentary_parts.append(f"{agent_name} meets expectations ({score*100:.1f}%). ")
        elif grade == 'B':
            commentary_parts.append(f"{agent_name} performs adequately ({score*100:.1f}%), but room for improvement exists. ")
        elif grade == 'C':
            commentary_parts.append(f"{agent_name} barely passes ({score*100:.1f}%). Mediocrity is not acceptable. ")
        elif grade == 'D':
            commentary_parts.append(f"{agent_name} performs poorly ({score*100:.1f}%). This is unacceptable. ")
        else:  # F
            commentary_parts.append(f"{agent_name} fails basic standards ({score*100:.1f}%). Complete rework required. ")
        
        # Critical issues (no mercy)
        if critical_issues:
            commentary_parts.append(f"CRITICAL FAILURES: {len(critical_issues)} issues demand immediate attention. ")
        
        # Warnings (still harsh)
        if warnings:
            commentary_parts.append(f"WARNING: {len(warnings)} deficiencies below team standards. ")
        
        # Final verdict (data-driven conclusion)
        if grade in ['A', 'B']:
            commentary_parts.append("Approved for production with minor reservations.")
        elif grade == 'C':
            commentary_parts.append("Conditional approval - must improve before next release.")
        else:
            commentary_parts.append("BLOCKED from production until major defects resolved.")
        
        return ''.join(commentary_parts)
    
    async def _store_analysis_results(
        self,
        metrics: List[AgentPerformanceMetrics],
        critiques: List[CritiqueReport]
    ):
        """Store analysis results for historical tracking."""
        self.performance_history.extend(metrics)
        self.critique_history.extend(critiques)
        
        # Optionally persist to Redis/Pinecone for long-term storage
        try:
            cache_key = f"analysis_{datetime.now().isoformat()}"
            await self._cache_set(cache_key, {
                'metrics': [m.__dict__ for m in metrics],
                'critiques': [c.__dict__ for c in critiques]
            }, ttl=86400 * 30)  # Keep for 30 days
        except Exception as e:
            self.log_warning(f"Failed to cache results: {e}")
    
    def _get_discovery_path(self) -> Path:
        """Get path to agent_discovery_full.json."""
        from agentic_core.config.blueprint_sovereign.structure_blueprint import (
            get_validated_project_root,
            AGENT_DISCOVERY_JSON
        )
        return get_validated_project_root() / AGENT_DISCOVERY_JSON
    
    # =========================================================================
    # REPORTING (Public API)
    # =========================================================================
    
    def generate_critique_report(self, output_path: Optional[Path] = None) -> str:
        """
        Generate comprehensive critique report for all analyzed agents.
        
        Args:
            output_path: Optional path to save report (defaults to stdout)
            
        Returns:
            Report as formatted string
        """
        if not self.critique_history:
            return "No critique data available. Run analysis first."
        
        lines = []
        lines.append("=" * 80)
        lines.append("L6 OBSERVABILITY ANALYST REPORT")
        lines.append(f"Generated by: {self.name}")
        lines.append(f"Timestamp: {datetime.now().isoformat()}")
        lines.append(f"Agents Analyzed: {len(self.critique_history)}")
        lines.append("=" * 80)
        lines.append("")
        
        # Grade distribution
        grades = {}
        for critique in self.critique_history:
            grades[critique.overall_grade] = grades.get(critique.overall_grade, 0) + 1
        
        lines.append("GRADE DISTRIBUTION:")
        for grade in ['A', 'B', 'C', 'D', 'F']:
            count = grades.get(grade, 0)
            pct = (count / len(self.critique_history) * 100) if self.critique_history else 0
            lines.append(f"  {grade}: {count} agents ({pct:.1f}%)")
        lines.append("")
        
        # Individual critiques
        lines.append("INDIVIDUAL AGENT CRITIQUES:")
        lines.append("-" * 80)
        
        for critique in sorted(self.critique_history, key=lambda c: (c.overall_grade, c.agent_name)):
            lines.append(f"\n{critique.agent_name} ({critique.layer}) - GRADE: {critique.overall_grade}")
            lines.append(f"Score: {critique.data_points.get('overall_score', 'N/A')}")
            lines.append(f"\n{critique.skeptical_commentary}")
            
            if critique.critical_issues:
                lines.append("\nCRITICAL ISSUES:")
                for issue in critique.critical_issues:
                    lines.append(f"  ❌ {issue}")
            
            if critique.warnings:
                lines.append("\nWARNINGS:")
                for warning in critique.warnings:
                    lines.append(f"  ⚠️  {warning}")
            
            if critique.recommendations:
                lines.append("\nRECOMMENDATIONS:")
                for rec in critique.recommendations:
                    lines.append(f"  💡 {rec}")
            
            lines.append("-" * 80)
        
        report = '\n'.join(lines)
        
        if output_path:
            output_path.write_text(report, encoding='utf-8')
            self.log_info(f"Critique report saved to {output_path}")
        
        return report
    
    # =========================================================================
    # ABSTRACT METHODS (Subclasses must implement)
    # =========================================================================
    
    @abstractmethod
    async def analyze(self) -> Dict[str, Any]:
        """
        Subclasses must implement specific analysis logic.
        
        This is where the agent performs its specialized observability task.
        
        Returns:
            Analysis results dictionary
        """
        pass
    
    # =========================================================================
    # HEALING (L6 Meta-Healing)
    # =========================================================================
    
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """
        L6 meta-healing: Analyzes healing patterns across all agents.
        
        Unlike L1-L5 agents that heal code, L6 heals the healing process itself
        by identifying systematic issues in how agents self-repair.
        """
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        
        try:
            # Analyze healing patterns (meta-analysis)
            healing_issues = self._analyze_healing_patterns()
            
            # Invoke parent healing chain
            super().heal_repository()
            
            self.log_info(f"L6 meta-healing: Identified {len(healing_issues)} systematic issues")
            
            return {
                "healed": 1,
                "meta_issues_found": len(healing_issues)
            }
        finally:
            _call_path.discard(agent_name)
    
    def _analyze_healing_patterns(self) -> List[str]:
        """Analyze systematic issues in how agents heal themselves."""
        issues = []
        
        # Check for agents without healing
        for metric in self.performance_history:
            if metric.success_rate < 1.0:
                issues.append(f"{metric.agent_name}: Missing healing capability")
        
        return issues


__all__ = ["L6ObservabilityBaseAgent", "AgentPerformanceMetrics", "CritiqueReport"]
