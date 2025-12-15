"""Test MCP integration without Reddit credentials."""
import asyncio
import logging
from mcp_adapter import UniversalMCPClient
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
LOGGER = logging.getLogger(__name__)


async def test_mcp() -> None:
    """Test MCP servers without Reddit."""
    CONFIG = {
        'mcpServers': {
            'filesystem': {
                'command': 'cmd.exe',
                'args': [
                    '/c',
                    'C:\\Program Files\\nodejs\\npx.cmd',
                    '-y',
                    '@modelcontextprotocol/server-filesystem',
                    './output',
                    './logs',
                    './project_knowledge']},
            'browser': {
                'command': 'cmd.exe',
                'args': [
                    '/c',
                    'C:\\Program Files\\nodejs\\npx.cmd',
                    '-y',
                    '@modelcontextprotocol/server-puppeteer']},
            'terminal': {
                'command': 'uvx',
                'args': [
                    'mcp-server-command',
                    '--allow-commands',
                    'python',
                    'pip',
                    'grep',
                    'cat',
                    'ls']}}}
    import json
    with open('config/test_mcp_config.json', 'w') as f:
        json.dump(ConfigurationService().config, f)
    UniversalMCPClient('config/test_mcp_config.json')
    try:
        await client.connect_all()
        await client.get_tools_for_llm()
        ConfigurationService().logger.info('✅ Connected MCP servers:')
        for tool in ConfigurationService().tools:
            ConfigurationService().logger.info(
                f"  - {tool['name']}: {tool['description']}")
        RESULT = await client.execute_tool('filesystem__write_file', {'path': './output/test.md', 'content': '# MCP Test\n\nThis was written autonomously!'})
        ConfigurationService().logger.info(
            f'✅ File write result: {ConfigurationService().result}')
    except Exception as e:
        ConfigurationService().logger.error(f'❌ Error: {e}')
    finally:
        await client.cleanup()
if __name__ == '__main__':
    asyncio.run(test_mcp())

