#!/usr/bin/env python3
"""Analyze directory structure for root-level files and organization issues."""

import ast
import os
from pathlib import Path
from typing import Dict, List, Optional
import json


def analyze_file_complexity(file_path: Path) -> Dict:
    """Analyze file complexity by parsing AST."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))

        functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
        imports = len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])

        return {
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'lines': len(content.splitlines()),
            'size': file_path.stat().st_size
        }
    except Exception as e:  # guardian: allow-broad-exception -- teardown/cleanup context -- swallow is conventional in resource-release paths
        return {
            'error': str(e),
            'lines': 0,
            'size': file_path.stat().st_size if file_path.exists() else 0
        }


def analyze_directory(root_dir: Path) -> Dict:
    """Analyze directory structure."""
    results = {
        'root_dir': str(root_dir),
        'root_level_files': [],
        'subdirs': {},
        'empty_subdirs': [],
        'low_signal_files': [],
        'high_signal_root_files': []
    }

    # Skip __pycache__
    if root_dir.name == '__pycache__':
        return results

    # Check root-level files
    for item in root_dir.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            complexity = analyze_file_complexity(item)
            results['root_level_files'].append({
                'file': str(item.relative_to(root_dir.parent)),
                'complexity': complexity
            })

            # Classify as high-signal if it has significant content
            if complexity.get('functions', 0) > 0 or complexity.get('classes', 0) > 0 or complexity.get('lines', 0) > 50:
                results['high_signal_root_files'].append(str(item.relative_to(root_dir.parent)))
            elif complexity.get('lines', 0) > 0:
                results['low_signal_files'].append(str(item.relative_to(root_dir.parent)))

    # Analyze subdirectories
    for item in root_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
            subdir_result = analyze_directory(item)
            results['subdirs'][item.name] = subdir_result

            if subdir_result['root_level_files'] or subdir_result['high_signal_root_files']:
                # Subdirectory has content
                pass
            else:
                # Check if empty or only __init__.py
                files = list(item.glob('*.py'))
                if len(files) == 0 or (len(files) == 1 and files[0].name == '__init__.py'):
                    results['empty_subdirs'].append(item.name)

    return results


def analyze_target_directory(target_path: str, output_path: Optional[str] = None):
    """Analyze a target directory and generate report."""
    root = Path(target_path)

    if not root.exists():
        print(f"Error: Directory {target_path} does not exist")
        return

    print(f"Analyzing directory: {target_path}")
    print("=" * 70)

    results = analyze_directory(root)

    # Print summary
    print(f"\nRoot-level files: {len(results['root_level_files'])}")
    print(f"High-signal root files: {len(results['high_signal_root_files'])}")
    print(f"Low-signal root files: {len(results['low_signal_files'])}")
    print(f"Subdirectories analyzed: {len(results['subdirs'])}")
    print(f"Empty or minimal subdirectories: {len(results['empty_subdirs'])}")

    # Print details
    if results.get('high_signal_root_files'):
        print("\nHIGH-SIGNAL ROOT FILES (should be in subdirectories):")
        for f in results['high_signal_root_files']:
            print(f"  - {f}")

    if results.get('low_signal_files'):
        print("\nLOW-SIGNAL ROOT FILES (should be in subdirectories):")
        for f in results['low_signal_files']:
            print(f"  - {f}")

    if results.get('empty_subdirs'):
        print("\nEMPTY OR MINIMAL SUBDIRECTORIES:")
        for d in results['empty_subdirs']:
            print(f"  - {d}")

    # Save to file if output path provided
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        print(f"\nDetailed report saved to: {output_path}")

    return results


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python directory_structure_analyzer.py <target_dir> [output_file]")
        sys.exit(1)

    target_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    analyze_target_directory(target_dir, output_file)
