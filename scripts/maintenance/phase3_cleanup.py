"""
Phase 3 Cleanup Utility
Moves legacy MCP and cache files to archives/agentic_core_archived/ to enforce Gateway patterns.
"""

import shutil
from pathlib import Path

# configuration
BASE_DIR = Path(__file__).resolve().parents[2]
ARCHIVE_DIR = BASE_DIR / "archives"
MCP_DIR = BASE_DIR / "agentic_core" / "L2_execution" / "mcp"

# Files to Archive (Pattern 1: MCP Sprawl)
MCP_TARGETS = [
    "llm_router_mcp_client.py",
    "archive_client.py",
    "knowledge_graph_sovereign_graph_client.py",
    "caching_redis_mcp_client.py",
    "shared_mcp_client.py",
]


def ensure_archive_dir():
    """Create archive directory if it doesn't exist."""
    if not ARCHIVE_DIR.exists():
        print(f"[+] Creating archive directory: {ARCHIVE_DIR}")
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def archive_files():
    """Move legacy files to archive - FULL DELETION from source."""
    ensure_archive_dir()

    print("=" * 60)
    print("PHASE 3: MCP CLIENT CONSOLIDATION")
    print("=" * 60)

    for filename in MCP_TARGETS:
        src = MCP_DIR / filename
        dst = ARCHIVE_DIR / filename

        if src.exists():
            print(f"[-] Archiving: {filename}")
            try:
                shutil.move(str(src), str(dst))
                # NO TOMBSTONE - Full deletion from source
                print(f"    [OK] Moved to archives/{dst.name}")
            except Exception as e:
                print(f"    [ERR] Failed to move: {e}")
        else:
            if dst.exists():
                print(f"[.] Already archived: {filename}")
            else:
                print(f"[?] File not found (skipped): {filename}")


if __name__ == "__main__":
    archive_files()
    print(
        "\n[SUCCESS] Phase 3 Cleanup Complete. Run tests/integration/test_phase3_consolidation.py to verify."
    )
