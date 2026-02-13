#!/bin/bash
set -e

echo "🚀 Starting Two-Phase Autonomous Pipeline"
echo "================================================"

# Phase A: Sanitization Boot Sequence
echo ""
echo "📋 PHASE A: SANITIZATION BOOT SEQUENCE"
echo "================================================"

echo "  Step 0: Running Librarian (Deduplication & Manifest Generation)..."
python apps_rg/L0_routing/deduplicate_and_index.py
if [ $? -ne 0 ]; then
    echo "❌ Librarian failed. Aborting pipeline."
    exit 1
fi

echo "  Step 1: Running Architect (Structural Debt Fixes)..."
python fix_structural_debt_llm.py --root-dir .
if [ $? -ne 0 ]; then
    echo "❌ Architect failed. Aborting pipeline."
    exit 1
fi

echo "  Step 2: Running Surgeon (Syntax Error Fixes)..."
python fix_syntax_llm.py --root-dir .
if [ $? -ne 0 ]; then
    echo "❌ Surgeon failed. Aborting pipeline."
    exit 1
fi

# Phase B: Runtime Execution
echo ""
echo "📋 PHASE B: RUNTIME EXECUTION"
echo "================================================"

echo "  Step 3: Starting Orchestrator (Workflow Coordination)..."
python orchestrator.py

echo ""
echo "✅ Pipeline Complete"
echo "================================================"
