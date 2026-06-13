"""
Canonical code paths per owning_layer.

These tell the implementation_mapper where to LOOK for code that satisfies a
requirement. They are deliberately generous (some layers list multiple
candidate roots) so that a candidate match is not silently lost.

The mapper records EVERY path under which an anchor symbol resolves; if
matches appear under both the canonical layer root AND outside it, we mark
CROSS_LAYER for human review rather than guessing.
"""

from __future__ import annotations

from typing import Tuple

# Directory roots searched for symbol matches per owning_layer.
# Repo-relative POSIX paths. Multiple entries = OR (match in any qualifies).
LAYER_CODE_ROOTS: dict[str, Tuple[str, ...]] = {
    "U0": (
        "agentic_core/L0_routing/intake/",
        "apps_eval/integrations/",
        "apps_exec/integrations/",
        "apps_research/integrations/",
        "apps_rg/integrations/",
        "apps_lic/integrations/",
        "apps_underwriting_ai/ingestion/",
        "agentic_core/runtime/entry/",
    ),
    "L1": (
        "agentic_core/L1_cognition/",
    ),
    "L0": (
        "agentic_core/L0_routing/",
    ),
    "L3": (
        "agentic_core/L3_orchestration/",
    ),
    "L2": (
        "agentic_core/L2_execution/",
    ),
    "L4": (
        "agentic_core/L4_state/",
    ),
    "L5": (
        "agentic_core/L5_safety/",
    ),
    "L6": (
        "agentic_core/L6_observability/",
    ),
    "C0": (
        "agentic_core/L1_cognition/c0_context/",
        "agentic_core/L0_routing/c0_retrieval/",
    ),
    "C0.0": (
        "agentic_core/L1_cognition/c0_context/",
        "agentic_core/L0_routing/c0_retrieval/",
    ),
    "C0.1": (
        "agentic_core/L1_cognition/c0_context/",
        "agentic_core/L0_routing/c0_retrieval/",
    ),
    "C0.2": (
        "agentic_core/L1_cognition/c0_context/",
        "agentic_core/L0_routing/c0_retrieval/",
    ),
    "C0.3": (
        "agentic_core/L1_cognition/c0_context/",
        "agentic_core/L0_routing/c0_retrieval/",
        "agentic_core/knowledge/",
    ),
    "C0.4": (
        "agentic_core/L1_cognition/c0_context/",
        "agentic_core/L0_routing/c0_retrieval/",
    ),
    "C0.5": (
        "agentic_core/L1_cognition/c0_context/",
        "agentic_core/L0_routing/c0_retrieval/",
        "agentic_core/runtime/contracts/",
    ),
    "C0.6": (
        "agentic_core/L1_cognition/c0_context/",
        "agentic_core/L0_routing/c0_retrieval/",
    ),
    "C0.7": (
        "agentic_core/L1_cognition/c0_context/",
        "agentic_core/L0_routing/c0_retrieval/",
    ),
    "PA": (
        "agentic_core/prompt_governance/",
    ),
    "Exit": (
        "agentic_core/L5_safety/exit_control/",
        "agentic_core/L5_safety/eval_spine/",
        "agentic_core/runtime/exceptions/",
        "apps_eval/engines/",
    ),
    "UWG": (
        "agentic_core/L4_state/",
    ),
    "RuntimeGates": (
        "agentic_core/L5_safety/runtime_gates/",
        "agentic_core/L5_safety/enforcement/",
        "agentic_core/L5_safety/validators/",
    ),
    "CrossCutting": (
        "agentic_core/",
        "apps_eval/",
        "apps_exec/",
    ),
}


# Test path roots searched for test coverage of a symbol.
TEST_PATH_ROOTS: Tuple[str, ...] = (
    "tests/agentic_core/",
    "tests/integration/",
    "tests/e2e/",
    "tests/runtime/",
    "tests/runtime_gates/",
    "tests/uwg/",
    "tests/l4/",
    "tests/governance/",
    "tests/system_learning/",
    "tests/unit/",
)


def candidate_roots_for_layer(owning_layer: str) -> Tuple[str, ...]:
    """Return the canonical code roots for the given owning_layer."""
    return LAYER_CODE_ROOTS.get(owning_layer, LAYER_CODE_ROOTS["CrossCutting"])
