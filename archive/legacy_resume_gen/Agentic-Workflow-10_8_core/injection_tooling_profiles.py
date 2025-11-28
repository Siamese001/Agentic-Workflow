from dataclasses import dataclass


@dataclass
class ToolingProfile:
    tool_feedback_enabled: bool
    evidence_binding_enabled: bool
    cross_tool_reconciliation: bool
    shadow_validation_enabled: bool
    model_switch_awareness: bool


DEFAULT_TOOLING_PROFILE = ToolingProfile(
    tool_feedback_enabled=True,
    evidence_binding_enabled=True,
    cross_tool_reconciliation=True,
    shadow_validation_enabled=True,
    model_switch_awareness=True,
)
