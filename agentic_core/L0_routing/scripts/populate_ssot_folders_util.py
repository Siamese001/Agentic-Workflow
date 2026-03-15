from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "populate_ssot_folders_util", "L0")
_emit_routes_through("p1", "populate_ssot_folders_util", "L0")
_emit_escalates_to_human("p1", "populate_ssot_folders_util", "L0")
_emit_reads_policy_state("p1", "populate_ssot_folders_util", "L0")

"\nIntelligent sovereign population of all approved SSOT subfolders.\nGenerates high-signal __init__.py with:\n- Layer-specific purpose derived from SSOT path\n- Best-practice guidelines\n- Canonical research references\n- Future curation roadmap\n"
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
# guardian: allow-global-mutation
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import CORE_SUBFOLDER_MAP
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

core_root = project_root / AGENTIC_CORE_DIR
LAYER_BEST_PRACTICES = {
    "L1_cognition": {
        "default": "Pure reasoning and thought generation. No side effects. Immutable inputs → deterministic outputs.",
        "thought_engine": "Chain-of-thought, tree-of-thought, ReAct pattern implementations. Reference: Yao et al. (2022) ReAct paper.",
        "planning": "Hierarchical Task decomposition. HTN, BDI patterns. Reference: Ghallab et al. 'PDDL'.",
        "knowledge": "Static, curated eternal truth. No dynamic retrieval here — use semantic_memory for runtime.",
        "static_index": "Permanent store of vetted research papers, prompt constitutions, tool schemas. Indexed at embed time.",
    },
    "L2_execution": {
        "default": "Safe, sandboxed tool interaction. All tools must be registered and validated.",
        "tool_registry": "Single source of truth for all available tools. Each tool: schema + implementation + safety policy.",
        "sandbox": "Isolated execution environment. No direct system access outside approved tools.",
    },
    "L3_orchestration": {
        "default": "Workflow composition and agent handoff. Memory-aware routing.",
        "workflow_engines": "State machine, DAG, and reactive workflow implementations. Reference: Temporal.io patterns.",
    },
    "L4_state": {
        "default": "Persistent, auditable state management. Redis-backed ledger.",
        "ValidationContext": "Checkpointing, session persistence, drift detection.",
        "persistence_layer": "Single interface to Redis/Pinecone/filesystem — abstraction only.",
    },
    "L5_safety": {
        "default": "Red-team guards, policy enforcement, auto-immune response.",
        "policy": "Formal policy definitions. All actions routed through L5 before execution.",
        "audit_logs": "Immutable forensic ledger. Every decision recorded.",
    },
    "semantic_memory": {
        "vector_stores": "Abstract interface to Pinecone/Chroma/etc. No direct imports — use registry.",
        "embedding_logic": "Gemini-only embedding pipeline. No fallback to other providers.",
    },
    "prompt_governance": {
        "meta_prompts": "Sovereign prompt constitution and system prompts. No raw strings outside this folder."
    },
}


def get_purpose(l1: str, l2: str, depth3: str = None) -> str:
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_purpose", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_purpose", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_purpose")
    layer_data = LAYER_BEST_PRACTICES.get(l1, {})
    key = depth3 if depth3 and depth3 in layer_data else l2
    specific = layer_data.get(key, layer_data.get("default", "Sovereign territory"))
    return specific


def generate_init_content(l1: str, l2: str, depth3: str = None) -> str:
    folder = f"{l1}/{l2}" + (f"/{depth3}" if depth3 else "")
    title = f"{folder} – Sovereign Territory"
    purpose = get_purpose(l1, l2, depth3)
    template = f'''"""\n{title}\n\nPurpose:\n    {purpose}\n\nBest Practices:\n    - Single responsibility per module\n    - Explicit imports only from approved layers (gravity compliance)\n    - All public functions/classes fully typed and documented\n    - No side effects unless explicitly in L2_execution or L4_state\n    - No raw strings — use prompt_governance for prompts\n    - No inline Pydantic models — use schemas/models\n\nCurrent Status (December 28, 2025):\n    - Territory claimed and protected\n    - Awaiting sovereign curation of high-signal implementations\n\nFuture Curation Roadmap:\n    - Implement canonical patterns for this layer\n    - Add unit + property + stateful tests\n    - Register with relevant L4/L5 systems\n"""\n\n# Public API surface — expose only what's intended\n__all__ = []\n\n# Example placeholder (replace when populated)\n# from .core_module import CoreImplementation\n'''
    return template.strip() + "\n"


def main():
    print("[*] Starting Intelligent Sovereign Population...")
    populated = 0
    if not core_root.exists():
        print(f"[!] Error: {core_root} not found.")
        return
    l1_folders = list(CORE_SUBFOLDER_MAP.keys())
    for l1 in l1_folders:
        l1_path = core_root / l1
        if not l1_path.exists():
            continue
        l2_folders = CORE_SUBFOLDER_MAP.get(l1, [])
        for l2 in l2_folders:
            l2_path = l1_path / l2
            if not l2_path.exists():
                continue
            init_path = l2_path / "__init__.py"
            if not init_path.exists() or init_path.stat().st_size < 200:
                assert_no_persistent_write("L0", "write_text")
                init_path.write_text(generate_init_content(l1, l2), encoding="utf-8")
                print(f"   [SMART POPULATED] {l2_path.relative_to(project_root)}/__init__.py")
                populated += 1
            for depth3 in l2_path.iterdir():
                if depth3.is_dir() and depth3.name not in {"__pycache__"}:
                    d3_init = depth3 / "__init__.py"
                    if not d3_init.exists() or d3_init.stat().st_size < 200:
                        assert_no_persistent_write("L0", "write_text")
                        d3_init.write_text(generate_init_content(l1, l2, depth3.name), encoding="utf-8")
                        print(f"   [SMART POPULATED] {depth3.relative_to(project_root)}/__init__.py")
                        populated += 1
    print(f"\n[COMPLETE] {populated} SSOT folders intelligently populated with layer-specific best practices")


if __name__ == "__main__":
    main()
