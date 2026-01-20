#!/bin/bash

# ZLM BOOTSTRAP: BATCH 1 (Categories 1 & 3)
# Goal: Fix 'structure_blueprint_1' and 'canonical_truth_1' import errors

LOG_FILE=".windsurf/logs/zlm_batch_1.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Starting ZLM Bootstrap Repair - Batch 1"

# 1. Verify Target Modules Exist (Safety Check)
# We expect 'structure_blueprint.py' and 'canonical_truth.py' to exist if we are removing the '_1'
if [ ! -f "agentic_core/L5_safety/validators/structure_blueprint.py" ]; then
    echo "CRITICAL: 'structure_blueprint.py' not found. Cannot safely rename import. Aborting."
    exit 1
fi
# Note: canonical_truth might be a variable inside a file, or a file itself. 
# We will proceed with the text replacement assuming the user analysis was correct, 
# but rely on pytest verification to confirm.

# 2. List Target Files
FILES=(
    "tests/test_base_class_count_validation.py"
    "tests/test_code_quality_table.py"
    "tests/test_dashboard_data_reconciliation.py"
    "tests/test_toxic_dependency_auditor.py"
    "tests/test_ssot_logic.py"
)

# 3. Shadow & Patch
echo "Applying fixes..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        # Shadow copy
        cp "$file" "$file.zlm.bak"
        
        # Patch: Remove '_1' from specific module names
        # Uses perl for consistent regex handling across environments
        perl -i -pe 's/agentic_core\.L5_safety\.validators\.structure_blueprint_1/agentic_core.L5_safety.validators.structure_blueprint/g' "$file"
        perl -i -pe 's/agentic_core\.L5_safety\.validators\.canonical_truth_1/agentic_core.L5_safety.validators.canonical_truth/g' "$file"
        echo "Patched: $file"
    else
        echo "Warning: $file not found, skipping."
    fi
done

# 4. Verification
echo "Verifying fix with pytest collection..."
COLLECT_OUTPUT=$(pytest --collect-only 2>&1)
ERROR_COUNT=$(echo "$COLLECT_OUTPUT" | grep -c "ImportError")

echo "Remaining Import Errors: $ERROR_COUNT"

# If errors dropped below 9, we consider this batch a success
# We do not revert here automatically because remaining errors are expected (Categories 2, 4, 5)
echo "Batch 1 Complete. Please check if error count dropped from 9."
