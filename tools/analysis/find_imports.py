import ast
import os
import sys
from collections import defaultdict


def get_imports(file_path):
    with open(file_path, encoding='utf-8', errors='ignore') as f:
        try:
            tree = ast.parse(f.read())
        except (SyntaxError, ValueError):
            return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:  # level 0 means absolute import
                imports.add(node.module.split('.')[0])
    return imports

def main():
    import_locations = defaultdict(set)
    root_dir = os.getcwd()

    internal_packages = {
        "agentic_core", "apps_lic", "apps_rg", "apps_shared",
        "apps_exec", "apps_rfp", "apps_research", "apps_eval",
        "tools", "tests", "ops_scripts", "infrastructure", "system_learning"
    }

    stdlib = set(sys.stdlib_module_names)

    for root, dirs, files in os.walk(root_dir):
        if any(d in root for d in [".venv", ".git", "__pycache__", "artifacts", "archives", ".backup"]):
            continue

        # Determine category
        category = "other"
        if "agentic_core" in root:
            category = "core"
        elif any(app in root for app in ["apps_lic", "apps_rg", "apps_shared", "apps_exec", "apps_rfp", "apps_research", "apps_eval"]):
            category = "apps"
        elif "tests" in root:
            category = "tests"
        elif "tools" in root or "ops_scripts" in root:
            category = "tools/scripts"

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_imports = get_imports(file_path)
                for imp in file_imports:
                    if imp not in stdlib and imp not in internal_packages and not imp.startswith('_') and imp != "setuptools":
                        import_locations[imp].add(category)

    print(f"{'Import':<30} | {'Locations'}")
    print("-" * 50)
    for imp in sorted(import_locations.keys()):
        locs = ", ".join(sorted(list(import_locations[imp])))
        print(f"{imp:<30} | {locs}")

if __name__ == "__main__":
    main()
