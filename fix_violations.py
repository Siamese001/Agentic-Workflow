import os
import re

# ==========================================
# CONFIGURATION
# ==========================================
ROOT_DIR = "."
# Standard excludes + any specific folders you want to protect
EXCLUDE_DIRS = {"archives", "data", "tests", ".git", "__pycache__", "venv", "node_modules", "scrapers"}
DRY_RUN = False  # SET TO FALSE: WILL MODIFY FILES

# ==========================================
# PATTERNS
# ==========================================
REGEX_PRINT = r"^(\s*)print\((.*)\)"
REGEX_EMPTY_EXCEPT = r"^(\s*)except(.*):\s*pass\s*(#.*)?$"
REGEX_RELATIVE_IMPORT = r"^(\s*)from\s+(\.+)([\w\.]*)\s+import\s+(.*)"

def get_module_path(file_path, root, dots_count):
    """
    Resolves relative imports (..utils) to absolute (src.core.utils).
    """
    rel_path = os.path.relpath(os.path.dirname(file_path), root)
    if rel_path == ".":
        return None 
        
    parts = rel_path.replace("\\", "/").split("/")
    
    # Logic: '.' = current dir (0 parent), '..' = parent (1 parent)
    parent_levels = dots_count - 1
    
    if parent_levels < 0: return None
    
    if parent_levels > 0:
        if parent_levels > len(parts):
            return None 
        base_parts = parts[:-parent_levels]
    else:
        base_parts = parts
        
    return ".".join(base_parts)

def fix_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print(f"Skipping binary/non-utf8 file: {file_path}")
        return

    new_lines = []
    modified = False
    
    for i, line in enumerate(lines):
        original_line = line
        
        # ----------------------------------------
        # 1. FIX KEY 08: Relative Imports
        # ----------------------------------------
        match_import = re.match(REGEX_RELATIVE_IMPORT, line)
        if match_import:
            indent, dots, module, imports = match_import.groups()
            base_module = get_module_path(file_path, ROOT_DIR, len(dots))
            
            if base_module:
                full_module = f"{base_module}.{module}" if module else base_module
                full_module = full_module.strip('.')
                
                new_line = f"{indent}from {full_module} import {imports}\n"
                print(f"[Key 08 Fixed] {file_path}:{i+1}")
                print(f"   Old: {line.strip()}")
                print(f"   New: {new_line.strip()}")
                line = new_line
                modified = True

        # ----------------------------------------
        # 2. FIX KEY 04: Empty Except Blocks
        # ----------------------------------------
        match_except = re.match(REGEX_EMPTY_EXCEPT, line)
        if match_except:
            indent, exception_type, comment = match_except.groups()
            exception_type = exception_type if exception_type else ""
            
            # We add a TODO because 'logger' might not be imported in this file yet.
            # This makes the error visible to linters.
            replacement = 'logger.error("Suppressed error in try/except") # TODO: Verify logger import'
            
            if " as " in exception_type:
                var_name = exception_type.split(" as ")[-1].strip()
                replacement = f'logger.error(f"Suppressed error: {{{var_name}}}") # TODO: Verify logger import'

            new_line = f"{indent}except{exception_type}:\n{indent}    {replacement}\n"
            
            print(f"[Key 04 Fixed] {file_path}:{i+1}")
            print(f"   Old: {line.strip()}")
            print(f"   New: {new_line.strip()}")
            line = new_line
            modified = True

        # ----------------------------------------
        # 3. FIX KEY 02: Print Statements
        # ----------------------------------------
        match_print = re.match(REGEX_PRINT, line)
        if match_print:
            indent, content = match_print.groups()
            # Comment out + TODO
            new_line = f"{indent}# print({content}) # TODO: Replace with logger (Key 02)\n"
            
            print(f"[Key 02 Fixed] {file_path}:{i+1}")
            line = new_line
            modified = True

        new_lines.append(line)

    if modified:
        if not DRY_RUN:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"--> SAVED {file_path}")
        else:
            print(f"--> WOULD SAVE {file_path}")

def run_batch_fix():
    print(f"=== STARTING SUBATOMIC BATCH FIX (Dry Run: {DRY_RUN}) ===\n")
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.endswith(".py") and file != "fix_violations.py":
                fix_file(os.path.join(root, file))

if __name__ == "__main__":
    run_batch_fix()
