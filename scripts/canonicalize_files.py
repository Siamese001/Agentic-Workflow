#!/usr/bin/env python3
"""Canonicalize path-encoded filenames and clean debug statements"""

import os
import re
import shutil
import hashlib
from pathlib import Path
from collections import defaultdict

def clean_debug_statements(file_path):
    """Remove print, pdb, and breakpoint statements from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_lines = content.count('\n')
        
        # Remove debug statements
        # Remove lines starting with print(
        content = re.sub(r'^\s*print\(.*\)\s*$', '', content, flags=re.MULTILINE)
        # Remove pdb. statements
        content = re.sub(r'^\s*pdb\.\w+.*$', '', content, flags=re.MULTILINE)
        # Remove breakpoint() calls
        content = re.sub(r'^\s*breakpoint\(\)\s*$', '', content, flags=re.MULTILINE)
        
        # Clean up multiple blank lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        cleaned_lines = content.count('\n')
        return original_lines - cleaned_lines  # Return number of lines removed
    except Exception as e:

        return 0

def get_file_hash(file_path):
    """Get SHA256 hash of file"""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def analyze_file_complexity(file_path):
    """Get simple complexity metrics"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Count non-empty, non-comment lines
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        file_size = os.path.getsize(file_path)
        
        return {
            'lines': code_lines,
            'size': file_size,
            'hash': get_file_hash(file_path)
        }
    except (OSError, IOError, UnicodeDecodeError):
        return {'lines': 0, 'size': 0, 'hash': ''}

def canonicalize_filename(encoded_name):
    """Convert path-encoded filename back to clean name"""
    # Remove common prefixes
    prefixes = [
        'agentic_core_', 'apps_shared_', 'apps_rg_', 'apps_lic_',
        'schemas_', 'config_', 'docs_', 'observability_', 'data_'
    ]
    
    clean_name = encoded_name
    for prefix in prefixes:
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]
            break
    
    return clean_name

def main():
    base_dir = Path('.')
    cleaned_files = 0
    deleted_duplicates = 0
    renamed_files = 0

    # Step 1: Find all path-encoded files
    encoded_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'archive_code', 'archives']]
        
        for file in files:
            if file.endswith('.py') or file.endswith('.json') or file.endswith('.md'):
                # Check if filename is path-encoded (contains multiple underscores)
                if '_' in file and file.count('_') >= 2:
                    full_path = Path(root) / file
                    encoded_files.append(full_path)

    # Step 2: Group files by their canonical target
    target_groups = defaultdict(list)
    
    for file_path in encoded_files:
        canonical_name = canonicalize_filename(file_path.name)
        target_path = file_path.parent / canonical_name
        
        # Check if this would conflict with an existing file
        if target_path.exists() and target_path != file_path:
            # This is a duplicate situation
            target_groups[str(target_path)].append(file_path)
        else:
            # No conflict, just needs rename
            target_groups[str(target_path)].append(file_path)
    
    # Step 3: Process duplicates

    for target_path, candidates in target_groups.items():
        if len(candidates) > 1:

            # Analyze each candidate
            analyses = []
            for candidate in candidates:
                analysis = analyze_file_complexity(candidate)
                analyses.append((candidate, analysis))

            # Select best candidate
            # Prefer: more lines, larger size, higher version number
            best = max(analyses, key=lambda x: (x[1]['lines'], x[1]['size']))
            
            # Delete others
            for candidate, analysis in analyses:
                if candidate != best[0]:

                    candidate.unlink()
                    deleted_duplicates += 1
    
    # Step 4: Clean debug statements from remaining files

    dirty_files = []
    
    # Find files that need cleaning (based on promoter output)
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'archive_code', 'archives']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                # Simple heuristic for dirty files
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'print(' in content or 'pdb.' in content or 'breakpoint()' in content:
                        dirty_files.append(file_path)

    for file_path in dirty_files:
        lines_removed = clean_debug_statements(file_path)
        if lines_removed > 0:

            cleaned_files += 1
    
    # Step 5: Rename files to canonical names

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'archive_code', 'archives']]
        
        for file in files:
            if file.endswith('.py') or file.endswith('.json') or file.endswith('.md'):
                file_path = Path(root) / file
                
                # Check if still path-encoded
                if '_' in file and file.count('_') >= 2:
                    canonical_name = canonicalize_filename(file)
                    target_path = file_path.parent / canonical_name
                    
                    if file_path != target_path and not target_path.exists():

                        file_path.rename(target_path)
                        renamed_files += 1
    
    # Summary

    # Count files in apps_rg
    apps_rg_count = len(list(Path('apps_rg').rglob('*.py'))) if Path('apps_rg').exists() else 0

if __name__ == "__main__":
    main()
