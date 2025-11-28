#!/bin/bash
# Verification script for v8.0 upgrade

echo "=========================================="
echo "Resume Engine v8.0 Upgrade Verification"
echo "=========================================="
echo ""

# Check all files exist
echo "📁 Checking files..."
files=(
    "core_v8_0.py"
    "agent_swarm_v8_0.py"
    "master_config_v8_0.json"
    "agentic_capability_assessment_v8_0.clj"
    "main_v8_0.py"
    "run_batch_v8_0.py"
    "run_learning_v8_0.py"
)

all_present=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        echo "  ✅ $file ($size)"
    else
        echo "  ❌ $file - MISSING"
        all_present=false
    fi
done
echo ""

# Check version strings
echo "🔍 Checking version strings..."
for file in *.py; do
    if grep -q "8.0\|v8_0\|v8\.0" "$file" 2>/dev/null; then
        echo "  ✅ $file contains v8.0 references"
    else
        echo "  ⚠️  $file may need version check"
    fi
done
echo ""

# Check imports
echo "📦 Checking import chains..."
if grep -q "from core_v8_0 import" main_v8_0.py 2>/dev/null; then
    echo "  ✅ main_v8_0.py imports core_v8_0"
else
    echo "  ❌ main_v8_0.py import issue"
fi

if grep -q "from agent_swarm_v8_0 import" main_v8_0.py 2>/dev/null; then
    echo "  ✅ main_v8_0.py imports agent_swarm_v8_0"
else
    echo "  ❌ main_v8_0.py import issue"
fi

if grep -q "from core_v8_0 import" agent_swarm_v8_0.py 2>/dev/null; then
    echo "  ✅ agent_swarm_v8_0.py imports core_v8_0"
else
    echo "  ❌ agent_swarm_v8_0.py import issue"
fi
echo ""

# Check new v8.0 agents
echo "🤖 Checking new v8.0 agents..."
agents=(
    "ProvenanceRouterAgent"
    "CustomizedBulletDrafterAgent"
    "SyntheticBulletDrafterAgent"
    "DraftingConductorAgent"
    "QAConductorAgent"
)

for agent in "${agents[@]}"; do
    if grep -q "class $agent" agent_swarm_v8_0.py 2>/dev/null; then
        echo "  ✅ $agent defined"
    else
        echo "  ❌ $agent missing"
    fi
done
echo ""

# Check new prompts
echo "📝 Checking new v8.0 prompts in config..."
prompts=(
    "rag_thought_system_prompt"
    "bullet_customizer_system_prompt"
    "drafting_conductor_system_prompt"
    "qa_conductor_system_prompt"
)

for prompt in "${prompts[@]}"; do
    if grep -q "$prompt" master_config_v8_0.json 2>/dev/null; then
        echo "  ✅ $prompt in config"
    else
        echo "  ❌ $prompt missing from config"
    fi
done
echo ""

# Summary
echo "=========================================="
if [ "$all_present" = true ]; then
    echo "✅ All files present"
    echo "✅ Upgrade to v8.0 complete"
    echo ""
    echo "Next steps:"
    echo "  1. Populate prompt text in master_config_v8_0.json"
    echo "  2. Implement Neo4j GraphDatabaseClient"
    echo "  3. Run: python main_v8_0.py --debug"
else
    echo "❌ Some files missing - check above"
fi
echo "=========================================="
