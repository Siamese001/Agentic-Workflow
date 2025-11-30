#!/usr/bin/env python3
"""
Create Canonical Directory Structure for Agentic Workflow v10_11
Builds the exact directory structure defined in markdown specs
"""

import os
from pathlib import Path

def create_agentic_core_structure(base_path: Path):
    """Create the complete agentic_core directory structure"""
    
    # L1 Planning
    l1_dirs = [
        "agentic_core/l1_planning/strategy_planning/blueprint/goals",
        "agentic_core/l1_planning/strategy_planning/blueprint/signals",
        "agentic_core/l1_planning/strategy_planning/blueprint/orchestration",
        "agentic_core/l1_planning/strategy_planning/decomposition",
        "agentic_core/l1_planning/strategy_planning/refinement",
        "agentic_core/l1_planning/qa_planning/question_understanding",
        "agentic_core/l1_planning/qa_planning/retrieval_plans",
        "agentic_core/l1_planning/qa_planning/answer_blueprints",
        "agentic_core/l1_planning/rag_planning/query_generation",
        "agentic_core/l1_planning/rag_planning/fusion",
        "agentic_core/l1_planning/rag_planning/routing",
        "agentic_core/l1_planning/safety_planning/detectors",
        "agentic_core/l1_planning/safety_planning/policies",
        "agentic_core/l1_planning/safety_planning/mitigation",
        "agentic_core/l1_planning/utils"
    ]
    
    # L2 Execution
    l2_dirs = [
        "agentic_core/l2_execution/tools/browser",
        "agentic_core/l2_execution/tools/file_ops",
        "agentic_core/l2_execution/tools/api",
        "agentic_core/l2_execution/execution_engines",
        "agentic_core/l2_execution/utils"
    ]
    
    # L3 Orchestration
    l3_dirs = [
        "agentic_core/l3_orchestration/dag/node_types",
        "agentic_core/l3_orchestration/react",
        "agentic_core/l3_orchestration/controllers"
    ]
    
    # L4 Memory
    l4_dirs = [
        "agentic_core/l4_memory/short_term",
        "agentic_core/l4_memory/long_term",
        "agentic_core/l4_memory/state"
    ]
    
    # L5 Safety
    l5_dirs = [
        "agentic_core/l5_safety/filters",
        "agentic_core/l5_safety/guardrails",
        "agentic_core/l5_safety/audit"
    ]
    
    all_dirs = l1_dirs + l2_dirs + l3_dirs + l4_dirs + l5_dirs
    
    print(f"Creating {len(all_dirs)} directories for agentic_core/")
    
    for dir_path in all_dirs:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {dir_path}")

def create_apps_structure(base_path: Path):
    """Create the complete apps directory structure"""
    
    apps_dirs = [
        # Resume Engine
        "apps/resume_engine/api/v1/endpoints",
        "apps/resume_engine/api/v1/schemas",
        "apps/resume_engine/api/v1/middleware",
        "apps/resume_engine/services/builders",
        "apps/resume_engine/services/enrichers",
        "apps/resume_engine/services/generators",
        "apps/resume_engine/services/pipelines",
        "apps/resume_engine/services/utils",
        "apps/resume_engine/workers",
        "apps/resume_engine/cli",
        "apps/resume_engine/tests/unit",
        "apps/resume_engine/tests/integration",
        "apps/resume_engine/tests/e2e",
        
        # Outreach Engine
        "apps/outreach_engine/api/v1/endpoints",
        "apps/outreach_engine/api/v1/schemas",
        "apps/outreach_engine/api/v1/middleware",
        "apps/outreach_engine/services/planners",
        "apps/outreach_engine/services/generators",
        "apps/outreach_engine/services/enrichers",
        "apps/outreach_engine/services/pipelines",
        "apps/outreach_engine/services/utils",
        "apps/outreach_engine/workers",
        "apps/outreach_engine/cli",
        "apps/outreach_engine/tests/unit",
        "apps/outreach_engine/tests/integration",
        "apps/outreach_engine/tests/e2e",
        
        # Shared
        "apps/shared/utils",
        "apps/shared/adapters",
        "apps/shared/tests/unit",
        "apps/shared/tests/integration",
        "apps/shared/tests/e2e"
    ]
    
    print(f"Creating {len(apps_dirs)} directories for apps/")
    
    for dir_path in apps_dirs:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {dir_path}")

def create_config_structure(base_path: Path):
    """Create the complete config directory structure"""
    
    config_dirs = [
        # Services - Resume Engine
        "config/services/resume_engine/routing",
        "config/services/resume_engine/prompts",
        "config/services/resume_engine/policies",
        "config/services/resume_engine/defaults",
        "config/services/resume_engine/schemas",
        
        # Services - Outreach Engine
        "config/services/outreach_engine/routing",
        "config/services/outreach_engine/prompts",
        "config/services/outreach_engine/policies",
        "config/services/outreach_engine/defaults",
        "config/services/outreach_engine/schemas",
        
        # Services - Shared
        "config/services/shared/llm",
        "config/services/shared/telemetry",
        "config/services/shared/memory",
        "config/services/shared/tools",
        
        # Other config directories
        "config/environments/dev",
        "config/environments/staging",
        "config/environments/prod",
        "config/loaders"
    ]
    
    print(f"Creating {len(config_dirs)} directories for config/")
    
    for dir_path in config_dirs:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {dir_path}")

def create_all_canonical_structures():
    """Create all canonical directory structures"""
    base_path = Path(__file__).parent
    
    print("=== Creating Canonical Directory Structures ===")
    
    # Create each root structure
    create_agentic_core_structure(base_path)
    create_apps_structure(base_path)
    create_config_structure(base_path)
    
    # TODO: Add other roots (data, observability, etc.)
    
    print("\n=== Canonical structure creation complete ===")

if __name__ == "__main__":
    create_all_canonical_structures()
