#!/bin/bash
# Duplicate File Cleanup - Docker Wrapper Script
# Executes cleanup_duplicate_files.py inside Docker container

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Duplicate File Cleanup - Docker Mode${NC}"
echo -e "${BLUE}========================================${NC}"

# Default values
MODE="scan"
DRY_RUN="--dry-run"
IDENTICAL_ONLY=""
CONFIRM_DELETE_ALL=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --delete-identical)
            MODE="delete"
            IDENTICAL_ONLY="--identical-only"
            shift
            ;;
        --delete-all)
            MODE="delete"
            CONFIRM_DELETE_ALL="--confirm-delete-all"
            shift
            ;;
        --no-dry-run)
            DRY_RUN=""
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --mode scan              Scan and report only (default)"
            echo "  --delete-identical       Delete identical duplicates (dry-run by default)"
            echo "  --delete-all             Delete ALL duplicates (dry-run by default)"
            echo "  --no-dry-run             Actually perform deletion (use with caution)"
            echo "  --help                   Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Scan only"
            echo "  $0 --delete-identical                 # Dry-run delete identical"
            echo "  $0 --delete-identical --no-dry-run    # REAL delete identical"
            echo "  $0 --delete-all --no-dry-run          # REAL delete all (dangerous)"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Build command
CMD="python3 /workspace/08_scripts/cleanup_duplicate_files.py --mode $MODE --root /workspace"

if [ -n "$IDENTICAL_ONLY" ]; then
    CMD="$CMD $IDENTICAL_ONLY"
fi

if [ -n "$CONFIRM_DELETE_ALL" ]; then
    CMD="$CMD $CONFIRM_DELETE_ALL"
fi

if [ -n "$DRY_RUN" ]; then
    CMD="$CMD $DRY_RUN"
fi

# Show what we're doing
echo -e "\n${YELLOW}Configuration:${NC}"
echo -e "  Mode: ${GREEN}$MODE${NC}"
if [ -n "$IDENTICAL_ONLY" ]; then
    echo -e "  Target: ${GREEN}Identical duplicates only${NC}"
elif [ -n "$CONFIRM_DELETE_ALL" ]; then
    echo -e "  Target: ${RED}ALL duplicates (including non-identical)${NC}"
fi
if [ -n "$DRY_RUN" ]; then
    echo -e "  Dry Run: ${GREEN}Yes (safe)${NC}"
else
    echo -e "  Dry Run: ${RED}No (REAL deletion)${NC}"
fi

echo -e "\n${YELLOW}Command:${NC}"
echo -e "  $CMD"

# Confirm if real deletion
if [ -z "$DRY_RUN" ] && [ "$MODE" = "delete" ]; then
    echo -e "\n${RED}⚠️  WARNING: This will ACTUALLY DELETE files!${NC}"
    read -p "Type 'YES' to continue: " CONFIRM
    if [ "$CONFIRM" != "YES" ]; then
        echo -e "${YELLOW}Cancelled.${NC}"
        exit 0
    fi
fi

# Execute in Docker
echo -e "\n${BLUE}Executing in Docker container...${NC}\n"

docker run --rm \
    -v "$PROJECT_ROOT:/workspace" \
    -w /workspace \
    python:3.11-slim \
    bash -c "$CMD"

echo -e "\n${GREEN}✅ Complete!${NC}"

# Show report location
if [ "$MODE" = "scan" ] || [ -n "$DRY_RUN" ]; then
    echo -e "\n${BLUE}📊 Report saved to: duplicate_scan_report.json${NC}"
fi

if [ -z "$DRY_RUN" ] && [ "$MODE" = "delete" ]; then
    echo -e "\n${GREEN}💾 Backup saved to: archives/cleanup_backup_*${NC}"
fi
