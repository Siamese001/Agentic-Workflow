
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, healer, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
"""
⚛️ Predictive Cost Auditor - The Efficiency Guard

Monitors Atomic Blackboard to track Economic ROI of healing efforts.
Identifies "Healing Sinks" where token spending exceeds value threshold.

Mission: Provide Go/No-Go signals for pipeline deployment
Strategy: Thermal mapping of repository to identify technical debt hotspots

Tracks: Token usage per file, healing attempts, success rates
Flags: Files consuming excessive tokens without reaching PASS state
Suggests: Where manual Atomic Fission would be more cost-effective
"""
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.L2_execution.ToolRegistry.base import SubAtomicAgent
from agentic_core.utils.core_extensions.timeout_decorator import timeout

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

Logger: Any = logging.getLogger(__name__)

@dataclass
class HealingMetrics:
    """Metrics for a single healing attempt."""
    file_path: str
    attempt_number: int
    tokens_used: int
    success: bool
    key_id: int
    timestamp: str
    model_used: str

@dataclass
class FileAudit:
    """Audit record for a single file."""
    file_path: str
    total_attempts: int
    total_tokens: int
    successful_attempts: int
    failed_attempts: int
    success_rate: float
    average_tokens_per_attempt: float
    is_healing_sink: bool
    sink_severity: str
    Recommendation: str

@dataclass
class CostReport:
    """Comprehensive cost report."""
    total_files: int
    total_attempts: int
    total_tokens: int
    successful_files: int
    failed_files: int
    healing_sinks: List[FileAudit]
    efficiency_score: float
    estimated_cost_usd: float
    recommendations: List[str]

# NAMING CANON ETERNAL — renamed for sovereign discovery — Phase 3 — 2025-12-30
class PredictiveCostAuditorAgent(MCPHardenedMixin, SubatomicTestingMixin, SubAtomicAgent):
    """
    The Efficiency Guard - Predictive Cost Auditor
    
    Monitors economic ROI of swarm healing efforts.
    Provides thermal map of repository identifying technical debt hotspots.
    
    Thresholds:
    - Healing Sink: >3 attempts without success
    - Critical Sink: >$5 in tokens without success
    - Fission Candidate: >$10 total tokens spent
    
    Provides:
    - Daily Mission Report
    - Go/No-Go signals for pipeline
    - Atomic Fission recommendations
    - Cost optimization strategies
    """

    def __init__(self, ctx: Any) -> None:
        """
        Initialize Predictive Cost Auditor.
        
        Args:
            ctx: ValidationContext
        """
        super().__init__(ctx)
        self.HEALING_SINK_ATTEMPTS = 3
        self.CRITICAL_SINK_COST = 5.0
        self.FISSION_CANDIDATE_COST = 10.0
        self.TOKEN_COST_PER_1K = 0.001
        self.healing_history: Dict[str, List[HealingMetrics]] = {}
        self.file_audits: Dict[str, FileAudit] = {}

    async def execute(self) -> Any:
        """
        Execute cost auditing.
        
        Analyzes healing history and generates cost report.
        """
        Logger.info('💰 Predictive Cost Auditor: Analyzing healing economics...')
        self._load_healing_history()
        self._audit_files()
        report: Any = self._generate_cost_report()
        self._display_report(report)
        if not hasattr(self.ctx, 'cost_reports'):
            self.ctx.cost_reports = []
        self.ctx.cost_reports.append(report)

    def _load_healing_history(self) -> Any:
        """Load healing history from context."""
        if not hasattr(self.ctx, 'healing_history'):
            Logger.warning('   No healing history available')
            return
        for file_path, history in self.ctx.healing_history.items():
            if file_path not in self.healing_history:
                self.healing_history[file_path] = []
            for key_id, data in history.items():
                metrics = HealingMetrics(file_path=file_path, attempt_number=data.get('round', 1), tokens_used=data.get('tokens_used', 0), success=data.get('status') == 'PASS', key_id=key_id, timestamp=data.get('timestamp', datetime.now(timezone.utc).isoformat()), model_used=data.get('model', 'unknown'))
                self.healing_history[file_path].append(metrics)

    def _audit_files(self) -> Any:
        """Audit each file for cost efficiency."""
        for file_path, metrics_list in self.healing_history.items():
            audit = self._audit_single_file(file_path, metrics_list)
            self.file_audits[file_path] = audit

    def _audit_single_file(self, file_path: str, metrics_list: List[HealingMetrics]) -> FileAudit:
        """Audit a single file."""
        total_attempts = len(metrics_list)
        total_tokens = sum((m.tokens_used for m in metrics_list))
        successful_attempts = sum((1 for m in metrics_list if m.success))
        failed_attempts = total_attempts - successful_attempts
        success_rate = successful_attempts / total_attempts * 100 if total_attempts > 0 else 0
        avg_tokens = total_tokens / total_attempts if total_attempts > 0 else 0
        cost_usd = total_tokens / 1000 * self.TOKEN_COST_PER_1K
        is_healing_sink = failed_attempts >= self.HEALING_SINK_ATTEMPTS or cost_usd >= self.CRITICAL_SINK_COST
        if cost_usd >= self.FISSION_CANDIDATE_COST:
            sink_severity = 'critical'
        elif cost_usd >= self.CRITICAL_SINK_COST:
            sink_severity = 'high'
        elif failed_attempts >= self.HEALING_SINK_ATTEMPTS:
            sink_severity = 'medium'
        elif failed_attempts > 0:
            sink_severity = 'low'
        else:
            sink_severity = 'none'
        Recommendation = self._generate_recommendation(file_path, total_attempts, cost_usd, success_rate, sink_severity)
        return FileAudit(file_path=file_path, total_attempts=total_attempts, total_tokens=total_tokens, successful_attempts=successful_attempts, failed_attempts=failed_attempts, success_rate=success_rate, average_tokens_per_attempt=avg_tokens, is_healing_sink=is_healing_sink, sink_severity=sink_severity, Recommendation=Recommendation)

    def _generate_recommendation(self, file_path: str, attempts: int, cost_usd: float, success_rate: float, Severity: str) -> str:
        """Generate Recommendation for file."""
        if Severity == 'critical':
            return f'CRITICAL: Apply Atomic Fission - ${cost_usd:.2f} spent, {attempts} attempts'
        elif Severity == 'high':
            return f'HIGH: Consider manual refactoring - ${cost_usd:.2f} spent'
        elif Severity == 'medium':
            return f'MEDIUM: Monitor closely - {attempts} failed attempts'
        elif Severity == 'low':
            return f'LOW: Continue automated healing'
        else:
            return 'GOOD: Efficient healing'

    def _generate_cost_report(self) -> CostReport:
        """Generate comprehensive cost report."""
        total_files = len(self.file_audits)
        total_attempts = sum((audit.total_attempts for audit in self.file_audits.values()))
        total_tokens = sum((audit.total_tokens for audit in self.file_audits.values()))
        successful_files = sum((1 for audit in self.file_audits.values() if audit.success_rate == 100))
        failed_files = sum((1 for audit in self.file_audits.values() if audit.success_rate == 0))
        healing_sinks = [audit for audit in self.file_audits.values() if audit.is_healing_sink]
        healing_sinks.sort(key=lambda x: x.total_tokens, reverse=True)
        if total_attempts > 0:
            success_count = sum((audit.successful_attempts for audit in self.file_audits.values()))
            efficiency_score = success_count / total_attempts * 100
        else:
            efficiency_score = 0
        estimated_cost_usd = total_tokens / 1000 * self.TOKEN_COST_PER_1K
        recommendations = self._generate_global_recommendations(healing_sinks, efficiency_score, estimated_cost_usd)
        return CostReport(total_files=total_files, total_attempts=total_attempts, total_tokens=total_tokens, successful_files=successful_files, failed_files=failed_files, healing_sinks=healing_sinks, efficiency_score=efficiency_score, estimated_cost_usd=estimated_cost_usd, recommendations=recommendations)

    def _generate_global_recommendations(self, healing_sinks: List[FileAudit], efficiency_score: float, cost_usd: float) -> List[str]:
        """Generate global recommendations."""
        recommendations = []
        if efficiency_score < 50:
            recommendations.append(f'[!]  Low efficiency ({efficiency_score:.1f}%) - Review healing strategy')
        if cost_usd > 50:
            recommendations.append(f'[!]  High cost (${cost_usd:.2f}) - Consider batch optimization')
        critical_sinks = [s for s in healing_sinks if s.sink_severity == 'critical']
        if critical_sinks:
            recommendations.append(f'🔴 {len(critical_sinks)} critical healing sinks - Apply Atomic Fission immediately')
        high_sinks = [s for s in healing_sinks if s.sink_severity == 'high']
        if high_sinks:
            recommendations.append(f'[!]  {len(high_sinks)} high-cost files - Consider manual refactoring')
        if not recommendations:
            recommendations.append('[OK] Healing efficiency is optimal')
        return recommendations

    def _display_report(self, report: CostReport) -> Any:
        """Display cost report."""
        Logger.info(f"\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin\n{'=' * 80}")
        Logger.info('💰 PREDICTIVE COST AUDIT REPORT')
        Logger.info(f"{'=' * 80}")
        Logger.info(f'Total Files Analyzed: {report.total_files}')
        Logger.info(f'Total Healing Attempts: {report.total_attempts}')
        Logger.info(f'Total Tokens Used: {report.total_tokens:,}')
        Logger.info(f'Estimated Cost: ${report.estimated_cost_usd:.2f}')
        Logger.info(f'')
        Logger.info(f'Success Metrics:')
        Logger.info(f'  Successful Files: {report.successful_files}')
        Logger.info(f'  Failed Files: {report.failed_files}')
        Logger.info(f'  Efficiency Score: {report.efficiency_score:.1f}%')
        Logger.info(f'')
        Logger.info(f'Healing Sinks: {len(report.healing_sinks)}')
        if report.healing_sinks:
            Logger.warning(f'\n[!]  TOP HEALING SINKS (by token usage):')
            for i, sink in enumerate(report.healing_sinks[:10], 1):
                cost = sink.total_tokens / 1000 * self.TOKEN_COST_PER_1K
                Logger.warning(f'  {i}. {sink.file_path}')
                Logger.warning(f'     Tokens: {sink.total_tokens:,} (${cost:.2f}) | Attempts: {sink.total_attempts} | Success Rate: {sink.success_rate:.0f}%')
                Logger.warning(f'     → {sink.Recommendation}')
            if len(report.healing_sinks) > 10:
                Logger.warning(f'  ... and {len(report.healing_sinks) - 10} more sinks')
        if report.recommendations:
            Logger.info(f'\n[PLAN] RECOMMENDATIONS:')
            for rec in report.recommendations:
                Logger.info(f'  {rec}')
        Logger.info(f"{'=' * 80}\n")

    def get_thermal_map(self) -> Dict[str, str]:
        """
        Generate thermal map of repository.
        
        Returns:
            Dictionary mapping file paths to thermal status
            (cold, warm, hot, critical)
        """
        thermal_map: Any = {}
        for file_path, audit in self.file_audits.items():
            if audit.sink_severity == 'critical':
                thermal_map[file_path] = '🔴 CRITICAL'
            elif audit.sink_severity == 'high':
                thermal_map[file_path] = '🟠 HOT'
            elif audit.sink_severity == 'medium':
                thermal_map[file_path] = '🟡 WARM'
            else:
                thermal_map[file_path] = '🟢 COLD'
        return thermal_map

    def get_fission_candidates(self) -> List[str]:
        """Get list of files that should undergo Atomic Fission."""
        candidates: Any = []
        for file_path, audit in self.file_audits.items():
            cost: Any = audit.total_tokens / 1000 * self.TOKEN_COST_PER_1K
            if cost >= self.FISSION_CANDIDATE_COST:
                candidates.append(file_path)
        return candidates

    def generate_daily_mission_report(self) -> str:
        """Generate daily mission report."""
        if not self.file_audits:
            return 'No healing activity to report'
        report: Any = self._generate_cost_report()
        thermal_map: Any = self.get_thermal_map()
        fission_candidates: Any = self.get_fission_candidates()
        lines: Any = ['💰 DAILY MISSION REPORT', '=' * 80, f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", '', '[STATS] HEALING SUMMARY', f'  Files Processed: {report.total_files}', f'  Healing Attempts: {report.total_attempts}', f'  Success Rate: {report.efficiency_score:.1f}%', f'  Total Cost: ${report.estimated_cost_usd:.2f}', '', '🌡️  THERMAL STATUS', f"  🔴 Critical: {sum((1 for v in thermal_map.values() if 'CRITICAL' in v))} files", f"  🟠 Hot: {sum((1 for v in thermal_map.values() if 'HOT' in v))} files", f"  🟡 Warm: {sum((1 for v in thermal_map.values() if 'WARM' in v))} files", f"  🟢 Cold: {sum((1 for v in thermal_map.values() if 'COLD' in v))} files", '', '⚛️  FISSION CANDIDATES', f'  {len(fission_candidates)} files recommended for Atomic Fission']
        if fission_candidates:
            lines.append('')
            lines.append('  Top Candidates:')
            for file_path in fission_candidates[:5]:
                audit: Any = self.file_audits[file_path]
                cost: Any = audit.total_tokens / 1000 * self.TOKEN_COST_PER_1K
                lines.append(f'    - {file_path} (${cost:.2f})')
        lines.extend(['', '[PLAN] RECOMMENDATIONS'])
        for rec in report.recommendations:
            lines.append(f'  {rec}')
        lines.extend(['', '=' * 80])
        return '\n'.join(lines)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
_cost_auditor = None

def get_cost_auditor(ctx: Any) -> PredictiveCostAuditor:
    """Get or create global Cost Auditor instance."""
    global _cost_auditor
    if _cost_auditor is None:
        _cost_auditor = PredictiveCostAuditor(ctx)
    return _cost_auditor

@timeout(300)
def _module_heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
    """Observability metrics - module-level operational stub."""
    if _call_path is None:
        _call_path = set()
    agent_name = "PredictiveCostAuditor"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] Observability metrics - operational only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)
