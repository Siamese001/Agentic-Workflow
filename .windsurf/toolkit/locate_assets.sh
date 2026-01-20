#!/bin/bash
echo "=== ASSET RECONNAISSANCE ==="

# 1. Find definition of REPORTS_DIR
echo "[SEARCH] REPORTS_DIR definition:"
grep -r "REPORTS_DIR =" agentic_core/ | head -n 5

# 2. Find missing Agent files
echo -e "\n[SEARCH] Moved Agents:"
find agentic_core -name "GospelSyncAgent.py"
find agentic_core -name "InterfaceBoundaryAgent.py"

# 3. Find SovereignBaseAgent class definition
echo -e "\n[SEARCH] SovereignBaseAgent class:"
grep -r "class SovereignBaseAgent" agentic_core/
