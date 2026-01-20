#!/bin/bash
echo "=== BATCH 3 DEEP DIVE ==="

# 1. Hunt for STRUCTURE_BLUEPRINT
echo "[SEARCH] STRUCTURE_BLUEPRINT definition:"
# Search for exact assignment or close fuzzy matches
grep -r "STRUCTURE_BLUEPRINT =" agentic_core/ || grep -r "BLUEPRINT =" agentic_core/

# 2. Hunt for MCPHardenedMixin
echo -e "\n[SEARCH] MCPHardenedMixin class definition:"
grep -r "class MCPHardenedMixin" agentic_core/

# 3. MRO Conflict Analysis (Capture full trace)
echo -e "\n[TRACE] MRO Error (L6 Observability):"
pytest tests/test_l6_observability_agents.py -vv 2>&1 | grep -A 20 "TypeError"

# 4. Toxic Dependency Failure (Capture full trace)
echo -e "\n[TRACE] Toxic Dependency Exec Failure:"
pytest tests/test_toxic_dependency_auditor.py -vv 2>&1 | grep -A 20 "ImportError\|ModuleNotFoundError\|AttributeError"

# 5. Inspect PerformanceAnalystAgent inheritance (MRO suspect)
grep -r "class PerformanceAnalystAgent" agentic_core/L6_observability
