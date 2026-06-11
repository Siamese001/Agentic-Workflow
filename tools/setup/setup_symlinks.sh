#!/usr/bin/env bash
# setup_symlinks.sh — POSIX contributor symlink setup for MCP config mirrors.
#
# Creates symlinks so deprecated global editor mirrors read the repo SSOT:
#   ~/.codeium/windsurf/mcp_config.json  ->  <repo>/.mcp.json
#
# Idempotent; safe to re-run. Backs up any pre-existing regular file before
# replacing it with a symlink. The --include-agents-md flag is retained for
# compatibility, but root AGENTS.md is already the SSOT and is not replaced.
#
# Usage:
#   bash tools/setup/setup_symlinks.sh
#   bash tools/setup/setup_symlinks.sh --include-agents-md
#   bash tools/setup/setup_symlinks.sh --dry-run

set -euo pipefail

INCLUDE_AGENTS_MD=0
DRY_RUN=0
FORCE=0

for arg in "$@"; do
    case "$arg" in
        --include-agents-md) INCLUDE_AGENTS_MD=1 ;;
        --dry-run)           DRY_RUN=1 ;;
        --force)             FORCE=1 ;;
        -h|--help)
            sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg" >&2
            exit 2
            ;;
    esac
done

log() { echo "[setup_symlinks] $*"; }

new_file_symlink() {
    local link_path="$1"
    local target_path="$2"

    if [[ ! -e "$target_path" ]]; then
        echo "ERROR: target does not exist: $target_path" >&2
        return 1
    fi
    local target_real
    target_real="$(readlink -f "$target_path")"

    local parent
    parent="$(dirname "$link_path")"
    if [[ ! -d "$parent" ]]; then
        if [[ $DRY_RUN -eq 1 ]]; then
            log "DRY-RUN: would mkdir -p $parent"
        else
            mkdir -p "$parent"
        fi
    fi

    if [[ -L "$link_path" ]]; then
        local current_real
        current_real="$(readlink -f "$link_path" 2>/dev/null || echo "")"
        if [[ "$current_real" == "$target_real" ]]; then
            log "OK: $link_path already symlinks to $target_real"
            return 0
        fi
        log "Replacing stale symlink at $link_path"
        [[ $DRY_RUN -eq 1 ]] || rm -f "$link_path"
    elif [[ -e "$link_path" ]]; then
        local backup="${link_path}.pre-symlink-backup"
        log "Backing up existing file: $link_path -> $backup"
        if [[ $DRY_RUN -eq 0 ]]; then
            if [[ -e "$backup" ]]; then
                if [[ $FORCE -eq 0 ]]; then
                    echo "ERROR: backup already exists: $backup (pass --force to overwrite)" >&2
                    return 1
                fi
                rm -f "$backup"
            fi
            mv "$link_path" "$backup"
        fi
    fi

    if [[ $DRY_RUN -eq 1 ]]; then
        log "DRY-RUN: would symlink $link_path -> $target_real"
    else
        ln -s "$target_real" "$link_path"
        log "Created: $link_path -> $target_real"
    fi
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"

repo_mcp="$repo_root/.mcp.json"
global_mcp="$HOME/.codeium/windsurf/mcp_config.json"

log "Repo root: $repo_root"
log "Mode: $([[ $DRY_RUN -eq 1 ]] && echo DRY-RUN || echo APPLY)"

log "--- MCP config ---"
new_file_symlink "$global_mcp" "$repo_mcp"

if [[ $INCLUDE_AGENTS_MD -eq 1 ]]; then
    log "--- AGENTS.md ---"
    log "SKIP: root AGENTS.md is already the SSOT; no legacy symlink is created"
fi

log "Done."
