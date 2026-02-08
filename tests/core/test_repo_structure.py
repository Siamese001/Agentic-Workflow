"""
Repo structure invariant tests.

Enforces ROOT_ALLOWED_PATTERNS from structure_blueprint_config.py:
- No .md files at repo root (must be routed via ARTIFACT_ROUTING_MAP)
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestRootHygiene:
    """Verify no report/plan/RCA markdown files sit at repo root."""

    def test_no_root_markdown_files(self) -> None:
        """All .md files must be in docs/reports/ subfolders, not repo root."""
        root_md = sorted(p.name for p in PROJECT_ROOT.glob("*.md"))
        assert root_md == [], (
            f"Found {len(root_md)} .md file(s) at repo root — violates ROOT_ALLOWED_PATTERNS.\n"
            f"Route these via ARTIFACT_ROUTING_MAP to docs/reports/ subfolders:\n"
            + "\n".join(f"  - {f}" for f in root_md)
        )
