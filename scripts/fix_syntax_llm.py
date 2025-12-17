import os
import argparse
import google.generativeai as genai
import time
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.config.exclusions import EXCLUDED_FILES, EXCLUDED_DIRS

# --- CONFIGURATION ---
API_KEY = os.environ.get("GOOGLE_API_KEY")

# TIERED TRIAGE STRATEGY (FINAL COST-OPTIMIZED VERSION)
# 1. Tier 1: Fastest/Cheapest. Fixes simple errors.
# 2. Tier 2: Stable, Mid-Range Flash. Fixes complex indentation and strings.
REPAIR_MODELS = [
    'gemini-2.5-flash-lite',  # Tier 1: High speed, lowest cost
    'gemini-2.5-flash'        # Tier 2: Stable, mid-range reasoning
]

if not API_KEY:
    # print("⚠️ WARNING: GOOGLE_API_KEY not found. Syntax repair will fail.")  # [Security Fix]

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    pass
pass
# print(f"❌ Failed to configure Gemini API: {e}")  # [Security Fix]

EXCLUDED_DIRS = {'reports', 'drafts', 'tests', '.git', '__pycache__', 'venv', 'archives', 'logs', '.pytest_cache', 'htmlcov', 'coverage.xml', '.mypy_cache', '.tox', 'build', 'dist', '.eggs', '*.egg-info'}
EXCLUDED_FILES = {'canon_validator_backup.py', 'resume_engine_backup.py', 'fix_structural_debt_backup.py', '*.pyc', '*.pyo', '*.pyd', '.DS_Store', 'Thumbs.db'}
MANIFEST_FILE = 'active_manifest.json'

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
        # print(f"❌ CRITICAL ERROR: {MANIFEST_FILE} not found!")  # [Security Fix]
        # print(f"   Please run the Librarian first: python apps_rg/L0_maintenance/deduplicate_and_index.py")  # [Security Fix]
        sys.exit(1)

    try:
        # print(f"📂 Loading active file list from {MANIFEST_FILE}...")  # [Security Fix]
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

        # print(f"✅ Loaded {len(files)} validated files from manifest")  # [Security Fix]
        # print(f"   - Duplicates removed: {manifest.get('stats', {}).get('duplicates_removed', 0)}")  # [Security Fix]
        # print(f"   - Created: {manifest.get('created_at', 'Unknown')}")  # [Security Fix]

        return files

    except Exception as e:
pass
# print(f"❌ Failed to load manifest: {e}")  # [Security Fix]
        # print(f"   Please ensure the manifest is valid JSON")  # [Security Fix]
        sys.exit(1)

def get_llm_syntax_fix(code_content: str, file_path: str, error_msg: str, model_name: str) -> str:
    """
    Sends raw broken code to a specific Gemini model to fix syntax errors.
    """
    try:
        model = genai.GenerativeModel(model_name)

        prompt = f'''
        You are an expert Python Syntax Repair Agent.

        FILE: {file_path}
        ERROR: {error_msg}

        BROKEN CODE:
        ```python
        {code_content}
        ```

        TASK:
        1. Fix the specific SyntaxError or IndentationError described above.
        2. Do NOT refactor the logic. Only fix the syntax so it compiles.
        3. If the error is an unterminated string, use Python triple-quotes to fix it.
        4. Return ONLY the valid Python code. No markdown formatting, no explanations.
        '''

        response = model.generate_content(prompt)

        if not response.text:
            return None
        # Strip markdown fences if the model adds them
        cleaned_code = response.text.replace("```python", "").replace("```", "").strip()
        return cleaned_code
    except Exception as e:
pass
# print(f"    ❌ {model_name} failed to generate: {e}")  # [Security Fix]
        return None

def check_and_fix_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except UnicodeDecodeError:
pass
return False # Skip binary files

    # 1. Initial Check: Is the code already valid?
    try:
        compile(source, file_path, 'exec')
        return False
    except SyntaxError as e:
pass
error_msg = f"{e.msg} at line {e.lineno}"
        # print(f"🔥 Syntax Error in {file_path}: {error_msg}")  # [Security Fix]
    except Exception as e:
pass
error_msg = str(e)
        # print(f"🔥 Unknown Error in {file_path}: {error_msg}")  # [Security Fix]

    # 2. Tiered Repair Loop
    for model_name in REPAIR_MODELS:
        # print(f"  🤖 Engaging {model_name}...")  # [Security Fix]

        fixed_code = get_llm_syntax_fix(source, file_path, error_msg, model_name)

        if fixed_code:
            # 3. Verify the fix immediately
            try:
                compile(fixed_code, file_path, 'exec')

                # If we get here, the code is valid! Save it.
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
                # print(f"  ✅ FIXED by {model_name}")  # [Security Fix]
                return True

            except SyntaxError as verify_error:
pass
# print(f"    ⚠️ {model_name} proposed code was still broken: {verify_error.msg}")  # [Security Fix]
                # Loop continues to the next model in the list
                continue

    # If the loop finishes, all available models failed.
    # print(f"  ❌ All models failed to repair {file_path}. Requires manual fix.")  # [Security Fix]
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root-dir', type=str, default='/app')
    args = parser.parse_args()

    # print(f"🚀 Starting Cost-Optimized Syntax Repair (Models: {REPAIR_MODELS})...")  # [Security Fix]
    count = 0

    # Get target files from manifest or fallback to os.walk
    target_files = get_target_files(args.root_dir)
    # print(f"📊 Processing {len(target_files)} files...")  # [Security Fix]

    for file_path in target_files:
        if check_and_fix_file(file_path):
            count += 1

    # print(f"🏁 Syntax Repair Cycle Complete. Files rescued: {count}")  # [Security Fix]

if __name__ == '__main__':
    main()

