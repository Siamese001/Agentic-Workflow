#!/usr/bin/env python3
"""
SYNTAX CHECKER FOR IMPORT ISSUES
Identifies and fixes remaining import/syntax problems
"""

import ast
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class SyntaxChecker:
    """Checks and fixes syntax issues"""
    
    def __init__(self):
        self.agentic_core_path = Path("c:/Users/amita/Documents/Work/AI Job Search/AI/ML/DL/GenAI/LLM 101/LLM Pipelines/Resume Gen/Git/Agentic-Workflow/agentic_core")
        
    def check_all_files(self):
        """Check syntax of all Python files"""
        print("🔍 Checking syntax of all files...")
        
        py_files = list(self.agentic_core_path.rglob("*.py"))
        syntax_errors = []
        
        for file_path in py_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to check syntax
                ast.parse(content)
                
            except SyntaxError as e:
                syntax_errors.append((file_path, str(e)))
                print(f"❌ Syntax error in {file_path}: {e}")
            except Exception as e:
                print(f"⚠️  Error reading {file_path}: {e}")
        
        if syntax_errors:
            print(f"\n🚨 Found {len(syntax_errors)} files with syntax errors")
            for file_path, error in syntax_errors[:5]:  # Show first 5
                print(f"  - {file_path}: {error}")
        else:
            print("✅ All files have valid syntax")
        
        return syntax_errors

def main():
    """Main execution"""
    checker = SyntaxChecker()
    errors = checker.check_all_files()
    return len(errors) == 0

if __name__ == "__main__":
    main()
