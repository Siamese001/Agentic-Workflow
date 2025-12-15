import os
import argparse
import google.generativeai as genai
import time
import json

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
    print("⚠️ WARNING: GOOGLE_API_KEY not found. Syntax repair will fail.")

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"❌ Failed to configure Gemini API: {e}")

EXCLUDED_DIRS = {'reports', 'drafts', 'tests', '.git', '__pycache__', 'venv', 'archives', 'logs', '.pytest_cache', 'htmlcov', 'coverage.xml', '.mypy_cache', '.tox', 'build', 'dist', '.eggs', '*.egg-info'}
EXCLUDED_FILES = {'canon_validator_backup.py', 'resume_engine_backup.py', 'fix_structural_debt_backup.py', '*.pyc', '*.pyo', '*.pyd', '.DS_Store', 'Thumbs.db'}
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
        print(f"    ❌ {model_name} failed to generate: {e}")
        return None

def check_and_fix_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
    except UnicodeDecodeError:
        return False # Skip binary files

    # 1. Initial Check: Is the code already valid?
    try:
        compile(source, file_path, 'exec')
        return False 
    except SyntaxError as e:
        error_msg = f"{e.msg} at line {e.lineno}"
        print(f"🔥 Syntax Error in {file_path}: {error_msg}")
    except Exception as e:
        error_msg = str(e)
        print(f"🔥 Unknown Error in {file_path}: {error_msg}")

    # 2. Tiered Repair Loop
    for model_name in REPAIR_MODELS:
        print(f"  🤖 Engaging {model_name}...")
        
        fixed_code = get_llm_syntax_fix(source, file_path, error_msg, model_name)

        if fixed_code:
            # 3. Verify the fix immediately
            try:
                compile(fixed_code, file_path, 'exec')
                
                # If we get here, the code is valid! Save it.
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_code)
                print(f"  ✅ FIXED by {model_name}")
                return True
            
            except SyntaxError as verify_error:
                print(f"    ⚠️ {model_name} proposed code was still broken: {verify_error.msg}")
                # Loop continues to the next model in the list
                continue
    
    # If the loop finishes, all available models failed.
    print(f"  ❌ All models failed to repair {file_path}. Requires manual fix.")
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root-dir', type=str, default='/app')
    args = parser.parse_args()

    print(f"🚀 Starting Cost-Optimized Syntax Repair (Models: {REPAIR_MODELS})...")
    count = 0
    
    # Get target files from manifest or fallback to os.walk
    target_files = get_target_files(args.root_dir)
    print(f"📊 Processing {len(target_files)} files...")
    
    for file_path in target_files:
        if check_and_fix_file(file_path):
            count += 1
    
    print(f"🏁 Syntax Repair Cycle Complete. Files rescued: {count}")

if __name__ == '__main__':
    main()
