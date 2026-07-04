"""apps-test-model: HARNESS.

Static import coverage for modules newly surfaced by the ADG test-harness gate.
"""

import agentic_core.L1_cognition.apps_research_c0_binding as apps_research_c0_binding
import agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway as qwen_inference_gateway
import agentic_core.L6_observability.shadow_eval.adapters.runtime_exhaust_v40 as runtime_exhaust_v40
import agentic_core.L6_observability.shadow_eval.post_boundary_runner as post_boundary_runner
import agentic_core.L6_system_learning.engine as l6_system_learning_engine
import agentic_core.L6_system_learning.shadow_evaluator as l6_shadow_evaluator
import apps_lic.engines.message_intelligence_packet as message_intelligence_packet
import apps_lic.integrations.governed_lic_exception as governed_lic_exception
from apps_exec.integrations import governed_exec_run
from apps_research.integrations import search_retrieval, searxng_readiness


def test_adg_harness_imports_newly_surfaced_modules() -> None:
    modules = [
        apps_research_c0_binding,
        qwen_inference_gateway,
        runtime_exhaust_v40,
        post_boundary_runner,
        l6_system_learning_engine,
        l6_shadow_evaluator,
        governed_exec_run,
        message_intelligence_packet,
        governed_lic_exception,
        search_retrieval,
        searxng_readiness,
    ]

    assert {module.__name__ for module in modules} == {
        "agentic_core.L1_cognition.apps_research_c0_binding",
        "agentic_core.L3_orchestration.inference.qwen_vllm.reasoning.qwen_inference_gateway",
        "agentic_core.L6_observability.shadow_eval.adapters.runtime_exhaust_v40",
        "agentic_core.L6_observability.shadow_eval.post_boundary_runner",
        "agentic_core.L6_system_learning.engine",
        "agentic_core.L6_system_learning.shadow_evaluator",
        "apps_exec.integrations.governed_exec_run",
        "apps_lic.engines.message_intelligence_packet",
        "apps_lic.integrations.governed_lic_exception",
        "apps_research.integrations.search_retrieval",
        "apps_research.integrations.searxng_readiness",
    }
