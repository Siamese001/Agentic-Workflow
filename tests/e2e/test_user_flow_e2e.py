"""
E2E test example - should be routed to tests/e2e/
"""
import pytest
from playwright.sync_api import Page

class TestUserFlowE2E:
    """E2E test for complete user flow."""
    
    @pytest.mark.e2e
    def test_user_registration_flow(self, page: Page):
        """Test complete user registration in browser."""
        page.goto("http://localhost:8000/register")
        page.fill("#username", "testuser")
        page.click("#register-button")
        page.wait_for_url("**/dashboard")
