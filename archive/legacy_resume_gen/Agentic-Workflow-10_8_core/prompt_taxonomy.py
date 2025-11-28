from enum import Enum


class PromptSection(str, Enum):
    FRAMING = "Framing"
    CONTEXT = "Context"
    REASONING = "Reasoning"
    INSTRUCTIONS = "Instructions"
    SAFETY = "Safety Signals"
    OUTPUT_SCHEMA = "Output Schema"


class InjectionType(str, Enum):
    OVERRIDE_SYSTEM = "override_system"
    IGNORE_PREVIOUS = "ignore_previous_instructions"
    DISABLE_SAFETY = "disable_safety"
    RUN_ARBITRARY_CODE = "run_arbitrary_code"


class InstructionalInjection(str, Enum):
    GLOBAL_GOAL = "global_goal_state_injection"
    SUCCESS_CRITERIA = "success_criteria_injection"
    TASK_MODE = "task_mode_declaration"
    SCOPE_BOUNDARIES = "scope_boundaries_injection"
    COST_LATENCY = "cost_latency_targets"

    UNTRUSTED_BLOCK = "untrusted_block_wrapping"
    CANONICALIZE_INPUT = "canonicalization_of_inputs"
    CONTEXT_PRUNING = "context_pruning_rules"
    CROSS_FIELD_CONSISTENCY = "cross_field_consistency_checks"
    STRUCTURED_ORDERING = "structured_context_ordering"

    FAILURE_ANTICIPATION = "failure_anticipation"
    SELF_CONSISTENCY = "self_consistency_multi_branch"
    UNCERTAINTY = "confidence_uncertainty_injection"
    REASON_THEN_ANSWER = "reason_then_answer"
    ERROR_SIMULATION = "error_simulation"

    TOOL_FEEDBACK = "tool_feedback_loop"
    CITATION_BINDING = "evidence_binding"
    TOOL_RECONCILIATION = "cross_tool_reconciliation"
    SHADOW_VALIDATION = "shadow_validation"
    MODEL_SWITCH = "model_switch_awareness"

    INJECTION_SHIELD = "prompt_injection_shielding"
    DATA_INSTRUCTION_SEPARATION = "data_instruction_separation"
    CONSTITUTIONAL = "constitutional_guardrails"
    DELEGATION = "delegation_guardrails"
    ADVERSARIAL = "expanded_adversarial_mode"

    STRICT_JSON = "strict_json_output"
    SCHEMA_ENFORCEMENT = "schema_enforcement"
    STABILITY_CONTRACT = "stability_contracts"
    ERROR_NORMALIZATION = "error_envelope_normalization"
    MINIMALITY = "minimality_constraints"


SECTION_ORDER = [
    PromptSection.FRAMING,
    PromptSection.CONTEXT,
    PromptSection.REASONING,
    PromptSection.INSTRUCTIONS,
    PromptSection.SAFETY,
    PromptSection.OUTPUT_SCHEMA,
]


DEFAULT_INJECTION_PATTERNS = [
    InjectionType.OVERRIDE_SYSTEM.value,
    InjectionType.IGNORE_PREVIOUS.value,
    InjectionType.DISABLE_SAFETY.value,
    InjectionType.RUN_ARBITRARY_CODE.value,
]


INSTRUCTIONAL_INJECTION_ALL = [i.value for i in InstructionalInjection]
