#!/usr/bin/env python3
"""
Comprehensive recursive analysis of reachout_engine_archive to design
a semantic caching model that fits this project's needs.
"""

import os
import json
from pathlib import Path
from collections import defaultdict, Counter
import ast

def analyze_file_content(file_path):
    """Analyze Python file content for semantic classification."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if not content.strip():
            return {'type': 'empty', 'classes': [], 'functions': [], 'imports': []}
        
        tree = ast.parse(content)
        
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        # Classify file type based on content
        file_type = 'unknown'
        
        # Core infrastructure detection
        if any(name in classes for name in ['BaseAgent', 'Config', 'CacheManager', 'ContextManager']):
            file_type = 'core_infrastructure'
        elif any(name in classes for name in ['Agent', 'Orchestrator', 'Workflow']):
            file_type = 'agent_system'
        elif any('prompt' in name.lower() for name in classes + functions):
            file_type = 'prompt_system'
        elif any('cache' in name.lower() or 'semantic' in name.lower() for name in classes + functions):
            file_type = 'caching_system'
        elif any('mcp' in name.lower() for name in classes + functions + imports):
            file_type = 'mcp_integration'
        elif any('test' in name.lower() or 'spec' in name.lower() for name in functions + classes):
            file_type = 'test'
        elif file_path.name.endswith('_v10_') or 'v10.' in file_path.name:
            file_type = 'versioned_core'
        elif len(classes) > 5:
            file_type = 'monolithic_core'
        elif len(functions) > 10:
            file_type = 'utility_library'
        
        return {
            'type': file_type,
            'classes': classes,
            'functions': functions,
            'imports': imports,
            'size': len(content),
            'lines': content.count('\n') + 1
        }
    
    except Exception as e:
        return {'type': 'parse_error', 'error': str(e), 'classes': [], 'functions': [], 'imports': [], 'size': 0, 'lines': 0}

def recursive_archive_analysis():
    """Perform comprehensive recursive analysis of reachout engine archive."""
    
    archive_root = Path("06_data/reachout_engine_archive")
    
    if not archive_root.exists():
        print(f"❌ Archive root not found: {archive_root}")
        return
    
    print("🔍 Starting comprehensive recursive analysis of reachout_engine_archive...")
    print("=" * 80)
    
    # Track statistics
    total_files = 0
    python_files = 0
    file_types = Counter()
    subfolder_stats = defaultdict(lambda: {'files': 0, 'python_files': 0, 'types': Counter()})
    
    # Content analysis
    class_patterns = Counter()
    import_patterns = Counter()
    size_distribution = []
    
    # Walk all subfolders recursively
    for root, dirs, files in os.walk(archive_root):
        relative_root = Path(root).relative_to(archive_root)
        print(f"\n📁 Analyzing: {relative_root}")
        
        for file in files:
            file_path = Path(root) / file
            total_files += 1
            
            # Track by subfolder
            subfolder = str(relative_root)
            subfolder_stats[subfolder]['files'] += 1
            
            # Analyze Python files
            if file.endswith('.py'):
                python_files += 1
                subfolder_stats[subfolder]['python_files'] += 1
                
                # Content analysis
                content_info = analyze_file_content(file_path)
                file_type = content_info.get('type', 'unknown')
                
                file_types[file_type] += 1
                subfolder_stats[subfolder]['types'][file_type] += 1
                
                # Track patterns
                class_patterns.update(content_info.get('classes', []))
                import_patterns.update(content_info.get('imports', []))
                size_distribution.append(content_info.get('size', 0))
                
                # Show interesting files
                if file_type in ['core_infrastructure', 'agent_system', 'monolithic_core', 'versioned_core']:
                    lines = content_info.get('lines', 0)
                    classes = content_info.get('classes', [])
                    print(f"  🎯 {file} ({file_type}, {lines} lines)")
                    if classes:
                        print(f"     Classes: {classes[:5]}...")
    
    # Print comprehensive analysis
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE ARCHIVE ANALYSIS RESULTS")
    print("=" * 80)
    
    print(f"\n📈 Overall Statistics:")
    print(f"  Total files: {total_files}")
    print(f"  Python files: {python_files}")
    print(f"  Python percentage: {python_files/total_files*100:.1f}%")
    
    print(f"\n🏗️ File Type Distribution:")
    for file_type, count in file_types.most_common():
        percentage = count / python_files * 100
        print(f"  {file_type:<20}: {count:>4} files ({percentage:>5.1f}%)")
    
    print(f"\n📁 Subfolder Breakdown:")
    for subfolder, stats in sorted(subfolder_stats.items()):
        if stats['python_files'] > 0:
            print(f"\n  {subfolder}:")
            print(f"    Files: {stats['files']} total, {stats['python_files']} Python")
            for file_type, count in stats['types'].most_common(3):
                if count > 0:
                    print(f"      {file_type}: {count}")
    
    print(f"\n🎯 Top Class Patterns:")
    for class_name, count in class_patterns.most_common(15):
        print(f"  {class_name:<25}: {count}")
    
    print(f"\n📦 Top Import Patterns:")
    for import_name, count in import_patterns.most_common(10):
        print(f"  {import_name:<30}: {count}")
    
    if size_distribution:
        avg_size = sum(size_distribution) / len(size_distribution)
        print(f"\n📏 File Size Statistics:")
        print(f"  Average size: {avg_size:.0f} characters")
        print(f"  Largest files: {sorted(size_distribution, reverse=True)[:3]}")
    
    # Design recommendations
    print(f"\n" + "=" * 80)
    print("🎯 SEMANTIC CACHING MODEL RECOMMENDATIONS")
    print("=" * 80)
    
    print(f"\n1. 🏗️ Multi-Layer Classification System:")
    print(f"   - Primary: Content-based classification (AST analysis)")
    print(f"   - Secondary: Filename/path patterns")
    print(f"   - Tertiary: File size and complexity metrics")
    
    print(f"\n2. 🎯 Content-Weighted Matching:")
    print(f"   - Core infrastructure classes: 0.8 weight")
    print(f"   - Agent system classes: 0.7 weight")
    print(f"   - Versioned core files: 0.6 weight")
    print(f"   - Path similarity: 0.2 weight (reduced from current 0.5)")
    
    print(f"\n3. 📁 Archive-Specific Handling:")
    for subfolder, stats in subfolder_stats.items():
        if stats['python_files'] > 10:
            dominant_type = stats['types'].most_common(1)[0][0] if stats['types'] else 'unknown'
            print(f"   - {subfolder}: Primarily {dominant_type} content")
    
    print(f"\n4. 🔧 Technical Improvements:")
    print(f"   - Fix Phase 0.5 engine metadata corruption")
    print(f"   - Implement AST-based content fingerprinting")
    print(f"   - Add class/function importance scoring")
    print(f"   - Create monolithic file decomposition logic")

if __name__ == "__main__":
    recursive_archive_analysis()
