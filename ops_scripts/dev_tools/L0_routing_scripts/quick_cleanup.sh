#!/bin/bash
# Quick Cleanup - One-Command Solution
# Scans, reports, and optionally cleans duplicate files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Duplicate File Cleanup - Quick Start                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will:"
echo "  1. Scan for duplicate files (_2, _3, _part_2, etc.)"
echo "  2. Generate a detailed report"
echo "  3. Optionally clean up identical duplicates"
echo ""

# Step 1: Scan
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Scanning for duplicates..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
bash "$SCRIPT_DIR/cleanup_duplicate_files.sh" --mode scan

# Check if report exists
if [ ! -f "duplicate_scan_report.json" ]; then
    echo "❌ Error: Scan report not found!"
    exit 1
fi

# Parse report for summary
TOTAL=$(grep -o '"total_duplicates": [0-9]*' duplicate_scan_report.json | grep -o '[0-9]*')
IDENTICAL=$(grep -o '"identical_duplicates": [0-9]*' duplicate_scan_report.json | grep -o '[0-9]*')

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Scan Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Total duplicates:    $TOTAL"
echo "  Identical copies:    $IDENTICAL"
echo "  Different content:   $((TOTAL - IDENTICAL))"
echo ""

if [ "$TOTAL" -eq 0 ]; then
    echo "✅ No duplicates found! Project is clean."
    exit 0
fi

# Step 2: Ask about cleanup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Cleanup Options"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "What would you like to do?"
echo ""
echo "  1) Delete identical duplicates (dry-run first)"
echo "  2) Delete identical duplicates (REAL - creates backup)"
echo "  3) Exit (review report manually)"
echo ""
read -p "Enter choice [1-3]: " CHOICE

case $CHOICE in
    1)
        echo ""
        echo "Running dry-run deletion of identical duplicates..."
        bash "$SCRIPT_DIR/cleanup_duplicate_files.sh" --delete-identical
        echo ""
        echo "✅ Dry-run complete! Review the output above."
        echo "   To perform real deletion, run:"
        echo "   bash 08_scripts/cleanup_duplicate_files.sh --delete-identical --no-dry-run"
        ;;
    2)
        echo ""
        echo "⚠️  WARNING: This will DELETE $IDENTICAL files!"
        echo "   (Backup will be created first)"
        echo ""
        read -p "Type 'DELETE' to confirm: " CONFIRM
        if [ "$CONFIRM" = "DELETE" ]; then
            bash "$SCRIPT_DIR/cleanup_duplicate_files.sh" --delete-identical --no-dry-run
            echo ""
            echo "✅ Cleanup complete!"
            echo "   Backup saved to: archives/cleanup_backup_*"
        else
            echo "❌ Cancelled."
        fi
        ;;
    3)
        echo ""
        echo "📊 Review the report at: duplicate_scan_report.json"
        echo "   Or run: bash 08_scripts/cleanup_duplicate_files.sh --help"
        ;;
    *)
        echo "❌ Invalid choice."
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Done!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
