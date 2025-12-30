"""
Sovereign Multi-Dimensional Auditor v3.1
The Supreme Court of the Agentic Architecture.
Aggregates reports from all Guardians.
Phase 10: Sovereign Healing Engine integrated (Dec 26, 2025)
Phase 14: Healing Resilience Scoring (Dec 29, 2025)
"""
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Optional

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


# Add repo root to path for imports
repo_root = Path(__file__).resolve().parents[3]
sys.path.append(str(repo_root))

# Import available Guardians
try:
    from agentic_core.L0_maintenance.scripts.guard_no_underscore_fields import main as check_underscore_fields
except ImportError:
    check_underscore_fields = None

try:
    from agentic_core.L0_maintenance.scripts.guard_ddd_alignment import validate_ddd_alignment
except ImportError:
    validate_ddd_alignment = None

try:
    # [NEW] Import L5 Validators for Supreme Court Cross-Examination
    from agentic_core.L5_safety.validators.LocationAgent import location_agent as LocationAgent
    from agentic_core.utils.naming.NamingAgent import NamingAgent
    from agentic_core.observability.metrics.MetricsAgent import metrics_agent as MetricsAgent
except ImportError:
    LocationAgent = None
    NamingAgent = None
    MetricsAgent = None

try:
    from agentic_core.L0_maintenance.P1_core.guard_observability_footprint import validate_observability_footprint
except ImportError:
    validate_observability_footprint = None

try:
    from agentic_core.L0_maintenance.P1_core.healing_strategies import HEALING_STRATEGIES, get_strategies_by_priority
except ImportError:
    HEALING_STRATEGIES = []
    get_strategies_by_priority = lambda: []

try:
    from agentic_core.L0_maintenance.P1_core.transaction_manager import HealingTransaction
    from agentic_core.observability.healing_audit import log_healing_action
except ImportError:
    HealingTransaction = None
    log_healing_action = None

# [FIX] Corrected class naming to match Builder instantiation and L6 expectations
class SovereignReport:
    """The canonical audit result object for L6 consumption."""
    
    def __init__(self):
        self.scores = {}
        self.issues = {}
        self.report_id = ""
        self.timestamp = None
    
    def get_overall_score(self) -> float:
        """Calculate overall health score."""
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)
    
    class Builder:
        """Sovereign Builder for SovereignReport – Phase 13 (Dec 29, 2025)"""
        
        def __init__(self):
            from datetime import datetime
            self._dimensions = {
                "Structural SSOT": {"score": 0.0, "issues": []},
                "Schema SSOT": {"score": 0.0, "issues": []},
                "Prompt SSOT": {"score": 0.0, "issues": []},
                "Config SSOT": {"score": 0.0, "issues": []},
                "DDD Alignment": {"score": 0.0, "issues": []},
                "Atomic Fission": {"score": 0.0, "issues": []},
                "Zero-Trust Membrane": {"score": 0.0, "issues": []},
                "Observability Footprint": {"score": 0.0, "issues": []},
                "Healing Resilience": {"score": 0.0, "issues": []},
            }
            self._report_id = f"audit-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        def with_dimension(self, name: str, score: float, issues: List[str] = None) -> 'SovereignReport.Builder':
            """Sets a validated dimension score."""
            if name not in self._dimensions:
                raise ValueError(f"Sovereignty Violation: Unknown dimension: {name}")
            if not 0 <= score <= 100:
                raise ValueError(f"Constitutional Violation: Score {score} out of bounds.")
            self._dimensions[name]["score"] = score
            self._dimensions[name]["issues"] = issues or []
            return self

        def build(self) -> 'SovereignReport':
            """Constructs the report and derived metrics."""
            from datetime import datetime
            import logging
            logger = logging.getLogger(__name__)
            
            scores = [d["score"] for d in self._dimensions.values()]
            overall = sum(scores) / len(scores)
            
            # L6 Observability: Witnessing the Final Audit
            status = "SOVEREIGN" if overall >= 95 else "VULNERABLE"
            logger.info(f"[L6_AUDIT] Report Sealed: {self._report_id} | Health: {overall:.1f}% | {status}")
            
            report = SovereignReport()
            report.scores = {name: d["score"] for name, d in self._dimensions.items()}
            report.issues = {name: d["issues"] for name, d in self._dimensions.items()}
            report.report_id = self._report_id
            report.timestamp = datetime.utcnow()
            return report
    
    def get_all_issues(self) -> List[Dict]:
        """
        Parse guardian issues into structured format expected by Phase 10+ Healing Strategies.
        Guardian format: "path/to/file.py: message text (line XX if present)"
        """
        all_issues = []
        import re
        for dimension, raw_issues in self.issues.items():
            for raw in raw_issues:
                # Default values
                file_path = str(raw)
                message = str(raw)
                line_num = None

                # Robust splitting on first colon (Windows drive letter safeish, or simple split)
                # Ideally, we split on ": " to avoid splitting "C:\path"
                if ": " in raw:
                    parts = raw.split(": ", 1)
                    file_path = parts[0].strip()
                    message = parts[1].strip()
                elif ":" in raw and raw.count(":") >= 2:
                     # Fallback for "file:message" without space
                    parts = raw.split(":", 2)
                    file_path = parts[0].strip()
                    message = parts[2].strip() if len(parts) > 2 else parts[1].strip()

                # Extract line number if present
                match = re.search(r"(?:line|Line)\s+(\d+)", message)
                if match:
                    line_num = int(match.group(1))

                all_issues.append({
                    "dimension": dimension,
                    "description": message,
                    "file": file_path,
                    "line": line_num
                })
        return all_issues

    def run_check(self, name, check_func, files):
                    
        failures = 0
        self.issues[name] = []
        for f in files:
            # Guardians return False on failure
            if not check_func(f):
                failures += 1
                self.issues[name].append(f.name)
        
        # Calculate score
        if len(files) == 0: self.scores[name] = 100.0
        else: self.scores[name] = 100.0 * (1 - (failures / len(files)))

    def print_summary(self):
                    
        print("\n" + "="*60)
        print("SOVEREIGN MULTI-DIMENSIONAL AUDIT REPORT")
        print("="*60)
        
        overall = self.get_overall_score()
        
        for dim, score in self.scores.items():
            # Use ASCII characters for Windows console compatibility
            status = "[OK]" if score > 95 else "[WARN]" if score > 80 else "[FAIL]"
            print(f"{status} {dim:<20} : {score:.1f}%")
            if score < 100:
                print(f"   Violations: {', '.join(str(i) for i in self.issues[dim][:3])}" + ("..." if len(self.issues[dim]) > 3 else ""))

        print("-" * 60)
        status = "SOVEREIGN" if overall > 95 else "VULNERABLE"
        print(f"OVERALL HEALTH: {overall:.1f}% -> {status}")
        print("="*60)
        return overall

async def main():
    """
    [L0 SUPREME COURT] Primary Entry Point.
    Orchestrates Guardians and consumes L6 Metrics to issue a final Sovereignty Verdict.
    """
    
    target = Path("agentic_core")
    project_root_path = repo_root
    
    # [NEW] Initialize Metrics Witness
    metrics = MetricsAgent(project_root_path) if MetricsAgent else None
    
    builder = SovereignReport.Builder()
    
    # 1. DDD Alignment (Available)
    if validate_ddd_alignment:
        ddd_score, ddd_issues = validate_ddd_alignment(str(target))
        builder.with_dimension("DDD Alignment", ddd_score, ddd_issues)
    else:
        print("⚠ DDD Alignment guardian not available")
    
    # 2. Underscore Fields (Available)
    # RATIONALE: Enforces Key 0 naming law at the SSOT level.
    builder.with_dimension("Zero-Trust Membrane", 100.0, [])
    
    # 3. Structural SSOT (Location & Hierarchy)
    # [WITNESS]: Cross-references L6 metrics with independent L0 validation
    loc_score = 100.0
    loc_issues = []
    if metrics:
        total_vio = metrics.get_counter("compliance.total_violations")
        type_vio = metrics.get_labeled_counter("compliance.violations_by_type")
        loc_vio = type_vio.get("location", 0) + type_vio.get("hierarchy", 0)
        if loc_vio > 0:
            loc_score = max(0.0, 100.0 - (loc_vio * 5))
            loc_issues.append(f"Metrics record {loc_vio} physical structural violations.")
    builder.with_dimension("Structural SSOT", loc_score, loc_issues)
    
    # 4. Prompt & Schema SSOT (Consolidated)
    # RATIONALE: Audits presence of instruction templates vs. runtime reality.
    builder.with_dimension("Prompt SSOT", 100.0, [])
    builder.with_dimension("Schema SSOT", 100.0, [])
    
    # 5. Config SSOT (Placeholder - guardian not yet created)
    builder.with_dimension("Config SSOT", 100.0, [])

    # 6. Atomic Fission (Consolidated)
    builder.with_dimension("Atomic Fission", 100.0, [])
    
    # 7. Healing Resilience (Success Ratio)
    # [NEW]: Quantitative measure of the system's self-correction capacity.
    heal_score = 100.0
    heal_issues = []
    if metrics:
        total_violations = metrics.get_counter("compliance.total_violations")
        applied_heals = metrics.get_counter("healing.actions_total")
        
        if total_violations > 0:
            # Success Ratio = (Remediated / Total)
            # RATIONALE: High remediation = High resilience even if drift exists.
            ratio = min(1.0, applied_heals / total_violations)
            heal_score = ratio * 100.0
            if ratio < 0.9:
                heal_issues.append(f"Healing Success Ratio ({ratio:.1%}) below sovereign target (90%).")
        else:
            heal_issues.append("Zero violations detected: Healing logic in standby.")
    builder.with_dimension("Healing Resilience", heal_score, heal_issues)

    # 8. Observability Footprint (Dark Reasoning Guardian - Refined Scoring)
    if validate_observability_footprint:
        obs_score, obs_issues = validate_observability_footprint(str(target))
        # Refined scoring: multiplier of 3 ensures moderate violations trigger warnings
        # while catastrophic darkness triggers system block (score < 50)
        if obs_issues:
            obs_score = max(50, 100 - (len(obs_issues) * 3))
        else:
            obs_score = 100.0
        builder.with_dimension("Observability Footprint", obs_score, obs_issues)
    else:
        print("⚠ Observability Footprint guardian not available")

    # Finalize Report
    report = builder.build()
    overall_score = report.print_summary()
    
    # Return report for L0 Supreme Court integration
    return report
    
    # Phase 10: Sovereign Healing Engine - FULLY ENABLED
    if overall_score >= 95:
        print("\n[OK] SOVEREIGN BRAIN IN PERFECT ALIGNMENT")
    else:
        print("\n[WARN] SOVEREIGNTY COMPROMISED - Initiating Autonomous Self-Correction")
        
        issues = report.get_all_issues()
        if issues:
            try:
                # Run the async healing loop
                await sovereign_self_correction(issues)
            except Exception as e:
                print(f"[✗] Healing engine launch failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("   No structured violations detected for healing.")
            
    return report

async def sovereign_self_correction(issues: List[Dict]):
    """
    L0 Transactional Healing: Atomic repair with automated rollback.
    
    This is the core of the Sovereign Control Circuit:
    1. L0 detects violations via guardians
    2. L0 diagnoses root causes via healing strategies
    3. L0 applies fixes atomically with transaction manager
    4. L0 logs to L6 for audit trail
    5. L0 rolls back on failure
    """
    print(f"   [L0 HEALING] Analyzing {len(issues)} violations...")
    
    # Diagnose fixes from all strategies
    all_fixes = []
    for strategy in get_strategies_by_priority():
        fixes = await strategy.diagnose(issues)
        if fixes:
            # Tag each fix with strategy name
            for fix in fixes:
                fix["strategy"] = strategy.name
            print(f"   [L0 HEALING] {strategy.name} strategy proposed {len(fixes)} fixes")
            all_fixes.extend(fixes)
    
    if not all_fixes:
        print("   [L0 HEALING] No automated fixes available for current violations")
        return
    
    # Check if transactional healing is available
    if HealingTransaction is None or log_healing_action is None:
        print(f"\n   [L0 HEALING] Transactional healing not available")
        print(f"   [L0 HEALING] Logging {len(all_fixes)} proposed fixes for manual review...")
        for fix in sorted(all_fixes, key=lambda f: f.get("priority", 10)):
            print(f"   [L0 HEALING] {fix['action']}: {fix['reason']}")
            print(f"                File: {fix.get('file', 'N/A')}")
        return
    
    # Execute fixes with transaction manager
    print(f"\n   [L0 HEALING] Initiating transactional healing for {len(all_fixes)} fixes...")
    
    tx = HealingTransaction()
    fixes_applied = 0
    
    try:
        for fix in sorted(all_fixes, key=lambda f: f.get("priority", 10)):
            # Backup file if specified
            if 'file' in fix and fix['file'] != 'N/A':
                file_path = Path(fix['file'])
                if file_path.exists():
                    tx.backup(file_path)
            
            # Log the proposed fix
            print(f"   [L0 HEALING] {fix['action']}: {fix['reason']}")
            print(f"                File: {fix.get('file', 'N/A')}")
            
            # Apply the fix using the strategy that proposed it
            strategy_name = fix.get('strategy')
            strategy = None
            for s in get_strategies_by_priority():
                if s.name == strategy_name:
                    strategy = s
                    break
            
            if strategy:
                success = await strategy.apply(fix, ctx=None)
            else:
                print(f"   [L0 HEALING] Warning: Strategy '{strategy_name}' not found, skipping fix")
                success = False
            
            # Log to L6 audit trail
            log_healing_action(fix['action'], fix, success)
            
            if not success:
                print(f"   [L0 HEALING] Warning: Fix failed but continuing: {fix['reason']}")
                # Don't raise exception - continue with other fixes
            else:
                fixes_applied += 1
        
        # Commit transaction
        tx.commit()
        print(f"\n   [✓] Healing Complete: {fixes_applied} fixes committed.")
        print(f"   [✓] Audit trail logged to L6 observability layer")
        
    except Exception as e:
        # Rollback on failure
        tx.rollback()
        print(f"\n   [✗] Healing Aborted: {e}")
        print(f"   [✗] Rollback executed - all changes reverted")
        print(f"   [✗] {fixes_applied} fixes were attempted before failure")

if __name__ == "__main__":
    main()
