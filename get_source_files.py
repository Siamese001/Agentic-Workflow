import os
import json

def get_source_files(root_dir):
    """
    Get only the main source files, excluding logs, temp, and generated files
    """
    source_files = []

    # Only scan these main directories
    source_dirs = [
        '01_agentic_core',
        '02_apps',
        '03_runtime',
        '04_tools',
        '05_data',
        '06_data',
        '07_config',
        '08_scripts',
        # Root level Python files
        '.'
    ]

    excluded_files = {
        'canon_validator_backup.py',
        'resume_engine_backup.py',
        'fix_structural_debt_backup.py',
        '__pycache__',
        '.pyc',
        '.pyo',
        '.pyd'
    }

    for dir_name in source_dirs:
        scan_path = os.path.join(root_dir, dir_name)
        if not os.path.exists(scan_path):
            continue

        if dir_name == '.':
            # Only scan root-level Python files
            for file in os.listdir(scan_path):
                if (file.endswith('.py') and
                    not any(x in file for x in excluded_files) and
                    not file.startswith('.')):
                    source_files.append(os.path.join(scan_path, file))
        else:
            # Recursively scan subdirectories
            for root, dirs, files in os.walk(scan_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if (file.endswith('.py') and
                        not any(x in file for x in excluded_files) and
                        not file.startswith('.')):
                        source_files.append(os.path.join(root, file))

    return source_files

def main():
    root_dir = '/app'
    source_files = get_source_files(root_dir)

    # Convert to relative paths for consistency
    rel_files = [os.path.relpath(f, root_dir) for f in source_files]

    print(f"Found {len(rel_files)} source files")

    # Save as manifest
    with open('active_manifest.json', 'w') as f:
        json.dump(rel_files, f, indent=2)

    print("Saved to active_manifest.json")

if __name__ == '__main__':
    main()

