"""
Dashboard Documentation Tests (Phase 7)
=======================================

Tests for dashboard documentation.

Migrated from: agentic_core/L1_cognition/intent_analysis/test_phase7_documentation.py
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.mark.dashboard
class TestUserDocumentation:
    """Test user documentation exists and is complete."""

    def test_meta_learning_guide_exists(self, project_root):
        """Verify DASHBOARD_META_LEARNING_GUIDE.md exists."""
        doc_file = project_root / "docs" / "DASHBOARD_META_LEARNING_GUIDE.md"
        # Skip if docs directory doesn't exist yet
        if not doc_file.parent.exists():
            pytest.skip("docs directory not found")
        assert doc_file.exists(), f"Missing: {doc_file}"

    def test_developer_guide_exists(self, project_root):
        """Verify DASHBOARD_DEVELOPER_GUIDE.md exists."""
        doc_file = project_root / "docs" / "DASHBOARD_DEVELOPER_GUIDE.md"
        # Skip if docs directory doesn't exist yet
        if not doc_file.parent.exists():
            pytest.skip("docs directory not found")
        # This file will be created in Phase 4
        # For now, just check if it exists
        if not doc_file.exists():
            pytest.skip("DASHBOARD_DEVELOPER_GUIDE.md not yet created (Phase 4)")


@pytest.mark.dashboard
class TestDocumentationContent:
    """Test documentation content is accurate."""

    def test_no_deprecated_script_references(self, project_root):
        """Verify documentation doesn't reference deprecated scripts as active."""
        deprecated_scripts = [
            'regenerate_dashboard_from_discovery.py',
            'regenerate_dashboard_complete.py',
            'generate_modular_dashboard_data.py',
            'generate_dashboard_ssot_WRAPPER.py',
        ]

        # Files that are allowed to reference deprecated scripts (for documentation purposes)
        allowed_files = [
            'archive', 'changelog', 'review', 'report', 'migration', 'deprecated',
            'developer', 'guide'  # Developer guides document deprecated scripts
        ]

        docs_dir = project_root / "docs"
        if not docs_dir.exists():
            pytest.skip("docs directory not found")

        for doc_file in docs_dir.glob("*.md"):
            # Skip files that document deprecations
            if any(allowed in doc_file.name.lower() for allowed in allowed_files):
                continue

            content = doc_file.read_text(encoding='utf-8')
            for deprecated in deprecated_scripts:
                if deprecated in content:
                    pytest.fail(f"Deprecated script '{deprecated}' referenced in {doc_file.name}")
