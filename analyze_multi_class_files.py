"""
Analyze multi-class files to show dry run of one-class-per-file refactoring.

Identifies Python files containing multiple agent classes and shows what
the refactoring would look like.
"""
import ast
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Load agent registry
with open('agent_discovery_full.json', 'r') as f:
    registry = json.load(f)

# Group agents by file path
agents_by_file: Dict[str, List[Dict]] = defaultdict(list)
for agent in registry:
    path = agent['path'].replace('\\', '/')
    agents_by_file[path].append(agent)

# Find files with multiple agents
multi_agent_files = {
    path: agents 
    for path, agents in agents_by_file.items() 
    if len(agents) > 1
}

print("=" * 80)
print("DRY RUN: One Class = One Agent Refactoring")
print("=" * 80)
print(f"\nTotal files analyzed: {len(agents_by_file)}")
print(f"Files with multiple agents: {len(multi_agent_files)}")
print(f"Total agents: {len(registry)}")
print()

if not multi_agent_files:
    print("✅ All files already follow one-class-per-file pattern!")
else:
    print("📋 REFACTORING PLAN\n")
    
    total_new_files = 0
    total_classes_to_move = 0
    
    for file_path, agents in sorted(multi_agent_files.items(), key=lambda x: len(x[1]), reverse=True):
        num_agents = len(agents)
        total_classes_to_move += num_agents - 1  # Keep one in original file
        total_new_files += num_agents - 1
        
        print(f"\n{'='*80}")
        print(f"📁 {file_path}")
        print(f"   Contains {num_agents} agent classes")
        print(f"{'='*80}")
        
        # Sort by line number if available
        agents_sorted = sorted(agents, key=lambda x: x.get('line_number', 0))
        
        for i, agent in enumerate(agents_sorted, 1):
            class_name = agent['class_name']
            layer = agent.get('layer', 'unknown')
            has_healing = agent.get('has_healing', False)
            has_tests = agent.get('has_tests', False)
            
            # Determine if this should stay or be extracted
            action = "KEEP in current file" if i == 1 else "EXTRACT to new file"
            
            print(f"\n{i}. {class_name}")
            print(f"   Layer: {layer}")
            print(f"   Healing: {'✓' if has_healing else '✗'}")
            print(f"   Tests: {'✓' if has_tests else '✗'}")
            
            if i > 1:
                # Show what the new file would be
                file_dir = Path(file_path).parent
                new_file_name = f"{class_name}.py"
                new_file_path = file_dir / new_file_name
                
                print(f"   → ACTION: {action}")
                print(f"   → New file: {new_file_path}")
                
                # Check if file already exists
                if Path(new_file_path).exists():
                    print(f"   ⚠️  WARNING: File already exists!")
            else:
                print(f"   → ACTION: {action}")
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files requiring refactoring: {len(multi_agent_files)}")
    print(f"New files to create: {total_new_files}")
    print(f"Classes to extract: {total_classes_to_move}")
    print()
    
    # Show top offenders
    print("\n📊 TOP 10 FILES BY AGENT COUNT")
    print(f"{'='*80}")
    top_files = sorted(multi_agent_files.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for i, (path, agents) in enumerate(top_files, 1):
        print(f"{i:2}. {len(agents)} agents - {path}")
    
    # Estimate impact
    print(f"\n{'='*80}")
    print("ESTIMATED IMPACT")
    print(f"{'='*80}")
    print(f"• Files to modify: {len(multi_agent_files)}")
    print(f"• New files to create: {total_new_files}")
    print(f"• Import statements to update: ~{total_classes_to_move * 3} (estimated)")
    print(f"• Test files to create/update: ~{total_classes_to_move}")
    print()
    
    # Show benefits
    print("✅ BENEFITS")
    print("  • Single Responsibility: Each file has exactly one purpose")
    print("  • Easier Navigation: File name = Class name (PascalCase)")
    print("  • Clearer Dependencies: Import graph shows true relationships")
    print("  • Better Git History: Changes to one agent don't pollute another's history")
    print("  • Simpler Testing: test_AgentName.py maps 1:1 to AgentName.py")
    print("  • Reduced Merge Conflicts: Smaller, focused files")
    print()
    
    # Show risks
    print("⚠️  RISKS & CONSIDERATIONS")
    print("  • Breaking Changes: Imports need to be updated across codebase")
    print("  • Test Coverage: Need to ensure all tests still pass")
    print("  • Circular Dependencies: May expose hidden coupling")
    print("  • File Proliferation: More files to manage (but better organized)")
    print()
    
    # Recommended approach
    print("🎯 RECOMMENDED APPROACH")
    print("  1. Start with files containing 2-3 agents (easier to validate)")
    print("  2. Extract one class at a time, test after each extraction")
    print("  3. Add backward-compatible imports in original files")
    print("  4. Update all import statements across codebase")
    print("  5. Run full test suite after each file")
    print("  6. Regenerate agent registry and verify count unchanged")
    print("  7. Move to larger files (4+ agents) once process is validated")
    print()

print(f"{'='*80}")
print("END OF DRY RUN")
print(f"{'='*80}")
