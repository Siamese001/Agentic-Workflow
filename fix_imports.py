import os

# Mapping of old imports to new imports
IMPORT_MAPPINGS = {
    # Migrated files
    'from runtime.executor': 'from runtime.inference.executor',
    'from runtime.execution_budget_manager': 'from runtime.inference.execution_budget_manager',
    'from runtime.context_manager': 'from runtime.inference.context_manager',
    'from runtime.runtime_utils': 'from runtime.inference.runtime_utils',
    'from runtime.policy_engine': 'from runtime.orchestration.policy_engine',
    'from runtime.tool_registry': 'from runtime.orchestration.tool_registry',
    'from runtime.cost_tracking': 'from runtime.cost.cost_tracking',
    'from runtime.telemetry': 'from runtime.telemetry.telemetry',
    'from runtime.metrics': 'from runtime.telemetry.metrics',
    'from runtime.observability': 'from runtime.utils.observability',
    # Existing runtime subdirectories (no changes needed, but included for completeness)
    'from runtime.infra': 'from runtime.infra',
    'from runtime.meta': 'from runtime.meta',
    'from runtime.eval': 'from runtime.eval',
    'from runtime.core': 'from runtime.core',
}


def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        changes_made = False

        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes_made = True

        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated: {file_path}")
            return True
        return False

    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False


def fix_all_imports(root_dir):
    """Fix imports in all Python files"""
    print("=== Fixing runtime imports ===")

    updated_files = []

    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_imports_in_file(file_path):
                    updated_files.append(file_path)

    print(f"\n=== Updated {len(updated_files)} files ===")
    for file_path in updated_files:
        print(f"  {file_path}")


if __name__ == "__main__":
    fix_all_imports(".")
