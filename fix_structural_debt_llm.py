import os
import ast
import time
import argparse
import google.generativeai as genai
import json
from typing import Optional
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.config.exclusions import EXCLUDED_FILES, EXCLUDED_DIRS

# --- CONFIGURATION ---
# Ensure GOOGLE_API_KEY is in your docker-compose environment variables
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    print("⚠️ WARNING: GOOGLE_API_KEY not found. Autonomous refactoring will be limited.")
    logging.warning("GOOGLE_API_KEY not found. Autonomous refactoring will be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Gemini
try:
    genai.configure(api_key=API_KEY)
    # Using Gemini 2.5 Flash Lite for refactoring
    MODEL = genai.GenerativeModel('models/gemini-2.5-flash-lite')
    logging.info("Gemini API configured successfully.")
except Exception as e:
    logging.error(f"❌ Failed to configure Gemini API: {e}")
    MODEL = None

EXCLUDED_FILES = [
    'fix_structural_debt.py',
    'fix_security_and_hygiene.py',
    'canon_validator_v2_agentic.py',
    'action_registry.py'
]
EXCLUDED_DIRS = ['reports', 'drafts', 'tests', '.git', '__pycache__', 'venv', 'archives']
MANIFEST_FILE = 'active_manifest.json'

def get_target_files(root_dir):
    """
    Returns files from the manifest if it exists, otherwise falls back to os.walk
    Uses a hybrid approach: smart manifest + safety net for critical directories
    """
    active_files = set()
    
    # 1. Load the smart manifest (The 72 files)
    manifest_path = os.path.join(root_dir, MANIFEST_FILE)
    if os.path.exists(manifest_path):
        print(f"📂 Loading dependency graph from {MANIFEST_FILE}...")
        with open(manifest_path, 'r') as f:
            manifest_files = json.load(f)
            # Normalize paths
            active_files.update([os.path.normpath(os.path.join(root_dir, f)) for f in manifest_files])
    
    # 2. SAFETY NET: Force-include critical directories (The "Lost Islands")
    #    This ensures anything in critical folders is fixed, even if the graph missed it.
    CRITICAL_DIRS = ['apps_rg', 'apps_shared', '01_agentic_core', '02_apps', '03_runtime', '04_tools', '08_scripts']
    
    print(f"🛡️  Scanning safety net directories: {CRITICAL_DIRS}...")
    for safety_dir in CRITICAL_DIRS:
        full_safety_path = os.path.join(root_dir, safety_dir)
        if os.path.exists(full_safety_path):
            for r, d, f in os.walk(full_safety_path):
                # Skip hidden directories and common excludes
                d[:] = [dir_name for dir_name in d if not dir_name.startswith('.') and dir_name not in ['__pycache__', 'venv', 'node_modules']]
                for file in f:
                    if file.endswith('.py') and not any(x in file for x in ['backup', '_old', '.pyc', '.pyo']):
                        active_files.add(os.path.join(r, file))
    
    # 3. Also include root-level Python files
    for file in os.listdir(root_dir):
        if (file.endswith('.py') and 
            not file.startswith('.') and 
            not any(x in file for x in ['backup', '_old', '.pyc', '.pyo']) and
            file not in EXCLUDED_FILES):
            active_files.add(os.path.join(root_dir, file))
    
    final_list = sorted(list(active_files))
    print(f"📊 Final processing list: {len(final_list)} files (Graph + Safety Net)")
    return final_list

def is_excluded(file_path: str) -> bool:
    """Checks if a file is in the exclusion list."""
    return os.path.basename(file_path) in EXCLUDED_FILES

def get_llm_refactor(code_content: str, file_path: str, violation_type: str) -> Optional[str]:
    """
    Sends the code to Gemini Flash to request a specific refactoring.

    Args:
        code_content: The source code to refactor.
        file_path: The path of the file being refactored.
        violation_type: The type of code violation to fix.

    Returns:
        The refactored code as a string, or None if refactoring fails.
    """
    if not MODEL:
        logging.warning(f"LLM model not available. Cannot refactor {file_path}.")
        return None

    prompt = f"""
    You are an expert Python Refactoring Agent.

    FILE: {file_path}
    VIOLATION: {violation_type}

    CODE:
    
    {code_content}
    

    TASK:
    1. Refactor the code to fix the '{violation_type}'.
    2. If the violation is "Large Function", break it into smaller, modular sub-functions.
    3. If the violation is "Bare Except Block (Security Risk)", replace 'except:' with 'except Exception as e:' and add logging.
    4. Maintain all original logic and functionality.
    5. Return ONLY the valid Python code. No markdown, no explanations.
    """

    try:
        logging.info(f"🤖 Engaging Gemini Flash for '{violation_type}' in {file_path}...")
        response = MODEL.generate_content(prompt)
        # Clean up potential markdown formatting or extra whitespace
        cleaned_code = response.text.strip()
        # Attempt to remove common markdown code block wrappers
        if cleaned_code.startswith(""):
            cleaned_code = cleaned_code[len(""):].strip()
        if cleaned_code.endswith(""):
            cleaned_code = cleaned_code[:-len("")].strip()

        # Basic sanity check: ensure it parses
        ast.parse(cleaned_code)
        logging.info(f"✅ LLM refactoring successful for {file_path}.")
        return cleaned_code
    except Exception as e:
        logging.error(f"  ❌ LLM Refactoring failed for {file_path}: {e}")
        return None

def analyze_and_fix_large_functions(file_path: str, original_code: str) -> tuple[str, bool]:
    """
    Analyzes a file for large functions and attempts to refactor them using LLM.

    Args:
        file_path: The path of the file to analyze.
        original_code: The original content of the file.

    Returns:
        A tuple containing the potentially modified code and a boolean indicating if modifications were made.
    """
    modified_code = original_code
    modified = False
    try:
        tree = ast.parse(modified_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Rough line count as a proxy for complexity/size
                # Use end_lineno if available, otherwise fall back to lineno
                end_line = getattr(node, 'end_lineno', node.lineno)
                lines = end_line - node.lineno
                logging.info(f"  🔍 Found function '{node.name}' in {file_path}: {lines} lines")
                if lines > 40:  # Threshold for "Large Function"
                    refactored = get_llm_refactor(modified_code, file_path, "Large Function")
                    if refactored:
                        modified_code = refactored
                        modified = True
                        # Apply one major fix per cycle to avoid thrashing and complex diffs
                        return modified_code, modified
    except SyntaxError as e:
        logging.error(f"  ⚠️ AST Parse Error checking large functions in {file_path}: {e}")
    except Exception as e:
        logging.error(f"  ⚠️ Unexpected error checking large functions in {file_path}: {e}")
    return modified_code, modified

def analyze_and_fix_bare_excepts(file_path: str, code_content: str) -> tuple[str, bool]:
    """
    Analyzes a file for bare except blocks and attempts to refactor them using LLM.

    Args:
        file_path: The path of the file to analyze.
        code_content: The content of the file to analyze.

    Returns:
        A tuple containing the potentially modified code and a boolean indicating if modifications were made.
    """
    modified_code = code_content
    modified = False

    # A more robust check for bare excepts, still relies on string matching for simplicity here
    # A proper AST traversal would be more accurate but adds complexity.
    # This simple check is sufficient for the LLM prompt.
    if "except:" in code_content:
        refactored = get_llm_refactor(code_content, file_path, "Bare Except Block (Security Risk)")
        if refactored:
            modified_code = refactored
            modified = True
    return modified_code, modified


def analyze_and_fix(file_path: str) -> bool:
    """
    Analyzes a Python file for structural debt violations and applies LLM-based fixes.

    Args:
        file_path: The path to the Python file.

    Returns:
        True if the file was modified, False otherwise.
    """
    if is_excluded(file_path):
        logging.info(f"Skipping excluded file: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
    except Exception as e:
        logging.error(f"❌ Error reading file {file_path}: {e}")
        return False

    modified = False
    new_code = original_code

    # --- CHECK 1: Large Functions ---
    # Analyze for large functions first, as they might introduce other issues or complexities.
    new_code_after_large_func, modified_large_func = analyze_and_fix_large_functions(file_path, new_code)
    if modified_large_func:
        modified = True
        new_code = new_code_after_large_func
        # Re-parse and re-evaluate for other violations in the newly refactored code
        try:
            ast.parse(new_code) # Basic check after first refactor
        except SyntaxError as e:
            logging.error(f"  ⚠️ Syntax error after large function refactor in {file_path}: {e}. Reverting to original.")
            new_code = original_code # Revert if major issue
            modified = False # Reset modification flag if reverted

    # --- CHECK 2: Bare Excepts ---
    # Analyze for bare excepts on the (potentially) updated code
    # This check should run on the code *after* any large function refactoring.
    new_code_after_bare_except, modified_bare_except = analyze_and_fix_bare_excepts(file_path, new_code)
    if modified_bare_except:
        new_code = new_code_after_bare_except
        modified = True

    if modified and new_code != original_code:
        # write back
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
            logging.info(f"  ✅ Applied LLM Fix to {file_path}")
            return True
        except Exception as e:
            logging.error(f"❌ Error writing modified code to {file_path}: {e}")
            return False

    return False

def get_target_files(root_dir: str) -> list[str]:
    """
    Returns files ONLY from the active_manifest.json.
    This ensures we only process files that have been deduplicated and validated.
    
    Args:
        root_dir: Root directory to search
        
    Returns:
        List of absolute file paths to process
    """
    manifest_path = os.path.join(root_dir, MANIFEST_FILE)
    
    if not os.path.exists(manifest_path):
        print(f"❌ CRITICAL ERROR: {MANIFEST_FILE} not found!")
        print(f"   Please run the Librarian first: python apps_rg/L0_maintenance/deduplicate_and_index.py")
        sys.exit(1)
    
    try:
        print(f"📂 Loading active file list from {MANIFEST_FILE}...")
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Extract file paths from manifest
        files = []
        for file_info in manifest.get("files", []):
            # Use absolute_path if available, otherwise construct from relative path
            if "absolute_path" in file_info:
                files.append(file_info["absolute_path"])
            else:
                files.append(os.path.join(root_dir, file_info["path"]))
        
        print(f"✅ Loaded {len(files)} validated files from manifest")
        print(f"   - Duplicates removed: {manifest.get('stats', {}).get('duplicates_removed', 0)}")
        print(f"   - Created: {manifest.get('created_at', 'Unknown')}")
        
        return files
        
    except Exception as e:
        print(f"❌ Failed to load manifest: {e}")
        print(f"   Please ensure the manifest is valid JSON")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root-dir', type=str, default='/app')
    args = parser.parse_args()

    print("🚀 Starting LLM-Powered Structural Debt Fixer...")
    
    count = 0
    
    # Get target files from manifest or fallback to os.walk
    target_files = get_target_files(args.root_dir)
    print(f"📊 Processing {len(target_files)} files...")
    
    for file_path in target_files:
        if analyze_and_fix(file_path):
            count += 1
            # Rate limit protection (simple)
            time.sleep(1) 
    print(f"🏁 LLM Refactoring Cycle Complete. Files modified: {count}")

if __name__ == '__main__':
    main()