#!/usr/bin/env bash
# Utility script to ensure a reproducible, clean repository before a major refactor.

set -euo pipefail

REMOTE="origin"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
FORCE=0

usage() {
    cat <<'USAGE'
prepare_clean_refactor.sh [options]

Ensures the working tree is synced with the selected remote branch and
removes any untracked artifacts. Useful before starting a large refactor.

Options:
  --remote <name>   Git remote to pull from (default: origin)
  --branch <name>   Branch to reset to (default: current checked out branch)
  --force           Proceed even if the working tree contains changes
  -h, --help        Display this help text
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --remote)
            REMOTE="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --force)
            FORCE=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "This script must be run inside a git repository." >&2
    exit 1
fi

if [[ $FORCE -eq 0 ]]; then
    if ! git diff --quiet --ignore-submodules HEAD || ! git diff --quiet --ignore-submodules --cached; then
        echo "Working tree contains changes. Commit, stash, or rerun with --force to discard them." >&2
        exit 1
    fi
fi

info() {
    printf '\n[clean-refactor] %s\n' "$1"
}

warn() {
    printf '\n[clean-refactor][WARN] %s\n' "$1" >&2
}

info "Fetching latest history from '$REMOTE'"
git fetch "$REMOTE" --prune

if git rev-parse --verify "$REMOTE/$BRANCH" >/dev/null 2>&1; then
    info "Hard resetting to $REMOTE/$BRANCH"
    git reset --hard "$REMOTE/$BRANCH"
else
    warn "Remote branch $REMOTE/$BRANCH not found. Skipping hard reset."
fi

info "Removing ignored/untracked files"
git clean -fdx

info "Repository is ready for a clean refactor."
