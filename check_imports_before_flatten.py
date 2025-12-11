#!/usr/bin/env python3
"""Check imports for single-file packages before flattening"""

import ast
from pathlib import Path
from collections import defaultdict

def find_single_file_packages():
    """Find directories with only __init__.py"""
    packages = []
    root = Path(".")
    
    for d in root.rglob("*"):
        if not d.is_dir():
            continue
        if d.name == "__pycache__":
            continue
            
        children = [c for c in d.iterdir() if c.name != "__pycache__"]
        if len(children) == 1 and children[0].name == "__init__.py":
            packages.append(d)
    
    return packages

def find_imports_for_packages(packages):
    """Find all imports that reference the single-file packages"""
    imports_by_package = defaultdict(list)
    
    # Convert packages to module paths
    pkg_to_module = {}
    for pkg in packages:
        # Convert path like 'a/b/c' to module 'a.b.c'
        parts = pkg.relative_to(Path(".")).parts
        pkg_to_module[pkg] = ".".join(parts)
    
    # Scan all Python files for imports
    root = Path(".")
    for f in root.rglob("*.py"):
        if f.name == "__init__.py":
            continue
        if any(ex in f.parts for ex in {".git", "__pycache__", "data", "archives", "node_modules"}):
            continue
            
        try:
            with open(f, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
        except:
            continue
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    check_import(alias.name, f, imports_by_package, pkg_to_module)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    check_import(node.module, f, imports_by_package, pkg_to_module)
    
    return imports_by_package

def check_import(module_name, file_path, imports_by_package, pkg_to_module):
    """Check if an import matches any single-file package"""
    for pkg, pkg_module in pkg_to_module.items():
        if module_name == pkg_module or module_name.startswith(pkg_module + "."):
            imports_by_package[pkg].append((file_path, module_name))

def main():
    print("Checking imports for single-file packages...")
    
    packages = find_single_file_packages()
    print(f"\nFound {len(packages)} single-file packages")
    
    imports = find_imports_for_packages(packages)
    
    # Count packages with imports
    with_imports = {pkg: imps for pkg, imps in imports.items() if imps}
    
    print(f"\nPackages with imports: {len(with_imports)}")
    
    if with_imports:
        print("\nImport details (first 10):")
        for i, (pkg, imps) in enumerate(list(with_imports.items())[:10]):
            print(f"\n  {pkg}:")
            for file_path, module in imps[:3]:
                rel_path = file_path.relative_to(Path("."))
                print(f"    - {rel_path}: import {module}")
            if len(imps) > 3:
                print(f"    ... and {len(imps) - 3} more")
    
    # Generate safe flatten list (packages without imports)
    safe_to_flatten = [pkg for pkg in packages if pkg not in with_imports]
    print(f"\nSafe to flatten (no imports): {len(safe_to_flatten)}")
    
    # Write PowerShell script for safe packages only
    with open("flatten_safe_packages.ps1", "w") as f:
        f.write("# Flatten single-file packages (safe ones only)\n")
        f.write("$errorActionPreference = \"Stop\"\n\n")
        
        for pkg in safe_to_flatten:
            rel_pkg = pkg.relative_to(Path("."))
            new_file = pkg.parent / f"{pkg.name}.py"
            rel_new = new_file.relative_to(Path("."))
            
            f.write(f'if (Test-Path "{rel_pkg}\\__init__.py") {{\n')
            f.write(f'    Write-Host "Flattening {rel_pkg}"\n')
            f.write(f'    git mv "{rel_pkg}/__init__.py" "{rel_new}"\n')
            f.write(f'    Remove-Item "{rel_pkg}" -Force\n')
            f.write('}\n\n')
    
    print("\nGenerated flatten_safe_packages.ps1 for packages without imports")

if __name__ == "__main__":
    main()
