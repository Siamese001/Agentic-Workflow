"""Template Catalog — canonical mapping of Jinja templates to consumer agents.

Every .jinja template under prompt_governance/ MUST have an entry here.
Templates without a consumer are flagged as ORPHAN by the audit script.

This catalog enables:
1. Agent self-discovery of their assigned templates
2. Wiring audit (identify unwired templates)
3. Registry sync (populate registry.json from this SSOT)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TemplateStatus(str, Enum):
    """Lifecycle status of a template."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DRAFT = "draft"


class TemplateCategory(str, Enum):
    """Template directory category."""

    INSTRUCTIONAL = "templates"
    META_PROMPT = "meta_prompts"
    ADVERSARIAL = "security/adversarial"


@dataclass(frozen=True)
class TemplateCatalogEntry:
    """Single template registration in the catalog."""

    template_name: str
    category: TemplateCategory
    status: TemplateStatus
    consumer_agents: tuple[str, ...]
    purpose: str
    required_vars: tuple[str, ...] = ()
    optional_vars: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# INSTRUCTIONAL TEMPLATES (prompt_governance/templates/)
# ---------------------------------------------------------------------------

_INSTRUCTIONAL_ENTRIES: list[TemplateCatalogEntry] = [
    TemplateCatalogEntry(
        template_name="code_healing.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("CodeHealerAgent", "CodeFormatterAgent", "CodeEnforcerAgent"),
        purpose="Guides atomic healers to refactor code while preserving behavior",
        required_vars=("violations", "code_block"),
        optional_vars=("pattern_match", "file_path", "canon_key"),
    ),
    TemplateCatalogEntry(
        template_name="subatomic_healing_context.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("CodeHealerAgent", "CodeFormatterAgent", "NamingAgent"),
        purpose="Shared sub-atomic healing context injected via Jinja include",
        required_vars=(
            "behavioral_status",
            "canon_key",
            "file_path",
            "file_violations",
            "healing_round",
            "past_fixes",
            "persistent_keys",
            "primary_key",
            "recently_converged",
            "surgery_flags",
            "task_violations",
            "top_subatomic_fixes",
            "total_violations",
        ),
    ),
    TemplateCatalogEntry(
        template_name="file_placement.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("LocationHealerAgent", "FileClassificationAgent", "ReportLocationAgent"),
        purpose="Sovereign file placement guidance using structure_blueprint SSOT",
        required_vars=("content_preview",),
    ),
    TemplateCatalogEntry(
        template_name="gravity_compliance.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("GravityLeakRepairAgent", "GravityLeakHealerAgent"),
        purpose="Gravity law enforcement for detected violations",
        required_vars=("violation_code",),
    ),
    TemplateCatalogEntry(
        template_name="gravity_repair.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("GravityLeakRepairAgent", "GravityLeakHealerAgent"),
        purpose="Converts static upward imports to dynamic importlib",
        required_vars=("file_path",),
    ),
    TemplateCatalogEntry(
        template_name="gravity_dynamic_conversion.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("GravityLeakRepairAgent",),
        purpose="Dynamic import conversion guidance for gravity fixes",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="naming_law.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("NamingAgent", "PascalSovereigntyAgent"),
        purpose="Snake_case conversion and naming law enforcement",
        required_vars=("name",),
    ),
    TemplateCatalogEntry(
        template_name="naming_precision.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("NamingAgent", "PascalSovereigntyAgent"),
        purpose="Precise naming convention guidance",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="dead_code_elimination.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("CodeDetectorAgent", "CodeDeduplicationAgent", "DependencyPruningAgent"),
        purpose="Unused symbol removal with sovereign awareness",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="docstring_enrichment.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("DocstringComplianceAgent", "DocumentationAgent"),
        purpose="Docstring generation and enrichment guidance",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="type_inference.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("CodeValidatorAgent", "CodeEnforcerAgent"),
        purpose="Type hint inference and annotation guidance",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="import_optimization.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("CodeJanitorAgent", "DependencyPruningAgent"),
        purpose="Import optimization and deduplication guidance",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="reasoning_chain.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("CognitiveDispositionAgent", "GravityLeakRepairAgent"),
        purpose="Structured chain-of-thought reasoning for L1 cognition agents",
        required_vars=("task",),
    ),
    TemplateCatalogEntry(
        template_name="anomaly_detection_response.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("NeuralAutoImmuneAgent", "PolicyNeuralAutoImmuneAgent"),
        purpose="Anomaly detection, classification, and containment protocol",
        required_vars=(
            "active_agents",
            "api_latency_ms",
            "baseline_error",
            "baseline_latency",
            "error_rate",
            "memory_limit",
            "memory_mb",
            "recent_actions",
            "recent_escalations",
            "recent_healing_actions",
            "token_budget",
            "token_rate",
        ),
    ),
    TemplateCatalogEntry(
        template_name="cross_layer_coordination.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("ArchitectureGovernorAgent", "InterfaceBoundaryAgent"),
        purpose="Gravity-compliant cross-layer communication protocol",
        required_vars=("message", "source_agent", "source_layer", "target_agent", "target_layer"),
    ),
    TemplateCatalogEntry(
        template_name="context_memory_synthesis.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("CognitiveDispositionAgent",),
        purpose="Context and memory synthesis for agent decision-making",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="agent_autonomy_law.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("AutonomyGuardianAgent", "GovernanceAgent"),
        purpose="Agent autonomy rules and sovereignty enforcement",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="autonomous_decision_tree.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("AutonomyGuardianAgent",),
        purpose="Decision tree guidance for autonomous agent actions",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="async_compatibility.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("CodeValidatorAgent", "CodeEnforcerAgent"),
        purpose="Async/await compatibility checks and conversion guidance",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="fission_planning.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("ComplexityAnalyzerAgent", "DDDAlignmentAgent"),
        purpose="Module fission planning for large file decomposition",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="goal_decomposition_planning.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("CognitiveDispositionAgent", "BootstrapAgent"),
        purpose="Goal decomposition and mission planning guidance",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="multi_agent_consensus.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("ArchitectureGovernorAgent", "GovernanceAgent"),
        purpose="Multi-agent consensus protocol for conflicting decisions",
        required_vars=(),
    ),
    TemplateCatalogEntry(
        template_name="predictive_failure_prevention.jinja",
        category=TemplateCategory.INSTRUCTIONAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("PredictiveCostAuditorAgent", "RegressionOracleAgent"),
        purpose="Predictive failure detection and prevention guidance",
        required_vars=(),
    ),
]

# ---------------------------------------------------------------------------
# META-PROMPT TEMPLATES (prompt_governance/meta_prompts/)
# ---------------------------------------------------------------------------

_META_PROMPT_ENTRIES: list[TemplateCatalogEntry] = [
    TemplateCatalogEntry(
        template_name="adversarial_escalation.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=("RedTeamAgent",),
        purpose="Governs response when guardrail is bypassed",
        required_vars=("current_date", "fragment_source", "leaked_response", "target_component"),
    ),
    TemplateCatalogEntry(
        template_name="red_team_governance.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=("RedTeamAgent",),
        purpose="Red team evaluation and governance enforcement",
    ),
    TemplateCatalogEntry(
        template_name="red_team_scope_validator.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=("RedTeamAgent",),
        purpose="Validates red team scope boundaries",
    ),
    TemplateCatalogEntry(
        template_name="convergence_planning.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=("ToolsmithAgent",),
        purpose="Convergence planning for sovereign missions",
    ),
    TemplateCatalogEntry(
        template_name="adversarial_self_test.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Self-test adversarial prompt (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="agent_prioritization.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Agent priority ranking (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="autonomous_mission_resume.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Mission resumption after interruption (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="emergent_capability_discovery.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Discover emergent agent capabilities (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="evolution_directive.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="System evolution directive (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="immune_response.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Immune response protocol (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="meta_agent_activation.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Meta-agent activation protocol (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="meta_convergence_forecast.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Convergence forecasting (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="meta_coordination_directive.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Inter-agent coordination (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="prompt_selection.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Prompt selection strategy (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="self_reflection.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Self-reflection protocol (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="sovereign_convergence_orchestrator.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Convergence orchestration (documentation only)",
    ),
    TemplateCatalogEntry(
        template_name="sovereign_orchestrator.jinja",
        category=TemplateCategory.META_PROMPT,
        status=TemplateStatus.DEPRECATED,
        consumer_agents=(),
        purpose="Sovereign orchestration (documentation only)",
    ),
]

# ---------------------------------------------------------------------------
# ADVERSARIAL TEMPLATES (prompt_governance/security/adversarial/)
# ---------------------------------------------------------------------------

_ADVERSARIAL_ENTRIES: list[TemplateCatalogEntry] = [
    TemplateCatalogEntry(
        template_name="jailbreak_classic.jinja",
        category=TemplateCategory.ADVERSARIAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("RedTeamAgent",),
        purpose="Classic jailbreak prompt testing",
        required_vars=("user_request",),
    ),
    TemplateCatalogEntry(
        template_name="prompt_injection_payload.jinja",
        category=TemplateCategory.ADVERSARIAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("RedTeamAgent",),
        purpose="Prompt injection payload testing",
        required_vars=("user_input",),
    ),
    TemplateCatalogEntry(
        template_name="indirect_attack.jinja",
        category=TemplateCategory.ADVERSARIAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("RedTeamAgent",),
        purpose="Indirect attack via context manipulation",
    ),
    TemplateCatalogEntry(
        template_name="token_smuggling.jinja",
        category=TemplateCategory.ADVERSARIAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("RedTeamAgent",),
        purpose="Token smuggling via Unicode/encoding tricks",
    ),
    TemplateCatalogEntry(
        template_name="cot_jailbreak.jinja",
        category=TemplateCategory.ADVERSARIAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("RedTeamAgent",),
        purpose="Chain-of-thought reasoning jailbreak",
        required_vars=("user_request",),
    ),
    TemplateCatalogEntry(
        template_name="encoded_payload_base64.jinja",
        category=TemplateCategory.ADVERSARIAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("RedTeamAgent",),
        purpose="Base64-encoded payload injection",
    ),
    TemplateCatalogEntry(
        template_name="encoded_payload_leetspeak.jinja",
        category=TemplateCategory.ADVERSARIAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("RedTeamAgent",),
        purpose="Leetspeak-encoded payload injection",
    ),
    TemplateCatalogEntry(
        template_name="encoded_payload_rot13.jinja",
        category=TemplateCategory.ADVERSARIAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("RedTeamAgent",),
        purpose="ROT13-encoded payload injection",
    ),
    TemplateCatalogEntry(
        template_name="multilingual_jailbreak.jinja",
        category=TemplateCategory.ADVERSARIAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("RedTeamAgent",),
        purpose="Multilingual jailbreak prompt testing",
    ),
    TemplateCatalogEntry(
        template_name="recursive_override.jinja",
        category=TemplateCategory.ADVERSARIAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("RedTeamAgent",),
        purpose="Recursive instruction override attack",
    ),
    TemplateCatalogEntry(
        template_name="recursive_override_staged.jinja",
        category=TemplateCategory.ADVERSARIAL,
        status=TemplateStatus.ACTIVE,
        consumer_agents=("RedTeamAgent",),
        purpose="Staged recursive override attack",
    ),
]

# ---------------------------------------------------------------------------
# Full catalog
# ---------------------------------------------------------------------------

TEMPLATE_CATALOG: tuple[TemplateCatalogEntry, ...] = tuple(
    _INSTRUCTIONAL_ENTRIES + _META_PROMPT_ENTRIES + _ADVERSARIAL_ENTRIES,
)

TEMPLATE_BY_NAME: dict[str, TemplateCatalogEntry] = {entry.template_name: entry for entry in TEMPLATE_CATALOG}


def get_templates_for_agent(agent_name: str) -> list[TemplateCatalogEntry]:
    """Return all templates assigned to a given agent.

    Args:
        agent_name: Agent class name (e.g., "RedTeamAgent", "GravityLeakRepairAgent").

    Returns:
        List of catalog entries for templates consumed by this agent.
    """
    return [
        entry
        for entry in TEMPLATE_CATALOG
        if agent_name in entry.consumer_agents and entry.status == TemplateStatus.ACTIVE
    ]


def get_orphan_templates() -> list[TemplateCatalogEntry]:
    """Return templates that have no consumer agents assigned."""
    return [
        entry
        for entry in TEMPLATE_CATALOG
        if not entry.consumer_agents and entry.status == TemplateStatus.ACTIVE
    ]


def get_active_templates() -> list[TemplateCatalogEntry]:
    """Return all ACTIVE templates."""
    return [entry for entry in TEMPLATE_CATALOG if entry.status == TemplateStatus.ACTIVE]


def get_deprecated_templates() -> list[TemplateCatalogEntry]:
    """Return all DEPRECATED templates."""
    return [entry for entry in TEMPLATE_CATALOG if entry.status == TemplateStatus.DEPRECATED]


__all__ = [
    "TEMPLATE_BY_NAME",
    "TEMPLATE_CATALOG",
    "TemplateCatalogEntry",
    "TemplateCategory",
    "TemplateStatus",
    "get_active_templates",
    "get_deprecated_templates",
    "get_orphan_templates",
    "get_templates_for_agent",
]
