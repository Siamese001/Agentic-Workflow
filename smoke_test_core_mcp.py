"""
Simple Smoke Test for Core MCPs
Minimal connectivity test without complex validation
"""
import logging
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SmokeTest")


def test_redis_connectivity():
    """Test basic Redis connectivity"""
    logger.info("\n=== Redis Smoke Test ===")

    try:
        from action_registry import ActionRegistry
        registry = ActionRegistry()
        tools = registry.get_tool_map()

        # Check if Redis tools exist
        string_set = tools.get('string_set')
        string_get = tools.get('string_get')

        if not string_set or not string_get:
            logger.error("❌ Redis tools not found in registry")
            return False

        logger.info("✅ Redis tools found in registry")

        # Test simple SET/GET
        test_key = "smoke:test"
        test_value = "test123"

        # Test SET
        set_result = string_set(test_key, test_value)
        logger.info(f"SET result: {set_result[:50]}...")

        # Test GET
        get_result = string_get(test_key)
        logger.info(f"GET result: {get_result}")

        if test_value in get_result:
            logger.info("✅ Redis basic operations work")
            return True
        else:
            logger.error("❌ Redis GET/SET mismatch")
            return False

    except Exception as e:
        logger.error(f"❌ Redis test failed: {e}")
        return False


def test_filesystem_connectivity():
    """Test basic Filesystem connectivity"""
    logger.info("\n=== Filesystem Smoke Test ===")

    try:
        from action_registry import ActionRegistry
        registry = ActionRegistry()
        tools = registry.get_tool_map()

        # Check filesystem tools
        save_file = tools.get('save_file')
        read_file = tools.get('read_file')

        if not save_file or not read_file:
            logger.error("❌ Filesystem tools not found in registry")
            return False

        logger.info("✅ Filesystem tools found in registry")

        # Test file operations
        test_file = "smoke_test.txt"
        test_content = "smoke test content"

        # Test save_file - check signature
        logger.info("Testing save_file...")
        try:
            # Use the correct signature: save_file(content, path)
            save_result = save_file(test_content, test_file)
            logger.info(
                f"save_file(content, path) result: {save_result[:50]}...")
        except Exception as e:
            logger.error(f"❌ save_file failed: {e}")
            return False

        # Test read_file
        try:
            read_result = read_file(test_file)
            logger.info(f"read_file result: {read_result[:50]}...")

            if test_content in read_result:
                logger.info("✅ Filesystem operations work")
                # Cleanup
                os.remove(test_file)
                return True
            else:
                logger.error("❌ File content mismatch")
        except Exception as e:
            logger.error(f"❌ read_file failed: {e}")

        # Cleanup
        try:
            os.remove(test_file)
        except:
            pass

        return False

    except Exception as e:
        logger.error(f"❌ Filesystem test failed: {e}")
        return False


def test_gitkraken_connectivity():
    """Test basic GitKraken connectivity"""
    logger.info("\n=== GitKraken Smoke Test ===")

    try:
        from action_registry import ActionRegistry
        registry = ActionRegistry()
        tools = registry.get_tool_map()

        # Check GitKraken tools
        commit = tools.get('commit')

        if not commit:
            logger.error("❌ GitKraken commit tool not found in registry")
            logger.info("Available tools: " + ", ".join(tools.keys()))
            return False

        logger.info("✅ GitKraken tools found in registry")

        # Test commit operation
        test_file = "smoke_git_test.txt"
        with open(test_file, 'w') as f:
            f.write("smoke test for git")

        try:
            commit_result = commit(test_file, "smoke test commit")
            logger.info(f"Commit result: {str(commit_result)[:100]}...")
            logger.info("✅ GitKraken commit works")
            return True
        except Exception as e:
            logger.error(f"❌ Commit failed: {e}")
            return False
        finally:
            try:
                os.remove(test_file)
            except:
                pass

    except Exception as e:
        logger.error(f"❌ GitKraken test failed: {e}")
        return False


def test_time_mcp_connectivity():
    """Test Time MCP connectivity"""
    logger.info("\n=== Time MCP Smoke Test ===")

    try:
        from action_registry import ActionRegistry
        registry = ActionRegistry()
        tools = registry.get_tool_map()

        # Check Time MCP tools
        get_current_time = tools.get('get_current_time')
        convert_time = tools.get('convert_time')

        if not get_current_time or not convert_time:
            logger.error("❌ Time MCP tools not found in registry")
            return False

        logger.info("✅ Time MCP tools found in registry")

        # Test get_current_time
        time_result = get_current_time("UTC")
        logger.info(f"Current time: {time_result}")

        # Test convert_time
        convert_result = convert_time("UTC", "14:00", "America/New_York")
        logger.info(f"Converted time: {convert_result}")

        logger.info("✅ Time MCP operations work")
        return True

    except Exception as e:
        logger.error(f"❌ Time MCP test failed: {e}")
        return False


def check_environment():
    """Check environment variables"""
    logger.info("\n=== Environment Check ===")

    # Check Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    logger.info(f"REDIS_URL: {redis_url}")

    # Check Gemini API
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        logger.info("✅ GEMINI_API_KEY is set")
    else:
        logger.warning("⚠️ GEMINI_API_KEY not set")

    # Check Pinecone
    pinecone_key = os.getenv("PINECONE_API_KEY")
    if pinecone_key:
        logger.info("✅ PINECONE_API_KEY is set")
    else:
        logger.warning("⚠️ PINECONE_API_KEY not set")


def main():
    """Run all smoke tests"""
    logger.info("="*50)
    logger.info("CORE MCP SMOKE TEST")
    logger.info("="*50)

    # Check environment
    check_environment()

    # Run tests
    results = []

    results.append(("Redis", test_redis_connectivity()))
    results.append(("Filesystem", test_filesystem_connectivity()))
    results.append(("GitKraken", test_gitkraken_connectivity()))
    results.append(("Time MCP", test_time_mcp_connectivity()))

    # Summary
    logger.info("\n" + "="*50)
    logger.info("SMOKE TEST SUMMARY")
    logger.info("="*50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{name}: {status}")

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n🎉 All core MCPs are connected!")
        return True
    else:
        logger.error(f"\n💥 {total - passed} MCP(s) have issues")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

