#!/usr/bin/env python3
"""
FIX ABC PATTERNS IN ALL AGENTIC_CORE FILES
Removes @abstractmethod decorator since we provide concrete implementations
"""

import re
from pathlib import Path

def fix_abc_patterns():
    """Fix ABC pattern violations in all generated files"""
    base_path = Path("c:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic-Workflow")
    agentic_core_path = base_path / "agentic_core"
    
    # Get all Python files
    py_files = list(agentic_core_path.rglob("*.py"))
    print(f"Found {len(py_files)} files to fix")
    
    fixed_count = 0
    
    for file_path in py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove @abstractmethod decorator and the abstract method declaration
            # Pattern to match the abstract method followed by pass
            abstract_pattern = r'    @abstractmethod\n    async def execute\(self, context: OperationContext\) -> Dict\[str, Any\]:\n        """Execute the primary operation"""\n        pass\n'
            
            # Check if pattern exists
            if re.search(abstract_pattern, content):
                # Remove the abstract method declaration
                content = re.sub(abstract_pattern, '', content)
                
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Fixed ABC pattern in: {file_path.relative_to(agentic_core_path)}")
                fixed_count += 1
            else:
                print(f"⚠️  No ABC pattern found in: {file_path.relative_to(agentic_core_path)}")
        
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
    
    print(f"\n🎯 Fixed {fixed_count} files with ABC pattern violations")

if __name__ == "__main__":
    fix_abc_patterns()
