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
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List

from agentic_core.agents.base import SubAtomicAgent

logger = logging.getLogger(__name__)


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
    sink_severity: str  # "none", "low", "medium", "high", "critical"
    recommendation: str


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


class PredictiveCostAuditor(SubAtomicAgent):
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
    
    def __init__(self, ctx):
        """
        Initialize Predictive Cost Auditor.
        
        Args:
            ctx: ValidationContext
        """
        super().__init__(ctx)
        
        # Cost thresholds
        self.HEALING_SINK_ATTEMPTS = 3
        self.CRITICAL_SINK_COST = 5.0  # USD
        self.FISSION_CANDIDATE_COST = 10.0  # USD
        
        # Token pricing (approximate)
        self.TOKEN_COST_PER_1K = 0.001  # $0.001 per 1K tokens
        
        # Audit data
        self.healing_history: Dict[str, List[HealingMetrics]] = {}
        self.file_audits: Dict[str, FileAudit] = {}
    
    async def execute(self):
        """
        Execute cost auditing.
        
        Analyzes healing history and generates cost report.
        """
        logger.info("💰 Predictive Cost Auditor: Analyzing healing economics...")
        
        # Load healing history from context
        self._load_healing_history()
        
        # Audit each file
        self._audit_files()
        
        # Generate report
        report = self._generate_cost_report()
        
        # Display report
        self._display_report(report)
        
        # Store report in context
        if not hasattr(self.ctx, 'cost_reports'):
            self.ctx.cost_reports = []
        self.ctx.cost_reports.append(report)
    
    def _load_healing_history(self):
        """Load healing history from context."""
        if not hasattr(self.ctx, 'healing_history'):
            logger.warning("   No healing history available")
            return
        
        for file_path, history in self.ctx.healing_history.items():
            if file_path not in self.healing_history:
                self.healing_history[file_path] = []
            
            for key_id, data in history.items():
                # Extract metrics from history
                metrics = HealingMetrics(
                    file_path=file_path,
                    attempt_number=data.get('round', 1),
                    tokens_used=data.get('tokens_used', 0),
                    success=data.get('status') == 'PASS',
                    key_id=key_id,
                    timestamp=data.get('timestamp', datetime.now(timezone.utc).isoformat()),
                    model_used=data.get('model', 'unknown')
                )
                
                self.healing_history[file_path].append(metrics)
    
    def _audit_files(self):
        """Audit each file for cost efficiency."""
        for file_path, metrics_list in self.healing_history.items():
            audit = self._audit_single_file(file_path, metrics_list)
            self.file_audits[file_path] = audit
    
    def _audit_single_file(self, file_path: str, metrics_list: List[HealingMetrics]) -> FileAudit:
        """Audit a single file."""
        total_attempts = len(metrics_list)
        total_tokens = sum(m.tokens_used for m in metrics_list)
        successful_attempts = sum(1 for m in metrics_list if m.success)
        failed_attempts = total_attempts - successful_attempts
        
        success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        avg_tokens = total_tokens / total_attempts if total_attempts > 0 else 0
        
        # Calculate cost
        cost_usd = (total_tokens / 1000) * self.TOKEN_COST_PER_1K
        
        # Determine if healing sink
        is_healing_sink = (
            failed_attempts >= self.HEALING_SINK_ATTEMPTS or
            cost_usd >= self.CRITICAL_SINK_COST
        )
        
        # Determine severity
        if cost_usd >= self.FISSION_CANDIDATE_COST:
            sink_severity = "critical"
        elif cost_usd >= self.CRITICAL_SINK_COST:
            sink_severity = "high"
        elif failed_attempts >= self.HEALING_SINK_ATTEMPTS:
            sink_severity = "medium"
        elif failed_attempts > 0:
            sink_severity = "low"
        else:
            sink_severity = "none"
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            file_path, total_attempts, cost_usd, success_rate, sink_severity
        )
        
        return FileAudit(
            file_path=file_path,
            total_attempts=total_attempts,
            total_tokens=total_tokens,
            successful_attempts=successful_attempts,
            failed_attempts=failed_attempts,
            success_rate=success_rate,
            average_tokens_per_attempt=avg_tokens,
            is_healing_sink=is_healing_sink,
            sink_severity=sink_severity,
            recommendation=recommendation
        )
    
    def _generate_recommendation(self, file_path: str, attempts: int,
                                cost_usd: float, success_rate: float,
                                severity: str) -> str:
        """Generate recommendation for file."""
        if severity == "critical":
            return f"CRITICAL: Apply Atomic Fission - ${cost_usd:.2f} spent, {attempts} attempts"
        
        elif severity == "high":
            return f"HIGH: Consider manual refactoring - ${cost_usd:.2f} spent"
        
        elif severity == "medium":
            return f"MEDIUM: Monitor closely - {attempts} failed attempts"
        
        elif severity == "low":
            return f"LOW: Continue automated healing"
        
        else:
            return "GOOD: Efficient healing"
    
    def _generate_cost_report(self) -> CostReport:
        """Generate comprehensive cost report."""
        total_files = len(self.file_audits)
        total_attempts = sum(audit.total_attempts for audit in self.file_audits.values())
        total_tokens = sum(audit.total_tokens for audit in self.file_audits.values())
        
        successful_files = sum(1 for audit in self.file_audits.values() if audit.success_rate == 100)
        failed_files = sum(1 for audit in self.file_audits.values() if audit.success_rate == 0)
        
        healing_sinks = [
            audit for audit in self.file_audits.values()
            if audit.is_healing_sink
        ]
        healing_sinks.sort(key=lambda x: x.total_tokens, reverse=True)
        
        # Calculate efficiency score (0-100)
        if total_attempts > 0:
            success_count = sum(audit.successful_attempts for audit in self.file_audits.values())
            efficiency_score = (success_count / total_attempts) * 100
        else:
            efficiency_score = 0
        
        # Estimate cost
        estimated_cost_usd = (total_tokens / 1000) * self.TOKEN_COST_PER_1K
        
        # Generate recommendations
        recommendations = self._generate_global_recommendations(
            healing_sinks, efficiency_score, estimated_cost_usd
        )
        
        return CostReport(
            total_files=total_files,
            total_attempts=total_attempts,
            total_tokens=total_tokens,
            successful_files=successful_files,
            failed_files=failed_files,
            healing_sinks=healing_sinks,
            efficiency_score=efficiency_score,
            estimated_cost_usd=estimated_cost_usd,
            recommendations=recommendations
        )
    
    def _generate_global_recommendations(self, healing_sinks: List[FileAudit],
                                        efficiency_score: float,
                                        cost_usd: float) -> List[str]:
        """Generate global recommendations."""
        recommendations = []
        
        if efficiency_score < 50:
            recommendations.append(
                f"⚠️  Low efficiency ({efficiency_score:.1f}%) - Review healing strategy"
            )
        
        if cost_usd > 50:
            recommendations.append(
                f"⚠️  High cost (${cost_usd:.2f}) - Consider batch optimization"
            )
        
        critical_sinks = [s for s in healing_sinks if s.sink_severity == "critical"]
        if critical_sinks:
            recommendations.append(
                f"🔴 {len(critical_sinks)} critical healing sinks - Apply Atomic Fission immediately"
            )
        
        high_sinks = [s for s in healing_sinks if s.sink_severity == "high"]
        if high_sinks:
            recommendations.append(
                f"⚠️  {len(high_sinks)} high-cost files - Consider manual refactoring"
            )
        
        if not recommendations:
            recommendations.append("✅ Healing efficiency is optimal")
        
        return recommendations
    
    def _display_report(self, report: CostReport):
        """Display cost report."""
        logger.info(f"\n{'='*80}")
        logger.info("💰 PREDICTIVE COST AUDIT REPORT")
        logger.info(f"{'='*80}")
        logger.info(f"Total Files Analyzed: {report.total_files}")
        logger.info(f"Total Healing Attempts: {report.total_attempts}")
        logger.info(f"Total Tokens Used: {report.total_tokens:,}")
        logger.info(f"Estimated Cost: ${report.estimated_cost_usd:.2f}")
        logger.info(f"")
        logger.info(f"Success Metrics:")
        logger.info(f"  Successful Files: {report.successful_files}")
        logger.info(f"  Failed Files: {report.failed_files}")
        logger.info(f"  Efficiency Score: {report.efficiency_score:.1f}%")
        logger.info(f"")
        logger.info(f"Healing Sinks: {len(report.healing_sinks)}")
        
        if report.healing_sinks:
            logger.warning(f"\n⚠️  TOP HEALING SINKS (by token usage):")
            for i, sink in enumerate(report.healing_sinks[:10], 1):
                cost = (sink.total_tokens / 1000) * self.TOKEN_COST_PER_1K
                logger.warning(
                    f"  {i}. {sink.file_path}"
                )
                logger.warning(
                    f"     Tokens: {sink.total_tokens:,} (${cost:.2f}) | "
                    f"Attempts: {sink.total_attempts} | "
                    f"Success Rate: {sink.success_rate:.0f}%"
                )
                logger.warning(f"     → {sink.recommendation}")
            
            if len(report.healing_sinks) > 10:
                logger.warning(f"  ... and {len(report.healing_sinks) - 10} more sinks")
        
        if report.recommendations:
            logger.info(f"\n📋 RECOMMENDATIONS:")
            for rec in report.recommendations:
                logger.info(f"  {rec}")
        
        logger.info(f"{'='*80}\n")
    
    def get_thermal_map(self) -> Dict[str, str]:
        """
        Generate thermal map of repository.
        
        Returns:
            Dictionary mapping file paths to thermal status
            (cold, warm, hot, critical)
        """
        thermal_map = {}
        
        for file_path, audit in self.file_audits.items():
            if audit.sink_severity == "critical":
                thermal_map[file_path] = "🔴 CRITICAL"
            elif audit.sink_severity == "high":
                thermal_map[file_path] = "🟠 HOT"
            elif audit.sink_severity == "medium":
                thermal_map[file_path] = "🟡 WARM"
            else:
                thermal_map[file_path] = "🟢 COLD"
        
        return thermal_map
    
    def get_fission_candidates(self) -> List[str]:
        """Get list of files that should undergo Atomic Fission."""
        candidates = []
        
        for file_path, audit in self.file_audits.items():
            cost = (audit.total_tokens / 1000) * self.TOKEN_COST_PER_1K
            if cost >= self.FISSION_CANDIDATE_COST:
                candidates.append(file_path)
        
        return candidates
    
    def generate_daily_mission_report(self) -> str:
        """Generate daily mission report."""
        if not self.file_audits:
            return "No healing activity to report"
        
        report = self._generate_cost_report()
        thermal_map = self.get_thermal_map()
        fission_candidates = self.get_fission_candidates()
        
        lines = [
            "💰 DAILY MISSION REPORT",
            "=" * 80,
            f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            "📊 HEALING SUMMARY",
            f"  Files Processed: {report.total_files}",
            f"  Healing Attempts: {report.total_attempts}",
            f"  Success Rate: {report.efficiency_score:.1f}%",
            f"  Total Cost: ${report.estimated_cost_usd:.2f}",
            "",
            "🌡️  THERMAL STATUS",
            f"  🔴 Critical: {sum(1 for v in thermal_map.values() if 'CRITICAL' in v)} files",
            f"  🟠 Hot: {sum(1 for v in thermal_map.values() if 'HOT' in v)} files",
            f"  🟡 Warm: {sum(1 for v in thermal_map.values() if 'WARM' in v)} files",
            f"  🟢 Cold: {sum(1 for v in thermal_map.values() if 'COLD' in v)} files",
            "",
            "⚛️  FISSION CANDIDATES",
            f"  {len(fission_candidates)} files recommended for Atomic Fission",
        ]
        
        if fission_candidates:
            lines.append("")
            lines.append("  Top Candidates:")
            for file_path in fission_candidates[:5]:
                audit = self.file_audits[file_path]
                cost = (audit.total_tokens / 1000) * self.TOKEN_COST_PER_1K
                lines.append(f"    - {file_path} (${cost:.2f})")
        
        lines.extend([
            "",
            "📋 RECOMMENDATIONS",
        ])
        
        for rec in report.recommendations:
            lines.append(f"  {rec}")
        
        lines.extend([
            "",
            "=" * 80
        ])
        
        return "\n".join(lines)


# Singleton instance
_cost_auditor = None

def get_cost_auditor(ctx) -> PredictiveCostAuditor:
    """Get or create global Cost Auditor instance."""
    global _cost_auditor
    if _cost_auditor is None:
        _cost_auditor = PredictiveCostAuditor(ctx)
    return _cost_auditor
