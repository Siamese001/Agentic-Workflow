import json
import os
import shutil
import logging
import argparse
import hashlib
import ast
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def aggressive_cleanup():
    """More aggressive cleanup targeting additional patterns"""
    purged_count = 0

    # Remove all test_repo directories
    for item in os.listdir('.'):
        if os.path.isdir(item) and item.startswith("test_repo"):
            try:
                shutil.rmtree(item)
                logger.info(f"🗑️ PURGED DIRECTORY: {item}")
                purged_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to delete directory {item}: {e}")

    # Remove temporary and cache files
    temp_patterns = ["*.tmp", "*.temp", "*.bak", "*~", ".DS_Store", "Thumbs.db"]
    for pattern in temp_patterns:
        import glob
        for file in glob.glob(pattern, recursive=True):
            try:
                os.remove(file)
                logger.info(f"🗑️ Purged temp file: {file}")
                purged_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to delete {file}: {e}")

    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                logger.info(f"🗑️ PURGED DIRECTORY: {pycache_path}")
                purged_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to delete directory {pycache_path}: {e}")

    return purged_count

def organize_structure():
    """Reorganize files into proper engine directories"""
    logger.info("📁 Starting folder reorganization...")

    # Create main directories if they don't exist
    engines_dir = "/app/engines"
    subdirs = ["resume_engine", "outreach_engine", "canon_validator"]

    for subdir in subdirs:
        path = os.path.join(engines_dir, subdir)
        os.makedirs(path, exist_ok=True)
        logger.info(f"📁 Created directory: {path}")

    # Move relevant files to appropriate directories
    file_mappings = {
        "resume": "resume_engine",
        "outreach": "outreach_engine",
        "canon": "canon_validator",
        "validator": "canon_validator"
    }

    moved_count = 0
    for root, dirs, files in os.walk('/app'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_lower = file.lower()

                # Determine target directory based on filename
                target_dir = None
                for keyword, directory in file_mappings.items():
                    if keyword in file_lower:
                        target_dir = directory
                        break

                if target_dir and not file.startswith('__'):
                    target_path = os.path.join(engines_dir, target_dir, file)
                    try:
                        # Avoid overwriting existing files
                        if not os.path.exists(target_path):
                            shutil.move(file_path, target_path)
                            logger.info(f"📁 Moved {file} to {target_dir}/")
                            moved_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to move {file}: {e}")

    logger.info(f"\n✨ Reorganization complete. Moved {moved_count} files.")
    return moved_count

def get_file_hash(filepath):
    """Calculate hash of file content for deduplication"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return None

def extract_functions(filepath):
    """Extract function definitions from a Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function source
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                lines = content.split('\n')[start_line:end_line]
                func_code = '\n'.join(lines)
                functions.append({
                    'name': node.name,
                    'code': func_code,
                    'hash': hashlib.md5(func_code.encode()).hexdigest()
                })
        
        return functions
    except Exception as e:
        logger.error(f"❌ Failed to parse {filepath}: {e}")
        return []

def merge_validator_logic(silos, exclude_dirs, merge_to):
    """Merge duplicate validator logic across silos into a single file"""
    logger.info("🔀 Starting validator logic merge...")
    
    # Find all Python files in specified silos
    all_files = []
    for silo in silos:
        silo_path = f"/app/{silo}"
        if os.path.exists(silo_path):
            for root, dirs, files in os.walk(silo_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        filepath = os.path.join(root, file)
                        all_files.append(filepath)
    
    # Extract and deduplicate functions
    function_map = defaultdict(list)
    function_sources = {}
    
    for filepath in all_files:
        functions = extract_functions(filepath)
        for func in functions:
            if func['name'] not in ['validate', 'check', 'verify', 'is_valid']:
                continue  # Focus on validation functions
            
            function_map[func['name']].append({
                'hash': func['hash'],
                'code': func['code'],
                'file': filepath
            })
    
    # Create merged file
    merged_content = '''#!/usr/bin/env python3
"""
Canon Validator v2.0 - Merged and Consolidated
All validator logic consolidated from multiple silos.
"""

import ast
import hashlib
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace")

# ==============================================================================
# CONFIGURATION: EXCLUSION ZONES
# ==============================================================================
EXCLUDED_DIRS = {
    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache',
    'node_modules', '.idea', '.vscode', 'build', 'dist', 'eggs',
    'archives', 'data',
}

EXCLUDED_FILES = {
    'canon_validator.py',
    'canon_validator_backup.py',
    'canon_validator_v2_agentic.py',
    'auto_canon.py',
    '.DS_Store'
}

def is_excluded(path: str) -> bool:
    """Check if a path should be excluded from validation."""
    path_parts = path.split(os.sep)
    
    # Check directory exclusions
    for part in path_parts:
        if part in EXCLUDED_DIRS:
            return True
    
    # Check file exclusions
    filename = os.path.basename(path)
    if filename in EXCLUDED_FILES:
        return True
    
    return False

'''
    
    # Add unique functions to merged file
    added_functions = set()
    for func_name, func_list in function_map.items():
        if func_list:
            # Use the first occurrence of each unique function
            func_data = func_list[0]
            if func_data['hash'] not in added_functions:
                merged_content += f"\n# Function: {func_name} (from {func_data['file']})\n"
                merged_content += func_data['code'] + "\n\n"
                added_functions.add(func_data['hash'])
    
    # Write merged file
    os.makedirs(os.path.dirname(merge_to), exist_ok=True)
    with open(merge_to, 'w', encoding='utf-8') as f:
        f.write(merged_content)
    
    logger.info(f"✅ Merged validator logic to {merge_to}")
    logger.info(f"📊 Processed {len(all_files)} files")
    logger.info(f"🔀 Merged {len(added_functions)} unique validation functions")
    
    return len(added_functions)

def purge_everything(aggressive=False, organize=False, merge_logic=False, 
                    merge_to=None, silos=None, exclude=None):
    purged_count = 0

    # 1. Target runaway directories identified in your logs
    for item in os.listdir('.'):
        if os.path.isdir(item) and item.startswith("test_repo_1765"):
            try:
                shutil.rmtree(item)
                logger.info(f"🗑️ PURGED DIRECTORY: {item}")
                purged_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to delete directory {item}: {e}")

    # 2. Target individual "clean" file clones and reports
    for root, dirs, files in os.walk('.'):
        for file in files:
            file_path = os.path.join(root, file)
            if "_clean.py" in file or file == "test_report.html":
                try:
                    os.remove(file_path)
                    logger.info(f"🗑️ Purged File: {file_path}")
                    purged_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to delete {file_path}: {e}")

    # 3. Aggressive cleanup if requested
    if aggressive:
        purged_count += aggressive_cleanup()

    logger.info(f"\n✨ Aggressive Cleanup Complete. {purged_count} items removed.")

    # 4. Organize structure if requested
    if organize:
        organize_structure()

    # 5. Merge validator logic if requested
    if merge_logic and merge_to and silos:
        merged_count = merge_validator_logic(silos, exclude or [], merge_to)
        logger.info(f"\n🔀 Merge Complete. {merged_count} functions merged.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean duplicates and organize code structure")
    parser.add_argument("--aggressive", action="store_true", help="Perform aggressive cleanup")
    parser.add_argument("--organize", action="store_true", help="Organize files into engine directories")
    parser.add_argument("--merge-logic", action="store_true", help="Merge duplicate validator logic")
    parser.add_argument("--merge-to", type=str, help="Target file for merged validator logic")
    parser.add_argument("--silos", type=str, help="Comma-separated list of silos to process")
    parser.add_argument("--exclude", type=str, help="Comma-separated list of directories to exclude")
    
    args = parser.parse_args()
    
    # Parse silos and exclude lists
    silos = args.silos.split(',') if args.silos else []
    exclude = args.exclude.split(',') if args.exclude else []
    
    purge_everything(
        aggressive=args.aggressive,
        organize=args.organize,
        merge_logic=args.merge_logic,
        merge_to=args.merge_to,
        silos=silos,
        exclude=exclude
    )
