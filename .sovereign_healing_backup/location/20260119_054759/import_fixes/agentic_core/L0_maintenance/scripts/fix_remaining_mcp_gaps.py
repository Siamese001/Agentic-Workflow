#!/usr/bin/env python3
"""
Fix remaining 36 MCP hardening gaps with targeted approach.
Handles edge cases like utility classes, stub files, etc.
"""
import json
import re
from pathlib import Path
from typing import List, Tuple
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

data = json.load(open('agent_discovery_full.json'))
remaining = [a for a in data if not a.get('mcp_hardened')]

print(f"Processing {len(remaining)} remaining agents...")
print()

fixed = 0
skipped = 0

# Agents that are utility classes or don't need MCP hardening
UTILITY_CLASSES = {
    'L1CognitionExerciserAgent', 'ActorCriticOrchestratorAgent', 'CoverageAgent',
    'GeneralExerciserAgent', 'MetaCoverageOptimizerAgent', 'PPOOrchestratorAgent',
    'QLearningOrchestratorAgent', 'RLOrchestratorAgent', 'ReinforceCriticOrchestratorAgent',
    'CheckpointManagerAgent', 'FileManagerAgent', 'L4StateExerciserAgent',
    'CompositeGuardrailAgent', 'L5SafetyExerciserAgent',
    'ContentCleanlinessValidatorAgent', 'MessageDiversityValidatorAgent',
    'PlaceholderDetectorAgent', 'ValidationAgent',
    'ConvergenceDetectorAgent', 'TestContentQualityAgent', 'TestProactiveAgent',
    'TestResumeLearningAgent', 'TestLeadQualityAgent', 'TestOutreachProactiveAgent',
    'TestValidationAgent', 'LLMPromptGovernorAgent', 'PromptRegistryAgent'
}

for agent in remaining:
    name = agent['class_name']
    path = Path(agent['path'])
    
    # Skip utility/test classes
    if name in UTILITY_CLASSES:
        print(f"⊘  SKIP: {name} - utility/test class")
        skipped += 1
        continue
    
    if not path.exists():
        print(f"⚠️  SKIP: {name} - file not found")
        skipped += 1
        continue
    
    try:
        content = path.read_text(encoding='utf-8')
        
        # Skip if already has MCP
        if 'MCPHardenedMixin' in content:
            print(f"⚠️  SKIP: {name} - already has MCPHardenedMixin")
            skipped += 1
            continue
        
        # Skip stub/re-export files
        if 'from agentic_core' in content and 'import' in content:
            if content.count(f"class {name}") == 0:
                print(f"⊘  SKIP: {name} - stub/re-export file")
                skipped += 1
                continue
        
        # Find class definition - more flexible pattern
        patterns = [
            rf'class\s+{re.escape(name)}\s*\((.*?)\)\s*:',  # With inheritance
            rf'class\s+{re.escape(name)}\s*:\s*\n',  # No inheritance
        ]
        
        match = None
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                break
        
        if not match:
            print(f"⚠️  SKIP: {name} - class pattern not found")
            skipped += 1
            continue
        
        # Get current inheritance
        if match.lastindex and match.group(1):
            current_inheritance = match.group(1).strip()
            new_inheritance = f"{current_inheritance}, MCPHardenedMixin" if current_inheritance else "MCPHardenedMixin"
            new_class_def = f"class {name}({new_inheritance}):"
        else:
            # No inheritance currently
            new_class_def = f"class {name}(MCPHardenedMixin):"
        
        # Replace class definition
        old_class_def = match.group(0).rstrip()
        content = content.replace(old_class_def, new_class_def)
        
        # Add import
        if 'from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin' not in content:
            lines = content.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    insert_idx = i + 1
            lines.insert(insert_idx, 'from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin')
            content = '\n'.join(lines)
        
        # Write back
        path.write_text(content, encoding='utf-8')
        print(f"✅ FIXED: {name}")
        fixed += 1
    
    except Exception as e:
        print(f"❌ ERROR: {name} - {str(e)}")

print()
print("=" * 80)
print(f"Fixed: {fixed}")
print(f"Skipped: {skipped}")
print(f"Total processed: {fixed + skipped}")
print("=" * 80)
print()
print("Next: Run metadata update and regenerate dashboard")
print("Command: python scripts/update_mcp_metadata.py && python agentic_core/L6_observability/dashboards/generate_dashboard.py")
