import os
import sys
import argparse
import json
import re

def extract_imports_regex(file_path):
    """
    Extract import statements from a Python file using regex.
    This works even if the file has syntax errors.
    """
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return imports
    
    # Regex patterns for various import styles
    patterns = [
        r'^from\s+([^\s]+)\s+import',  # from module import
        r'^import\s+([^\s]+)',         # import module
    ]
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            continue
            
        for pattern in patterns:
            match = re.match(pattern, line, re.MULTILINE)
            if match:
                module = match.group(1)
                # Handle multi-part imports (e.g., from package.module import)
                base_module = module.split('.')[0]
                if not base_module.startswith('.'):
                    imports.add(base_module)
    
    return imports

def find_module_file(module_name, root_dir):
    """
    Find the actual file for a module name within the project.
    """
    # Try different file patterns
    candidates = [
        f"{module_name}.py",
        os.path.join(module_name, "__init__.py"),
    ]
    
    for candidate in candidates:
        full_path = os.path.join(root_dir, candidate)
        if os.path.exists(full_path):
            return candidate
    
    return None

def trace_dependencies(entry_points, root_dir, max_depth=3):
    """
    Trace dependencies using regex-based import extraction.
    """
    visited = set()
    to_visit = set(entry_points)
    active_files = set()
    
    # Convert entry points to relative paths
    entry_files = set()
    for ep in entry_points:
        if os.path.isabs(ep):
            rel_path = os.path.relpath(ep, root_dir)
        else:
            rel_path = ep
        entry_files.add(rel_path)
    
    to_visit.update(entry_files)
    
    print(f"🔍 Tracing dependencies from: {entry_files}")
    
    depth = 0
    while to_visit and depth < max_depth:
        depth += 1
        print(f"\n📦 Depth {depth}: Processing {len(to_visit)} files...")
        
        current_batch = list(to_visit)
        to_visit = set()
        
        for file_path in current_batch:
            if file_path in visited:
                continue
                
            visited.add(file_path)
            active_files.add(file_path)
            
            full_path = os.path.join(root_dir, file_path)
            if not os.path.exists(full_path):
                continue
                
            # Extract imports from this file
            imports = extract_imports_regex(full_path)
            
            for module in imports:
                # Try to find the module file in our project
                module_file = find_module_file(module, root_dir)
                if module_file and module_file not in visited:
                    to_visit.add(module_file)
    
    return sorted(list(active_files))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--entry-points', nargs='+', required=True, 
                        help='Main script(s) that trigger the application')
    parser.add_argument('--root-dir', type=str, default='/app',
                        help='Root directory of the project')
    parser.add_argument('--output', type=str, default='active_manifest.json',
                        help='Output file to store the list of active files')
    parser.add_argument('--max-depth', type=int, default=3,
                        help='Maximum depth to trace imports')
    args = parser.parse_args()

    print("🚀 Starting Regex-Based Dependency Assessment...")
    active_files = trace_dependencies(args.entry_points, args.root_dir, args.max_depth)
    
    print(f"\n✅ Assessment Complete. Found {len(active_files)} active files.")
    
    # Count total Python files for comparison
    total_py_files = 0
    for root, dirs, files in os.walk(args.root_dir):
        total_py_files += sum(1 for f in files if f.endswith('.py'))
    print(f"   Ignored {total_py_files - len(active_files)} potentially unused files.")
    
    with open(args.output, 'w') as f:
        json.dump(active_files, f, indent=2)
    print(f"💾 Manifest saved to {args.output}")

if __name__ == '__main__':
    main()
