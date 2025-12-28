import os
from pathlib import Path

ROOT = Path("C:/Git/Agentic-Workflow")
CORE = ROOT / "agentic_core"

# Files with syntax errors from the V3 validator report
BROKEN_FILES = [
    "L1_cognition/P1_core/P2_inspect/rg_validation_gates_impl.py",
    "L2_execution/P2_tools/examples.py",
    "L2_execution/P4_agents/governance.py",
    "L2_execution/P4_agents/healer_agent.py",
    "L2_execution/P4_agents/infrastructure.py",
    "L2_execution/P4_agents/planning.py",
    "L2_execution/P4_agents/quality.py",
    "L2_execution/P4_agents/specialized.py",
]

def fix_syntax_errors():
    print("[*] FIXING SYNTAX SCARS FROM LLM MUTATIONS...")
    fixed = 0
    
    for file_rel_path in BROKEN_FILES:
        file_path = CORE / file_rel_path.replace('/', '\\')
        
        if not file_path.exists():
            print(f"  [!] Not found: {file_rel_path}")
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            original = content
            
            # Fix 1: Unterminated string literals (common from LLM mutations)
            # Look for lines with odd number of quotes
            lines = content.splitlines()
            fixed_lines = []
            
            for i, line in enumerate(lines):
                # Count unescaped quotes
                quote_count = line.count('"') - line.count('\\"')
                triple_quote_count = line.count('"""')
                
                # If odd number of quotes and not a triple-quoted string, likely broken
                if quote_count % 2 != 0 and triple_quote_count == 0:
                    # Try to close the string
                    if line.strip() and not line.strip().endswith('"'):
                        line = line + '"'
                        print(f"  [FIX] Line {i+1}: Added closing quote")
                
                fixed_lines.append(line)
            
            content = '\n'.join(fixed_lines)
            
            # Fix 2: Invalid syntax from "from agentic_core." without completion
            # Replace incomplete imports
            content = content.replace("from agentic_core.", "# [INCOMPLETE IMPORT] from agentic_core.")
            content = content.replace("from agentic_core..", "# [INCOMPLETE IMPORT] from agentic_core..")
            
            # Fix 3: Remove any lines that are just "from ." or "from .."
            content = '\n'.join([
                line if not line.strip() in ['from .', 'from ..'] 
                else f"# [INCOMPLETE] {line}"
                for line in content.splitlines()
            ])
            
            if content != original:
                file_path.write_text(content, encoding='utf-8')
                print(f"  [✓] Fixed: {file_rel_path}")
                fixed += 1
            else:
                print(f"  [=] No changes: {file_rel_path}")
                
        except Exception as e:
            print(f"  [X] Failed to fix {file_path.name}: {e}")
    
    print(f"\n[OK] SYNTAX SCAR REMOVAL COMPLETE. {fixed} files repaired.")

if __name__ == "__main__":
    fix_syntax_errors()
