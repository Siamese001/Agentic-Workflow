"""
Simple Smoke Test for Core MCPs
Minimal connectivity test without complex validation
"""
import logging
import os
import sys
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger: Any = logging.getLogger('SmokeTest')

def test_redis_connectivity() -> Any:
    """Test basic Redis connectivity"""
    logger.info('\n=== Redis Smoke Test ===')
    try:
        from action_registry import ActionRegistry
        registry: Any = ActionRegistry()
        tools: Any = registry.get_tool_map()
        string_set: Any = tools.get('string_set')
        string_get: Any = tools.get('string_get')
        if not string_set or not string_get:
            logger.error('❌ Redis tools not found in registry')
            return False
        logger.info('✅ Redis tools found in registry')
        test_key: Any = 'smoke:test'
        test_value: Any = 'test123'
        set_result: Any = string_set(test_key, test_value)
        logger.info(f'SET result: {set_result[:50]}...')
        get_result: Any = string_get(test_key)
        logger.info(f'GET result: {get_result}')
        if test_value in get_result:
            logger.info('✅ Redis basic operations work')
            return True
        else:
            logger.error('❌ Redis GET/SET mismatch')
            return False
    except Exception as e:
        pass
        logger.error(f'❌ Redis test failed: {e}')
        return False

def test_filesystem_connectivity() -> Any:
    """Test basic Filesystem connectivity"""
    logger.info('\n=== Filesystem Smoke Test ===')
    try:
        from action_registry import ActionRegistry
        registry: Any = ActionRegistry()
        tools: Any = registry.get_tool_map()
        save_file: Any = tools.get('save_file')
        read_file: Any = tools.get('read_file')
        if not save_file or not read_file:
            logger.error('❌ Filesystem tools not found in registry')
            return False
        logger.info('✅ Filesystem tools found in registry')
        test_file: Any = 'smoke_test.txt'
        test_content: Any = 'smoke test content'
        logger.info('Testing save_file...')
        try:
            save_result: Any = save_file(test_content, test_file)
            logger.info(f'save_file(content, path) result: {save_result[:50]}...')
        except Exception as e:
            pass
            logger.error(f'❌ save_file failed: {e}')
            return False
        try:
            read_result: Any = read_file(test_file)
            logger.info(f'read_file result: {read_result[:50]}...')
            if test_content in read_result:
                logger.info('✅ Filesystem operations work')
                os.remove(test_file)
                return True
            else:
                logger.error('❌ File content mismatch')
        except Exception as e:
            pass
            logger.error(f'❌ read_file failed: {e}')
        try:
            os.remove(test_file)
        except Exception:
            pass
            pass
        return False
    except Exception as e:
        pass
        logger.error(f'❌ Filesystem test failed: {e}')
        return False

def test_gitkraken_connectivity() -> Any:
    """Test basic GitKraken connectivity"""
    logger.info('\n=== GitKraken Smoke Test ===')
    try:
        from action_registry import ActionRegistry
        registry: Any = ActionRegistry()
        tools: Any = registry.get_tool_map()
        commit: Any = tools.get('commit')
        if not commit:
            logger.error('❌ GitKraken commit tool not found in registry')
            logger.info('Available tools: ' + ', '.join(tools.keys()))
            return False
        logger.info('✅ GitKraken tools found in registry')
        test_file: Any = 'smoke_git_test.txt'
        with open(test_file, 'w') as f:
            f.write('smoke test for git')
        try:
            commit_result: Any = commit(test_file, 'smoke test commit')
            logger.info(f'Commit result: {str(commit_result)[:100]}...')
            logger.info('✅ GitKraken commit works')
            return True
        except Exception as e:
            pass
            logger.error(f'❌ Commit failed: {e}')
            return False
        finally:
            try:
                os.remove(test_file)
            except Exception:
                pass
                pass
    except Exception as e:
        pass
        logger.error(f'❌ GitKraken test failed: {e}')
        return False

def test_time_mcp_connectivity() -> Any:
    """Test Time MCP connectivity"""
    logger.info('\n=== Time MCP Smoke Test ===')
    try:
        from action_registry import ActionRegistry
        registry: Any = ActionRegistry()
        tools: Any = registry.get_tool_map()
        get_current_time: Any = tools.get('get_current_time')
        convert_time: Any = tools.get('convert_time')
        if not get_current_time or not convert_time:
            logger.error('❌ Time MCP tools not found in registry')
            return False
        logger.info('✅ Time MCP tools found in registry')
        time_result: Any = get_current_time('UTC')
        logger.info(f'Current time: {time_result}')
        convert_result: Any = convert_time('UTC', '14:00', 'America/New_York')
        logger.info(f'Converted time: {convert_result}')
        logger.info('✅ Time MCP operations work')
        return True
    except Exception as e:
        pass
        logger.error(f'❌ Time MCP test failed: {e}')
        return False

def check_environment() -> Any:
    """Check environment variables"""
    logger.info('\n=== Environment Check ===')
    redis_url: Any = os.getenv('REDIS_URL', 'redis://localhost:6379')
    logger.info(f'REDIS_URL: {redis_url}')
    gemini_key: Any = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        logger.info('✅ GEMINI_API_KEY is set')
    else:
        logger.warning('⚠️ GEMINI_API_KEY not set')
    pinecone_key: Any = os.getenv('PINECONE_API_KEY')
    if pinecone_key:
        logger.info('✅ PINECONE_API_KEY is set')
    else:
        logger.warning('⚠️ PINECONE_API_KEY not set')

def main() -> Any:
    """Run all smoke tests"""
from typing import Any
    logger.info('=' * 50)
    logger.info('CORE MCP SMOKE TEST')
    logger.info('=' * 50)
    check_environment()
    results: Any = []
    results.append(('Redis', test_redis_connectivity()))
    results.append(('Filesystem', test_filesystem_connectivity()))
    results.append(('GitKraken', test_gitkraken_connectivity()))
    results.append(('Time MCP', test_time_mcp_connectivity()))
    logger.info('\n' + '=' * 50)
    logger.info('SMOKE TEST SUMMARY')
    logger.info('=' * 50)
    passed: Any = sum((1 for _, result in results if result))
    total: Any = len(results)
    for name, result in results:
        status: Any = '✅ PASS' if result else '❌ FAIL'
        logger.info(f'{name}: {status}')
    logger.info(f'\nOverall: {passed}/{total} tests passed')
    if passed == total:
        logger.info('\n🎉 All core MCPs are connected!')
        return True
    else:
        logger.error(f'\n💥 {total - passed} MCP(s) have issues')
        return False
if __name__ == '__main__':
    success: Any = main()
    sys.exit(0 if success else 1)
