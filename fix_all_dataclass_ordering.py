#!/usr/bin/env python3
"""
Comprehensive script to fix dataclass field ordering issues across all schema files
Ensures fields without defaults come before fields with defaults for mypy compliance
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple, Optional

class DataclassFieldOrderFixer:
    def __init__(self, schemas_dir: str = "schemas"):
        self.schemas_dir = Path(schemas_dir)
        self.files_with_dataclasses = []
        
    def find_dataclass_files(self) -> List[Path]:
        """Find all Python files with dataclasses"""
        python_files = list(self.schemas_dir.rglob("*.py"))
        python_files = [f for f in python_files if f.name != "__init__.py"]
        
        dataclass_files = []
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if '@dataclass' in content:
                    dataclass_files.append(file_path)
                    
            except Exception:
                continue
                
        return dataclass_files
    
    def fix_dataclass_field_ordering(self, file_path: Path) -> bool:
        """Fix dataclass field ordering in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Track if we made any changes
            made_changes = False
            new_content = content
            
            # Process each class in the file
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a dataclass
                    has_dataclass_decorator = any(
                        (isinstance(decorator, ast.Name) and decorator.id == 'dataclass') or
                        (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == 'dataclass')
                        for decorator in node.decorator_list
                    )
                    
                    if has_dataclass_decorator:
                        # Find annotated assignments (dataclass fields)
                        fields = []
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign):
                                has_default = item.value is not None
                                fields.append((item, has_default))
                        
                        # Check if fields with defaults come before fields without defaults
                        seen_default = False
                        needs_fix = False
                        for field, has_default in fields:
                            if has_default:
                                seen_default = True
                            elif seen_default:
                                needs_fix = True
                                break
                        
                        if needs_fix:
                            # Fix the field ordering
                            new_content = self._fix_class_field_ordering(new_content, node.name, fields)
                            made_changes = True
            
            if made_changes:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed field ordering in {file_path}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def _fix_class_field_ordering(self, content: str, class_name: str, fields: List[Tuple[ast.AnnAssign, bool]]) -> str:
        """Fix field ordering for a specific class"""
        # Split content into lines
        lines = content.split('\n')
        
        # Find the class definition
        class_start = -1
        class_indent = 0
        
        for i, line in enumerate(lines):
            if f'class {class_name}' in line:
                class_start = i
                class_indent = len(line) - len(line.lstrip())
                break
        
        if class_start == -1:
            return content
        
        # Find the end of the class
        class_end = class_start + 1
        for i in range(class_start + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= class_indent and line.strip():
                class_end = i
                break
        else:
            class_end = len(lines)
        
        # Extract field lines and their properties
        field_lines = []
        current_field_start = class_start + 1
        
        for i in range(class_start + 1, class_end):
            line = lines[i]
            if ':' in line and not line.strip().startswith('#') and not line.strip().startswith('"""'):
                # This looks like a field definition
                field_lines.append((i, line, '=' in line))
        
        # Separate fields with and without defaults
        fields_no_default = [(i, line) for i, line, has_default in field_lines if not has_default]
        fields_with_default = [(i, line) for i, line, has_default in field_lines if has_default]
        
        # Reorder fields
        reordered_fields = fields_no_default + fields_with_default
        
        # Create new content
        new_lines = lines[:class_start + 1]
        
        # Add reordered fields
        for i, line in reordered_fields:
            new_lines.append(line)
        
        # Add the rest of the class content (non-field lines)
        field_indices = set(i for i, _, _ in field_lines)
        for i in range(class_start + 1, class_end):
            if i not in field_indices:
                new_lines.append(lines[i])
        
        # Add the rest of the file
        new_lines.extend(lines[class_end:])
        
        return '\n'.join(new_lines)
    
    def fix_all_files(self):
        """Fix dataclass field ordering in all files"""
        dataclass_files = self.find_dataclass_files()
        print(f"Found {len(dataclass_files)} files with dataclasses")
        
        fixed_count = 0
        for file_path in dataclass_files:
            if self.fix_dataclass_field_ordering(file_path):
                fixed_count += 1
        
        print(f"Fixed field ordering in {fixed_count} files")
        return fixed_count

def main():
    fixer = DataclassFieldOrderFixer()
    fixed_count = fixer.fix_all_files()
    
    if fixed_count > 0:
        print(f"\n✅ Successfully fixed dataclass field ordering in {fixed_count} files")
    else:
        print("\n✅ No dataclass field ordering issues found")

if __name__ == "__main__":
    main()
