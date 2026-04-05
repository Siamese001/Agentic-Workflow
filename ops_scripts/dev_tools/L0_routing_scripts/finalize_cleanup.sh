#!/bin/bash
# Finalize Cleanup - Handle orphans and fix merged files

set -e

echo "=========================================="
echo "Finalizing Duplicate File Cleanup"
echo "=========================================="
echo ""

BACKUP_DIR="/workspace/archives/cleanup_backup_$(date +%Y%m%d_%H%M%S)_finalize"
echo "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Clean up merged files (remove duplicate headers)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function to clean merged file
clean_merged_file() {
    local file="$1"
    if [ -f "/workspace/$file" ]; then
        echo "Cleaning: $file"
        # Backup original
        cp "/workspace/$file" "$BACKUP_DIR/$(basename $file).backup"

        # Remove duplicate docstrings and imports after merge markers
        python3 << 'PYTHON_SCRIPT'
import sys
import re

file_path = "/workspace/" + sys.argv[1]

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Split by merge markers
parts = content.split('# ============================================')

if len(parts) > 1:
    # Keep first part (original)
    cleaned = parts[0]

    # Process merged parts
    for i in range(1, len(parts)):
        part = parts[i]

        # Skip the merge comment line
        lines = part.split('\n', 2)
        if len(lines) > 2:
            # Skip docstring if it's duplicate
            rest = lines[2]

            # Remove duplicate imports
            code_lines = []
            in_imports = True
            for line in rest.split('\n'):
                stripped = line.strip()
                # Skip duplicate imports and docstrings at start
                if in_imports:
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        continue
                    if stripped.startswith('from ') or stripped.startswith('import '):
                        continue
                    if not stripped:
                        continue
                    in_imports = False

                code_lines.append(line)

            # Add cleaned content
            cleaned += '\n' + '\n'.join(code_lines)

    # Write cleaned content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    print(f"  ✓ Cleaned: {sys.argv[1]}")
else:
    print(f"  ℹ No merge markers found in: {sys.argv[1]}")

PYTHON_SCRIPT
        python3 -c "import sys; sys.argv.append('$file')" "$file"
    fi
}

# Clean all merged files
clean_merged_file "config/config_models.py"
clean_merged_file "apps_lic/L1_cognition/P3_aggregate/lic_archetypes_models.py"
clean_merged_file "apps_lic/L2_execution/data_models_models.py"
clean_merged_file "apps_rg/L1_cognition/k25_models.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Handle orphan files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# These are legitimate split modules - rename them
echo ""
echo "Renaming legitimate orphan files (removing _2 suffix):"

rename_orphan() {
    local src="$1"
    local dst="$2"
    if [ -f "/workspace/$src" ]; then
        cp "/workspace/$src" "$BACKUP_DIR/$(basename $src).backup"
        mv "/workspace/$src" "/workspace/$dst"
        echo "  ✓ Renamed: $src → $dst"
    fi
}

rename_orphan "apps_lic/L1_cognition/P3_aggregate/route_models_2.py" "apps_lic/L1_cognition/P3_aggregate/route_models.py"
rename_orphan "apps_rg/L1_cognition/P3_aggregate/brief_models_2.py" "apps_rg/L1_cognition/P3_aggregate/brief_models.py"
rename_orphan "apps_rg/L3_orchestration/wf_types_models_2.py" "apps_rg/L3_orchestration/wf_types_models.py"
rename_orphan "config/logic/data_access/get_info/load_models_2.py" "config/logic/data_access/get_info/load_models.py"
rename_orphan "observability/pipeline/data_access/get_info/obs_models_2.py" "observability/pipeline/data_access/get_info/obs_models.py"
rename_orphan "shared/safety/const_ai_part_2.py" "shared/safety/const_ai_part.py"
rename_orphan "shared/types/wf_types_part_2.py" "shared/types/wf_types_part.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Finalization Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Summary:"
echo "  - Cleaned merged files (removed duplicate imports/docstrings)"
echo "  - Renamed 7 orphan files (removed _2 suffix)"
echo "  - Backup saved to: $BACKUP_DIR"
echo ""
