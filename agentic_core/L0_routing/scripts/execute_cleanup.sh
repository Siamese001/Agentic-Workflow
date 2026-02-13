#!/bin/bash
# Execute Duplicate File Cleanup - Docker Safe
# Merges split modules and deletes duplicate directories

set -e

echo "=========================================="
echo "Duplicate File Cleanup - Active Code Only"
echo "=========================================="
echo ""

# Create backup directory
BACKUP_DIR="/workspace/archives/cleanup_backup_$(date +%Y%m%d_%H%M%S)"
echo "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Function to backup file before deletion
backup_file() {
    local file="$1"
    if [ -f "/workspace/$file" ]; then
        local backup_path="$BACKUP_DIR/$file"
        mkdir -p "$(dirname "$backup_path")"
        cp "/workspace/$file" "$backup_path"
        echo "  ✓ Backed up: $file"
    fi
}

# Function to merge files
merge_files() {
    local original="$1"
    shift
    local duplicates=("$@")

    echo ""
    echo "Merging into: $original"

    for dup in "${duplicates[@]}"; do
        if [ -f "/workspace/$dup" ]; then
            backup_file "$dup"
            echo "  → Appending: $dup"
            echo "" >> "/workspace/$original"
            echo "# ============================================" >> "/workspace/$original"
            echo "# Merged from: $dup" >> "/workspace/$original"
            echo "# ============================================" >> "/workspace/$original"
            cat "/workspace/$dup" >> "/workspace/$original"
            rm "/workspace/$dup"
            echo "  ✓ Deleted: $dup"
        fi
    done
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Delete duplicate config/core/ directory"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "/workspace/config/core" ]; then
    echo "Backing up config/core/ directory..."
    cp -r /workspace/config/core "$BACKUP_DIR/config_core_backup"
    echo "Deleting config/core/ directory..."
    rm -rf /workspace/config/core
    echo "✓ Deleted: config/core/"
else
    echo "⚠ config/core/ not found (already deleted?)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Merge config/ split modules"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

merge_files "config/config_models.py" \
    "config/config_models_2.py" \
    "config/config_models_3.py"

merge_files "config/logic/data_access/get_info/load_planning_models.py" \
    "config/logic/data_access/get_info/load_planning_models_2.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Merge apps_lic/ split modules"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

merge_files "apps_lic/L1_cognition/P3_aggregate/lic_archetypes_models.py" \
    "apps_lic/L1_cognition/P3_aggregate/lic_archetypes_models_2.py"

merge_files "apps_lic/L2_execution/data_models_models.py" \
    "apps_lic/L2_execution/data_models_models_2.py" \
    "apps_lic/L2_execution/data_models_models_3.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Merge apps_rg/ split modules"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

merge_files "apps_rg/L1_cognition/k25_models.py" \
    "apps_rg/L1_cognition/k25_models_2.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Merge schemas/ split modules"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

merge_files "schemas/logic/data_access/get_schema_request/load_schema_planning_models.py" \
    "schemas/logic/data_access/get_schema_request/load_schema_planning_models_2.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 6: Merge shared/ split modules"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

merge_files "shared/configuration/config_types_part.py" \
    "shared/configuration/config_types_part_2.py"

merge_files "shared/core/config_types_part.py" \
    "shared/core/config_types_part_2.py"

merge_files "shared/core/exceptions_impl_part.py" \
    "shared/core/exceptions_impl_part_2.py"

merge_files "shared/core/models_types_part.py" \
    "shared/core/models_types_part_2.py"

merge_files "shared/errors/exceptions_impl_part.py" \
    "shared/errors/exceptions_impl_part_2.py"

merge_files "shared/result_types_types_part.py" \
    "shared/result_types_types_part_2.py"

merge_files "shared/types/models_types_part.py" \
    "shared/types/models_types_part_2.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 7: Report orphan files (manual review needed)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "The following files have _2 suffix but no original:"
echo "  - apps_lic/L1_cognition/P3_aggregate/route_models_2.py"
echo "  - apps_rg/L1_cognition/P3_aggregate/brief_models_2.py"
echo "  - apps_rg/L3_orchestration/wf_types_models_2.py"
echo "  - config/logic/data_access/get_info/load_models_2.py"
echo "  - observability/pipeline/data_access/get_info/obs_models_2.py"
echo "  - shared/safety/const_ai_part_2.py"
echo "  - shared/types/wf_types_part_2.py"
echo ""
echo "⚠ These files were NOT modified. Manual review required."

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Cleanup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Summary:"
echo "  - Deleted: config/core/ directory"
echo "  - Merged: 13 split module files"
echo "  - Backup saved to: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "  1. Review merged files for duplicate imports/classes"
echo "  2. Investigate 7 orphan files"
echo "  3. Run tests to verify functionality"
echo "  4. Commit changes if all tests pass"
