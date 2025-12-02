#!/usr/bin/env python3
"""
Phase 2C-CACHE-GENERATION: Generate Semantic Cache for Agentic Core

Creates semantic cache entries for all 96 agentic_core skeleton files by
performing AST/code-analysis sweep and storing metadata in JSON format.
"""

import os
import json
import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SemanticCacheEntry:
    """Structure for semantic cache entry matching existing format"""
    file_hash: str
    file_path: str
    ast_tree: Dict[str, Any]
    signature_map: Dict[str, Any]
    docstring_map: Dict[str, Any]
    import_map: Dict[str, Any]
    responsibility_tags: List[str]
    quality_scores: Dict[str, float]
    error_branch_map: Dict[str, Any]


class SemanticCacheGenerator:
    """Generates semantic cache entries for agentic_core files"""
    
    def __init__(self, project_root: Path, cache_dir: Path):
        self.project_root = project_root
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_file_hash(self, file_path: str) -> str:
        """Generate SHA256 hash for file path"""
        return hashlib.sha256(file_path.encode('utf-8')).hexdigest()
    
    def extract_layer_info(self, file_path: str) -> List[str]:
        """Extract layer and responsibility information from file path"""
        path_parts = Path(file_path).parts
        tags = []
        
        if 'plan-layer' in path_parts:
            tags.append('L1_Cognitive_Planning')
        elif 'exec-layer' in path_parts:
            tags.append('L2_Execution')
        elif 'orc-layer' in path_parts:
            tags.append('L3_Orchestration')
        elif 'mem-layer' in path_parts:
            tags.append('L4_Memory')
        elif 'safe-layer' in path_parts:
            tags.append('L5_Safety')
            
        if 'plan-phase' in path_parts:
            tags.append('planning_phase')
        elif 'act-phase' in path_parts:
            tags.append('action_phase')
        elif 'coordinate-phase' in path_parts:
            tags.append('coordination_phase')
        elif 'retrieve-phase' in path_parts:
            tags.append('retrieval_phase')
        elif 'store-phase' in path_parts:
            tags.append('storage_phase')
        elif 'safety-phase' in path_parts:
            tags.append('safety_phase')
        elif 'validate-phase' in path_parts:
            tags.append('validation_phase')
            
        return tags
    
    def parse_ast_to_dict(self, node: ast.AST) -> Dict[str, Any]:
        """Convert AST node to dictionary format"""
        if node is None:
            return {}
            
        result = {
            'type': node.__class__.__name__,
            'lineno': getattr(node, 'lineno', None),
            'col_offset': getattr(node, 'col_offset', None),
            'fields': {}
        }
        
        for field_name, field_value in ast.iter_fields(node):
            if isinstance(field_value, list):
                result['fields'][field_name] = [
                    self.parse_ast_to_dict(item) if isinstance(item, ast.AST) else item
                    for item in field_value
                ]
            elif isinstance(field_value, ast.AST):
                result['fields'][field_name] = self.parse_ast_to_dict(field_value)
            else:
                result['fields'][field_value] = field_value
                
        return result
    
    def extract_signatures(self, tree: ast.AST) -> Dict[str, Any]:
        """Extract function and class signatures from AST"""
        signatures = {
            'functions': [],
            'classes': [],
            'variables': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'lineno': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'defaults': len(node.args.defaults) if node.args.defaults else 0,
                    'returns': ast.unparse(node.returns) if hasattr(ast, 'unparse') and node.returns else None,
                    'decorators': [ast.unparse(d) if hasattr(ast, 'unparse') else d.__class__.__name__ for d in node.decorator_list]
                }
                signatures['functions'].append(func_info)
                
            elif isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'lineno': node.lineno,
                    'bases': [ast.unparse(base) if hasattr(ast, 'unparse') else base.__class__.__name__ for base in node.bases],
                    'methods': [],
                    'decorators': [ast.unparse(d) if hasattr(ast, 'unparse') else d.__class__.__name__ for d in node.decorator_list]
                }
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            'name': item.name,
                            'args': [arg.arg for arg in item.args.args],
                            'lineno': item.lineno
                        }
                        class_info['methods'].append(method_info)
                        
                signatures['classes'].append(class_info)
                
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_info = {
                            'name': target.id,
                            'lineno': node.lineno,
                            'type': 'variable'
                        }
                        signatures['variables'].append(var_info)
        
        return signatures
    
    def extract_docstrings(self, tree: ast.AST) -> Dict[str, str]:
        """Extract docstrings from module, classes, and functions"""
        docstrings = {}
        
        # Module docstring
        if (tree.body and isinstance(tree.body[0], ast.Expr) and 
            isinstance(tree.body[0].value, ast.Constant) and 
            isinstance(tree.body[0].value.value, str)):
            docstrings['module'] = tree.body[0].value.value
        
        # Class and function docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if (node.body and isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant) and 
                    isinstance(node.body[0].value.value, str)):
                    key = f"{'class' if isinstance(node, ast.ClassDef) else 'function'}_{node.name}"
                    docstrings[key] = node.body[0].value.value
        
        return docstrings
    
    def extract_imports(self, tree: ast.AST) -> Dict[str, Any]:
        """Extract import information"""
        imports = {
            'imports': [],
            'from_imports': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_info = {
                        'module': alias.name,
                        'alias': alias.asname,
                        'lineno': node.lineno
                    }
                    imports['imports'].append(import_info)
                    
            elif isinstance(node, ast.ImportFrom):
                module_info = {
                    'module': node.module,
                    'level': node.level,
                    'imports': [],
                    'lineno': node.lineno
                }
                for alias in node.names:
                    import_info = {
                        'name': alias.name,
                        'alias': alias.asname
                    }
                    module_info['imports'].append(import_info)
                imports['from_imports'].append(module_info)
        
        return imports
    
    def extract_error_branches(self, tree: ast.AST) -> Dict[str, Any]:
        """Extract error handling and branch information"""
        branches = {
            'try_blocks': [],
            'except_blocks': [],
            'if_statements': [],
            'conditional_branches': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                try_info = {
                    'line': node.lineno,
                    'handlers': [{'type': ast.unparse(h.type) if h.type else 'Exception', 'lineno': h.lineno} for h in node.handlers]
                }
                branches['try_blocks'].append(try_info)
                
                for handler in node.handlers:
                    except_info = {
                        'line': handler.lineno,
                        'exception_type': ast.unparse(handler.type) if handler.type else 'Exception'
                    }
                    branches['except_blocks'].append(except_info)
                    
            elif isinstance(node, ast.If):
                if_info = {
                    'line': node.lineno,
                    'condition': 'conditional'  # Simplified for skeleton files
                }
                branches['if_statements'].append(if_info)
        
        return branches
    
    def calculate_quality_scores(self, tree: ast.AST, file_path: str) -> Dict[str, float]:
        """Calculate basic quality metrics"""
        scores = {
            'complexity': 0.0,
            'documentation': 0.0,
            'structure': 0.0,
            'imports': 0.0
        }
        
        # Count nodes for complexity
        node_count = len(list(ast.walk(tree)))
        scores['complexity'] = min(node_count / 50.0, 1.0)  # Normalize
        
        # Check for docstrings
        docstrings = self.extract_docstrings(tree)
        scores['documentation'] = min(len(docstrings) / 3.0, 1.0)  # Normalize
        
        # Check structure (functions, classes)
        signatures = self.extract_signatures(tree)
        total_entities = len(signatures['functions']) + len(signatures['classes'])
        scores['structure'] = min(total_entities / 5.0, 1.0)  # Normalize
        
        # Check imports
        imports = self.extract_imports(tree)
        total_imports = len(imports['imports']) + len(imports['from_imports'])
        scores['imports'] = min(total_imports / 10.0, 1.0)  # Normalize
        
        return scores
    
    def process_file(self, file_path: Path) -> Optional[SemanticCacheEntry]:
        """Process a single Python file and generate semantic cache entry"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Generate file hash
            file_hash = self.generate_file_hash(str(file_path))
            
            # Extract all required information
            ast_dict = self.parse_ast_to_dict(tree)
            signatures = self.extract_signatures(tree)
            docstrings = self.extract_docstrings(tree)
            imports = self.extract_imports(tree)
            error_branches = self.extract_error_branches(tree)
            quality_scores = self.calculate_quality_scores(tree, str(file_path))
            responsibility_tags = self.extract_layer_info(str(file_path))
            
            # Create cache entry
            entry = SemanticCacheEntry(
                file_hash=file_hash,
                file_path=str(file_path),
                ast_tree=ast_dict,
                signature_map=signatures,
                docstring_map=docstrings,
                import_map=imports,
                responsibility_tags=responsibility_tags,
                quality_scores=quality_scores,
                error_branch_map=error_branches
            )
            
            return entry
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def generate_cache(self) -> Dict[str, Any]:
        """Generate semantic cache for all agentic_core files"""
        agentic_core_dir = self.project_root / "agentic_core"
        
        if not agentic_core_dir.exists():
            raise FileNotFoundError(f"agentic_core directory not found: {agentic_core_dir}")
        
        # Find all Python files (excluding __init__.py)
        python_files = []
        for file_path in agentic_core_dir.rglob("*.py"):
            if file_path.name != "__init__.py":
                python_files.append(file_path)
        
        print(f"Found {len(python_files)} Python files to process")
        
        # Process each file
        cache_entries = {}
        successful_entries = 0
        
        for file_path in python_files:
            print(f"Processing: {file_path.relative_to(self.project_root)}")
            
            entry = self.process_file(file_path)
            if entry:
                cache_entries[entry.file_hash] = entry
                successful_entries += 1
                
                # Write cache file
                cache_file = self.cache_dir / f"agentic_core_{entry.file_hash}.meta.json"
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(entry), f, indent=2, default=str)
        
        print(f"Successfully generated {successful_entries} cache entries")
        
        return {
            'total_files': len(python_files),
            'successful_entries': successful_entries,
            'cache_directory': str(self.cache_dir),
            'entries': list(cache_entries.keys())
        }
    
    def validate_cache(self) -> bool:
        """Validate that cache meets all requirements"""
        cache_files = list(self.cache_dir.glob("agentic_core_*.meta.json"))
        
        print(f"Validation: Found {len(cache_files)} cache files")
        
        # Check exact count
        if len(cache_files) != 96:
            print(f"ERROR: Expected 96 entries, found {len(cache_files)}")
            return False
        
        # Validate each entry has required fields
        required_fields = ['file_hash', 'file_path', 'ast_tree', 'signature_map', 
                          'docstring_map', 'import_map', 'responsibility_tags', 
                          'quality_scores', 'error_branch_map']
        
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                
                missing_fields = [field for field in required_fields if field not in entry]
                if missing_fields:
                    print(f"ERROR: {cache_file.name} missing fields: {missing_fields}")
                    return False
                    
                # Validate agentic_core path
                if 'agentic_core' not in entry['file_path']:
                    print(f"ERROR: {cache_file.name} does not contain agentic_core path")
                    return False
                    
            except Exception as e:
                print(f"ERROR: Cannot validate {cache_file.name}: {e}")
                return False
        
        print("✓ All validation requirements met")
        return True


def main():
    """Main execution function"""
    project_root = Path(__file__).parent
    cache_dir = Path("C:\\Git\\.windsurf_cache\\semantic")
    
    print("=== Phase 2C-CACHE-GENERATION: Semantic Cache Generation ===")
    print(f"Project Root: {project_root}")
    print(f"Cache Directory: {cache_dir}")
    print()
    
    generator = SemanticCacheGenerator(project_root, cache_dir)
    
    # Generate cache
    result = generator.generate_cache()
    
    print("\n=== Generation Results ===")
    for key, value in result.items():
        if key != 'entries':
            print(f"{key}: {value}")
    
    # Validate cache
    print("\n=== Validation ===")
    is_valid = generator.validate_cache()
    
    if is_valid:
        print("\n✓ Phase 2C-CACHE-GENERATION completed successfully!")
        print("✓ Ready for Phase 2C reconstruction")
    else:
        print("\n✗ Phase 2C-CACHE-GENERATION failed validation")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
