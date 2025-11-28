from dataclasses import dataclass


@dataclass
class SafetyOutputProfile:
    prompt_shield: bool
    data_instruction_separation: bool
    constitutional_guardrails_enabled: bool
    delegation_guardrails_enabled: bool
    adversarial_mode_enabled: bool
    strict_json_output: bool
    enforce_schema: bool
    stability_contracts: bool
    error_normalization: bool
    minimality_constraints: bool


DEFAULT_SAFETY_OUTPUT_PROFILE = SafetyOutputProfile(
    prompt_shield=True,
    data_instruction_separation=True,
    constitutional_guardrails_enabled=True,
    delegation_guardrails_enabled=True,
    adversarial_mode_enabled=True,
    strict_json_output=False,     # opt-in for stacks using schema
    enforce_schema=False,
    stability_contracts=True,
    error_normalization=True,
    minimality_constraints=True,
)
