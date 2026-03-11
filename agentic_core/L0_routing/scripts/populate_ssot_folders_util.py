from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# scripts/populate_ssot_folders_util.py
"""
Intelligent sovereign population of all approved SSOT subfolders.
Generates high-signal __init__.py with:
- Layer-specific purpose derived from SSOT path
- Best-practice guidelines
- Canonical research references
- Future curation roadmap
"""

import sys
from pathlib import Path

# Anchor to project root to allow imports
project_root = (
    Path(__file__).resolve().parents[3]
)  # Go up 3 levels: scripts -> L0_routing -> agentic_core -> project_root
if str(project_root) not in sys.path:
    # guardian: allow-global-mutation
    sys.path.insert(0, str(project_root))

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L0_routing.config.path_constants import CORE_SUBFOLDER_MAP

core_root = project_root / AGENTIC_CORE_DIR

# Layer-specific high-signal content
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
        "meta_prompts": "Sovereign prompt constitution and system prompts. No raw strings outside this folder.",
    },
}


def get_purpose(l1: str, l2: str, depth3: str = None) -> str:
    layer_data = LAYER_BEST_PRACTICES.get(l1, {})
    # Check depth3 match, then l2 match, then layer default
    key = depth3 if depth3 and depth3 in layer_data else l2
    specific = layer_data.get(key, layer_data.get("default", "Sovereign territory"))
    return specific


def generate_init_content(l1: str, l2: str, depth3: str = None) -> str:
    folder = f"{l1}/{l2}" + (f"/{depth3}" if depth3 else "")
    title = f"{folder} – Sovereign Territory"
    purpose = get_purpose(l1, l2, depth3)

    template = f'''"""
{title}

Purpose:
    {purpose}

Best Practices:
    - Single responsibility per module
    - Explicit imports only from approved layers (gravity compliance)
    - All public functions/classes fully typed and documented
    - No side effects unless explicitly in L2_execution or L4_state
    - No raw strings — use prompt_governance for prompts
    - No inline Pydantic models — use schemas/models

Current Status (December 28, 2025):
    - Territory claimed and protected
    - Awaiting sovereign curation of high-signal implementations

Future Curation Roadmap:
    - Implement canonical patterns for this layer
    - Add unit + property + stateful tests
    - Register with relevant L4/L5 systems
"""

# Public API surface — expose only what's intended
__all__ = []

# Example placeholder (replace when populated)
# from .core_module import CoreImplementation
'''
    return template.strip() + "\n"


def main():
    print("[*] Starting Intelligent Sovereign Population...")
    populated = 0

    # Ensure core root exists
    if not core_root.exists():
        print(f"[!] Error: {core_root} not found.")
        return

    # Iterate over SSOT structure
    # UPDATED: Use SOVEREIGN_TERRITORIES to get agentic_core subfolders
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

            # Populate L2
            init_path = l2_path / "__init__.py"
            # Overwrite if empty or very small (low signal)
            if not init_path.exists() or init_path.stat().st_size < 200:
                assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
                init_path.write_text(generate_init_content(l1, l2), encoding="utf-8")
                print(f"   [SMART POPULATED] {l2_path.relative_to(project_root)}/__init__.py")
                populated += 1

            # Populate Depth-3
            for depth3 in l2_path.iterdir():
                if depth3.is_dir() and depth3.name not in {"__pycache__"}:
                    d3_init = depth3 / "__init__.py"
                    if not d3_init.exists() or d3_init.stat().st_size < 200:
                        assert_no_persistent_write("L0", "write_text")  # G-12-1: mutation prohibition guard
                        d3_init.write_text(generate_init_content(l1, l2, depth3.name), encoding="utf-8")
                        print(f"   [SMART POPULATED] {depth3.relative_to(project_root)}/__init__.py")
                        populated += 1

    print(f"\n[COMPLETE] {populated} SSOT folders intelligently populated with layer-specific best practices")


if __name__ == "__main__":
    main()
