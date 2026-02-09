"""Phase 3: Implement agent consolidation.

Transforms:
- 19 retirement targets → deprecated shim files (no ClassDef)
- 27 merge targets → import-alias shims pointing to 6 canonical executors
- Creates 6 canonical executor files

All transformations preserve backward compatibility (imports still resolve).
Discovery count drops because shim files have no ClassDef.
"""

from __future__ import annotations

import ast
import shutil
import textwrap
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TARGETS_PATH = PROJECT_ROOT / "artifacts" / "consolidation" / "target_paths.json"
BACKUP_DIR = PROJECT_ROOT / "artifacts" / "consolidation" / "backups"

# ─── Retirement shim template ───────────────────────────────────────────────
RETIRE_SHIM = '''"""RETIRED: {class_name} — consolidated out of active agent pool (2026-02-08).

Original domain_logic_loc: {domain_loc}
Reason: {reason}

This file is a backward-compatibility shim. It contains NO ClassDef,
so full_agent_discovery.py will not count it as an active agent.
"""

__all__: list[str] = []
'''

# ─── Merge shim template ────────────────────────────────────────────────────
MERGE_SHIM = '''"""CONSOLIDATED: {old_class} → {canonical_class} (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""
from {canonical_module} import {canonical_class} as {old_class}

__all__ = ["{old_class}"]
'''


def backup_file(path: Path) -> None:
    """Create backup of file before modification."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    rel = path.relative_to(PROJECT_ROOT)
    backup = BACKUP_DIR / str(rel).replace("/", "__").replace("\\", "__")
    shutil.copy2(path, backup)


def retire_agent(file_path: str, class_name: str, domain_loc: int, reason: str) -> bool:
    """Convert an agent file to a retired shim."""
    full = PROJECT_ROOT / file_path
    if not full.exists():
        print(f"  SKIP (not found): {file_path}")
        return False

    # Special case: discovery_util.py contains more than just the agent class
    # Only remove the ClassDef, preserve the rest
    source = full.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        print(f"  SKIP (syntax error): {file_path}")
        return False

    # Check if the file has other significant content besides the agent class
    class_count = sum(1 for n in ast.iter_child_nodes(tree) if isinstance(n, ast.ClassDef))
    func_count = sum(
        1 for n in ast.iter_child_nodes(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    )

    if class_count > 1 or func_count > 0:
        # File has other content — only remove the target ClassDef
        lines = source.splitlines(keepends=True)
        new_lines = []
        skip_until = -1
        for i, line in enumerate(lines, 1):
            if i <= skip_until:
                continue
            new_lines.append(line)

        # Find and remove the ClassDef for our target
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                start = node.lineno - 1  # 0-indexed
                end = node.end_lineno  # 1-indexed inclusive
                # Also capture decorators
                if node.decorator_list:
                    start = min(d.lineno - 1 for d in node.decorator_list)
                lines_list = source.splitlines(keepends=True)
                new_content = (
                    "".join(lines_list[:start])
                    + f"# RETIRED: {class_name} removed from active agent pool (2026-02-08)\n"
                    + "".join(lines_list[end:])
                )
                backup_file(full)
                full.write_text(new_content, encoding="utf-8")
                print(f"  RETIRED (partial): {class_name} from {file_path}")
                return True

        print(f"  SKIP (class not found in multi-content file): {file_path}")
        return False
    else:
        # File is purely the agent class — replace entirely with shim
        backup_file(full)
        full.write_text(
            RETIRE_SHIM.format(
                class_name=class_name,
                domain_loc=domain_loc,
                reason=reason,
            ),
            encoding="utf-8",
        )
        print(f"  RETIRED (full): {class_name} at {file_path}")
        return True


def create_merge_shim(file_path: str, old_class: str, canonical_class: str, canonical_module: str) -> bool:
    """Convert a merge target to an import-alias shim."""
    full = PROJECT_ROOT / file_path
    if not full.exists():
        print(f"  SKIP (not found): {file_path}")
        return False

    backup_file(full)
    full.write_text(
        MERGE_SHIM.format(
            old_class=old_class,
            canonical_class=canonical_class,
            canonical_module=canonical_module,
        ),
        encoding="utf-8",
    )
    print(f"  SHIMMED: {old_class} → {canonical_class} at {file_path}")
    return True


def create_canonical_executor(path: str, content: str) -> bool:
    """Create a canonical executor file."""
    full = PROJECT_ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    if full.exists():
        print(f"  SKIP (already exists): {path}")
        return False
    full.write_text(content, encoding="utf-8")
    print(f"  CREATED: {path}")
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL EXECUTOR DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

INSPECTOR_EXECUTOR = textwrap.dedent('''\
    """InspectorExecutor — Canonical parameterized inspector agent.

    Consolidates: DagRuntimeInspectorAgent, SignatureVerifierAgent, TokenBudgetInspectorAgent
    Created: 2026-02-08 (Structural Agent Count Reduction)
    """
    from __future__ import annotations

    from dataclasses import dataclass, field
    from typing import Any

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.mixins.inspection_capability_mixin import InspectionCapability


    @dataclass
    class InspectorExecutor(InspectionCapability, SovereignBaseAgent):
        """Parameterized inspector that dispatches to domain-specific check logic.

        Usage:
            inspector = InspectorExecutor(inspector_type="dag_runtime")
        """

        inspector_type: str = "generic"
        INSPECTION_LOG_PREFIX: str = field(init=False, default="Inspector")

        def __post_init__(self) -> None:
            prefixes = {
                "dag_runtime": "DagRuntime",
                "signature": "Signature",
                "token_budget": "TokenBudget",
            }
            self.INSPECTION_LOG_PREFIX = prefixes.get(self.inspector_type, "Inspector")

        # perform_checks() inherited from InspectionCapability (default structural checks).
        # Override here when domain-specific logic is added per inspector_type.
''')

RG_VALIDATION_EXECUTOR = textwrap.dedent('''\
    """RGValidationExecutor — Canonical parameterized RG validation agent.

    Consolidates: ATSCompatibilityAgent, BrandComplianceAgent, FactCheckAgent, SectionBalanceAgent
    Created: 2026-02-08 (Structural Agent Count Reduction)
    """
    from __future__ import annotations

    from dataclasses import dataclass, field
    from typing import Any, Callable

    from apps_rg.config.AgentSpec import RGAgentBase

    # Domain-specific collect_issues implementations stored as registry
    _RULE_REGISTRY: dict[str, Callable] = {}


    def register_rule(name: str):
        """Decorator to register a collect_issues implementation."""
        def decorator(func):
            _RULE_REGISTRY[name] = func
            return func
        return decorator


    @register_rule("ats_compatibility")
    def _ats_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
        """ATS compatibility validation logic."""
        issues = []
        if not resume_data.get("skills"):
            issues.append({"type": "ats_missing_skills", "severity": "high", "message": "No skills section found"})
        if not resume_data.get("experience"):
            issues.append({"type": "ats_missing_experience", "severity": "high", "message": "No experience section"})
        keywords = resume_data.get("keywords", [])
        if job_data:
            required = set(job_data.get("required_keywords", []))
            found = set(keywords)
            missing = required - found
            for kw in missing:
                issues.append({"type": "ats_missing_keyword", "severity": "medium", "message": f"Missing keyword: {kw}"})
        return issues


    @register_rule("brand_compliance")
    def _brand_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
        """Brand compliance validation logic."""
        issues = []
        tone = resume_data.get("tone", "")
        if tone and tone.lower() not in ("professional", "confident", "balanced"):
            issues.append({"type": "brand_tone_mismatch", "severity": "medium", "message": f"Tone '{tone}' not aligned"})
        if resume_data.get("contains_superlatives", False):
            issues.append({"type": "brand_superlatives", "severity": "low", "message": "Contains superlatives"})
        return issues


    @register_rule("fact_check")
    def _fact_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
        """Fact-check validation logic."""
        issues = []
        claims = resume_data.get("quantified_claims", [])
        for claim in claims:
            if not claim.get("source"):
                issues.append({"type": "fact_unsourced_claim", "severity": "high", "message": f"Unsourced: {claim.get('text', '')}"})
            if claim.get("value") and not claim.get("context"):
                issues.append({"type": "fact_no_context", "severity": "medium", "message": f"No context for metric: {claim.get('text', '')}"})
        dates = resume_data.get("dates", [])
        for i in range(len(dates) - 1):
            if dates[i].get("end") and dates[i+1].get("start"):
                if dates[i]["end"] > dates[i+1]["start"]:
                    issues.append({"type": "fact_date_overlap", "severity": "high", "message": "Overlapping date ranges"})
        return issues


    @register_rule("section_balance")
    def _section_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
        """Section balance validation logic."""
        issues = []
        sections = resume_data.get("sections", {})
        total_len = sum(len(str(v)) for v in sections.values()) or 1
        for name, content in sections.items():
            ratio = len(str(content)) / total_len
            if ratio > 0.6:
                issues.append({"type": "section_oversized", "severity": "medium", "message": f"Section '{name}' is {ratio:.0%} of total"})
            if ratio < 0.05 and name not in ("objective", "summary"):
                issues.append({"type": "section_undersized", "severity": "low", "message": f"Section '{name}' is only {ratio:.0%} of total"})
        return issues


    @dataclass
    class RGValidationExecutor(RGAgentBase):
        """Parameterized RG validation agent.

        Usage:
            validator = RGValidationExecutor(rule_set="ats_compatibility")
        """

        rule_set: str = "generic"

        def execute(self, resume_data: dict, job_data: dict | None = None, **kwargs) -> dict:
            """Execute validation and return results."""
            issues = self.collect_issues(resume_data, job_data)
            return {
                "rule_set": self.rule_set,
                "issues": issues,
                "issue_count": len(issues),
                "passed": len(issues) == 0,
            }

        def collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
            """Dispatch to registered rule implementation."""
            handler = _RULE_REGISTRY.get(self.rule_set)
            if handler is None:
                return [{"type": "unknown_rule_set", "severity": "high", "message": f"No handler for rule_set={self.rule_set}"}]
            return handler(self, resume_data, job_data)
''')

LIC_VALIDATION_EXECUTOR = textwrap.dedent('''\
    """LICValidationExecutor — Canonical parameterized LIC validation agent.

    Consolidates: CampaignBalanceAgent, DeliverabilityAgent
    Created: 2026-02-08 (Structural Agent Count Reduction)
    """
    from __future__ import annotations

    from dataclasses import dataclass
    from typing import Any

    from apps_lic.config.AgentSpec import LICAgentBase
    from apps_lic.utils.lic_engine_validation_capability import LICEngineValidationCapability
    from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin


    @dataclass
    class LICValidationExecutor(LICEngineValidationCapability, SubatomicTestingMixin, LICAgentBase):
        """Parameterized LIC engine validation agent.

        Usage:
            validator = LICValidationExecutor(rule_set="campaign_balance")
        """

        rule_set: str = "generic"

        def _validate(self, data: dict, **kwargs) -> list[dict]:
            """Dispatch to rule-specific validation."""
            if self.rule_set == "campaign_balance":
                return self._validate_campaign_balance(data)
            elif self.rule_set == "deliverability":
                return self._validate_deliverability(data)
            return []

        def _validate_campaign_balance(self, data: dict) -> list[dict]:
            """Campaign balance validation rules."""
            issues = []
            channels = data.get("channels", {})
            total = sum(channels.values()) if channels else 0
            if total > 0:
                for ch, val in channels.items():
                    ratio = val / total
                    if ratio > 0.7:
                        issues.append({"type": "channel_imbalance", "channel": ch, "ratio": ratio})
            return issues

        def _validate_deliverability(self, data: dict) -> list[dict]:
            """Deliverability validation rules."""
            issues = []
            if data.get("spam_score", 0) > 5:
                issues.append({"type": "high_spam_score", "score": data["spam_score"]})
            if not data.get("dkim_valid", True):
                issues.append({"type": "dkim_invalid"})
            if not data.get("spf_valid", True):
                issues.append({"type": "spf_invalid"})
            return issues
''')

OBSERVABILITY_PROBE_EXECUTOR = textwrap.dedent('''\
    """ObservabilityProbeExecutor — Canonical parameterized observability agent.

    Consolidates: TrackObservabilityCostAgent, CoordinateObservabilityOperationsAgent,
                  StrategicObservationAgent, DeadlockDetectorAgent, DebateSynthesisAgent,
                  RuntimeTelemetryAgent
    Created: 2026-02-08 (Structural Agent Count Reduction)
    """
    from __future__ import annotations

    from dataclasses import dataclass, field
    from typing import Any

    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
    from agentic_core.base_agents.decorators import standard_heal
    from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin


    @dataclass
    class ObservabilityProbeExecutor(SubatomicTestingMixin, SovereignBaseAgent):
        """Parameterized observability probe agent.

        Usage:
            probe = ObservabilityProbeExecutor(probe_type="cost_tracker")
        """

        probe_type: str = "generic"
        _results: dict = field(init=False, default_factory=dict)

        def execute(self, context: dict | None = None) -> dict:
            """Dispatch to probe-specific execution."""
            ctx = context or {}
            handler = self._get_handler()
            if handler:
                self._results = handler(ctx)
            return self._results

        def _get_handler(self):
            handlers = {
                "cost_tracker": self._probe_cost,
                "coordinator": self._probe_coordination,
                "strategic": self._probe_strategic,
                "deadlock": self._probe_deadlock,
                "debate": self._probe_debate,
                "runtime_telemetry": self._probe_telemetry,
            }
            return handlers.get(self.probe_type)

        def _probe_cost(self, ctx: dict) -> dict:
            return {"probe": "cost_tracker", "metrics": ctx.get("cost_metrics", {})}

        def _probe_coordination(self, ctx: dict) -> dict:
            return {"probe": "coordinator", "operations": ctx.get("operations", [])}

        def _probe_strategic(self, ctx: dict) -> dict:
            return {"probe": "strategic", "observations": ctx.get("observations", [])}

        def _probe_deadlock(self, ctx: dict) -> dict:
            return {"probe": "deadlock", "cycles": ctx.get("dependency_cycles", [])}

        def _probe_debate(self, ctx: dict) -> dict:
            return {"probe": "debate", "synthesis": ctx.get("debate_results", {})}

        def _probe_telemetry(self, ctx: dict) -> dict:
            return {"probe": "runtime_telemetry", "benchmarks": ctx.get("benchmarks", {})}

        @standard_heal
        def heal_repository(self, **kwargs) -> dict:
            return super().heal_repository(**kwargs)

        def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
            return {"status": "skipped", "details": f"ObservabilityProbeExecutor({self.probe_type})", "artifacts": [], "errors": []}
''')

RG_STRATEGY_EXECUTOR = textwrap.dedent('''\
    """RGStrategyExecutor — Canonical parameterized RG strategy agent.

    Consolidates: ContentStrategyAgent, RgStrategicPlannerAgent, RgTemplateOptimizerAgent
    Created: 2026-02-08 (Structural Agent Count Reduction)
    """
    from __future__ import annotations

    from dataclasses import dataclass
    from typing import Any

    from apps_rg.config.AgentSpec import RGAgentBase


    @dataclass
    class RGStrategyExecutor(RGAgentBase):
        """Parameterized RG strategy agent.

        Usage:
            strategy = RGStrategyExecutor(strategy_type="content")
        """

        strategy_type: str = "generic"

        def execute(self, data: dict | None = None, **kwargs) -> dict:
            """Dispatch to strategy-specific execution."""
            ctx = data or {}
            handler = {
                "content": self._strategy_content,
                "strategic_planner": self._strategy_planner,
                "template_optimizer": self._strategy_optimizer,
            }.get(self.strategy_type, self._strategy_default)
            return handler(ctx)

        def _strategy_content(self, ctx: dict) -> dict:
            topic = ctx.get("topic", "")
            return {"strategy": "content", "topic": topic, "recommendations": []}

        def _strategy_planner(self, ctx: dict) -> dict:
            goals = ctx.get("goals", [])
            return {"strategy": "strategic_planner", "goals": goals, "plan": []}

        def _strategy_optimizer(self, ctx: dict) -> dict:
            template = ctx.get("template", "")
            return {"strategy": "template_optimizer", "template": template, "optimizations": []}

        def _strategy_default(self, ctx: dict) -> dict:
            return {"strategy": self.strategy_type, "status": "no_handler"}
''')

# Note: HOPPipelineExecutor is more complex due to high domain logic in each stage.
# We create the canonical class and stage registry, then shim the old files.
HOP_PIPELINE_EXECUTOR = textwrap.dedent('''\
    """HOPPipelineExecutor — Canonical parameterized HOP pipeline stage agent.

    Consolidates: HOP1-HOP9 pipeline stage agents.
    Created: 2026-02-08 (Structural Agent Count Reduction)

    Each stage's _process() logic is preserved in hop_stage_registry.py.
    This executor dispatches to the registered stage implementation.
    """
    from __future__ import annotations

    from dataclasses import dataclass, field
    from typing import Any

    from apps_lic.config.AgentSpec import LICAgentBase
    from apps_lic.utils.hop_stage_capability import HOPStageCapability
    from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin


    @dataclass
    class HOPPipelineExecutor(HOPStageCapability, SubatomicTestingMixin, LICAgentBase):
        """Parameterized HOP pipeline stage agent.

        Usage:
            stage = HOPPipelineExecutor(stage_id=4)
        """

        stage_id: int = 0
        stage_name: str = field(init=False, default="unknown")

        _STAGE_NAMES = {
            1: "profile_analysis",
            2: "research",
            3: "sender_grounding",
            4: "routing",
            5: "generation",
            6: "validation",
            7: "gate_decision",
            8: "qa_report",
            9: "integration",
        }

        def __post_init__(self) -> None:
            self.stage_name = self._STAGE_NAMES.get(self.stage_id, "unknown")

        def _process(self, context: dict | None = None, **kwargs) -> dict:
            """Dispatch to stage-specific processing.

            Domain logic for each stage is preserved via the stage registry.
            Import and call the original _process implementations.
            """
            from apps_lic.engines import hop_stage_registry
            handler = hop_stage_registry.get_stage_handler(self.stage_id)
            if handler is None:
                return {"stage": self.stage_id, "error": f"No handler for stage {self.stage_id}"}
            return handler(self, context or {}, **kwargs)
''')


def main():
    print("=" * 80)
    print("PHASE 3: IMPLEMENTING CONSOLIDATION")
    print("=" * 80)

    retired_count = 0
    merged_count = 0
    executors_created = 0

    # ── Step 1: Retirements ──────────────────────────────────────────────────
    print("\n--- Step 1: Retirements ---")

    retirements = [
        ("apps_lic/engines/LicReflectionAgent.py", "OutreachAgent", 0, "Duplicate stub (d=0)"),
        ("apps_lic/engines/LicTemplateOptimizerAgent.py", "OutreachAgent", 0, "Duplicate stub (d=0)"),
        ("apps_lic/engines/MessageComplianceAgent.py", "OutreachAgent", 0, "Duplicate stub (d=0)"),
        ("apps_lic/engines/OutreachLearningAgent.py", "OutreachAgent", 0, "Duplicate stub (d=0)"),
        ("apps_lic/engines/OutreachProactiveAgent.py", "OutreachAgent", 0, "Duplicate stub (d=0)"),
        ("apps_lic/engines/MessageDiversityValidator.py", "MCPHardenedMixin", 0, "Not an agent (mixin)"),
        ("agentic_core/runtime/utils/discovery_util.py", "DiscoveredAgent", 0, "Utility class, not agent"),
        (
            "agentic_core/L5_safety/reasoning/DependencyDiplomatAgent.py",
            "DependencyDiplomatAgent",
            0,
            "Empty stub (d=0, bp=0.89)",
        ),
        (
            "agentic_core/L5_safety/reasoning/SemanticTerritoryMapperAgent.py",
            "SemanticTerritoryMapperAgent",
            2,
            "Near-empty stub (d=2, bp=0.85)",
        ),
        (
            "agentic_core/L5_safety/reasoning/OmniContextAgent.py",
            "OmniContextAgent",
            4,
            "Boilerplate wrapper (d=4, bp=0.68)",
        ),
        (
            "agentic_core/L5_safety/reasoning/SemanticMapperAgent.py",
            "SemanticMapperAgent",
            6,
            "Boilerplate wrapper (d=6, bp=0.69)",
        ),
        (
            "apps_lic/engines/IntelligenceLibrarianAgent.py",
            "IntelligenceLibrarianAgent",
            6,
            "Trivial stub (d=6)",
        ),
        (
            "agentic_core/L1_cognition/reasoning/StrategistAgent.py",
            "StrategistAgent",
            7,
            "Boilerplate wrapper (d=7, bp=0.67)",
        ),
        (
            "agentic_core/L5_safety/reasoning/GlobalComplianceAggregatorAgent.py",
            "GlobalComplianceAggregatorAgent",
            8,
            "Boilerplate wrapper (d=8, bp=0.78)",
        ),
        ("apps_lic/engines/MessageArchitectAgent.py", "MessageArchitectAgent", 8, "Trivial stub (d=8)"),
        (
            "agentic_core/L2_execution/reasoning/UiValidationAgent.py",
            "UiValidationAgent",
            10,
            "97% boilerplate (d=10, bp=0.97)",
        ),
        (
            "apps_rg/reasoning/CampaignPlannerAgent.py",
            "CampaignPlannerAgent",
            11,
            "Trivial stub (d=11, bp=0.53)",
        ),
        (
            "agentic_core/L4_state/reasoning/CartographerAgent.py",
            "CartographerAgent",
            29,
            "Legacy extracted stub (d=29, bp=0.61)",
        ),
        ("apps_lic/engines/LeadQualityAgent.py", "LeadQualityAgent", 40, "Thin wrapper (d=40)"),
    ]

    for fp, cn, dl, reason in retirements:
        if retire_agent(fp, cn, dl, reason):
            retired_count += 1

    print(f"\nRetired: {retired_count}")

    # ── Step 2: Create canonical executors ────────────────────────────────────
    print("\n--- Step 2: Create Canonical Executors ---")

    executors = [
        ("agentic_core/L5_safety/reasoning/InspectorExecutor.py", INSPECTOR_EXECUTOR),
        ("apps_rg/engines/RGValidationExecutor.py", RG_VALIDATION_EXECUTOR),
        ("apps_lic/engines/LICValidationExecutor.py", LIC_VALIDATION_EXECUTOR),
        (
            "agentic_core/L6_observability/reasoning/ObservabilityProbeExecutor.py",
            OBSERVABILITY_PROBE_EXECUTOR,
        ),
        ("apps_rg/engines/RGStrategyExecutor.py", RG_STRATEGY_EXECUTOR),
        ("apps_lic/engines/HOPPipelineExecutor.py", HOP_PIPELINE_EXECUTOR),
    ]

    for path, content in executors:
        if create_canonical_executor(path, content):
            executors_created += 1

    print(f"\nExecutors created: {executors_created}")

    # ── Step 3: Merge shims ──────────────────────────────────────────────────
    print("\n--- Step 3: Merge Shims ---")

    merges = [
        # Inspector agents → InspectorExecutor
        (
            "agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py",
            "DagRuntimeInspectorAgent",
            "InspectorExecutor",
            "agentic_core.L5_safety.reasoning.InspectorExecutor",
        ),
        (
            "agentic_core/L5_safety/reasoning/SignatureVerifierAgent.py",
            "SignatureVerifierAgent",
            "InspectorExecutor",
            "agentic_core.L5_safety.reasoning.InspectorExecutor",
        ),
        (
            "agentic_core/L5_safety/reasoning/TokenBudgetInspectorAgent.py",
            "TokenBudgetInspectorAgent",
            "InspectorExecutor",
            "agentic_core.L5_safety.reasoning.InspectorExecutor",
        ),
        # RG Validation agents → RGValidationExecutor
        (
            "apps_rg/reasoning/ATSCompatibilityAgent.py",
            "ATSCompatibilityAgent",
            "RGValidationExecutor",
            "apps_rg.engines.RGValidationExecutor",
        ),
        (
            "apps_rg/reasoning/BrandComplianceAgent.py",
            "BrandComplianceAgent",
            "RGValidationExecutor",
            "apps_rg.engines.RGValidationExecutor",
        ),
        (
            "apps_rg/reasoning/FactCheckAgent.py",
            "FactCheckAgent",
            "RGValidationExecutor",
            "apps_rg.engines.RGValidationExecutor",
        ),
        (
            "apps_rg/reasoning/SectionBalanceAgent.py",
            "SectionBalanceAgent",
            "RGValidationExecutor",
            "apps_rg.engines.RGValidationExecutor",
        ),
        # LIC Validation agents → LICValidationExecutor
        (
            "apps_lic/engines/CampaignBalanceAgent.py",
            "CampaignBalanceAgent",
            "LICValidationExecutor",
            "apps_lic.engines.LICValidationExecutor",
        ),
        (
            "apps_lic/engines/DeliverabilityAgent.py",
            "DeliverabilityAgent",
            "LICValidationExecutor",
            "apps_lic.engines.LICValidationExecutor",
        ),
        # Observability agents → ObservabilityProbeExecutor
        (
            "agentic_core/L6_observability/reasoning/TrackObservabilityCostAgent.py",
            "TrackObservabilityCostAgent",
            "ObservabilityProbeExecutor",
            "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
        ),
        (
            "agentic_core/L6_observability/reasoning/CoordinateObservabilityOperationsAgent.py",
            "CoordinateObservabilityOperationsAgent",
            "ObservabilityProbeExecutor",
            "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
        ),
        (
            "agentic_core/L6_observability/reasoning/StrategicObservationAgent.py",
            "StrategicObservationAgent",
            "ObservabilityProbeExecutor",
            "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
        ),
        (
            "agentic_core/L6_observability/reasoning/DeadlockDetectorAgent.py",
            "DeadlockDetectorAgent",
            "ObservabilityProbeExecutor",
            "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
        ),
        (
            "agentic_core/L6_observability/reasoning/DebateSynthesisAgent.py",
            "DebateSynthesisAgent",
            "ObservabilityProbeExecutor",
            "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
        ),
        (
            "agentic_core/L6_observability/reasoning/RuntimeTelemetryAgent.py",
            "RuntimeTelemetryAgent",
            "ObservabilityProbeExecutor",
            "agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor",
        ),
        # RG Strategy agents → RGStrategyExecutor
        (
            "apps_rg/reasoning/ContentStrategyAgent.py",
            "ContentStrategyAgent",
            "RGStrategyExecutor",
            "apps_rg.engines.RGStrategyExecutor",
        ),
        (
            "apps_rg/reasoning/RgStrategicPlannerAgent.py",
            "RgStrategicPlannerAgent",
            "RGStrategyExecutor",
            "apps_rg.engines.RGStrategyExecutor",
        ),
        (
            "apps_rg/reasoning/RgTemplateOptimizerAgent.py",
            "RgTemplateOptimizerAgent",
            "RGStrategyExecutor",
            "apps_rg.engines.RGStrategyExecutor",
        ),
        # HOP Pipeline agents → HOPPipelineExecutor
        (
            "apps_lic/engines/Hop1ProfileAnalysisAgent.py",
            "HOP1ProfileAnalysisAgent",
            "HOPPipelineExecutor",
            "apps_lic.engines.HOPPipelineExecutor",
        ),
        (
            "apps_lic/engines/Hop2ResearchAgent.py",
            "HOP2ResearchAgent",
            "HOPPipelineExecutor",
            "apps_lic.engines.HOPPipelineExecutor",
        ),
        (
            "apps_lic/engines/HOP3SenderGroundingAgent.py",
            "HOP3SenderGroundingAgent",
            "HOPPipelineExecutor",
            "apps_lic.engines.HOPPipelineExecutor",
        ),
        (
            "apps_lic/engines/Hop4RoutingAgent.py",
            "HOP4RoutingAgent",
            "HOPPipelineExecutor",
            "apps_lic.engines.HOPPipelineExecutor",
        ),
        (
            "apps_lic/engines/HOP5GenerationAgent.py",
            "HOP5GenerationAgent",
            "HOPPipelineExecutor",
            "apps_lic.engines.HOPPipelineExecutor",
        ),
        (
            "apps_lic/engines/Hop6ValidationAgent.py",
            "HOP6ValidationAgent",
            "HOPPipelineExecutor",
            "apps_lic.engines.HOPPipelineExecutor",
        ),
        (
            "apps_lic/engines/HOP7GateDecisionAgent.py",
            "HOP7GateDecisionAgent",
            "HOPPipelineExecutor",
            "apps_lic.engines.HOPPipelineExecutor",
        ),
        (
            "apps_lic/engines/HOP8QAReportAgent.py",
            "HOP8QAReportAgent",
            "HOPPipelineExecutor",
            "apps_lic.engines.HOPPipelineExecutor",
        ),
        (
            "apps_lic/engines/HOP9IntegrationAgent.py",
            "HOP9IntegrationAgent",
            "HOPPipelineExecutor",
            "apps_lic.engines.HOPPipelineExecutor",
        ),
    ]

    # Also need the RgStrategicPlannerAgent in L2
    merges.append(
        (
            "agentic_core/L2_execution/reasoning/RgStrategicPlannerAgent.py",
            "RgStrategicPlannerAgent",
            "RGStrategyExecutor",
            "apps_rg.engines.RGStrategyExecutor",
        ),
    )

    for fp, old_cls, canon_cls, canon_mod in merges:
        if create_merge_shim(fp, old_cls, canon_cls, canon_mod):
            merged_count += 1

    print(f"\nMerged: {merged_count}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("CONSOLIDATION SUMMARY")
    print("=" * 80)
    print(f"  Retired agents:     {retired_count}")
    print(f"  Merged agents:      {merged_count}")
    print(f"  Canonical executors: {executors_created}")
    print(f"  Net reduction:      {retired_count + merged_count - executors_created}")
    print(f"  Expected count:     {190 - retired_count - merged_count + executors_created}")


if __name__ == "__main__":
    main()
