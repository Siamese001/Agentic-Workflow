from __future__ import annotations
"""
Sovereign Playwright MCP Client – Phase 14
L3 Routed | L5 Shielded | L6 Observable

Visual & Behavioral Intelligence for external validation.
Designed for L6 Observability to ensure external outputs meet Sovereign Canon.
"""
import logging
from typing import Dict, Any, Optional
from agentic_core.config.blueprint_sovereign.sovereign_config import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

Logger: Any = logging.getLogger('L2.Playwright')

class SovereignPlaywrightMcpClient(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    Playwright MCP Client for visual and behavioral validation.
    
    This client doesn't just "browse"; it validates.
    Used by L6 Observability to ensure external outputs meet Sovereign Canon.
    """

    def __init__(self):
        """Initialize Playwright client with sovereign routing."""
        super().__init__()
        self.router = SovereignMCPRouter(role='browser_validation')
        self.initialized = False
        self._mcp_audit('init')
        Logger.info('[L2 PLAYWRIGHT] Client initialized')

    async def initialize(self) -> Any:
        """Async initialization of MCP router."""
        try:
            await self.router.initialize()
            self.initialized = True
            Logger.info('[L2 PLAYWRIGHT] Router initialized successfully')
        except Exception as e:
            Logger.error(f'[L2 PLAYWRIGHT] Initialization failed: {e}')
            raise

    async def _ensure_initialized(self):
        """Ensure MCP client is initialized."""
        if not self.initialized:
            await self.initialize()

    async def navigate_and_capture(self, url: str, wait_until: str='networkidle') -> Dict[str, Any]:
        """
        Navigates to a URL, waits for load, and returns a structural/visual snapshot.
        
        Args:
            url: Target URL to navigate to
            wait_until: Wait condition (networkidle, load, domcontentloaded)
            
        Returns:
            Dict with status, screenshot data, and content
        """
        if not config.PLAYWRIGHT_MCP_ENABLED:
            return {'status': 'error', 'message': 'Playwright MCP disabled'}
        await self._ensure_initialized()
        Logger.info(f'🌐 [L2 PLAYWRIGHT] Validating URL: {url}')
        try:
            page_result: Any = await self.router.manager.call_tool(tool_name='mcp6_browser_navigate', args={'url': url})
            if wait_until == 'networkidle':
                await self.router.manager.call_tool(tool_name='mcp6_browser_wait_for', args={'time': 2})
            screenshot: Any = await self.router.manager.call_tool(tool_name='mcp6_browser_take_screenshot', args={'fullPage': config.PLAYWRIGHT_SCREENSHOT_ON_FAILURE, 'type': 'png'})
            snapshot: Any = await self.router.manager.call_tool(tool_name='mcp6_browser_snapshot', args={})
            Logger.info(f'✅ [L2 PLAYWRIGHT] Successfully captured: {url}')
            return {'status': 'success', 'url': url, 'screenshot_data': screenshot.get('data') if isinstance(screenshot, dict) else None, 'content': snapshot.get('content') if isinstance(snapshot, dict) else str(snapshot), 'page_result': page_result}
        except Exception as e:
            Logger.error(f'[L2 PLAYWRIGHT] Navigation failed for {url}: {e}')
            if config.PLAYWRIGHT_SCREENSHOT_ON_FAILURE:
                try:
                    failure_screenshot: Any = await self.router.manager.call_tool(tool_name='mcp6_browser_take_screenshot', args={'type': 'png'})
                    return {'status': 'error', 'url': url, 'error': str(e), 'failure_screenshot': failure_screenshot.get('data')}
                except:
                    pass
            return {'status': 'error', 'url': url, 'error': str(e)}

    async def click_element(self, selector: str, element_description: Optional[str]=None) -> Dict[str, Any]:
        """
        Execute a remote click via MCP.
        
        Args:
            selector: CSS selector for the element
            element_description: Human-readable description for L5 validation
            
        Returns:
            Click result
        """
        if not config.PLAYWRIGHT_MCP_ENABLED:
            return {'status': 'error', 'message': 'Playwright MCP disabled'}
        await self._ensure_initialized()
        Logger.info(f'🖱️ [L2 PLAYWRIGHT] Clicking element: {selector}')
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp6_browser_click', args={'ref': selector, 'element': element_description or f'Element: {selector}'})
            Logger.info(f'✅ [L2 PLAYWRIGHT] Click successful: {selector}')
            return {'status': 'success', 'selector': selector, 'result': result}
        except Exception as e:
            Logger.error(f'[L2 PLAYWRIGHT] Click failed for {selector}: {e}')
            return {'status': 'error', 'selector': selector, 'error': str(e)}

    async def type_text(self, selector: str, text: str, submit: bool=False) -> Dict[str, Any]:
        """
        Type text into an element.
        
        Args:
            selector: CSS selector for the input element
            text: Text to type
            submit: Whether to press Enter after typing
            
        Returns:
            Type result
        """
        if not config.PLAYWRIGHT_MCP_ENABLED:
            return {'status': 'error', 'message': 'Playwright MCP disabled'}
        await self._ensure_initialized()
        Logger.info(f'⌨️ [L2 PLAYWRIGHT] Typing into: {selector}')
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp6_browser_type', args={'ref': selector, 'text': text, 'submit': submit, 'element': f'Input field: {selector}'})
            Logger.info(f'✅ [L2 PLAYWRIGHT] Type successful: {selector}')
            return {'status': 'success', 'selector': selector, 'result': result}
        except Exception as e:
            Logger.error(f'[L2 PLAYWRIGHT] Type failed for {selector}: {e}')
            return {'status': 'error', 'selector': selector, 'error': str(e)}

    async def take_screenshot(self, filename: Optional[str]=None, full_page: bool=False) -> Dict[str, Any]:
        """
        Take a screenshot of the current page.
        
        Args:
            filename: Optional filename to save screenshot
            full_page: Whether to capture full scrollable page
            
        Returns:
            Screenshot data
        """
        if not config.PLAYWRIGHT_MCP_ENABLED:
            return {'status': 'error', 'message': 'Playwright MCP disabled'}
        await self._ensure_initialized()
        Logger.info(f'📸 [L2 PLAYWRIGHT] Taking screenshot')
        try:
            args: Any = {'type': 'png', 'fullPage': full_page}
            if filename:
                args['filename'] = filename
            result: Any = await self.router.manager.call_tool(tool_name='mcp6_browser_take_screenshot', args=args)
            Logger.info(f'✅ [L2 PLAYWRIGHT] Screenshot captured')
            return {'status': 'success', 'data': result}
        except Exception as e:
            Logger.error(f'[L2 PLAYWRIGHT] Screenshot failed: {e}')
            return {'status': 'error', 'error': str(e)}

    async def get_page_snapshot(self) -> Dict[str, Any]:
        """
        Get accessibility snapshot of current page.
        Better than screenshot for structural analysis.
        
        Returns:
            Page snapshot with accessibility tree
        """
        if not config.PLAYWRIGHT_MCP_ENABLED:
            return {'status': 'error', 'message': 'Playwright MCP disabled'}
        await self._ensure_initialized()
        Logger.info(f'📋 [L2 PLAYWRIGHT] Getting page snapshot')
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp6_browser_snapshot', args={})
            Logger.info(f'✅ [L2 PLAYWRIGHT] Snapshot captured')
            return {'status': 'success', 'snapshot': result}
        except Exception as e:
            Logger.error(f'[L2 PLAYWRIGHT] Snapshot failed: {e}')
            return {'status': 'error', 'error': str(e)}

    async def close_browser(self) -> Dict[str, Any]:
        """
        Close the browser session.
        
        Returns:
            Close result
        """
        if not config.PLAYWRIGHT_MCP_ENABLED:
            return {'status': 'error', 'message': 'Playwright MCP disabled'}
        await self._ensure_initialized()
        Logger.info(f'🔒 [L2 PLAYWRIGHT] Closing browser')
        try:
            result: Any = await self.router.manager.call_tool(tool_name='mcp6_browser_close', args={})
            Logger.info(f'✅ [L2 PLAYWRIGHT] Browser closed')
            return {'status': 'success', 'result': result}
        except Exception as e:
            Logger.error(f'[L2 PLAYWRIGHT] Close failed: {e}')
            return {'status': 'error', 'error': str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Playwright connection.
        
        Returns:
            Health status
        """
        try:
            result: Any = await self.navigate_and_capture('about:blank')
            if result.get('status') == 'success':
                return {'status': 'healthy', 'browser_type': config.PLAYWRIGHT_BROWSER_TYPE, 'headless': config.PLAYWRIGHT_HEADLESS, 'initialized': self.initialized}
            else:
                return {'status': 'unhealthy', 'error': result.get('error', 'Unknown error')}
        except Exception as e:
            Logger.error(f'[L2 PLAYWRIGHT] Health check failed: {e}')
            return {'status': 'unhealthy', 'error': str(e)}

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
_playwright_client: Optional[SovereignPlaywrightMCPClient] = None

def get_playwright_client() -> SovereignPlaywrightMCPClient:
    """Get or create the global Playwright client."""
    global _playwright_client
    if _playwright_client is None:
        _playwright_client = SovereignPlaywrightMCPClient()
    return _playwright_client