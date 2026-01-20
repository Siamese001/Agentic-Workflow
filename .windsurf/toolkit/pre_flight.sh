#!/bin/bash
# Zero-Trust Pre-Flight Diagnostic Script
# Collects evidence for security and architectural audit

LOG_DIR=".windsurf/logs"
mkdir -p "$LOG_DIR"

echo "=== Zero-Trust Pre-Flight Diagnostics ==="
echo "Timestamp: $(date -Iseconds)"

# 1. Capture git status and recent changes
echo "[1/6] Capturing git context..."
{
    echo "=== Git Status ==="
    git status
    echo ""
    echo "=== Recent Commits ==="
    git log --oneline -10
} > "$LOG_DIR/git_context.txt"

# 2. Dependency tree (multi-language, depth-limited for performance)
echo "[2/6] Gathering dependency tree..."
npm list --depth=1 > "$LOG_DIR/dep_tree.txt" 2>/dev/null || \
pip freeze > "$LOG_DIR/dep_tree.txt" 2>/dev/null || \
poetry show --tree > "$LOG_DIR/dep_tree.txt" 2>/dev/null || \
cargo tree > "$LOG_DIR/dep_tree.txt" 2>/dev/null || \
echo "No supported package manager" > "$LOG_DIR/dep_tree.txt"

# 3. Vulnerability scan
# Attempt to auto-install pip-audit if missing and pip is available
if command -v pip &> /dev/null && ! command -v pip-audit &> /dev/null; then
    echo "Installing pip-audit..."
    pip install pip-audit &> /dev/null
fi

echo "[3/6] Running vulnerability scan..."
npm audit > "$LOG_DIR/vuln_scan.txt" 2>/dev/null || \
pip-audit --local > "$LOG_DIR/vuln_scan.txt" 2>/dev/null || \
cargo audit > "$LOG_DIR/vuln_scan.txt" 2>/dev/null || \
echo "No vuln scanner available" > "$LOG_DIR/vuln_scan.txt"

# 4. Circular dependency check (JS/TS only)
echo "[4/6] Checking circular dependencies..."
npx madge --circular . > "$LOG_DIR/circular_deps.txt" 2>/dev/null || echo "N/A" > "$LOG_DIR/circular_deps.txt"

# 5. God files / large files (Excluding node_modules and vendors)
echo "[5/6] Identifying large files..."
git ls-files | xargs wc -l 2>/dev/null | sort -nr | head -n 15 > "$LOG_DIR/large_files.txt"

# 6. Run tests to establish baseline
# Added -vv and stderr capture to diagnose import errors
echo "[6/6] Establishing test baseline..."
npm test -- --watchAll=false > "$LOG_DIR/test_baseline.txt" 2>&1 || \
pytest -vv > "$LOG_DIR/test_baseline.txt" 2>&1 || \
cargo test > "$LOG_DIR/test_baseline.txt" 2>/dev/null || \
echo "No test runner detected" > "$LOG_DIR/test_baseline.txt"

echo ""
echo "=== Pre-Flight Complete ==="
echo "Logs generated in $LOG_DIR:"
ls -la "$LOG_DIR"
