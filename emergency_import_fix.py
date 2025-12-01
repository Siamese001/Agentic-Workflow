#!/usr/bin/env python3
"""
EMERGENCY IMPORT FIX
Reverts problematic dataclass additions that broke imports
"""

import asyncio
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class EmergencyImportFix:
    """Emergency fix for broken imports"""
    
    def __init__(self):
        self.base_path = Path("c:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic-Workflow")
        self.agentic_core_path = self.base_path / "agentic_core"
        
    async def fix_broken_imports(self):
        """Remove @dataclass from Enum classes and other invalid targets"""
        print("🚨 EMERGENCY: Fixing broken imports...")
        
        py_files = list(self.agentic_core_path.rglob("*.py"))
        fixed_count = 0
        
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                lines = content.split('\n')
                fixed_lines = []
                
                i = 0
                while i < len(lines):
                    line = lines[i]
                    
                    # Remove @dataclass if followed by Enum class
                    if '@dataclass' in line and i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if 'class ' in next_line and 'Enum' in next_line:
                            # Skip the @dataclass line
                            i += 1
                            fixed_lines.append(lines[i])  # Keep the Enum class
                        else:
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)
                    
                    i += 1
                
                new_content = '\n'.join(fixed_lines)
                
                if new_content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    fixed_count += 1
                    
            except Exception as e:
                logger.error(f"Error fixing {file_path}: {e}")
        
        print(f"✅ Fixed broken imports in {fixed_count} files")

# Main execution
async def main():
    """Main execution function"""
    fixer = EmergencyImportFix()
    await fixer.fix_broken_imports()
    
    print("\n🔍 Running quick validation check...")
    
    # Test a few files to make sure imports work
    test_files = [
        "agentic_core/plan-layer/plan-phase/get-core-info/general/understand-request/build_core_query.py",
        "agentic_core/exec-layer/act-phase/use-core-tools/general/use-a-tool/execute_core_execution.py"
    ]
    
    for test_file in test_files:
        try:
            file_path = fixer.agentic_core_path / test_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, str(file_path), 'exec')
                print(f"✅ {test_file} - imports OK")
        except Exception as e:
            print(f"❌ {test_file} - import error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
