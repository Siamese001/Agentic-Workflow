"""
E2E test file - should go to tests/e2e/
"""
import pytest
from playwright.sync_api import Page

class TestExampleE2E:
    """E2E test class."""
    
    @pytest.mark.e2e
    def test_full_flow(self, page: Page):
        """Test full user flow."""
        page.goto("http://localhost:8000")
        page.click("#button")
        page.wait_for_url("**/success")
