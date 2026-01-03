#!/usr/bin/env python3
"""Phase 4 Part 2 Batch 2: Scale to 30-50 agents (L2/L3 priority)."""

import re
from pathlib import Path

# Batch 2: Priority L2/L3 agents from invocation gap alerts
agents_to_fix = [
    # L2 ToolRegistry (remaining from initial list)
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\CodeDeduplicationAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\IntegrityGateExecutorAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\SovereignActionPlaneAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\SovereignRedisOrchestratorAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\ManifestManagerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\McpConnectionManagerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\FirecrackerManagerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\FallbackManagerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\DynamicModelRouterAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\ProactiveResourceManagerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\StructuralEngineerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\SystemArchitectAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\ToolsmithAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L2_execution\ToolRegistry\CodeJanitorAgent.py',
    # L3 Orchestration (high priority)
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\AgentRegistryValidatorAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\DAGManagerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\HardenedWorkflowOrchestratorAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\NervousSystemAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\OrchestrationBaseAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\P1CoreSemanticTerritoryMapperAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\P1CoreTerritoryHealerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\SemanticGatekeeperAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\SemanticTerritoryMapperAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\SubatomicHopAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\TerritoryHealerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\WorkflowOrchestrationAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\WorkflowStateManagerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\ExecutionPlannerAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\ContextBridgeAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L3_orchestration\workflow_engines\DependencyResolverAgent.py',
    # L0 Maintenance (lower priority but included for coverage)
    r'C:\Git\Agentic-Workflow\agentic_core\L0_maintenance\scripts\BootstrapAgent.py',
    r'C:\Git\Agentic-Workflow\agentic_core\L0_maintenance\scripts\MaintenanceBaseAgent.py',
]

fixed_count = 0
skipped_count = 0

for agent_path in agents_to_fix:
    path = Path(agent_path)
    if not path.exists():
        skipped_count += 1
        continue
    
    content = path.read_text(encoding='utf-8')
    
    # Check if already has super().heal_repository()
    if 'super().heal_repository()' in content:
        skipped_count += 1
        continue
    
    # Check if has heal_repository method
    if 'def heal_repository(self' not in content:
        skipped_count += 1
        continue
    
    # Find heal_repository method and insert super() call after docstring
    lines = content.split('\n')
    new_lines = []
    i = 0
    inserted = False
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check if this is the heal_repository method definition
        if 'def heal_repository(self' in line and not inserted:
            # Add the next line (decorator or docstring start)
            i += 1
            if i < len(lines):
                new_lines.append(lines[i])
            
            # Find and skip the docstring
            if '"""' in lines[i]:
                i += 1
                # Find closing """
                while i < len(lines) and '"""' not in lines[i]:
                    new_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    new_lines.append(lines[i])  # closing """
                    i += 1
                
                # Now insert super() call before the next statement
                # Skip empty lines
                while i < len(lines) and lines[i].strip() == '':
                    new_lines.append(lines[i])
                    i += 1
                
                # Insert super().heal_repository() call
                if i < len(lines):
                    # Get indentation from next line
                    next_line = lines[i]
                    indent = len(next_line) - len(next_line.lstrip())
                    indent_str = ' ' * indent
                    
                    new_lines.append(f'{indent_str}# CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)')
                    new_lines.append(f'{indent_str}super().heal_repository()')
                    new_lines.append('')
                    inserted = True
                
                continue
        
        i += 1
    
    new_content = '\n'.join(new_lines)
    
    if new_content != content:
        path.write_text(new_content, encoding='utf-8')
        fixed_count += 1

print(f"✓ Batch 2 complete: {fixed_count} agents fixed, {skipped_count} skipped")
print(f"✓ Total fixed so far: {6 + fixed_count} agents")
