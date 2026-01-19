"""
file: tests/maintenance/verify_restored_agents.py
description: Smoke test to identify broken imports in the 10 recently restored agents.
"""
import sys
import importlib
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from typing import List, Tuple

# The 10 agents we just restored
RESTORED_TARGETS = [
    ("MetaLearningAgent", "agentic_core.L1_cognition.thought_engine.MetaLearningAgent"),
    ("StrategicRecommendationAgent", "agentic_core.L1_cognition.thought_engine.StrategicRecommendationAgent"),
    ("BudgetAgent", "agentic_core.L1_cognition.thought_engine.BudgetAgent"),
    ("CodeDeduplicationAgent", "agentic_core.L5_safety.validators.CodeDeduplicationAgent"),
    ("PatternEnforcerAgent", "agentic_core.L5_safety.validators.PatternEnforcerAgent"),
    ("DeadlockDetectorAgent", "agentic_core.L5_safety.validators.DeadlockDetectorAgent"),
    ("IntegrityGateExecutorAgent", "agentic_core.L5_safety.validators.IntegrityGateExecutorAgent"),
    ("TypeMechanicAgent", "agentic_core.L5_safety.validators.TypeMechanicAgent"),
    ("DocumentationAgent", "agentic_core.L5_safety.validators.DocumentationAgent"),
    ("BenchmarkingAgent", "agentic_core.L6_observability.BenchmarkingAgent"),
]

def check_agent_import(class_name, module_path):
    print(f"Testing {class_name}...", end=" ")
    try:
        module = importlib.import_module(module_path)
        if not hasattr(module, class_name):
            print(f"❌ FAIL: Class not found in {module_path}")
            return False
        print("✅ OK")
        return True
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_restoration_integrity():
    print("\n=== Restored Agents Integrity Check ===\n")
    failures = []
    for cls, path in RESTORED_TARGETS:
        if not check_agent_import(cls, path):
            failures.append(cls)
    
    if failures:
        pytest.fail(f"Failed to import {len(failures)} restored agents: {failures}")

if __name__ == "__main__":
    try:
        test_restoration_integrity()
    except Exception as e:
        sys.exit(1)
